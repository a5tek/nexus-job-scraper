import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: "var(--canvas)",
        surface: {
          DEFAULT: "var(--surface)",
          hover: "var(--surface-hover)",
        },
        primaryText: "var(--primary-text)",
        secondaryText: "var(--secondary-text)",
        softBorder: "var(--soft-border)",
        accentBlue: {
          DEFAULT: "var(--accent-blue)",
          hover: "var(--accent-blue-hover)",
          subtle: "var(--accent-blue-subtle)",
        },
        accentGreen: {
          DEFAULT: "var(--accent-green)",
          subtle: "var(--accent-green-subtle)",
        },
        accentYellow: {
          DEFAULT: "var(--accent-yellow)",
          subtle: "var(--accent-yellow-subtle)",
        },
        accentRed: {
          DEFAULT: "var(--accent-red)",
          subtle: "var(--accent-red-subtle)",
        },
      },
      borderRadius: {
        card: "22px",
        btn: "13px",
        container: "28px",
        pill: "9999px",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "Inter", "system-ui", "-apple-system", "sans-serif"],
        display: ["var(--font-display)", "var(--font-sans)", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
