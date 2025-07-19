/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        'crypto-dark': '#1a1a2e',
        'crypto-blue': '#16213e',
        'crypto-accent': '#0f3460',
        'crypto-gold': '#f39c12',
        'crypto-green': '#27ae60',
        'crypto-red': '#e74c3c'
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
        'spin-slow': 'spin 3s linear infinite',
      }
    },
  },
  plugins: [],
}