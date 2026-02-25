from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# ==================== Brand ====================
class BrandCreate(BaseModel):
    name: str
    niche: str
    tone: str = "professional"
    voice_examples: list[str] = []
    target_audience: Optional[str] = None


class BrandResponse(BaseModel):
    id: str
    user_id: str
    name: str
    niche: str
    tone: str
    voice_examples: list[str]
    target_audience: Optional[str]
    created_at: datetime


# ==================== Content Generation ====================
class GenerateRequest(BaseModel):
    brand_id: str
    platform: str = Field(pattern=r"^(linkedin|instagram|twitter)$")
    niche_override: Optional[str] = None
    tone_override: Optional[str] = None


class ContentVariant(BaseModel):
    id: str
    content: str
    hook: str
    hashtags: list[str]
    image_url: Optional[str]
    predicted_score: float
    platform: str
    trend_angle: str


class GenerateResponse(BaseModel):
    variants: list[ContentVariant]
    trend_report: "TrendReportResponse"


# ==================== Trend Report ====================
class TrendAngle(BaseModel):
    angle: str
    keywords: list[str]
    example_hooks: list[str]
    trending_score: float


class TrendReportResponse(BaseModel):
    id: str
    niche: str
    angles: list[TrendAngle]
    created_at: datetime


# ==================== Posts ====================
class PostResponse(BaseModel):
    id: str
    brand_id: str
    content: str
    hook: Optional[str]
    hashtags: list[str]
    image_url: Optional[str]
    platform: str
    status: str
    scheduled_at: Optional[datetime]
    published_at: Optional[datetime]
    engagement_score: Optional[float]
    predicted_score: Optional[float]
    created_at: datetime


class PostApproveRequest(BaseModel):
    scheduled_at: Optional[datetime] = None


class ScheduleRequest(BaseModel):
    post_id: str
    scheduled_at: datetime


# ==================== Analytics ====================
class EngagementPoint(BaseModel):
    date: str
    score: float


class PlatformBreakdown(BaseModel):
    platform: str
    posts: int
    avg_score: float


class SentimentBreakdown(BaseModel):
    positive: float
    neutral: float
    negative: float


class AnalyticsResponse(BaseModel):
    engagement_trend: list[EngagementPoint]
    top_posts: list[PostResponse]
    sentiment_breakdown: SentimentBreakdown
    platform_breakdown: list[PlatformBreakdown]
    total_reach: int
    total_posts: int
    avg_engagement: float


# ==================== Metrics ====================
class MetricsResponse(BaseModel):
    id: str
    post_id: str
    likes: int
    comments: int
    shares: int
    reach: int
    impressions: int
    clicks: int
    sentiment_score: Optional[float]
    sentiment_breakdown: Optional[dict]
    fetched_at: datetime
