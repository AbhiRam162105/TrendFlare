import { AppShell } from "@/components/layout/app-shell";

export default function GenerateLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AppShell>{children}</AppShell>;
}
