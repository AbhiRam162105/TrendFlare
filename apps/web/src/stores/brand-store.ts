import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Brand } from "@/lib/api";

interface BrandState {
  activeBrand: Brand | null;
  setActiveBrand: (brand: Brand) => void;
  clearBrand: () => void;
}

export const useBrandStore = create<BrandState>()(
  persist(
    (set) => ({
      activeBrand: null,
      setActiveBrand: (brand) => set({ activeBrand: brand }),
      clearBrand: () => set({ activeBrand: null }),
    }),
    { name: "trendflare-brand" }
  )
);
