"use client";

import { useState } from "react";
import {
  Sparkles,
  ArrowUpRight,
  Check,
  RotateCcw,
  Pencil,
  Image as ImageIcon,
  Copy,
  Instagram,
  Loader2,
  Zap,
  TrendingUp,
} from "lucide-react";

const platforms = [
  { id: "instagram", name: "Instagram", icon: Instagram, color: "bg-pink-500" },
];

const mockVariants = [
  {
    id: "1",
    hook: "Stop scrolling. This changes everything about AI in healthcare.",
    content:
      "The future of healthcare isn't just digital — it's intelligent. AI-powered diagnostics are reducing misdiagnosis rates by 40% in early trials.\n\nHere's what most people miss: it's not about replacing doctors. It's about giving them superhuman pattern recognition.\n\n3 ways AI is transforming patient outcomes right now:\n\n→ Predictive analytics catching conditions 2 years earlier\n→ Personalized treatment plans based on genomic data\n→ 24/7 monitoring that actually learns your baseline\n\nThe companies investing now will define the next decade of care.\n\n#AIHealthcare #DigitalHealth #FutureOfMedicine #HealthTech",
    predicted_score: 0.082,
    image_url: null,
  },
  {
    id: "2",
    hook: "I analyzed 500 health-tech startups. Here's the pattern nobody talks about.",
    content:
      "After studying 500+ health-tech companies, one trend is crystal clear:\n\nThe winners aren't building the most complex AI. They're building the most trusted AI.\n\nTrust > Accuracy in healthcare adoption. Here's why:\n\n1. Doctors won't use tools they can't explain to patients\n2. Patients won't trust black-box diagnoses\n3. Regulators require interpretability\n\nThe AI healthcare revolution will be led by companies that solve for trust, not just precision.\n\n#HealthTech #AITrust #MedTech #Innovation",
    predicted_score: 0.071,
    image_url: null,
  },
  {
    id: "3",
    hook: "Healthcare AI just hit a tipping point. Most people won't realize until 2027.",
    content:
      "2025 is the year healthcare AI goes from 'experimental' to 'essential.'\n\nWhat changed?\n\n→ FDA approved 170+ AI medical devices last year alone\n→ Cost of AI inference dropped 90% in 18 months\n→ Major hospital systems now mandate AI-assisted reads\n\nThis isn't hype. This is infrastructure being built in real-time.\n\nIf you're in health-tech and not building with AI, you're building for yesterday.\n\n#Healthcare #AI #Startups #TechTrends",
    predicted_score: 0.065,
    image_url: null,
  },
];

export default function GeneratePage() {
  const [selectedPlatform, setSelectedPlatform] = useState("instagram");
  const [isGenerating, setIsGenerating] = useState(false);
  const [variants, setVariants] = useState<typeof mockVariants | null>(null);

  const handleGenerate = () => {
    setIsGenerating(true);
    // Simulate API call
    setTimeout(() => {
      setVariants(mockVariants);
      setIsGenerating(false);
    }, 2500);
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="font-display text-3xl font-bold tracking-tight text-brand-dark">
          Generate Content
        </h1>
        <p className="mt-2 font-display text-sm text-brand-text-muted">
          AI-powered content creation with trend-grounded insights
        </p>
      </div>

      {/* Controls */}
      <div className="card mb-8">
        <div className="card-header">
          <div className="flex items-center gap-3">
            <div className="card-icon">
              <Sparkles className="h-5 w-5 text-brand-dark" />
            </div>
            <span className="card-title">Content Generator</span>
          </div>
        </div>

        <div className="space-y-5">
          {/* Platform Selector */}
          <div>
            <label className="stat-label mb-3 block">Platform</label>
            <div className="flex gap-3">
              {platforms.map((p) => (
                <button
                  key={p.id}
                  onClick={() => setSelectedPlatform(p.id)}
                  className={`flex items-center gap-2 rounded-xl border-2 px-5 py-3 font-display text-sm font-bold uppercase tracking-wide transition-all ${
                    selectedPlatform === p.id
                      ? "border-brand-border bg-brand-accent text-brand-dark shadow-card-sm"
                      : "border-brand-border-light bg-brand-bg-card text-brand-text-muted hover:border-brand-border"
                  }`}
                >
                  <div className={`h-2.5 w-2.5 rounded-full ${p.color}`} />
                  {p.name}
                </button>
              ))}
            </div>
          </div>

          {/* Niche Override */}
          <div>
            <label className="stat-label mb-3 block">
              Niche Override (optional)
            </label>
            <input
              type="text"
              placeholder="e.g., AI in Healthcare, Sustainable Tech..."
              className="input"
            />
          </div>

          {/* Tone */}
          <div>
            <label className="stat-label mb-3 block">Tone</label>
            <div className="flex gap-2">
              {["Professional", "Casual", "Bold", "Educational"].map(
                (tone) => (
                  <button
                    key={tone}
                    className="badge bg-brand-bg-card hover:bg-brand-accent hover:text-brand-dark transition-all"
                  >
                    {tone}
                  </button>
                )
              )}
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="btn-primary w-full justify-center py-4 text-base"
          >
            {isGenerating ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                AI is generating 3 variants...
              </>
            ) : (
              <>
                <Zap className="mr-2 h-5 w-5" />
                Generate Content
              </>
            )}
          </button>
        </div>
      </div>

      {/* Loading Skeleton */}
      {isGenerating && (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card animate-pulse">
              <div className="mb-4 h-40 rounded-xl bg-brand-bg-muted" />
              <div className="space-y-3">
                <div className="h-4 w-3/4 rounded bg-brand-bg-muted" />
                <div className="h-4 w-full rounded bg-brand-bg-muted" />
                <div className="h-4 w-5/6 rounded bg-brand-bg-muted" />
                <div className="h-4 w-2/3 rounded bg-brand-bg-muted" />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Variants */}
      {variants && !isGenerating && (
        <>
          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-accent">
              <TrendingUp className="h-4 w-4 text-brand-dark" />
            </div>
            <h2 className="font-display text-lg font-bold uppercase tracking-wide">
              3 Variants Generated
            </h2>
            <span className="badge border-brand-green bg-green-50 text-brand-green">
              Ranked by predicted engagement
            </span>
          </div>

          <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
            {variants.map((variant, i) => (
              <div key={variant.id} className="card flex flex-col">
                {/* Rank Badge */}
                <div className="mb-4 flex items-center justify-between">
                  <span
                    className={`badge ${
                      i === 0
                        ? "border-brand-accent bg-brand-accent text-brand-dark"
                        : "bg-brand-bg-card"
                    }`}
                  >
                    #{i + 1} {i === 0 && "Best"}
                  </span>
                  <span className="font-display text-xs font-bold text-brand-green">
                    {(variant.predicted_score * 100).toFixed(1)}% predicted
                  </span>
                </div>

                {/* Image Placeholder */}
                <div className="mb-4 flex h-40 items-center justify-center rounded-xl border-2 border-dashed border-brand-border-light bg-brand-bg-muted">
                  <div className="text-center">
                    <ImageIcon className="mx-auto h-8 w-8 text-brand-text-muted" />
                    <span className="mt-1 block font-display text-[10px] font-bold uppercase tracking-widest text-brand-text-muted">
                      AI Image
                    </span>
                  </div>
                </div>

                {/* Hook */}
                <p className="mb-3 font-display text-sm font-bold leading-snug text-brand-dark">
                  {variant.hook}
                </p>

                {/* Content Preview */}
                <p className="mb-4 flex-1 text-xs leading-relaxed text-brand-text-muted line-clamp-6">
                  {variant.content}
                </p>

                {/* Actions */}
                <div className="flex gap-2 border-t-2 border-brand-border-light pt-4">
                  <button className="btn-primary flex-1 py-2 text-xs">
                    <Check className="mr-1 h-3 w-3" />
                    Approve
                  </button>
                  <button className="btn-secondary px-3 py-2">
                    <RotateCcw className="h-3 w-3" />
                  </button>
                  <button className="btn-secondary px-3 py-2">
                    <Pencil className="h-3 w-3" />
                  </button>
                  <button className="btn-secondary px-3 py-2">
                    <Copy className="h-3 w-3" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
