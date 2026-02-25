"""
SchedulerAgent — Predicts optimal posting times and creates Celery tasks for scheduled posts.
Uses Gemini to analyze patterns and platform-specific best practices.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional

import google.generativeai as genai
import structlog

from core.config import get_settings
from core.celery_app import celery_app
from core.supabase import get_supabase_client

logger = structlog.get_logger()

# Default optimal posting windows by platform
DEFAULT_WINDOWS = {
    "instagram": {
        "best_days": [0, 2, 4],  # Mon, Wed, Fri
        "best_hours": [11, 12, 18, 19, 20],
        "timezone": "America/New_York",
    },
}


class SchedulerAgent:
    def __init__(self):
        self.settings = get_settings()

    async def run(
        self,
        post_id: str,
        platform: str,
        brand_id: str,
    ) -> datetime:
        """
        Determine optimal posting time and create a Celery task.
        Returns the scheduled datetime.
        """
        # Get optimal time
        optimal_time = await self._predict_optimal_time(platform, brand_id)

        # Schedule the Celery task
        self.schedule_publish(post_id, optimal_time)

        # Update post in database
        supabase = get_supabase_client()
        supabase.table("posts").update({
            "scheduled_at": optimal_time.isoformat(),
            "status": "scheduled",
        }).eq("id", post_id).execute()

        logger.info(
            "Post scheduled",
            post_id=post_id,
            at=optimal_time.isoformat(),
            platform=platform,
        )

        return optimal_time

    async def _predict_optimal_time(
        self,
        platform: str,
        brand_id: str,
    ) -> datetime:
        """
        Predict the best time to post based on:
        1. Platform defaults
        2. Historical engagement patterns for this brand
        """
        now = datetime.now(timezone.utc)

        # Get historical patterns
        best_hours = self._analyze_historical_patterns(brand_id, platform)

        if not best_hours:
            # Use platform defaults
            defaults = DEFAULT_WINDOWS.get(platform, DEFAULT_WINDOWS["instagram"])
            best_hours = defaults["best_hours"]
            best_days = defaults["best_days"]
        else:
            best_days = list(range(5))  # Weekdays by default

        # Find the next optimal slot
        candidate = now + timedelta(hours=1)  # At least 1 hour from now
        for _ in range(14):  # Search up to 14 days ahead
            if candidate.weekday() in best_days:
                for hour in sorted(best_hours):
                    slot = candidate.replace(
                        hour=hour, minute=0, second=0, microsecond=0
                    )
                    if slot > now + timedelta(hours=1):
                        return slot
            candidate += timedelta(days=1)

        # Fallback: tomorrow at 10am UTC
        tomorrow = (now + timedelta(days=1)).replace(
            hour=10, minute=0, second=0, microsecond=0
        )
        return tomorrow

    def _analyze_historical_patterns(
        self,
        brand_id: str,
        platform: str,
    ) -> list[int]:
        """Analyze past posts to find hours with highest engagement."""
        try:
            supabase = get_supabase_client()
            result = (
                supabase.table("posts")
                .select("published_at, engagement_score")
                .eq("brand_id", brand_id)
                .eq("platform", platform)
                .eq("status", "published")
                .not_.is_("engagement_score", "null")
                .not_.is_("published_at", "null")
                .order("engagement_score", desc=True)
                .limit(20)
                .execute()
            )

            if not result.data or len(result.data) < 5:
                return []

            # Group by hour and calculate average score
            hour_scores: dict[int, list[float]] = {}
            for post in result.data:
                pub_time = datetime.fromisoformat(post["published_at"].replace("Z", "+00:00"))
                hour = pub_time.hour
                score = post["engagement_score"] or 0
                hour_scores.setdefault(hour, []).append(score)

            # Get top 4 hours by average score
            hour_avgs = {
                h: sum(scores) / len(scores)
                for h, scores in hour_scores.items()
            }
            top_hours = sorted(hour_avgs, key=hour_avgs.get, reverse=True)[:4]
            return sorted(top_hours)

        except Exception as e:
            logger.debug("Historical analysis failed", error=str(e))
            return []

    def schedule_publish(self, post_id: str, publish_at: datetime) -> None:
        """Create a Celery task to publish at the scheduled time."""
        delay = (publish_at - datetime.now(timezone.utc)).total_seconds()
        delay = max(delay, 0)

        celery_app.send_task(
            "agents.publish_agent.publish_post_task",
            args=[post_id],
            countdown=delay,
        )

        logger.info(
            "Celery task scheduled",
            post_id=post_id,
            delay_seconds=int(delay),
        )
