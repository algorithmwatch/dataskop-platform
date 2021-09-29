const path = require('path');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const CopyPlugin = require('copy-webpack-plugin');

const isDev = process.env.NODE_ENV !== 'production';

module.exports = {
  entry: {
    main: './dataskop/frontend/js/main.js',
  },

  module: {
    rules: [
      {
        test: /\.m?js$/i,
        exclude: /(node_modules)/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env'],
          },
        },
      },
      {
        test: /\.s?css$/i,
        use: [
          {
            loader: MiniCssExtractPlugin.loader,
          },
          {
            loader: 'css-loader',
          },
          {
            loader: 'postcss-loader',
          },
          {
            loader: 'sass-loader',
          },
        ],
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/i,
        type: 'asset/resource',
      },
    ],
  },

  resolve: {
    extensions: ['.js', '.css'],
    modules: ['node_modules'],
  },

  output: {
    filename: '[name].js',
    path: path.resolve(__dirname, 'dataskop/static/'),
    publicPath: '/static/',
  },

  devtool: isDev ? 'inline-source-map' : false,

  devServer: {
    static: {
      directory: path.resolve(__dirname, 'dataskop/static/'),
    },
    devMiddleware: {
      writeToDisk: true,
    },
  },

  plugins: [
    new CleanWebpackPlugin({ cleanStaleWebpackAssets: false }),
    new MiniCssExtractPlugin({
      filename: '[name].css',
    }),
    // Copy Font Awesome SVGs to Django's static dir to reference them individually.
    // This is useful when icons are assigned to objects (created by users / admins).
    // Since we only add a subset of all FA icons to the library (see main.js).
    new CopyPlugin({
      patterns: [
        {
          from: 'img/**/*',
          context: 'dataskop/frontend/',
        },
        {
          from: 'node_modules/@fortawesome/fontawesome-free/svgs/**/*',
          to({ context, absoluteFilename }) {
            const all = [];
            const lastTwo = absoluteFilename.split('/').slice(-2);
            if (lastTwo[0] == 'brands') all.push('fab');
            if (lastTwo[0] == 'regular') all.push('far');
            if (lastTwo[0] == 'solid') all.push('fas');
            all.push('fa');
            all.push(lastTwo[1]);
            return 'fontawesome/' + all.join('-');
          },
        },
      ],
    }),
  ],

  optimization: {
    minimizer: [
      // minify js
      new TerserPlugin({
        // remove comments in build
        terserOptions: {
          format: {
            comments: false,
          },
        },
        extractComments: false,
      }),
      // minimize CSS
      new CssMinimizerPlugin(),
    ],
  },
};
