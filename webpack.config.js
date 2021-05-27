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
    wizard: './dataskop/frontend/js/wizard.js',
  },

  module: {
    rules: [
      {
        test: /\.m?js$/i,
        exclude: /(node_modules|bower_components)/,
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
            // options: {
            //     includePaths: [
            //         path.resolve(__dirname, './node_modules')
            //     ]
            // }
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

  // mode: process.env.NODE_ENV,

  devServer: {
    contentBase: path.resolve(__dirname, 'dataskop/static/'),
    writeToDisk: true,
  },

  plugins: [
    new CleanWebpackPlugin({ cleanStaleWebpackAssets: false }),
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
    new MiniCssExtractPlugin({
      filename: '[name].css',
    }),
  ],

  optimization: {
    // minimize: !isDev,
    minimizer: [
      // For webpack@5 you can use the `...` syntax to extend existing minimizers (i.e. `terser-webpack-plugin`), uncomment the next line
      // `...`,
      new TerserPlugin({
        // avoid comments in build
        terserOptions: {
          format: {
            comments: false,
          },
        },
        extractComments: false,
      }), // to minify js
      new CssMinimizerPlugin(),
    ],
  },
};
