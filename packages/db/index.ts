export type Platform = "instagram";
export type PostStatus = "draft" | "scheduled" | "published" | "failed";

export interface Brand {
  id: string;
  user_id: string;
  name: string;
  niche: string;
  tone: string;
  voice_examples: string[];
  target_audience: string | null;
  created_at: string;
  updated_at: string;
}

export interface Post {
  id: string;
  brand_id: string;
  content: string;
  hook: string | null;
  hashtags: string[];
  image_url: string | null;
  platform: Platform;
  status: PostStatus;
  scheduled_at: string | null;
  published_at: string | null;
  engagement_score: number | null;
  predicted_score: number | null;
  variant_rank: number | null;
  trend_angle: string | null;
  created_at: string;
  updated_at: string;
}

export interface Metrics {
  id: string;
  post_id: string;
  likes: number;
  comments: number;
  shares: number;
  reach: number;
  impressions: number;
  clicks: number;
  sentiment_score: number | null;
  sentiment_breakdown: {
    positive: number;
    neutral: number;
    negative: number;
  } | null;
  fetched_at: string;
}

export interface TrendAngle {
  angle: string;
  keywords: string[];
  example_hooks: string[];
  trending_score: number;
}

export interface TrendReport {
  id: string;
  brand_id: string;
  niche: string;
  angles: TrendAngle[];
  sources: { type: string; count: number }[];
  created_at: string;
}

export interface Profile {
  id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  created_at: string;
}
