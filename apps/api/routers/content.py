from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from core.auth import get_current_user
from core.supabase import get_supabase_client
from models.schemas import (
    BrandCreate,
    BrandResponse,
    GenerateRequest,
    GenerateResponse,
    PostResponse,
)
import structlog

logger = structlog.get_logger()

router = APIRouter()


# ==================== Brands ====================

@router.get("/brands")
async def list_brands(user: dict = Depends(get_current_user)):
    """List all brands for the current user."""
    supabase = get_supabase_client()
    result = (
        supabase.table("brands")
        .select("*")
        .eq("user_id", user["id"])
        .order("created_at", desc=True)
        .execute()
    )
    return {"brands": result.data}


@router.post("/brands")
async def create_brand(
    brand: BrandCreate,
    user: dict = Depends(get_current_user),
):
    """Create a new brand."""
    supabase = get_supabase_client()
    result = (
        supabase.table("brands")
        .insert(
            {
                "user_id": user["id"],
                "name": brand.name,
                "niche": brand.niche,
                "tone": brand.tone,
                "voice_examples": brand.voice_examples,
                "target_audience": brand.target_audience,
            }
        )
        .execute()
    )
    return result.data[0]


@router.put("/brands/{brand_id}")
async def update_brand(
    brand_id: str,
    updates: BrandCreate,
    user: dict = Depends(get_current_user),
):
    """Update a brand."""
    supabase = get_supabase_client()
    # Verify ownership
    existing = (
        supabase.table("brands")
        .select("id")
        .eq("id", brand_id)
        .eq("user_id", user["id"])
        .single()
        .execute()
    )
    if not existing.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

    result = (
        supabase.table("brands")
        .update(updates.model_dump(exclude_none=True))
        .eq("id", brand_id)
        .execute()
    )
    return result.data[0]


# ==================== Content Generation ====================

@router.post("/generate")
async def generate_content(
    req: GenerateRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
):
    """
    Generate 3 content variants for a brand.
    Runs the full pipeline: TrendAgent -> ContentAgent -> ImageAgent.
    """
    supabase = get_supabase_client()

    # Verify brand ownership
    brand = (
        supabase.table("brands")
        .select("*")
        .eq("id", req.brand_id)
        .eq("user_id", user["id"])
        .single()
        .execute()
    )
    if not brand.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

    # Run pipeline
    try:
        from agents.pipeline import run_pipeline

        result = await run_pipeline(
            brand_data=brand.data,
            platform=req.platform,
            niche_override=req.niche_override,
            tone_override=req.tone_override,
        )
        return result
    except Exception as e:
        logger.error("Pipeline failed", error=str(e), brand_id=req.brand_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}",
        )


# ==================== Posts ====================

@router.get("/posts")
async def list_posts(
    brand_id: str,
    status_filter: str | None = None,
    user: dict = Depends(get_current_user),
):
    """List posts for a brand."""
    supabase = get_supabase_client()

    # Verify brand ownership
    brand = (
        supabase.table("brands")
        .select("id")
        .eq("id", brand_id)
        .eq("user_id", user["id"])
        .single()
        .execute()
    )
    if not brand.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

    query = (
        supabase.table("posts")
        .select("*")
        .eq("brand_id", brand_id)
        .order("created_at", desc=True)
    )
    if status_filter:
        query = query.eq("status", status_filter)

    result = query.limit(50).execute()
    return {"posts": result.data}


@router.post("/posts/{post_id}/approve")
async def approve_post(
    post_id: str,
    user: dict = Depends(get_current_user),
):
    """Approve a draft post and move it to scheduled status."""
    supabase = get_supabase_client()

    # Get post and verify ownership through brand
    post = supabase.table("posts").select("*, brands(user_id)").eq("id", post_id).single().execute()
    if not post.data or post.data.get("brands", {}).get("user_id") != user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.data["status"] != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Post is already {post.data['status']}",
        )

    result = (
        supabase.table("posts")
        .update({"status": "scheduled"})
        .eq("id", post_id)
        .execute()
    )
    return result.data[0]


@router.put("/posts/{post_id}")
async def update_post(
    post_id: str,
    updates: dict,
    user: dict = Depends(get_current_user),
):
    """Update a post's content or scheduling."""
    supabase = get_supabase_client()

    post = supabase.table("posts").select("*, brands(user_id)").eq("id", post_id).single().execute()
    if not post.data or post.data.get("brands", {}).get("user_id") != user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    allowed = {"content", "hook", "hashtags", "scheduled_at", "platform"}
    safe = {k: v for k, v in updates.items() if k in allowed}

    result = supabase.table("posts").update(safe).eq("id", post_id).execute()
    return result.data[0]


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    user: dict = Depends(get_current_user),
):
    """Delete a draft post."""
    supabase = get_supabase_client()

    post = supabase.table("posts").select("*, brands(user_id)").eq("id", post_id).single().execute()
    if not post.data or post.data.get("brands", {}).get("user_id") != user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.data["status"] == "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a published post",
        )

    supabase.table("posts").delete().eq("id", post_id).execute()
    return {"deleted": True}
