const { createTailwindPlugin } = require('./tailwind.postcss');
const autoprefixer = require('autoprefixer');

module.exports = {
  plugins: [
    createTailwindPlugin(),
    autoprefixer,
  ],
};
