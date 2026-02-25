from fastapi import APIRouter, Depends, HTTPException, status
from core.auth import get_current_user
from core.supabase import get_supabase_client
from models.schemas import ScheduleRequest
from datetime import datetime, timezone
import structlog

logger = structlog.get_logger()

router = APIRouter()


@router.post("/schedule")
async def schedule_post(
    req: ScheduleRequest,
    user: dict = Depends(get_current_user),
):
    """Schedule a post for publishing at a specific time."""
    supabase = get_supabase_client()

    # Verify ownership
    post = supabase.table("posts").select("*, brands(user_id)").eq("id", req.post_id).single().execute()
    if not post.data or post.data.get("brands", {}).get("user_id") != user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.data["status"] == "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post is already published",
        )

    # Validate future time
    if req.scheduled_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scheduled time must be in the future",
        )

    # Update post and create Celery task
    result = (
        supabase.table("posts")
        .update({
            "status": "scheduled",
            "scheduled_at": req.scheduled_at.isoformat(),
        })
        .eq("id", req.post_id)
        .execute()
    )

    # Schedule Celery task
    try:
        from agents.scheduler_agent import SchedulerAgent

        scheduler = SchedulerAgent()
        scheduler.schedule_publish(req.post_id, req.scheduled_at)
        logger.info("Post scheduled", post_id=req.post_id, at=req.scheduled_at.isoformat())
    except Exception as e:
        logger.error("Failed to create celery task", error=str(e))
        # Post is still scheduled in DB, Celery beat can pick it up

    return result.data[0]


@router.post("/publish/{post_id}")
async def publish_now(
    post_id: str,
    user: dict = Depends(get_current_user),
):
    """Immediately publish a post."""
    supabase = get_supabase_client()

    post = supabase.table("posts").select("*, brands(user_id)").eq("id", post_id).single().execute()
    if not post.data or post.data.get("brands", {}).get("user_id") != user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.data["status"] == "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post is already published",
        )

    try:
        from agents.publish_agent import PublishAgent

        publisher = PublishAgent()
        result = await publisher.publish(post.data)

        supabase.table("posts").update({
            "status": "published",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "external_post_id": result.get("id"),
        }).eq("id", post_id).execute()

        # Schedule feedback collection 24hr later
        from agents.feedback_agent import schedule_feedback_collection

        schedule_feedback_collection(post_id)

        return {"published": True, "external_id": result.get("id")}
    except Exception as e:
        logger.error("Publish failed", post_id=post_id, error=str(e))
        supabase.table("posts").update({"status": "failed"}).eq("id", post_id).execute()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Publishing failed: {str(e)}",
        )


@router.get("/status/{post_id}")
async def get_publish_status(
    post_id: str,
    user: dict = Depends(get_current_user),
):
    """Get the publishing status of a post."""
    supabase = get_supabase_client()

    post = (
        supabase.table("posts")
        .select("id, status, scheduled_at, published_at, external_post_id, brands(user_id)")
        .eq("id", post_id)
        .single()
        .execute()
    )
    if not post.data or post.data.get("brands", {}).get("user_id") != user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    return {
        "post_id": post.data["id"],
        "status": post.data["status"],
        "scheduled_at": post.data.get("scheduled_at"),
        "published_at": post.data.get("published_at"),
        "external_post_id": post.data.get("external_post_id"),
    }
