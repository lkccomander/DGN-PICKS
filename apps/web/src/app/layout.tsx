import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "DGN-PICKS | Picks dashboard", description: "A focused home for picks, odds, and results." };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
