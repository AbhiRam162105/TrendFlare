from fastapi import APIRouter, Depends, HTTPException, status, Query
from core.auth import get_current_user
from core.supabase import get_supabase_client
from datetime import datetime, timedelta, timezone
import structlog

logger = structlog.get_logger()

router = APIRouter()


@router.get("/overview")
async def get_analytics_overview(
    brand_id: str,
    days: int = Query(default=30, ge=1, le=365),
    user: dict = Depends(get_current_user),
):
    """Get analytics overview for a brand."""
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

    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    # Fetch published posts with metrics
    posts = (
        supabase.table("posts")
        .select("*, metrics(*)")
        .eq("brand_id", brand_id)
        .eq("status", "published")
        .gte("published_at", since)
        .order("engagement_score", desc=True)
        .execute()
    )

    post_data = posts.data or []
    total_posts = len(post_data)

    # Aggregate metrics
    total_reach = 0
    total_likes = 0
    total_comments = 0
    total_shares = 0
    sentiment_pos = 0
    sentiment_neu = 0
    sentiment_neg = 0
    engagement_scores = []
    platform_stats: dict[str, dict] = {}

    for post in post_data:
        metrics_list = post.get("metrics", [])
        if metrics_list:
            m = metrics_list[-1]  # Most recent metrics
            total_reach += m.get("reach", 0)
            total_likes += m.get("likes", 0)
            total_comments += m.get("comments", 0)
            total_shares += m.get("shares", 0)

            sb = m.get("sentiment_breakdown", {})
            sentiment_pos += sb.get("positive", 0)
            sentiment_neu += sb.get("neutral", 0)
            sentiment_neg += sb.get("negative", 0)

        score = post.get("engagement_score", 0) or 0
        engagement_scores.append(score)

        platform = post.get("platform", "unknown")
        if platform not in platform_stats:
            platform_stats[platform] = {"posts": 0, "total_score": 0}
        platform_stats[platform]["posts"] += 1
        platform_stats[platform]["total_score"] += score

    avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0

    # Build engagement trend (group by week)
    engagement_trend = []
    if post_data:
        sorted_posts = sorted(post_data, key=lambda p: p.get("published_at", ""))
        week_buckets: dict[str, list[float]] = {}
        for p in sorted_posts:
            pub_date = p.get("published_at", "")[:10]
            score = p.get("engagement_score", 0) or 0
            week_buckets.setdefault(pub_date, []).append(score)

        for date_str, scores in week_buckets.items():
            engagement_trend.append({
                "date": date_str,
                "score": round(sum(scores) / len(scores) * 100, 2),
            })

    # Sentiment breakdown (normalize)
    total_sentiment = sentiment_pos + sentiment_neu + sentiment_neg
    sentiment = {
        "positive": round(sentiment_pos / total_sentiment * 100, 1) if total_sentiment else 0,
        "neutral": round(sentiment_neu / total_sentiment * 100, 1) if total_sentiment else 0,
        "negative": round(sentiment_neg / total_sentiment * 100, 1) if total_sentiment else 0,
    }

    # Platform breakdown
    platform_breakdown = [
        {
            "platform": p,
            "posts": stats["posts"],
            "avg_score": round(stats["total_score"] / stats["posts"] * 100, 2) if stats["posts"] else 0,
        }
        for p, stats in platform_stats.items()
    ]

    # Top posts (top 5)
    top_posts = post_data[:5]

    return {
        "engagement_trend": engagement_trend,
        "top_posts": top_posts,
        "sentiment_breakdown": sentiment,
        "platform_breakdown": platform_breakdown,
        "total_reach": total_reach,
        "total_posts": total_posts,
        "avg_engagement": round(avg_engagement * 100, 2),
    }


@router.get("/post/{post_id}/metrics")
async def get_post_metrics(
    post_id: str,
    user: dict = Depends(get_current_user),
):
    """Get detailed metrics for a specific post."""
    supabase = get_supabase_client()

    post = supabase.table("posts").select("*, brands(user_id)").eq("id", post_id).single().execute()
    if not post.data or post.data.get("brands", {}).get("user_id") != user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    metrics = (
        supabase.table("metrics")
        .select("*")
        .eq("post_id", post_id)
        .order("fetched_at", desc=True)
        .execute()
    )

    return {
        "post": post.data,
        "metrics_history": metrics.data,
    }
