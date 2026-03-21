const { FlatCompat } = require('@eslint/eslintrc')

module.exports = FlatCompat({
  base: [
    require('eslint-config-next').default
  ],
  rules: {
    // Disable deprecated rules
    'no-console': 'off',
    'prefer-const': 'error',
    'no-unused-vars': 'warn'
  }
})
