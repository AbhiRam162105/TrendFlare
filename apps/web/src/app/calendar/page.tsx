"use client";

import { useState } from "react";
import {
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  ArrowUpRight,
  Plus,
} from "lucide-react";
import {
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  eachDayOfInterval,
  format,
  isSameMonth,
  isSameDay,
  isToday,
  addMonths,
  subMonths,
} from "date-fns";

interface ScheduledPost {
  id: string;
  date: Date;
  platform: "linkedin" | "instagram" | "twitter";
  status: "draft" | "scheduled" | "published";
  title: string;
}

const platformStyle = {
  linkedin: { color: "bg-blue-500", label: "LI" },
  instagram: { color: "bg-pink-500", label: "IG" },
  twitter: { color: "bg-sky-400", label: "X" },
};

const mockPosts: ScheduledPost[] = [
  {
    id: "1",
    date: new Date(),
    platform: "linkedin",
    status: "scheduled",
    title: "AI Healthcare Trends",
  },
  {
    id: "2",
    date: new Date(),
    platform: "instagram",
    status: "scheduled",
    title: "Brand Story Visual",
  },
  {
    id: "3",
    date: new Date(Date.now() + 86400000),
    platform: "twitter",
    status: "draft",
    title: "Tech Thread",
  },
  {
    id: "4",
    date: new Date(Date.now() + 86400000 * 2),
    platform: "linkedin",
    status: "scheduled",
    title: "Remote Work Insights",
  },
  {
    id: "5",
    date: new Date(Date.now() + 86400000 * 4),
    platform: "instagram",
    status: "draft",
    title: "Sustainable Tech Infographic",
  },
  {
    id: "6",
    date: new Date(Date.now() - 86400000),
    platform: "linkedin",
    status: "published",
    title: "Industry Report Share",
  },
  {
    id: "7",
    date: new Date(Date.now() - 86400000 * 2),
    platform: "twitter",
    status: "published",
    title: "Quick Tip Thread",
  },
];

const statusStyle = {
  draft: "border-brand-accent bg-brand-accent-muted text-brand-dark",
  scheduled: "border-brand-green bg-green-50 text-brand-green",
  published: "border-brand-border-light bg-brand-bg-muted text-brand-text-muted",
};

export default function CalendarPage() {
  const [currentMonth, setCurrentMonth] = useState(new Date());

  const monthStart = startOfMonth(currentMonth);
  const monthEnd = endOfMonth(currentMonth);
  const calStart = startOfWeek(monthStart);
  const calEnd = endOfWeek(monthEnd);
  const days = eachDayOfInterval({ start: calStart, end: calEnd });

  const getPostsForDay = (date: Date) =>
    mockPosts.filter((p) => isSameDay(p.date, date));

  return (
    <div>
      {/* Header */}
      <div className="mb-8 flex items-end justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold tracking-tight text-brand-dark">
            Content Calendar
          </h1>
          <p className="mt-2 font-display text-sm text-brand-text-muted">
            Plan, schedule, and track your content pipeline
          </p>
        </div>
        <button className="btn-primary">
          <Plus className="mr-2 h-4 w-4" />
          New Post
        </button>
      </div>

      {/* Calendar */}
      <div className="card">
        {/* Month Navigation */}
        <div className="card-header">
          <div className="flex items-center gap-3">
            <div className="card-icon">
              <CalendarDays className="h-5 w-5 text-brand-dark" />
            </div>
            <span className="font-display text-lg font-bold uppercase tracking-wide">
              {format(currentMonth, "MMMM yyyy")}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentMonth(subMonths(currentMonth, 1))}
              className="flex h-9 w-9 items-center justify-center rounded-xl border-2 border-brand-border transition-all hover:bg-brand-bg-muted"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              onClick={() => setCurrentMonth(new Date())}
              className="badge bg-brand-accent text-brand-dark hover:bg-brand-accent-hover transition-all"
            >
              Today
            </button>
            <button
              onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
              className="flex h-9 w-9 items-center justify-center rounded-xl border-2 border-brand-border transition-all hover:bg-brand-bg-muted"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Day Headers */}
        <div className="grid grid-cols-7 border-b-2 border-brand-border-light">
          {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((d) => (
            <div
              key={d}
              className="py-3 text-center font-display text-xs font-bold uppercase tracking-widest text-brand-text-muted"
            >
              {d}
            </div>
          ))}
        </div>

        {/* Calendar Grid */}
        <div className="grid grid-cols-7">
          {days.map((day, idx) => {
            const dayPosts = getPostsForDay(day);
            const inMonth = isSameMonth(day, currentMonth);
            const today = isToday(day);

            return (
              <div
                key={idx}
                className={`min-h-[120px] border-b border-r border-brand-border-light p-2 transition-colors hover:bg-brand-bg-muted ${
                  !inMonth ? "bg-brand-bg-muted/50" : ""
                }`}
              >
                <div className="mb-1 flex items-center justify-between">
                  <span
                    className={`flex h-7 w-7 items-center justify-center rounded-lg font-display text-xs font-bold ${
                      today
                        ? "bg-brand-accent text-brand-dark"
                        : inMonth
                          ? "text-brand-dark"
                          : "text-brand-text-muted"
                    }`}
                  >
                    {format(day, "d")}
                  </span>
                  {dayPosts.length > 0 && (
                    <span className="font-display text-[10px] font-bold text-brand-text-muted">
                      {dayPosts.length}
                    </span>
                  )}
                </div>

                <div className="space-y-1">
                  {dayPosts.slice(0, 3).map((post) => (
                    <div
                      key={post.id}
                      className={`flex cursor-pointer items-center gap-1.5 rounded-lg border px-2 py-1 transition-all hover:-translate-y-0.5 ${statusStyle[post.status]}`}
                    >
                      <div
                        className={`h-1.5 w-1.5 rounded-full ${platformStyle[post.platform].color}`}
                      />
                      <span className="truncate font-display text-[10px] font-bold">
                        {post.title}
                      </span>
                    </div>
                  ))}
                  {dayPosts.length > 3 && (
                    <span className="block pl-1 font-display text-[10px] font-bold text-brand-text-muted">
                      +{dayPosts.length - 3} more
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="mt-4 flex items-center gap-6">
        <div className="flex items-center gap-2">
          <div className="h-2.5 w-2.5 rounded-full bg-blue-500" />
          <span className="font-display text-xs font-bold text-brand-text-muted">
            LinkedIn
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-2.5 w-2.5 rounded-full bg-pink-500" />
          <span className="font-display text-xs font-bold text-brand-text-muted">
            Instagram
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-2.5 w-2.5 rounded-full bg-sky-400" />
          <span className="font-display text-xs font-bold text-brand-text-muted">
            X (Twitter)
          </span>
        </div>
        <div className="mx-4 h-4 w-px bg-brand-border-light" />
        <div className="flex items-center gap-2">
          <div className="h-2.5 w-6 rounded border border-brand-green bg-green-50" />
          <span className="font-display text-xs font-bold text-brand-text-muted">
            Scheduled
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-2.5 w-6 rounded border border-brand-accent bg-brand-accent-muted" />
          <span className="font-display text-xs font-bold text-brand-text-muted">
            Draft
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-2.5 w-6 rounded border border-brand-border-light bg-brand-bg-muted" />
          <span className="font-display text-xs font-bold text-brand-text-muted">
            Published
          </span>
        </div>
      </div>
    </div>
  );
}
