"""
TrendAgent — Discovers trending topics using Pytrends + Gemini Search Grounding.
Returns structured TrendReport with scored angles for Instagram content creation.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from typing import Optional

import google.generativeai as genai
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from core.config import get_settings
from core.supabase import get_supabase_client

logger = structlog.get_logger()


@dataclass
class TrendAngle:
    angle: str
    keywords: list[str]
    example_hooks: list[str]
    trending_score: float


@dataclass
class TrendReport:
    id: str = ""
    niche: str = ""
    angles: list[TrendAngle] = field(default_factory=list)
    sources: list[dict] = field(default_factory=list)
    created_at: str = ""


class TrendAgent:
    def __init__(self):
        self.settings = get_settings()
        genai.configure(api_key=self.settings.gemini_api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    async def run(
        self,
        niche: str,
        brand_id: str,
        force_refresh: bool = False,
    ) -> TrendReport:
        """
        Main entry point. Checks cache first, then runs full discovery pipeline.
        """
        # Check cache (6-hour TTL)
        if not force_refresh:
            cached = self._get_cached_report(brand_id, niche)
            if cached:
                logger.info("Using cached trend report", brand_id=brand_id)
                return cached

        logger.info("Running trend discovery", niche=niche, brand_id=brand_id)

        # Step 1: Fetch Google Trends data
        trends_data = self._fetch_google_trends(niche)

        # Step 2: Synthesize with Gemini + search grounding
        report = await self._synthesize_trends(niche, trends_data)

        # Cache the result
        self._cache_report(brand_id, niche, report)

        return report

    def _fetch_google_trends(self, niche: str) -> list[dict]:
        """Fetch trending topics from Google Trends via pytrends."""
        try:
            from pytrends.request import TrendReq

            pytrends = TrendReq(hl="en-US", tz=360)
            pytrends.build_payload([niche], timeframe="now 7-d")

            # Get related queries
            related = pytrends.related_queries()
            results = []

            if niche in related:
                top = related[niche].get("top")
                rising = related[niche].get("rising")

                if top is not None and not top.empty:
                    for _, row in top.head(10).iterrows():
                        results.append({
                            "query": row["query"],
                            "value": int(row["value"]),
                            "type": "top",
                        })

                if rising is not None and not rising.empty:
                    for _, row in rising.head(10).iterrows():
                        results.append({
                            "query": row["query"],
                            "value": int(row["value"]),
                            "type": "rising",
                        })

            logger.info("Google Trends fetched", count=len(results))
            return results

        except Exception as e:
            logger.warning("Google Trends fetch failed, continuing", error=str(e))
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    async def _synthesize_trends(
        self,
        niche: str,
        trends_data: list[dict],
    ) -> TrendReport:
        """Use Gemini 2.0 Flash with search grounding to synthesize top 3 trend angles."""

        prompt = f"""You are a social media trend analyst specializing in Instagram content. Analyze the following data about the "{niche}" niche and identify the top 3 most actionable trending angles for Instagram content creation.

## Google Trends Data (past 7 days):
{json.dumps(trends_data, indent=2) if trends_data else "No Google Trends data available."}

Based on this data AND your knowledge of current Instagram trends (including trending hashtags and Reels topics), return EXACTLY 3 trending angles as a JSON array.

Each angle must have:
- "angle": A clear, specific content angle (not generic)
- "keywords": 5-8 relevant keywords/phrases for this angle
- "example_hooks": 3 scroll-stopping first lines for posts about this angle
- "trending_score": A score from 0-100 based on how trending/timely this is

Return ONLY the JSON array, no markdown formatting or explanation.
Example format:
[
  {{
    "angle": "Specific trend angle here",
    "keywords": ["keyword1", "keyword2", ...],
    "example_hooks": ["Hook 1...", "Hook 2...", "Hook 3..."],
    "trending_score": 85
  }}
]"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2000,
                ),
            )

            # Parse response
            text = response.text.strip()
            # Handle markdown code blocks
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
                text = text.rsplit("```", 1)[0]

            angles_raw = json.loads(text)
            angles = [
                TrendAngle(
                    angle=a["angle"],
                    keywords=a["keywords"],
                    example_hooks=a["example_hooks"],
                    trending_score=a["trending_score"],
                )
                for a in angles_raw[:3]
            ]

            return TrendReport(
                niche=niche,
                angles=angles,
                sources=[
                    {"type": "google_trends", "count": len(trends_data)},
                ],
                created_at=datetime.now(timezone.utc).isoformat(),
            )

        except json.JSONDecodeError as e:
            logger.error("Failed to parse Gemini trend response", error=str(e))
            # Fallback with generic angles
            return TrendReport(
                niche=niche,
                angles=[
                    TrendAngle(
                        angle=f"Latest developments in {niche}",
                        keywords=[niche, "trends", "2025", "innovation"],
                        example_hooks=[
                            f"The {niche} landscape just changed forever.",
                            f"Nobody's talking about this {niche} shift yet.",
                            f"I spent 40 hours researching {niche}. Here's what I found.",
                        ],
                        trending_score=70,
                    )
                ],
                sources=[],
                created_at=datetime.now(timezone.utc).isoformat(),
            )

    def _get_cached_report(self, brand_id: str, niche: str) -> Optional[TrendReport]:
        """Check Supabase for a cached trend report less than 6 hours old."""
        try:
            supabase = get_supabase_client()
            cutoff = (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat()

            result = (
                supabase.table("trend_reports")
                .select("*")
                .eq("brand_id", brand_id)
                .eq("niche", niche)
                .gte("expires_at", datetime.now(timezone.utc).isoformat())
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )

            if result.data:
                r = result.data[0]
                angles = [TrendAngle(**a) for a in r["angles"]]
                return TrendReport(
                    id=r["id"],
                    niche=r["niche"],
                    angles=angles,
                    sources=r.get("sources", []),
                    created_at=r["created_at"],
                )
            return None
        except Exception as e:
            logger.warning("Cache lookup failed", error=str(e))
            return None

    def _cache_report(self, brand_id: str, niche: str, report: TrendReport) -> None:
        """Store trend report in Supabase with 6-hour TTL."""
        try:
            supabase = get_supabase_client()
            expires = (datetime.now(timezone.utc) + timedelta(hours=6)).isoformat()

            result = (
                supabase.table("trend_reports")
                .insert({
                    "brand_id": brand_id,
                    "niche": niche,
                    "angles": [asdict(a) for a in report.angles],
                    "sources": report.sources,
                    "expires_at": expires,
                })
                .execute()
            )

            if result.data:
                report.id = result.data[0]["id"]
                logger.info("Trend report cached", id=report.id)
        except Exception as e:
            logger.warning("Cache write failed", error=str(e))
