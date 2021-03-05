/**
 * Project global configuration
 */

// Base configuration
const CONFIG_BASE = {
  htmlTitle: 'Soil - {title}'
}

// DEVELOPMENT configuration
const CONFIG_DEV = {
  // domain: 'http://c.bu86.com/api',
  domain: '/api',
}


// Test configuration
const CONFIG_TEST = {
  domain: '/api',
}

// Production configuration 
const CONFIG_PRO = {
  domain: '/api',
}

// Environment Configuration
const ENV_CONFIG_MAP = {
  development: CONFIG_DEV,
  test: CONFIG_TEST,
  production: CONFIG_PRO
}

export default { ...CONFIG_BASE, ...ENV_CONFIG_MAP[process.env.NODE_ENV!] }