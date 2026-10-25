/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          bg: "#0a0f1d",
          card: "#111827",
          surface: "#1a2234",
          border: "#243048",
          hover: "#222d42",
          cyan: "#06b6d4",
          teal: "#14b8a6",
          violet: "#8b5cf6",
          critical: "#ef4444",
          high: "#f97316",
          medium: "#eab308",
          low: "#3b82f6",
          success: "#10b981",
        }
      }
    },
  },
  plugins: [],
}
