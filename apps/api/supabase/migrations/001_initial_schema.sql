-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "pgvector";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- Users table (extended from Supabase Auth)
-- =============================================
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    full_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- Brands table
-- =============================================
CREATE TABLE IF NOT EXISTS public.brands (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    niche TEXT NOT NULL,
    tone TEXT NOT NULL DEFAULT 'professional',
    voice_examples JSONB DEFAULT '[]'::jsonb,
    target_audience TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_brands_user_id ON public.brands(user_id);

-- =============================================
-- Posts table
-- =============================================
CREATE TABLE IF NOT EXISTS public.posts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    brand_id UUID NOT NULL REFERENCES public.brands(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    hook TEXT,
    hashtags TEXT[] DEFAULT '{}',
    image_url TEXT,
    image_prompt TEXT,
    platform TEXT NOT NULL CHECK (platform IN ('instagram')),
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'scheduled', 'published', 'failed')),
    scheduled_at TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    external_post_id TEXT,
    engagement_score FLOAT,
    predicted_score FLOAT,
    variant_rank INTEGER,
    trend_angle TEXT,
    embedding vector(384),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_posts_brand_id ON public.posts(brand_id);
CREATE INDEX idx_posts_status ON public.posts(status);
CREATE INDEX idx_posts_scheduled_at ON public.posts(scheduled_at);
CREATE INDEX idx_posts_platform ON public.posts(platform);

-- =============================================
-- Metrics table
-- =============================================
CREATE TABLE IF NOT EXISTS public.metrics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    post_id UUID NOT NULL REFERENCES public.posts(id) ON DELETE CASCADE,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    reach INTEGER DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    sentiment_score FLOAT,
    sentiment_breakdown JSONB DEFAULT '{"positive": 0, "neutral": 0, "negative": 0}'::jsonb,
    fetched_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_metrics_post_id ON public.metrics(post_id);

-- =============================================
-- Trend reports table (cached)
-- =============================================
CREATE TABLE IF NOT EXISTS public.trend_reports (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    brand_id UUID NOT NULL REFERENCES public.brands(id) ON DELETE CASCADE,
    niche TEXT NOT NULL,
    angles JSONB NOT NULL DEFAULT '[]'::jsonb,
    sources JSONB DEFAULT '[]'::jsonb,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_trend_reports_brand_id ON public.trend_reports(brand_id);
CREATE INDEX idx_trend_reports_expires_at ON public.trend_reports(expires_at);

-- =============================================
-- DSPy optimizer state
-- =============================================
CREATE TABLE IF NOT EXISTS public.dspy_state (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    brand_id UUID NOT NULL REFERENCES public.brands(id) ON DELETE CASCADE,
    compiled_state JSONB NOT NULL,
    training_examples JSONB DEFAULT '[]'::jsonb,
    score FLOAT,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_dspy_state_brand_id ON public.dspy_state(brand_id);

-- =============================================
-- Row Level Security (RLS)
-- =============================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.brands ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trend_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dspy_state ENABLE ROW LEVEL SECURITY;

-- Profiles: users can read/update their own profile
CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

-- Brands: users can CRUD their own brands
CREATE POLICY "Users can view own brands"
    ON public.brands FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create brands"
    ON public.brands FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own brands"
    ON public.brands FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own brands"
    ON public.brands FOR DELETE
    USING (auth.uid() = user_id);

-- Posts: users can access posts belonging to their brands
CREATE POLICY "Users can view own posts"
    ON public.posts FOR SELECT
    USING (brand_id IN (SELECT id FROM public.brands WHERE user_id = auth.uid()));

CREATE POLICY "Users can create posts"
    ON public.posts FOR INSERT
    WITH CHECK (brand_id IN (SELECT id FROM public.brands WHERE user_id = auth.uid()));

CREATE POLICY "Users can update own posts"
    ON public.posts FOR UPDATE
    USING (brand_id IN (SELECT id FROM public.brands WHERE user_id = auth.uid()));

CREATE POLICY "Users can delete own posts"
    ON public.posts FOR DELETE
    USING (brand_id IN (SELECT id FROM public.brands WHERE user_id = auth.uid()));

-- Metrics: read-only for users through their posts
CREATE POLICY "Users can view metrics for own posts"
    ON public.metrics FOR SELECT
    USING (post_id IN (
        SELECT p.id FROM public.posts p
        JOIN public.brands b ON p.brand_id = b.id
        WHERE b.user_id = auth.uid()
    ));

-- Trend reports: users can view reports for their brands
CREATE POLICY "Users can view own trend reports"
    ON public.trend_reports FOR SELECT
    USING (brand_id IN (SELECT id FROM public.brands WHERE user_id = auth.uid()));

-- DSPy state: users can view optimizer state for their brands
CREATE POLICY "Users can view own dspy state"
    ON public.dspy_state FOR SELECT
    USING (brand_id IN (SELECT id FROM public.brands WHERE user_id = auth.uid()));

-- =============================================
-- Auto-update timestamps trigger
-- =============================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER brands_updated_at
    BEFORE UPDATE ON public.brands
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER posts_updated_at
    BEFORE UPDATE ON public.posts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- =============================================
-- Auto-create profile on auth signup
-- =============================================
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name, avatar_url)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.raw_user_meta_data->>'full_name',
        NEW.raw_user_meta_data->>'avatar_url'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION handle_new_user();
