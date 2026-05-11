import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17211a",
        market: "#256d4f",
        alert: "#b42318",
        shelf: "#f4f1ea",
      },
    },
  },
  plugins: [],
};

export default config;
