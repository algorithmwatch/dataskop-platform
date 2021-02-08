const plugin = require('tailwindcss/plugin')

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
      white: '#fff',

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

      brown: {
        100: '#EAE9E6',
        200: '#D6D3CE',
        300: '#C1BEB5',
        400: '#ADA89D',
        500: '#989284',
        600: '#837C6B',
        700: '#6F6653',
        800: '#5A513A',
        900: '#463B22',
        1000: '#312509', // text
      },

      green: {
        100: '#E7EEED',
        200: '#D0DEDC',
        300: '#B9CECB',
        400: '#A2BDBA',
        500: '#8BADA8',
        600: '#759D97',
        700: '#618984',
        800: '#51726E',
        900: '#415C58',
        1000: '#314542',
      },

      red: {
        100: '#FDE1D7',
        200: '#FBC5B2',
        300: '#F9A98D',
        400: '#F78D68',
        500: '#F67242',
        600: '#F4561D',
        700: '#DF430B',
        800: '#BA3809',
        900: '#952D07',
        1000: '#6F2106',
      },

      blue: {
        100: '#E4EDF5',
        200: '#C1D6E8',
        300: '#9FBFDB',
        400: '#7CA8CF',
        500: '#5A91C2',
        600: '#4079AD',
        700: '#33618A',
        800: '#264968',
        900: '#1A3145',
        1000: '#0D1823',
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
    extend: {
      margin: ['last', 'first'],
      padding: ['last', 'first'],
    },
  },
  plugins: [

    // error-, info- success- classes
    plugin(function({ addUtilities, theme }) {
      const newUtilities = {
        '.error-bg': {
          'background-color': theme('colors.red.200'),
        },
        '.error-text': {
          'color': theme('colors.red.900'),
        },
        '.info-bg': {
          'background-color': theme('colors.blue.200'),
        },
        '.info-text': {
          'color': theme('colors.blue.900'),
        },
        '.success-bg': {
          'background-color': theme('colors.green.200'),
        },
        '.success-text': {
          'color': theme('colors.green.900'),
        },
      }

      addUtilities(newUtilities)
    })
  ],
}
