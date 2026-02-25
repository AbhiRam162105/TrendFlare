import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          bg: "#FEF9F0",
          "bg-card": "#FFFFFF",
          "bg-muted": "#FDF5E6",
          accent: "#F5C542",
          "accent-hover": "#E8B830",
          "accent-muted": "rgba(245, 197, 66, 0.15)",
          dark: "#1C1C1C",
          border: "#1C1C1C",
          "border-light": "#E5E5E5",
          text: "#1C1C1C",
          "text-muted": "#71717A",
          green: "#16A34A",
          red: "#DC2626",
          blue: "#2563EB",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["Space Grotesk", "Inter", "system-ui", "sans-serif"],
      },
      borderWidth: {
        3: "3px",
      },
      boxShadow: {
        card: "0 4px 0 0 #1C1C1C",
        "card-hover": "0 6px 0 0 #1C1C1C",
        "card-sm": "0 2px 0 0 #1C1C1C",
      },
    },
  },
  plugins: [],
};

export default config;
