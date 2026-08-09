/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#f7faf8',
        foreground: '#0f172a',
        primary: {
          DEFAULT: '#10b981',
          foreground: '#ffffff',
        },
        secondary: {
          DEFAULT: '#f1f5f9',
          foreground: '#334155',
        },
        accent: {
          DEFAULT: 'rgba(16, 185, 129, 0.08)',
          foreground: '#059669',
        },
        harvest: {
          DEFAULT: '#f59e0b',
          foreground: '#ffffff',
        },
        border: '#cbd5e1',
        muted: {
          DEFAULT: '#f8fafc',
          foreground: '#64748b',
        },
        card: {
          DEFAULT: '#ffffff',
          foreground: '#0f172a',
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
