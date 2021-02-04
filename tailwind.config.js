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
    screens: {
      sm: '640px',
      md: '768px',
      lg: '1024px',
      xl: '1280px',
      // '2xl': '1536px',
    },
    colors: {
      transparent: 'transparent',
      current: 'currentColor',

      black: '#111111',
      white: '#fcfcfc',
      // primary: colors.indigo['700'],

      gray: {
        100: '#e9e9e9',
        200: '#d3d3d3',
        300: '#bdbdbd',
        400: '#a7a7a7',
        500: '#919191',
        600: '#7a7a7a',
        700: '#646464',
        800: '#4e4e4e',
        900: '#383838',
      },
    },
    fontFamily: {
      sans: ['Inter', 'sans-serif'],
      serif: ['Georgia', 'Cambria', '"Times New Roman"', 'Times', 'serif'],
      mono: ['ui-monospace','SFMono-Regular','Menlo','Monaco','Consolas','"Liberation Mono"','"Courier New"','monospace'],
    },
    fontWeight: {
      // thin: '100',
      // extralight: '200',
      // light: '300',
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
      // extrabold: '800',
      // black: '900',
    },
    extend: {},
  },
  variants: {
    extend: {},
  },
  plugins: [],
}
