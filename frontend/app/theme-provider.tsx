"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

type ThemeMode = "light" | "dark";

const ThemeContext = createContext<{
  theme: ThemeMode;
  ready: boolean;
  toggleTheme: () => void;
} | null>(null);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<ThemeMode>("light");
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const savedTheme = window.localStorage.getItem("berozgaar-theme");
    const initialTheme = savedTheme === "light" || savedTheme === "dark" ? savedTheme : "light";
    setTheme(initialTheme);
    document.documentElement.dataset.theme = initialTheme;
    setReady(true);
  }, []);

  useEffect(() => {
    if (!ready) return;
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem("berozgaar-theme", theme);
  }, [theme, ready]);

  return (
    <ThemeContext.Provider value={{ theme, ready, toggleTheme: () => setTheme((current) => (current === "light" ? "dark" : "light")) }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error("useTheme must be used inside ThemeProvider");
  return context;
}
