"use client";

import { useState } from "react";
import {
  Settings,
  User,
  Palette,
  Globe,
  Bell,
  Key,
  Save,
  Plus,
  Trash2,
  Check,
  ExternalLink,
} from "lucide-react";

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("brand");

  const tabs = [
    { id: "brand", label: "Brand Voice", icon: Palette },
    { id: "accounts", label: "Social Accounts", icon: Globe },
    { id: "notifications", label: "Notifications", icon: Bell },
    { id: "api", label: "API Keys", icon: Key },
  ];

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="font-display text-3xl font-bold tracking-tight text-brand-dark">
          Settings
        </h1>
        <p className="mt-2 font-display text-sm text-brand-text-muted">
          Configure your brand, connect accounts, and manage preferences
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-4">
        {/* Tab Navigation */}
        <div className="space-y-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex w-full items-center gap-3 rounded-xl border-2 px-4 py-3 font-display text-sm font-bold uppercase tracking-wide transition-all ${
                activeTab === tab.id
                  ? "border-brand-border bg-brand-accent text-brand-dark shadow-card-sm"
                  : "border-brand-border-light bg-brand-bg-card text-brand-text-muted hover:border-brand-border"
              }`}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="md:col-span-3">
          {activeTab === "brand" && <BrandVoiceSettings />}
          {activeTab === "accounts" && <SocialAccountsSettings />}
          {activeTab === "notifications" && <NotificationSettings />}
          {activeTab === "api" && <APIKeysSettings />}
        </div>
      </div>
    </div>
  );
}

function BrandVoiceSettings() {
  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center gap-3">
          <div className="card-icon">
            <Palette className="h-5 w-5 text-brand-dark" />
          </div>
          <span className="card-title">Brand Voice Configuration</span>
        </div>
      </div>

      <div className="space-y-6">
        <div>
          <label className="stat-label mb-2 block">Brand Name</label>
          <input
            type="text"
            defaultValue="TrendFlare.ai"
            className="input"
          />
        </div>

        <div>
          <label className="stat-label mb-2 block">Niche / Industry</label>
          <input
            type="text"
            defaultValue="AI & Technology"
            className="input"
          />
        </div>

        <div>
          <label className="stat-label mb-2 block">Tone of Voice</label>
          <div className="flex flex-wrap gap-2">
            {[
              "Professional",
              "Bold",
              "Educational",
              "Conversational",
              "Witty",
              "Authoritative",
            ].map((tone) => (
              <button
                key={tone}
                className={`badge transition-all ${
                  ["Professional", "Bold"].includes(tone)
                    ? "bg-brand-accent text-brand-dark"
                    : "bg-brand-bg-card hover:bg-brand-bg-muted"
                }`}
              >
                {tone}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="stat-label mb-2 block">
            Voice Examples (paste your best-performing posts)
          </label>
          <textarea
            rows={4}
            className="input resize-none"
            defaultValue="We don't follow trends. We decode them before they peak and turn them into content that converts."
            placeholder="Paste examples of your brand's writing style..."
          />
          <button className="btn-ghost mt-2 text-xs">
            <Plus className="mr-1 h-3 w-3" />
            Add another example
          </button>
        </div>

        <div className="flex justify-end border-t-2 border-brand-border-light pt-4">
          <button className="btn-primary">
            <Save className="mr-2 h-4 w-4" />
            Save Brand Voice
          </button>
        </div>
      </div>
    </div>
  );
}

function SocialAccountsSettings() {
  const accounts = [
    {
      name: "Instagram",
      connected: true,
      handle: "@trendflare.ai",
      color: "bg-pink-500",
    },
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
      </div>

      <p className="mb-5 text-sm text-brand-text-muted">
        Connect your social media accounts via Ayrshare to enable automated
        publishing.
      </p>

      <div className="space-y-3">
        {accounts.map((acct) => (
          <div
            key={acct.name}
            className="flex items-center justify-between rounded-xl border-2 border-brand-border-light px-5 py-4"
          >
            <div className="flex items-center gap-4">
              <div className={`h-3 w-3 rounded-full ${acct.color}`} />
              <div>
                <span className="font-display text-sm font-bold">
                  {acct.name}
                </span>
                <span className="ml-3 font-display text-xs text-brand-text-muted">
                  {acct.handle}
                </span>
              </div>
            </div>
            {acct.connected ? (
              <div className="flex items-center gap-3">
                <span className="badge border-brand-green bg-green-50 text-brand-green">
                  <Check className="mr-1 h-3 w-3" />
                  Connected
                </span>
                <button className="btn-ghost text-xs text-brand-red">
                  Disconnect
                </button>
              </div>
            ) : (
              <button className="btn-primary py-2 text-xs">
                <ExternalLink className="mr-1 h-3 w-3" />
                Connect
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function NotificationSettings() {
  const settings = [
    { label: "Post published successfully", enabled: true },
    { label: "Post failed to publish", enabled: true },
    { label: "Trending topic alert (high score)", enabled: true },
    { label: "Weekly engagement report", enabled: false },
    { label: "DSPy optimization completed", enabled: false },
  ];

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center gap-3">
          <div className="card-icon">
            <Bell className="h-5 w-5 text-brand-dark" />
          </div>
          <span className="card-title">Notification Preferences</span>
        </div>
      </div>

      <div className="space-y-3">
        {settings.map((s) => (
          <div
            key={s.label}
            className="flex items-center justify-between rounded-xl border-2 border-brand-border-light px-5 py-4"
          >
            <span className="font-display text-sm font-bold">{s.label}</span>
            <button
              className={`flex h-6 w-11 items-center rounded-full border-2 border-brand-border transition-all ${
                s.enabled ? "bg-brand-accent" : "bg-brand-bg-muted"
              }`}
            >
              <div
                className={`h-4 w-4 rounded-full bg-white shadow transition-transform ${
                  s.enabled ? "translate-x-5" : "translate-x-0.5"
                }`}
              />
            </button>
          </div>
        ))}
      </div>

      <div className="mt-4 flex justify-end">
        <button className="btn-primary">
          <Save className="mr-2 h-4 w-4" />
          Save Preferences
        </button>
      </div>
    </div>
  );
}

function APIKeysSettings() {
  const keys = [
    { name: "GEMINI_API_KEY", set: true },
    { name: "HF_TOKEN", set: true },
    { name: "AYRSHARE_API_KEY", set: false },
  ];

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center gap-3">
          <div className="card-icon">
            <Key className="h-5 w-5 text-brand-dark" />
          </div>
          <span className="card-title">API Key Management</span>
        </div>
      </div>

      <p className="mb-5 text-sm text-brand-text-muted">
        API keys are stored encrypted. Keys are never displayed after being
        saved.
      </p>

      <div className="space-y-3">
        {keys.map((k) => (
          <div
            key={k.name}
            className="flex items-center justify-between rounded-xl border-2 border-brand-border-light px-5 py-4"
          >
            <div className="flex items-center gap-3">
              <code className="font-display text-sm font-bold">{k.name}</code>
              {k.set ? (
                <span className="badge border-brand-green bg-green-50 text-[10px] text-brand-green">
                  Set
                </span>
              ) : (
                <span className="badge border-brand-red bg-red-50 text-[10px] text-brand-red">
                  Missing
                </span>
              )}
            </div>
            <button className="btn-ghost text-xs">Update</button>
          </div>
        ))}
      </div>
    </div>
  );
}
