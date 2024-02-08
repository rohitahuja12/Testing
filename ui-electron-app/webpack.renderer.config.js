const rules = require('./webpack.rules.js');

rules.push({
  test: /\.css$/,
  use: [{ loader: 'style-loader' }, { loader: 'css-loader' }]
});

module.exports = {
  // Put your normal webpack config below here
  module: {
    rules
  }
};
