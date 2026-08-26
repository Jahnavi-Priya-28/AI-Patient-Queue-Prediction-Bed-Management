import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: {
          night: "#000000",
          "night-elevated": "#0a0a0a",
          light: "#ffffff",
          cream: "#fbfbf5",
        },
        surface: {
          "elevated-dark": "#1e2c31",
        },
        aloe: {
          10: "#c1fbd4",
        },
        pistachio: {
          10: "#d4f9e0",
        },
        hairline: {
          light: "#e4e4e7",
          dark: "#1e2c31",
        },
        shade: {
          30: "#d4d4d8",
          40: "#a1a1aa",
          50: "#71717a",
          60: "#52525b",
          70: "#3f3f46",
        },
        link: {
          "cool-1": "#9dabad",
          "cool-2": "#9797a2",
          "cool-3": "#bdbdca",
          mint: "#99b3ad",
        },
        ink: "#000000",
        "on-primary": "#ffffff",
      },
      fontFamily: {
        display: [
          '"Neue Haas Grotesk Display Pro"',
          '"Neue Haas Grotesk Display"',
          'Inter',
          '-apple-system',
          'sans-serif',
        ],
        body: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      fontWeight: {
        thin: "330",
        light: "330",
        normal: "420",
        medium: "500",
        semibold: "550",
        bold: "700",
      },
      letterSpacing: {
        "display-xxl": "2.4px",
        "eyebrow": "0.72px",
      },
      borderRadius: {
        pill: "9999px",
      },
    },
  },
  plugins: [],
};

export default config;
