/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      height: {
        '24': '6rem',
        '32': '8rem',
        '40': '10rem',
        '56': '14rem',
        '64': '16rem',
      },
    },
  },
  plugins: [],
}

