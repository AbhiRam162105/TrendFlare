"use client";

import {
  BarChart3,
  TrendingUp,
  ArrowUpRight,
  ArrowDownRight,
  Eye,
  MessageCircle,
  Share2,
  Heart,
} from "lucide-react";

const engagementData = [
  { date: "Jan 1", score: 3.2 },
  { date: "Jan 8", score: 4.1 },
  { date: "Jan 15", score: 3.8 },
  { date: "Jan 22", score: 5.2 },
  { date: "Jan 29", score: 4.7 },
  { date: "Feb 5", score: 6.1 },
  { date: "Feb 12", score: 5.8 },
  { date: "Feb 19", score: 7.3 },
  { date: "Feb 26", score: 8.2 },
];

const topPosts = [
  {
    title: "AI Healthcare Disruption Thread",
    platform: "linkedin",
    score: 8.2,
    likes: 234,
    comments: 45,
    shares: 67,
  },
  {
    title: "Remote Work Future — 5 Predictions",
    platform: "linkedin",
    score: 7.1,
    likes: 189,
    comments: 32,
    shares: 54,
  },
  {
    title: "Sustainable Tech Stack Guide",
    platform: "twitter",
    score: 6.8,
    likes: 312,
    comments: 28,
    shares: 89,
  },
  {
    title: "Brand Building with AI Tools",
    platform: "instagram",
    score: 6.3,
    likes: 456,
    comments: 67,
    shares: 23,
  },
  {
    title: "Startup Growth Metrics Decoded",
    platform: "linkedin",
    score: 5.9,
    likes: 167,
    comments: 41,
    shares: 38,
  },
];

const platformColors: Record<string, string> = {
  linkedin: "bg-blue-500",
  instagram: "bg-pink-500",
  twitter: "bg-sky-400",
};

export default function AnalyticsPage() {
  const maxScore = Math.max(...engagementData.map((d) => d.score));

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="font-display text-3xl font-bold tracking-tight text-brand-dark">
          Analytics
        </h1>
        <p className="mt-2 font-display text-sm text-brand-text-muted">
          Track engagement, measure performance, and optimize strategy
        </p>
      </div>

      {/* Stat Cards */}
      <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-4">
        {[
          {
            label: "Total Reach",
            value: "24.8K",
            delta: "+18%",
            up: true,
            icon: Eye,
          },
          {
            label: "Engagement Rate",
            value: "6.4%",
            delta: "+2.1%",
            up: true,
            icon: Heart,
          },
          {
            label: "Comments",
            value: "213",
            delta: "+34%",
            up: true,
            icon: MessageCircle,
          },
          {
            label: "Shares",
            value: "271",
            delta: "-5%",
            up: false,
            icon: Share2,
          },
        ].map((stat) => (
          <div key={stat.label} className="card">
            <div className="flex items-center justify-between">
              <span className="stat-label">{stat.label}</span>
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-accent">
                <stat.icon className="h-4 w-4 text-brand-dark" />
              </div>
            </div>
            <p className="mt-3 stat-value">{stat.value}</p>
            <div className="mt-1 flex items-center gap-1">
              {stat.up ? (
                <ArrowUpRight className="h-3 w-3 text-brand-green" />
              ) : (
                <ArrowDownRight className="h-3 w-3 text-brand-red" />
              )}
              <span
                className={`font-display text-xs font-bold ${stat.up ? "text-brand-green" : "text-brand-red"}`}
              >
                {stat.delta}
              </span>
              <span className="font-display text-xs text-brand-text-muted">
                vs last month
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        {/* Engagement Trend Chart */}
        <div className="card md:col-span-2">
          <div className="card-header">
            <div className="flex items-center gap-3">
              <div className="card-icon">
                <TrendingUp className="h-5 w-5 text-brand-dark" />
              </div>
              <span className="card-title">Engagement Trend</span>
            </div>
            <div className="flex gap-2">
              {["7D", "30D", "90D"].map((period) => (
                <button
                  key={period}
                  className={`badge text-[10px] ${period === "30D" ? "bg-brand-accent text-brand-dark" : "bg-brand-bg-card"}`}
                >
                  {period}
                </button>
              ))}
            </div>
          </div>

          {/* Bar Chart */}
          <div className="mt-4 flex items-end gap-2" style={{ height: 200 }}>
            {engagementData.map((d, i) => (
              <div key={i} className="flex flex-1 flex-col items-center gap-1">
                <span className="font-display text-[10px] font-bold text-brand-text-muted">
                  {d.score}%
                </span>
                <div
                  className="w-full rounded-t-lg bg-brand-accent transition-all hover:bg-brand-accent-hover"
                  style={{
                    height: `${(d.score / maxScore) * 160}px`,
                  }}
                />
                <span className="font-display text-[9px] font-bold text-brand-text-muted">
                  {d.date.split(" ")[1]}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Sentiment Breakdown */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center gap-3">
              <div className="card-icon">
                <MessageCircle className="h-5 w-5 text-brand-dark" />
              </div>
              <span className="card-title">Sentiment</span>
            </div>
          </div>

          {/* Donut-like display */}
          <div className="mt-4 flex flex-col items-center">
            <div className="relative flex h-36 w-36 items-center justify-center">
              <svg viewBox="0 0 36 36" className="h-full w-full -rotate-90">
                <circle
                  cx="18"
                  cy="18"
                  r="15.92"
                  fill="none"
                  stroke="#E5E5E5"
                  strokeWidth="3"
                />
                <circle
                  cx="18"
                  cy="18"
                  r="15.92"
                  fill="none"
                  stroke="#16A34A"
                  strokeWidth="3"
                  strokeDasharray="68 32"
                  strokeDashoffset="0"
                />
                <circle
                  cx="18"
                  cy="18"
                  r="15.92"
                  fill="none"
                  stroke="#F5C542"
                  strokeWidth="3"
                  strokeDasharray="22 78"
                  strokeDashoffset="-68"
                />
                <circle
                  cx="18"
                  cy="18"
                  r="15.92"
                  fill="none"
                  stroke="#DC2626"
                  strokeWidth="3"
                  strokeDasharray="10 90"
                  strokeDashoffset="-90"
                />
              </svg>
              <div className="absolute text-center">
                <span className="font-display text-2xl font-bold">68%</span>
                <span className="block font-display text-[10px] font-bold uppercase tracking-widest text-brand-text-muted">
                  Positive
                </span>
              </div>
            </div>

            <div className="mt-4 w-full space-y-2">
              {[
                { label: "Positive", pct: 68, color: "bg-brand-green" },
                { label: "Neutral", pct: 22, color: "bg-brand-accent" },
                { label: "Negative", pct: 10, color: "bg-brand-red" },
              ].map((s) => (
                <div key={s.label} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`h-2.5 w-2.5 rounded-full ${s.color}`} />
                    <span className="font-display text-xs font-bold">
                      {s.label}
                    </span>
                  </div>
                  <span className="font-display text-xs font-bold text-brand-text-muted">
                    {s.pct}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Top Posts Table */}
      <div className="card mt-6">
        <div className="card-header">
          <div className="flex items-center gap-3">
            <div className="card-icon">
              <BarChart3 className="h-5 w-5 text-brand-dark" />
            </div>
            <span className="card-title">Top Performing Posts</span>
          </div>
          <ArrowUpRight className="h-5 w-5 text-brand-text-muted" />
        </div>

        <div className="overflow-hidden rounded-xl border-2 border-brand-border">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-brand-border bg-brand-bg-muted">
                <th className="px-4 py-3 text-left font-display text-xs font-bold uppercase tracking-widest text-brand-text-muted">
                  Post
                </th>
                <th className="px-4 py-3 text-left font-display text-xs font-bold uppercase tracking-widest text-brand-text-muted">
                  Platform
                </th>
                <th className="px-4 py-3 text-right font-display text-xs font-bold uppercase tracking-widest text-brand-text-muted">
                  Score
                </th>
                <th className="px-4 py-3 text-right font-display text-xs font-bold uppercase tracking-widest text-brand-text-muted">
                  Likes
                </th>
                <th className="px-4 py-3 text-right font-display text-xs font-bold uppercase tracking-widest text-brand-text-muted">
                  Comments
                </th>
                <th className="px-4 py-3 text-right font-display text-xs font-bold uppercase tracking-widest text-brand-text-muted">
                  Shares
                </th>
              </tr>
            </thead>
            <tbody>
              {topPosts.map((post, i) => (
                <tr
                  key={i}
                  className="border-b border-brand-border-light transition-colors hover:bg-brand-bg-muted"
                >
                  <td className="px-4 py-3">
                    <span className="font-display text-sm font-bold">
                      {post.title}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div
                        className={`h-2 w-2 rounded-full ${platformColors[post.platform]}`}
                      />
                      <span className="font-display text-xs font-bold uppercase text-brand-text-muted">
                        {post.platform}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span className="font-display text-sm font-bold text-brand-green">
                      {post.score}%
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right font-display text-sm">
                    {post.likes}
                  </td>
                  <td className="px-4 py-3 text-right font-display text-sm">
                    {post.comments}
                  </td>
                  <td className="px-4 py-3 text-right font-display text-sm">
                    {post.shares}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
