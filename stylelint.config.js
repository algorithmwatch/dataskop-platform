module.exports = {
  extends: 'stylelint-config-recommended-scss',
  plugins: ['stylelint-order', 'stylelint-scss'],
  rules: {
    'order/properties-alphabetical-order': true,
    'scss/at-import-no-partial-leading-underscore': null,

    'at-rule-no-unknown': null,
    'scss/at-rule-no-unknown': [
      true,
      {
        ignoreAtRules: [
          'tailwind',
          'apply',
          'variants',
          'responsive',
          'screen',
          'layer',
        ],
      },
    ],
    'declaration-block-trailing-semicolon': null,
    'no-descending-specificity': null,
  },
};
