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
        canvas: "#F7F6F2",
        surface: "#FFFFFF",
        primaryText: "#302A29",
        secondaryText: "#77736F",
        softBorder: "#E7E4DF",
        accentBlue: {
          DEFAULT: "#5278F4",
          hover: "#4164D8",
          subtle: "#EFF3FE",
        },
        accentGreen: {
          DEFAULT: "#18B978",
          subtle: "#E9F8F2",
        },
        accentYellow: {
          DEFAULT: "#F2C94C",
          subtle: "#FEF9EC",
        },
        accentRed: {
          DEFAULT: "#E86A6A",
          subtle: "#FDF0F0",
        },
      },
      borderRadius: {
        card: "22px",
        btn: "13px",
        container: "28px",
        pill: "9999px",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
        display: ["Inter Tight", "Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
