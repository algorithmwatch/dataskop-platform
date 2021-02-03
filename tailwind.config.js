module.exports = {
  purge: {
    content: [
      './goliath/templates/**/*.html',
    ],

    // These options are passed through directly to PurgeCSS
    options: {}
  },
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {},
  },
  variants: {
    extend: {},
  },
  plugins: [],
}
