# Gemini Image Generation Setup

This document explains how to set up image generation using Google's Gemini 2.0 Flash model in the React Chatbot Intercom application.

## Overview

The application now supports **Gemini 2.0 Flash Preview Image Generation**, which provides:
- **Text-to-image generation** via REST API
- **Conversational image generation** with accompanying text descriptions
- **No SDK dependency** - works with standard HTTP requests
- **Better integration** with existing Gemini text models

## Models Available

1. **Gemini 2.0 Flash Preview Image Generation** (✅ Supported via REST API)
   - Model: `gemini-2.0-flash-preview-image-generation`
   - Supports: Text-to-image via `generateContent` with `responseModalities: ['TEXT', 'IMAGE']`
   - Pricing: $0.039 per image (see [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing))

2. **Imagen 3** (❌ SDK Only)
   - Model: `imagen-3.0-generate-002`
   - Requires: Google's generative AI SDK (not available via REST API)
   - Use case: When SDK integration is available

## Setup Instructions

### 1. Get API Key

Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey) and ensure you're on the **paid tier** (image generation is not available on the free tier).

### 2. Backend Proxy Setup

Due to CORS restrictions, a backend proxy is required:

```bash
# Navigate to the backend proxy directory
cd backend-proxy-example

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Start the proxy server
npm start
```

The proxy provides:
- **Text generation**: `POST /api/generate-text`
- **Image generation**: `POST /api/generate-image`
- **Health check**: `GET /health`

### 3. Frontend Configuration

In the app settings:

1. Set **Image Generation Provider** to "Gemini (2.0 Flash)"
2. Set **Model** to "Gemini 2.0 Flash Image Generation"
3. Set **Backend Proxy URL** to `http://localhost:3001/api/generate-image`

### 4. Test Image Generation

Try sending a message that starts with "draw" or includes image-related keywords:
- "draw a cat sitting on a windowsill"
- "create an image of a futuristic city"
- "generate a picture of a rainbow over mountains"

## How It Works

1. **Detection**: The chat system detects drawing/image requests using keywords
2. **API Call**: Sends the prompt to Gemini 2.0 Flash via the backend proxy
3. **Response**: Receives both generated image (as base64) and descriptive text
4. **Display**: Shows the image in the chat interface with the accompanying description

## API Request/Response

### Request
```json
{
  "prompt": "A cute robot holding a paintbrush"
}
```

### Response
```json
{
  "imageUrl": "data:image/png;base64,...",
  "text": "I will generate an image of a charming, small robot...",
  "success": true,
  "metadata": {
    "model": "gemini-2.0-flash-preview-image-generation",
    "prompt": "A cute robot holding a paintbrush",
    "mimeType": "image/png",
    "timestamp": "2025-06-22T..."
  }
}
```

## Troubleshooting

### "Model not found" error
- Ensure you're using `gemini-2.0-flash-preview-image-generation` (not `imagen-3.0-generate-002`)
- Verify your API key has access to Gemini 2.0 models

### CORS errors
- Make sure the backend proxy is running on port 3001
- Check that the proxy URL is configured correctly in settings

### "Not available on free tier"
- Image generation requires a paid Gemini API subscription
- Upgrade at [Google AI Studio](https://aistudio.google.com/apikey)

### Images not displaying
- Check browser console for errors
- Verify the response contains valid base64 image data
- Ensure the ImageViewer component is working correctly

## Cost Considerations

- **Gemini 2.0 Flash Text**: $0.40 per 1M output tokens (free tier available)
- **Image Generation**: $0.039 per image (paid tier only)
- **Rate Limits**: Check [Gemini API docs](https://ai.google.dev/gemini-api/docs/rate-limits) for current limits

## Next Steps

- Test different image prompts to see the model's capabilities
- Experiment with different aspect ratios and styles
- Consider implementing image editing features using Gemini's multimodal capabilities
- Explore batch image generation for multiple variations
