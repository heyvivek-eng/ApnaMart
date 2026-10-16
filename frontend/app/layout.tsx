import type { Metadata } from "next";
import "./globals.css";
import { ThemeProvider } from "./theme-provider";

export const metadata: Metadata = {
  title: "ApnaMart — Har Zaroorat, Ek Bazaar",
  description: "Discover thoughtful everyday finds at ApnaMart.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body><ThemeProvider>{children}</ThemeProvider></body></html>;
}
