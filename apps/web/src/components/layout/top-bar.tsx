"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Sparkles,
  CalendarDays,
  BarChart3,
  Settings,
  Flame,
  Bell,
  User,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Generate", href: "/generate", icon: Sparkles },
  { name: "Calendar", href: "/calendar", icon: CalendarDays },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function TopBar() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-40 border-b-2 border-brand-border bg-brand-bg-card">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        {/* Logo */}
        <Link href="/dashboard" className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-accent">
            <Flame className="h-5 w-5 text-brand-dark" />
          </div>
          <span className="font-display text-xl font-bold tracking-tight">
            Trend<span className="text-brand-accent">Flare</span>
            <span className="text-brand-text-muted">.ai</span>
          </span>
        </Link>

        {/* Navigation */}
        <nav className="flex items-center gap-1">
          {navigation.map((item) => {
            const isActive =
              pathname === item.href ||
              (item.href !== "/dashboard" && pathname?.startsWith(item.href));
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-2 rounded-xl px-4 py-2 font-display text-sm font-bold uppercase tracking-wide transition-all",
                  isActive
                    ? "border-2 border-brand-border bg-brand-accent text-brand-dark shadow-card-sm"
                    : "border-2 border-transparent text-brand-text-muted hover:bg-brand-bg-muted hover:text-brand-dark"
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <button className="flex h-9 w-9 items-center justify-center rounded-xl border-2 border-brand-border bg-brand-bg-card transition-all hover:bg-brand-bg-muted">
            <Bell className="h-4 w-4 text-brand-dark" />
          </button>
          <button className="flex h-9 w-9 items-center justify-center rounded-xl border-2 border-brand-border bg-brand-accent transition-all hover:bg-brand-accent-hover">
            <User className="h-4 w-4 text-brand-dark" />
          </button>
        </div>
      </div>
    </header>
  );
}
