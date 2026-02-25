"use client";

import {
  TrendingUp,
  Zap,
  Calendar,
  Brain,
  Globe,
  ArrowUpRight,
  ArrowDownRight,
  Flame,
  Clock,
  BarChart3,
  Sparkles,
} from "lucide-react";

function WelcomeSection() {
  const now = new Date();
  const greeting =
    now.getHours() < 12
      ? "Good morning"
      : now.getHours() < 18
        ? "Good afternoon"
        : "Good evening";
  const dateStr = now.toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  });
  const timeStr = now.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className="mb-8 flex items-end justify-between">
      <div>
        <h1 className="font-display text-3xl font-bold tracking-tight text-brand-dark">
          {greeting}!
        </h1>
        <div className="mt-2 flex items-center gap-3">
          <span className="badge bg-brand-accent text-brand-dark">
            <Flame className="mr-1.5 h-3 w-3" />
            TrendFlare.ai
          </span>
          <span className="font-display text-sm text-brand-text-muted">
            {dateStr}
          </span>
        </div>
      </div>
      <div className="flex items-center gap-2 text-brand-text-muted">
        <Clock className="h-4 w-4" />
        <span className="font-display text-sm font-bold">{timeStr}</span>
      </div>
    </div>
  );
}

function EngagementCard() {
  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center gap-3">
          <div className="card-icon">
            <TrendingUp className="h-5 w-5 text-brand-dark" />
          </div>
          <span className="card-title">Today&apos;s Engagement</span>
        </div>
        <ArrowUpRight className="h-5 w-5 text-brand-text-muted" />
      </div>

      <div className="space-y-4">
        <div className="flex items-baseline justify-between">
          <div>
            <p className="stat-value text-brand-green">+24.8%</p>
            <p className="mt-1 text-xs text-brand-text-muted">
              vs last week avg
            </p>
          </div>
          <div className="flex items-center gap-1 rounded-lg bg-green-50 px-2 py-1">
            <ArrowUpRight className="h-3 w-3 text-brand-green" />
            <span className="font-display text-xs font-bold text-brand-green">
              12%
            </span>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3 border-t-2 border-brand-border-light pt-4">
          <div>
            <p className="stat-label">Posts</p>
            <p className="mt-1 font-display text-lg font-bold">12</p>
          </div>
          <div>
            <p className="stat-label">Impressions</p>
            <p className="mt-1 font-display text-lg font-bold">8.4K</p>
          </div>
          <div>
            <p className="stat-label">Clicks</p>
            <p className="mt-1 font-display text-lg font-bold">342</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function TrendingCard() {
  const trends = [
    { topic: "AI in Healthcare", score: 94, delta: "+12" },
    { topic: "Remote Work Tools", score: 87, delta: "+8" },
    { topic: "Sustainable Tech", score: 76, delta: "+23" },
  ];

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center gap-3">
          <div className="card-icon">
            <Zap className="h-5 w-5 text-brand-dark" />
          </div>
          <span className="card-title">Trending Now</span>
        </div>
        <ArrowUpRight className="h-5 w-5 text-brand-text-muted" />
      </div>

      <div className="space-y-3">
        {trends.map((trend, i) => (
          <div
            key={trend.topic}
            className="flex items-center justify-between rounded-xl border-2 border-brand-border-light px-4 py-3 transition-colors hover:border-brand-border hover:bg-brand-bg-muted"
          >
            <div className="flex items-center gap-3">
              <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand-bg-muted font-display text-xs font-bold text-brand-text-muted">
                {i + 1}
              </span>
              <span className="font-display text-sm font-bold">
                {trend.topic}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-display text-xs font-bold text-brand-green">
                {trend.delta}
              </span>
              <div className="h-1.5 w-16 overflow-hidden rounded-full bg-brand-bg-muted">
                <div
                  className="h-full rounded-full bg-brand-accent"
                  style={{ width: `${trend.score}%` }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ScheduledCard() {
  const posts = [
    {
      platform: "LinkedIn",
      time: "10:00 AM",
      status: "ready",
      color: "bg-blue-500",
    },
    {
      platform: "Instagram",
      time: "2:30 PM",
      status: "ready",
      color: "bg-pink-500",
    },
    {
      platform: "X (Twitter)",
      time: "6:00 PM",
      status: "generating",
      color: "bg-sky-400",
    },
  ];

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center gap-3">
          <div className="card-icon">
            <Calendar className="h-5 w-5 text-brand-dark" />
          </div>
          <span className="card-title">Scheduled Posts</span>
        </div>
        <ArrowUpRight className="h-5 w-5 text-brand-text-muted" />
      </div>

      <div className="mb-4 flex items-baseline gap-2">
        <span className="stat-value">3</span>
        <span className="stat-label">posts today</span>
      </div>

      <div className="space-y-2">
        {posts.map((post) => (
          <div
            key={post.platform}
            className="flex items-center justify-between rounded-xl border-2 border-brand-border-light px-4 py-3"
          >
            <div className="flex items-center gap-3">
              <div className={`h-2.5 w-2.5 rounded-full ${post.color}`} />
              <span className="font-display text-sm font-bold">
                {post.platform}
              </span>
            </div>
            <div className="flex items-center gap-3">
              <span className="font-display text-xs text-brand-text-muted">
                {post.time}
              </span>
              <span
                className={`badge text-[10px] ${
                  post.status === "ready"
                    ? "border-brand-green bg-green-50 text-brand-green"
                    : "border-brand-accent bg-brand-accent-muted text-brand-dark"
                }`}
              >
                {post.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function AIPerformanceCard() {
  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center gap-3">
          <div className="card-icon">
            <Brain className="h-5 w-5 text-brand-dark" />
          </div>
          <span className="card-title">AI Performance</span>
        </div>
        <ArrowUpRight className="h-5 w-5 text-brand-text-muted" />
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div>
          <p className="stat-label">DSPy Score</p>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="stat-value">87</span>
            <span className="stat-label">/100</span>
          </div>
          <div className="mt-2 flex items-center gap-1">
            <ArrowUpRight className="h-3 w-3 text-brand-green" />
            <span className="font-display text-xs font-bold text-brand-green">
              +5 this week
            </span>
          </div>
        </div>
        <div>
          <p className="stat-label">Prompts Optimized</p>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="stat-value">142</span>
          </div>
          <div className="mt-2 flex items-center gap-1">
            <Sparkles className="h-3 w-3 text-brand-accent" />
            <span className="font-display text-xs font-bold text-brand-text-muted">
              auto-tuning active
            </span>
          </div>
        </div>
      </div>

      <div className="mt-5 border-t-2 border-brand-border-light pt-4">
        <div className="flex items-center justify-between">
          <span className="stat-label">Content Quality</span>
          <span className="font-display text-sm font-bold text-brand-green">
            Excellent
          </span>
        </div>
        <div className="mt-2 h-2 overflow-hidden rounded-full bg-brand-bg-muted">
          <div className="h-full w-[87%] rounded-full bg-gradient-to-r from-brand-accent to-brand-green" />
        </div>
      </div>
    </div>
  );
}

function AccountsCard() {
  const accounts = [
    { name: "LinkedIn", connected: true, followers: "2.4K", color: "bg-blue-500" },
    { name: "Instagram", connected: true, followers: "5.1K", color: "bg-pink-500" },
    { name: "X (Twitter)", connected: false, followers: "—", color: "bg-sky-400" },
  ];

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center gap-3">
          <div className="card-icon">
            <Globe className="h-5 w-5 text-brand-dark" />
          </div>
          <span className="card-title">Connected Accounts</span>
        </div>
        <ArrowUpRight className="h-5 w-5 text-brand-text-muted" />
      </div>

      <div className="mb-4 flex items-baseline gap-2">
        <span className="stat-value">2</span>
        <span className="stat-label">of 3 connected</span>
      </div>

      <div className="space-y-2">
        {accounts.map((acct) => (
          <div
            key={acct.name}
            className="flex items-center justify-between rounded-xl border-2 border-brand-border-light px-4 py-3"
          >
            <div className="flex items-center gap-3">
              <div className={`h-2.5 w-2.5 rounded-full ${acct.color}`} />
              <span className="font-display text-sm font-bold">
                {acct.name}
              </span>
            </div>
            <div className="flex items-center gap-3">
              <span className="font-display text-xs text-brand-text-muted">
                {acct.followers}
              </span>
              {acct.connected ? (
                <span className="badge border-brand-green bg-green-50 text-[10px] text-brand-green">
                  Live
                </span>
              ) : (
                <button className="badge border-brand-border bg-brand-bg-muted text-[10px] text-brand-text-muted hover:bg-brand-accent hover:text-brand-dark">
                  Connect
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function QuickActions() {
  return (
    <div className="mt-6 flex items-center gap-3">
      <button className="btn-primary">
        <Sparkles className="mr-2 h-4 w-4" />
        Generate Content
      </button>
      <button className="btn-secondary">
        <BarChart3 className="mr-2 h-4 w-4" />
        View Analytics
      </button>
      <button className="btn-ghost">
        <Calendar className="mr-2 h-4 w-4" />
        Open Calendar
      </button>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <div>
      <WelcomeSection />

      {/* Top row — 3 cards */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <EngagementCard />
        <TrendingCard />
        <ScheduledCard />
      </div>

      {/* Bottom row — 2 cards */}
      <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2">
        <AIPerformanceCard />
        <AccountsCard />
      </div>

      <QuickActions />
    </div>
  );
}
