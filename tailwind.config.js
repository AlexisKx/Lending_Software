/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./*/templates/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          revenue: "#378ADD",
          interest: "#1D9E75",
          overdue: "#E24B4A",
          warn:    "#FAC775",
        },
      },
    },
  },
  plugins: [],
};
