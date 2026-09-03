/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        nexus: {
          950: "#071013",
          900: "#0d1b1d",
          emerald: "#61d6b1",
          amber: "#e2a161",
        },
      },
      boxShadow: {
        glow: "0 0 24px rgba(97, 214, 177, .18)",
      },
    },
  },
  plugins: [],
};
