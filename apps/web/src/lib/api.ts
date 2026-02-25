const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type FetchOptions = RequestInit & {
  token?: string;
};

async function fetchApi<T>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const { token, ...fetchOptions } = options;

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
    ...fetchOptions.headers,
  };

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...fetchOptions,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `API error: ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Content generation
  generateContent: (brandId: string, platform: string, token: string) =>
    fetchApi<{ variants: ContentVariant[] }>("/api/content/generate", {
      method: "POST",
      body: JSON.stringify({ brand_id: brandId, platform }),
      token,
    }),

  // Posts
  getPosts: (brandId: string, token: string) =>
    fetchApi<{ posts: Post[] }>(`/api/content/posts?brand_id=${brandId}`, { token }),

  approveVariant: (postId: string, token: string) =>
    fetchApi<Post>(`/api/content/posts/${postId}/approve`, {
      method: "POST",
      token,
    }),

  schedulePost: (postId: string, scheduledAt: string, token: string) =>
    fetchApi<Post>(`/api/publishing/schedule`, {
      method: "POST",
      body: JSON.stringify({ post_id: postId, scheduled_at: scheduledAt }),
      token,
    }),

  // Analytics
  getAnalytics: (brandId: string, days: number, token: string) =>
    fetchApi<AnalyticsData>(`/api/analytics/overview?brand_id=${brandId}&days=${days}`, {
      token,
    }),

  // Brands
  getBrands: (token: string) =>
    fetchApi<{ brands: Brand[] }>("/api/content/brands", { token }),

  createBrand: (data: Partial<Brand>, token: string) =>
    fetchApi<Brand>("/api/content/brands", {
      method: "POST",
      body: JSON.stringify(data),
      token,
    }),

  // Health
  health: () => fetchApi<{ status: string }>("/health"),
};

// Types
export interface Brand {
  id: string;
  name: string;
  niche: string;
  tone: string;
  voice_examples: string[];
  created_at: string;
}

export interface ContentVariant {
  id: string;
  content: string;
  hook: string;
  hashtags: string[];
  image_url: string | null;
  predicted_score: number;
  platform: string;
}

export interface Post {
  id: string;
  brand_id: string;
  content: string;
  image_url: string | null;
  platform: string;
  status: "draft" | "scheduled" | "published" | "failed";
  scheduled_at: string | null;
  published_at: string | null;
  engagement_score: number | null;
}

export interface AnalyticsData {
  engagement_trend: { date: string; score: number }[];
  top_posts: Post[];
  sentiment_breakdown: { positive: number; neutral: number; negative: number };
  platform_breakdown: { platform: string; posts: number; avg_score: number }[];
  total_reach: number;
  total_posts: number;
  avg_engagement: number;
}
