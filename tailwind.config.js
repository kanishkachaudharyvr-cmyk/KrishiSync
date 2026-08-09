/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#f3f8f4',
        foreground: '#0f172a',
        primary: {
          DEFAULT: '#1b8354',
          foreground: '#ffffff',
        },
        secondary: {
          DEFAULT: '#e6ede8',
          foreground: '#2f4f3e',
        },
        accent: {
          DEFAULT: 'rgba(27, 131, 84, 0.08)',
          foreground: '#1b8354',
        },
        harvest: {
          DEFAULT: '#f59e0b',
          foreground: '#ffffff',
        },
        border: '#dbe5df',
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
