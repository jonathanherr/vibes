# Gemini AI Proxy Server

A comprehensive Express.js server that acts as a proxy for both Gemini text and image generation APIs, enabling AI functionality from browser applications by bypassing CORS restrictions.

## Current Status

✅ **Text Generation**: Fully working with Gemini text API  
⚠️ **Image Generation**: Imagen API endpoint may require special access or different configuration

The text generation proxy is fully functional and provides excellent CORS bypass for chat functionality. Image generation may require additional setup or API access permissions.

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your Gemini API key
   ```

3. **Start the server:**
   ```bash
   npm start
   ```

4. **Test the endpoints:**
   ```bash
   # Test text generation
   curl -X POST http://localhost:3001/api/generate-text \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Hello, how are you?"}'

   # Test image generation
   curl -X POST http://localhost:3001/api/generate-image \
     -H "Content-Type: application/json" \
     -d '{"prompt": "A beautiful sunset over mountains"}'
   ```

## Environment Variables

### Required Variables

- `GEMINI_API_KEY` (required): Your Google Gemini API key

### Optional Variables

- `PORT` (default: 3001): Server port
- `NODE_ENV` (default: development): Environment mode
- `CORS_ORIGIN` (default: *): Allowed CORS origins, use `http://localhost:3000` for local React app
- `REQUEST_TIMEOUT` (default: 30000): API request timeout in milliseconds
- `MAX_REQUESTS_PER_MINUTE` (default: 60): Rate limiting (not yet implemented)
- `LOG_LEVEL` (default: info): Logging level

### Best Practices for Environment Variables

1. **Use .env file for development:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

2. **Never commit .env to version control:**
   - The `.env` file is in `.gitignore`
   - Use `.env.example` as a template for others

3. **Use specific CORS origins in production:**
   ```bash
   CORS_ORIGIN=https://your-production-domain.com
   ```

4. **Validate environment variables:**
   - The server automatically validates required variables
   - Missing required variables will prevent startup
   - Invalid API key format will show warnings

5. **Environment-specific configurations:**
   ```bash
   # Development
   NODE_ENV=development
   CORS_ORIGIN=http://localhost:3000
   LOG_LEVEL=debug

   # Production  
   NODE_ENV=production
   CORS_ORIGIN=https://your-domain.com
   LOG_LEVEL=warn
   REQUEST_TIMEOUT=15000
   ```

## API Endpoints

### `POST /api/generate-text`
Generate text using Gemini with conversation history support.

**Request Body:**
```json
{
  "prompt": "Your question or message",
  "model": "gemini-1.5-flash",
  "temperature": 0.7,
  "maxTokens": 1000,
  "conversationHistory": ["previous message 1", "previous message 2"]
}
```

**Response:**
```json
{
  "text": "Generated response text",
  "success": true,
  "metadata": {
    "model": "gemini-1.5-flash",
    "temperature": 0.7,
    "maxTokens": 1000,
    "finishReason": "STOP",
    "timestamp": "2025-06-22T..."
  }
}
```

### `POST /api/generate-image`
Generate an image using Gemini Imagen.

**Request Body:**
```json
{
  "prompt": "A description of the image to generate"
}
```

**Response:**
```json
{
  "imageUrl": "https://...",
  "success": true,
  "metadata": {
    "model": "imagen-3.0-generate-001",
    "prompt": "A description of the image to generate",
    "timestamp": "2025-06-22T..."
  }
}
```

### `GET /health`
Health check endpoint that shows server status and available endpoints.

**Response:**
```json
{
  "status": "OK",
  "message": "Gemini AI Proxy is running",
  "environment": "development",
  "hasApiKey": true,
  "endpoints": ["/api/generate-text", "/api/generate-image"]
}
```

## Integration with React App

1. Start this proxy server on port 3001
2. In your React app settings:
   - **For unified proxy (recommended)**: Set "Proxy Base URL" to `http://localhost:3001/api`
   - **For image-only proxy**: Set "Backend Proxy URL" to `http://localhost:3001/api/generate-image`
3. The React app will automatically use the proxy for API calls, bypassing CORS restrictions

### Benefits of Using the Proxy

- **CORS Bypass**: No more browser CORS restrictions
- **Rate Limiting**: Better control over API usage
- **Caching**: Potential to add response caching
- **Security**: API keys are kept on the server
- **Monitoring**: Centralized logging and monitoring
- **Flexibility**: Easy to add features like request preprocessing

## Security Notes

- This proxy server should only be used in development or in a trusted environment
- For production, implement proper authentication and rate limiting
- Consider using environment-specific API keys
- Add request validation and sanitization as needed

## Production Deployment

For production use, consider:
- Adding authentication/authorization
- Implementing rate limiting
- Adding request logging and monitoring
- Using a reverse proxy (nginx, etc.)
- Implementing proper error handling and logging
