"""
ContentAgent — Uses DSPy with Gemini 2.0 Flash to generate 3 post variants per trend angle.
Includes BootstrapFewShot optimization from historical engagement data.
"""

import json
from dataclasses import dataclass, field
from typing import Optional

import dspy
import google.generativeai as genai
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from core.config import get_settings
from core.supabase import get_supabase_client
from agents.trend_agent import TrendReport, TrendAngle

logger = structlog.get_logger()


@dataclass
class PostVariant:
    content: str
    hook: str
    hashtags: list[str]
    predicted_score: float
    trend_angle: str
    variant_rank: int


@dataclass
class ContentResult:
    variants: list[PostVariant] = field(default_factory=list)


class GeneratePost(dspy.Signature):
    """Generate an engaging social media post from a trend angle and brand voice."""

    trend_angle = dspy.InputField(desc="trending topic angle with keywords")
    brand_voice = dspy.InputField(desc="brand tone, style guide, and voice examples")
    platform = dspy.InputField(desc="target platform: linkedin, instagram, or twitter")
    past_winners = dspy.InputField(desc="examples of high-engagement past posts")

    caption = dspy.OutputField(desc="engaging social media caption with hashtags included at the end")
    hook = dspy.OutputField(desc="compelling first line that stops the scroll, max 15 words")


class ContentAgent:
    def __init__(self):
        self.settings = get_settings()
        self._configure_dspy()

    def _configure_dspy(self):
        """Configure DSPy with Gemini 2.0 Flash."""
        try:
            self.lm = dspy.LM(
                model="gemini/gemini-2.0-flash",
                api_key=self.settings.gemini_api_key,
                temperature=0.8,
                max_tokens=1500,
            )
            dspy.configure(lm=self.lm)
            self.generator = dspy.ChainOfThought(GeneratePost)
            logger.info("DSPy configured with Gemini 2.0 Flash")
        except Exception as e:
            logger.warning("DSPy init failed, using direct Gemini", error=str(e))
            genai.configure(api_key=self.settings.gemini_api_key)
            self.generator = None
            self.model = genai.GenerativeModel("gemini-2.0-flash")

    async def run(
        self,
        trend_report: TrendReport,
        brand_data: dict,
        platform: str,
        tone_override: Optional[str] = None,
    ) -> ContentResult:
        """
        Generate 3 content variants from the top trend angle.
        Uses DSPy with BootstrapFewShot optimization when available.
        """
        if not trend_report.angles:
            logger.warning("No trend angles available")
            return ContentResult()

        # Build brand voice context
        brand_voice = self._build_brand_voice(brand_data, tone_override)

        # Get past winning posts for few-shot context
        past_winners = self._get_past_winners(brand_data["id"], platform)

        # Load compiled DSPy state if available
        self._load_compiled_state(brand_data["id"])

        # Generate 3 variants from the best trend angle
        top_angle = trend_report.angles[0]
        variants = []

        for i in range(3):
            variant = await self._generate_variant(
                angle=top_angle,
                brand_voice=brand_voice,
                platform=platform,
                past_winners=past_winners,
                variant_index=i,
            )
            if variant:
                variant.variant_rank = i + 1
                variants.append(variant)

        # Sort by predicted score descending
        variants.sort(key=lambda v: v.predicted_score, reverse=True)
        for i, v in enumerate(variants):
            v.variant_rank = i + 1

        logger.info("Content generation complete", count=len(variants))
        return ContentResult(variants=variants)

    async def _generate_variant(
        self,
        angle: TrendAngle,
        brand_voice: str,
        platform: str,
        past_winners: str,
        variant_index: int,
    ) -> Optional[PostVariant]:
        """Generate a single post variant."""
        angle_text = (
            f"Angle: {angle.angle}\n"
            f"Keywords: {', '.join(angle.keywords)}\n"
            f"Example hooks: {'; '.join(angle.example_hooks)}\n"
            f"Trending score: {angle.trending_score}/100"
        )

        try:
            if self.generator:
                return self._generate_with_dspy(
                    angle_text, brand_voice, platform, past_winners, angle, variant_index
                )
            else:
                return await self._generate_with_gemini_direct(
                    angle_text, brand_voice, platform, past_winners, angle, variant_index
                )
        except Exception as e:
            logger.error("Variant generation failed", index=variant_index, error=str(e))
            return None

    def _generate_with_dspy(
        self,
        angle_text: str,
        brand_voice: str,
        platform: str,
        past_winners: str,
        angle: TrendAngle,
        variant_index: int,
    ) -> PostVariant:
        """Generate using DSPy's ChainOfThought."""
        style_hint = [
            "Write in a confident, authority-building tone with data points.",
            "Write in a conversational, relatable tone with a personal story angle.",
            "Write in a provocative, contrarian tone that challenges conventional wisdom.",
        ][variant_index % 3]

        result = self.generator(
            trend_angle=f"{angle_text}\nStyle: {style_hint}",
            brand_voice=brand_voice,
            platform=platform,
            past_winners=past_winners or "No past data available yet.",
        )

        # Extract hashtags from caption
        caption = result.caption
        hashtags = [w for w in caption.split() if w.startswith("#")]
        clean_caption = " ".join(w for w in caption.split() if not w.startswith("#"))
        if hashtags:
            clean_caption = clean_caption.strip() + "\n\n" + " ".join(hashtags)

        # Predict engagement score (simple heuristic, DSPy optimizer improves this)
        predicted = self._predict_score(clean_caption, platform, angle.trending_score)

        return PostVariant(
            content=clean_caption,
            hook=result.hook,
            hashtags=hashtags,
            predicted_score=predicted,
            trend_angle=angle.angle,
            variant_rank=0,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=8))
    async def _generate_with_gemini_direct(
        self,
        angle_text: str,
        brand_voice: str,
        platform: str,
        past_winners: str,
        angle: TrendAngle,
        variant_index: int,
    ) -> PostVariant:
        """Fallback: generate directly with Gemini when DSPy is unavailable."""
        style = [
            "authoritative with data points and stats",
            "conversational with a personal story angle",
            "provocative and contrarian, challenging assumptions",
        ][variant_index % 3]

        platform_guide = {
            "linkedin": "Professional tone, 150-300 words, use line breaks and bullet points, end with CTA",
            "instagram": "Casual but polished, 80-150 words, emoji-friendly, strong visual hook",
            "twitter": "Punchy and concise, max 280 chars, thread-ready, quotable statements",
        }

        prompt = f"""Generate a {platform} social media post.

TREND:
{angle_text}

BRAND VOICE:
{brand_voice}

STYLE: {style}

PLATFORM GUIDELINES: {platform_guide.get(platform, "")}

PAST HIGH-PERFORMING POSTS:
{past_winners or "None yet."}

Return ONLY a JSON object with these keys:
- "caption": The full post caption with hashtags at the end
- "hook": The first line / scroll-stopping hook (max 15 words)
- "hashtags": Array of hashtags (without the # symbol)

Return raw JSON, no markdown formatting."""

        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.85,
                max_output_tokens=1500,
            ),
        )

        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]

        data = json.loads(text)
        hashtags = [f"#{h}" if not h.startswith("#") else h for h in data.get("hashtags", [])]
        predicted = self._predict_score(data["caption"], platform, angle.trending_score)

        return PostVariant(
            content=data["caption"],
            hook=data["hook"],
            hashtags=hashtags,
            predicted_score=predicted,
            trend_angle=angle.angle,
            variant_rank=0,
        )

    def _predict_score(self, content: str, platform: str, trending_score: float) -> float:
        """
        Predict engagement score based on content heuristics.
        This is the baseline — DSPy optimizer replaces this with learned weights.
        """
        score = 0.03  # base engagement rate

        # Trending boost
        score += (trending_score / 100) * 0.02

        # Content quality signals
        words = content.split()
        word_count = len(words)

        # Optimal length per platform
        optimal = {"linkedin": 200, "instagram": 100, "twitter": 50}
        target = optimal.get(platform, 150)
        length_score = 1 - abs(word_count - target) / target
        score += max(0, length_score * 0.015)

        # Has hashtags
        hashtag_count = sum(1 for w in words if w.startswith("#"))
        if 3 <= hashtag_count <= 8:
            score += 0.005

        # Has call to action
        cta_words = {"comment", "share", "follow", "subscribe", "thoughts", "agree", "disagree"}
        if any(w.lower().strip("?.!") in cta_words for w in words):
            score += 0.008

        # Has numbers/data
        if any(c.isdigit() for c in content):
            score += 0.005

        return round(min(score, 0.15), 4)

    def _build_brand_voice(self, brand_data: dict, tone_override: Optional[str]) -> str:
        """Build brand voice description from brand data."""
        tone = tone_override or brand_data.get("tone", "professional")
        examples = brand_data.get("voice_examples", [])
        niche = brand_data.get("niche", "")

        voice = f"Brand: {brand_data.get('name', 'Unknown')}\n"
        voice += f"Niche: {niche}\n"
        voice += f"Tone: {tone}\n"

        if brand_data.get("target_audience"):
            voice += f"Target Audience: {brand_data['target_audience']}\n"

        if examples:
            voice += f"\nVoice Examples:\n"
            for ex in examples[:3]:
                voice += f'- "{ex}"\n'

        return voice

    def _get_past_winners(self, brand_id: str, platform: str) -> str:
        """Fetch top-performing past posts for few-shot context."""
        try:
            supabase = get_supabase_client()
            result = (
                supabase.table("posts")
                .select("content, hook, engagement_score")
                .eq("brand_id", brand_id)
                .eq("platform", platform)
                .eq("status", "published")
                .not_.is_("engagement_score", "null")
                .order("engagement_score", desc=True)
                .limit(3)
                .execute()
            )

            if not result.data:
                return ""

            winners = []
            for p in result.data:
                score_pct = (p["engagement_score"] or 0) * 100
                winners.append(
                    f"[Score: {score_pct:.1f}%] Hook: {p.get('hook', 'N/A')}\n{p['content'][:200]}"
                )

            return "\n---\n".join(winners)
        except Exception as e:
            logger.warning("Failed to fetch past winners", error=str(e))
            return ""

    def _load_compiled_state(self, brand_id: str) -> None:
        """Load DSPy compiled state from Supabase if available."""
        if not self.generator:
            return

        try:
            supabase = get_supabase_client()
            result = (
                supabase.table("dspy_state")
                .select("compiled_state")
                .eq("brand_id", brand_id)
                .order("version", desc=True)
                .limit(1)
                .execute()
            )

            if result.data and result.data[0].get("compiled_state"):
                state = result.data[0]["compiled_state"]
                self.generator.load_state(state)
                logger.info("Loaded DSPy compiled state", brand_id=brand_id)
        except Exception as e:
            logger.debug("No DSPy state to load", error=str(e))
