/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0b0f19',
        foreground: '#f1f5f9',
        primary: {
          DEFAULT: '#10b981',
          foreground: '#0f172a',
        },
        secondary: {
          DEFAULT: '#1e293b',
          foreground: '#f1f5f9',
        },
        accent: {
          DEFAULT: '#10b98115',
          foreground: '#34d399',
        },
        harvest: {
          DEFAULT: '#f59e0b',
          foreground: '#ffffff',
        },
        border: '#1e293b',
        muted: {
          DEFAULT: '#64748b',
          foreground: '#94a3b8',
        },
        card: {
          DEFAULT: '#0f172a',
          foreground: '#f1f5f9',
        }
      },
      fontFamily: {
        display: ['Playfair Display', 'serif'],
        sans: ['DM Sans', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
