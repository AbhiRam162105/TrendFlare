import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/components/layout/providers";

export const metadata: Metadata = {
  title: "TrendFlare.ai — AI Social Media Manager",
  description:
    "Automated social media management powered by AI. Trend discovery, content generation, and smart scheduling.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-brand-bg text-brand-text">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
