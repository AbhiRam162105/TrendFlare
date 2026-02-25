"""
Pipeline — Orchestrates the full content generation pipeline:
TrendAgent -> ContentAgent -> ImageAgent -> SchedulerAgent

Entry point for the /api/content/generate endpoint.
"""

from dataclasses import asdict
from typing import Optional

import structlog

from core.supabase import get_supabase_client
from agents.trend_agent import TrendAgent
from agents.content_agent import ContentAgent
from agents.image_agent import ImageAgent
from agents.scheduler_agent import SchedulerAgent

logger = structlog.get_logger()


async def run_pipeline(
    brand_data: dict,
    platform: str,
    niche_override: Optional[str] = None,
    tone_override: Optional[str] = None,
) -> dict:
    """
    Run the full content generation pipeline.

    Flow:
    1. TrendAgent discovers current trending angles for the brand's niche
    2. ContentAgent generates 3 post variants using DSPy + Gemini
    3. ImageAgent creates an AI image for each variant
    4. Posts are saved to database as drafts
    5. Return variants for user approval

    Args:
        brand_data: Full brand record from database
        platform: Target platform (linkedin/instagram/twitter)
        niche_override: Optional niche to use instead of brand's default
        tone_override: Optional tone to use instead of brand's default

    Returns:
        dict with variants and trend report
    """
    brand_id = brand_data["id"]
    niche = niche_override or brand_data.get("niche", "technology")

    logger.info(
        "Pipeline started",
        brand_id=brand_id,
        platform=platform,
        niche=niche,
    )

    # ========== Step 1: Trend Discovery ==========
    logger.info("Step 1: Running TrendAgent")
    trend_agent = TrendAgent()
    trend_report = await trend_agent.run(niche=niche, brand_id=brand_id)

    if not trend_report.angles:
        raise ValueError("TrendAgent returned no angles. Check API keys and connectivity.")

    logger.info(
        "TrendAgent complete",
        angles_count=len(trend_report.angles),
        top_angle=trend_report.angles[0].angle,
    )

    # ========== Step 2: Content Generation ==========
    logger.info("Step 2: Running ContentAgent")
    content_agent = ContentAgent()
    content_result = await content_agent.run(
        trend_report=trend_report,
        brand_data=brand_data,
        platform=platform,
        tone_override=tone_override,
    )

    if not content_result.variants:
        raise ValueError("ContentAgent returned no variants. Check Gemini API key.")

    logger.info("ContentAgent complete", variants_count=len(content_result.variants))

    # ========== Step 3: Image Generation ==========
    logger.info("Step 3: Running ImageAgent")
    image_agent = ImageAgent()

    for variant in content_result.variants:
        try:
            image_url = await image_agent.run(
                caption=variant.content,
                brand_data=brand_data,
                platform=platform,
            )
            variant_image_url = image_url
        except Exception as e:
            logger.warning("Image generation failed for variant", error=str(e))
            variant_image_url = None

        # Save variant as draft post in database
        variant.image_url = variant_image_url if hasattr(variant, 'image_url') else None

    # ========== Step 4: Save to Database ==========
    logger.info("Step 4: Saving variants to database")
    supabase = get_supabase_client()
    saved_variants = []

    for variant in content_result.variants:
        post_data = {
            "brand_id": brand_id,
            "content": variant.content,
            "hook": variant.hook,
            "hashtags": variant.hashtags,
            "image_url": getattr(variant, "image_url", None),
            "image_prompt": "",
            "platform": platform,
            "status": "draft",
            "predicted_score": variant.predicted_score,
            "variant_rank": variant.variant_rank,
            "trend_angle": variant.trend_angle,
        }

        result = supabase.table("posts").insert(post_data).execute()

        if result.data:
            saved = result.data[0]
            saved_variants.append({
                "id": saved["id"],
                "content": saved["content"],
                "hook": saved.get("hook"),
                "hashtags": saved.get("hashtags", []),
                "image_url": saved.get("image_url"),
                "predicted_score": saved.get("predicted_score", 0),
                "platform": saved["platform"],
                "trend_angle": saved.get("trend_angle", ""),
            })

    logger.info(
        "Pipeline complete",
        brand_id=brand_id,
        saved_variants=len(saved_variants),
    )

    return {
        "variants": saved_variants,
        "trend_report": {
            "id": trend_report.id,
            "niche": trend_report.niche,
            "angles": [asdict(a) for a in trend_report.angles],
            "created_at": trend_report.created_at,
        },
    }
