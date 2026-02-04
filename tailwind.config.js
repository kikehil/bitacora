/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./client/src/**/*.{js,jsx,ts,tsx}",
    "./bitacora.html",
  ],
  theme: {
    extend: {
      colors: {
        'oxxo-red': '#E30613',
        'oxxo-yellow': '#FFD200',
        'dark-vps': '#0a0a0a',
        'card-bg': '#161616',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'glow-red': '0 0 15px rgba(227, 6, 19, 0.3)',
        'glow-yellow': '0 0 15px rgba(255, 210, 0, 0.3)',
        'vps': '0 4px 20px rgba(0, 0, 0, 0.8)',
      },
      borderWidth: {
        '1': '1px',
      }
    },
  },
  plugins: [],
}

