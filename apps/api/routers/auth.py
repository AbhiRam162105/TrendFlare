from fastapi import APIRouter, Depends
from core.auth import get_current_user
from core.supabase import get_supabase_client

router = APIRouter()


@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    """Get current authenticated user profile."""
    supabase = get_supabase_client()
    result = supabase.table("profiles").select("*").eq("id", user["id"]).single().execute()
    return result.data


@router.put("/me")
async def update_profile(
    updates: dict,
    user: dict = Depends(get_current_user),
):
    """Update current user profile."""
    supabase = get_supabase_client()
    allowed_fields = {"full_name", "avatar_url"}
    safe_updates = {k: v for k, v in updates.items() if k in allowed_fields}

    result = (
        supabase.table("profiles")
        .update(safe_updates)
        .eq("id", user["id"])
        .execute()
    )
    return result.data[0] if result.data else {}
