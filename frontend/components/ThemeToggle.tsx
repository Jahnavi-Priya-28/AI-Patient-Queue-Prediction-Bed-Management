"use client";

import { useTheme } from "@/components/ThemeProvider";
import { Sun, Moon } from "lucide-react";

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      aria-label="Toggle theme"
      className="relative p-2.5 rounded-full border transition-all duration-300
        border-hairline-light dark:border-white/15
        bg-canvas-cream dark:bg-white/10
        text-ink dark:text-on-primary
        hover:bg-shade-30 dark:hover:bg-white/20"
    >
      {theme === "light" ? (
        <Moon className="w-4 h-4" />
      ) : (
        <Sun className="w-4 h-4" />
      )}
    </button>
  );
}
