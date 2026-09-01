/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        capf: {
          50: '#f0f5fa',
          100: '#e1ecf5',
          200: '#c3d8eb',
          300: '#94bcdd',
          400: '#5e9bcb',
          500: '#387fb8',
          600: '#27659a',
          700: '#21517d',
          800: '#1e4568',
          900: '#0f2438',
          950: '#0a1724',
        },
      },
    },
  },
  plugins: [],
};
