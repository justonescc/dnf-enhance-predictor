/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'dnf-dark': '#1a1a2e',
        'dnf-darker': '#16213e',
        'dnf-card': '#0f3460',
        'dnf-gold': '#ffd700',
        'dnf-gold-dark': '#b8960f',
        'dnf-red': '#ff4444',
        'dnf-green': '#44ff44',
        'dnf-yellow': '#ffdd44',
        'dnf-orange': '#ff8844',
      },
    },
  },
  plugins: [],
}
