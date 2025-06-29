const path = require('path');

// Load environment variables with explicit path
require('dotenv').config({
  path: path.resolve(__dirname, '.env')
});

// Environment configuration with defaults and validation
const config = {
  // Server configuration
  PORT: parseInt(process.env.PORT) || 3001,
  NODE_ENV: process.env.NODE_ENV || 'development',
  
  // Gemini API configuration
  GEMINI_API_KEY: process.env.GEMINI_API_KEY,
  
  // Optional configurations
  CORS_ORIGIN: process.env.CORS_ORIGIN || '*', // Allow all origins by default
  REQUEST_TIMEOUT: parseInt(process.env.REQUEST_TIMEOUT) || 30000, // 30 seconds
  MAX_REQUESTS_PER_MINUTE: parseInt(process.env.MAX_REQUESTS_PER_MINUTE) || 60,
  LOG_LEVEL: process.env.LOG_LEVEL || 'info'
};

// Validate required environment variables
const requiredEnvVars = [
  { key: 'GEMINI_API_KEY', value: config.GEMINI_API_KEY }
];

const missingEnvVars = requiredEnvVars.filter(env => !env.value);

if (missingEnvVars.length > 0) {
  console.error('❌ Missing required environment variables:');
  missingEnvVars.forEach(env => {
    console.error(`   - ${env.key}`);
  });
  console.error('\n💡 Please create a .env file with the required variables.');
  console.error('   Copy .env.example to .env and fill in your values.\n');
  
  if (config.NODE_ENV === 'production') {
    process.exit(1);
  } else {
    console.warn('⚠️  Running in development mode without required env vars - some features may not work.\n');
  }
}

// Validate API key format (basic check)
if (config.GEMINI_API_KEY && !config.GEMINI_API_KEY.startsWith('AIza')) {
  console.warn('⚠️  Gemini API key format looks incorrect. Expected format: AIza...\n');
}

module.exports = config;
