"""
PublishAgent — Publishes posts to social platforms via Ayrshare API.
Handles platform-specific formatting and webhook callbacks.
"""

from datetime import datetime, timezone

import requests
import structlog

from core.config import get_settings
from core.celery_app import celery_app
from core.supabase import get_supabase_client

logger = structlog.get_logger()

AYRSHARE_API_URL = "https://app.ayrshare.com/api"


class PublishAgent:
    def __init__(self):
        self.settings = get_settings()
        self.headers = {
            "Authorization": f"Bearer {self.settings.ayrshare_api_key}",
            "Content-Type": "application/json",
        }

    async def publish(self, post_data: dict) -> dict:
        """
        Publish a post to the target platform via Ayrshare.
        Returns the external post data including ID.
        """
        platform = post_data["platform"]
        content = post_data["content"]
        image_url = post_data.get("image_url")

        # Map to Ayrshare platform names
        platform_map = {
            "linkedin": "linkedin",
            "instagram": "instagram",
            "twitter": "twitter",
        }
        ayrshare_platform = platform_map.get(platform, platform)

        # Build Ayrshare request
        payload = {
            "post": content,
            "platforms": [ayrshare_platform],
        }

        if image_url:
            payload["mediaUrls"] = [image_url]

        # Platform-specific options
        if platform == "linkedin":
            payload["linkedinOptions"] = {"visibility": "public"}
        elif platform == "twitter":
            # Handle thread if content > 280 chars
            if len(content) > 280:
                payload["twitterOptions"] = {"thread": True}

        logger.info(
            "Publishing to Ayrshare",
            platform=ayrshare_platform,
            content_length=len(content),
        )

        response = requests.post(
            f"{AYRSHARE_API_URL}/post",
            headers=self.headers,
            json=payload,
            timeout=30,
        )

        if response.status_code in (200, 201):
            result = response.json()
            logger.info("Published successfully", result_id=result.get("id"))
            return result
        else:
            error_body = response.text[:500]
            logger.error(
                "Ayrshare publish failed",
                status=response.status_code,
                body=error_body,
            )
            raise Exception(f"Ayrshare API error ({response.status_code}): {error_body}")

    def get_post_analytics(self, external_post_id: str) -> dict:
        """Fetch analytics for a published post from Ayrshare."""
        response = requests.get(
            f"{AYRSHARE_API_URL}/analytics/post",
            headers=self.headers,
            params={"id": external_post_id},
            timeout=30,
        )

        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(
                "Failed to fetch analytics",
                post_id=external_post_id,
                status=response.status_code,
            )
            return {}


@celery_app.task(name="agents.publish_agent.publish_post_task", bind=True, max_retries=3)
def publish_post_task(self, post_id: str):
    """Celery task: publish a scheduled post."""
    import asyncio

    supabase = get_supabase_client()

    try:
        # Fetch post data
        post = supabase.table("posts").select("*").eq("id", post_id).single().execute()
        if not post.data:
            logger.error("Post not found for publishing", post_id=post_id)
            return

        if post.data["status"] == "published":
            logger.info("Post already published, skipping", post_id=post_id)
            return

        # Publish
        publisher = PublishAgent()
        result = asyncio.get_event_loop().run_until_complete(publisher.publish(post.data))

        # Update status
        supabase.table("posts").update({
            "status": "published",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "external_post_id": result.get("id"),
        }).eq("id", post_id).execute()

        # Schedule feedback collection 24hr later
        from agents.feedback_agent import schedule_feedback_collection
        schedule_feedback_collection(post_id)

        logger.info("Post published via Celery task", post_id=post_id)

    except Exception as e:
        logger.error("Celery publish task failed", post_id=post_id, error=str(e))
        supabase.table("posts").update({"status": "failed"}).eq("id", post_id).execute()
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
