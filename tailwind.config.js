const plugin = require('tailwindcss/plugin')

module.exports = {
  purge: {
    content: [
      './goliath/templates/**/*.html',
      './goliath/src/js/**/*.js',
    ],

    // These options are passed through directly to PurgeCSS
    options: {
      safelist: ['animate-bounce'],
    }
  },
  darkMode: false, // or 'media' or 'class'
  theme: {
    screens: {
      xs: '425px',
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

      // error: {
      //   light: '#FBC5B2', // red 200
      //   dark: '#952D07', // red 900
      // },
      // info: {
      //   light: '#C1D6E8',
      //   dark: '#1A3145',
      // },
      // success: {
      //   light: '#D0DEDC',
      //   dark: '#415C58',
      // },

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

      orange: {
        100: '#F4E4CE',
        200: '#ECD0A9',
        300: '#E4BB84',
        400: '#DBA760',
        500: '#D3933B',
        600: '#B87C29',
        700: '#936321',
        800: '#6E4A19',
        900: '#4A3110',
        1000: '#251908',
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
    extend: {
      zIndex: {
        '-10': '-10',
       },
      height: {
        '80vh': '80vh',
        '90vh': '90vh',
      },
      backgroundSize: {
        '1300px': '1300px'
      },
      width: {
        '240': '15rem',
      }
    },
  },
  variants: {
    extend: {
      margin: ['last', 'first'],
      padding: ['last', 'first'],
      ringColor: ['hover', 'active'],
      ringWidth: ['hover', 'active'],
      ringOpacity: ['hover', 'active'],
    },
  },
  plugins: [

    // heading plugin
    plugin(function({ addComponents, config, theme }) {
      const headings = {
        '.hl-6xl': {
          fontSize: theme('fontSize.6xl'),
          lineHeight: config('theme.fontSize.6xl')[1].lineHeight,
          fontWeight: theme('fontWeight.bold'),
        },
        '.hl-5xl': {
          fontSize: theme('fontSize.5xl'),
          lineHeight: config('theme.fontSize.5xl')[1].lineHeight,
          fontWeight: theme('fontWeight.bold'),
        },
        '.hl-4xl': {
          fontSize: theme('fontSize.4xl'),
          lineHeight: config('theme.fontSize.4xl')[1].lineHeight,
          fontWeight: theme('fontWeight.bold'),
        },
        '.hl-3xl': {
          fontSize: theme('fontSize.3xl'),
          lineHeight: config('theme.fontSize.3xl')[1].lineHeight,
          fontWeight: theme('fontWeight.bold'),
        },
        '.hl-2xl': {
          fontSize: theme('fontSize.2xl'),
          lineHeight: config('theme.fontSize.2xl')[1].lineHeight,
          fontWeight: theme('fontWeight.bold'),
        },
        '.hl-xl': {
          fontSize: theme('fontSize.xl'),
          lineHeight: config('theme.fontSize.xl')[1].lineHeight,
          fontWeight: theme('fontWeight.bold'),
        },
        '.hl-lg': {
          fontSize: theme('fontSize.lg'),
          lineHeight: config('theme.fontSize.lg')[1].lineHeight,
          fontWeight: theme('fontWeight.bold'),
        },
      }

      addComponents(headings, ['responsive'])
    }),

  ],
}
