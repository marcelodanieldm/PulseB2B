/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        zinc: {
          950: '#09090b',
        },
        indigo: {
          500: '#6366f1',
        },
      },
      fontFamily: {
        geist: ["Geist", "Inter", "sans-serif"],
      },
      letterSpacing: {
        tightest: '-.04em',
      },
      borderWidth: {
        ultra: '0.5px',
      },
    },
  },
  plugins: [],
};
