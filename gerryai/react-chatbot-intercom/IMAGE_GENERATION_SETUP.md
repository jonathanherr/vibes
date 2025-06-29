# AI Generation Backend Setup

Due to CORS restrictions, Gemini APIs (both text and image) cannot be called directly from the browser. Here are solutions to enable real AI generation with enhanced flexibility:

## Quick Setup: Use the Included Example

We've included a ready-to-use Express.js proxy server in the `backend-proxy-example/` directory that handles both **text and image generation**:

1. **Navigate to the proxy directory:**
   ```bash
   cd backend-proxy-example
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure your API key:**
   ```bash
   cp .env.example .env
   # Edit .env and add your Gemini API key: GEMINI_API_KEY=your_key_here
   ```

4. **Start the proxy server:**
   ```bash
   npm start
   ```

5. **In the React app settings panel:**
   - Open LLM Settings
   - **For text generation**: Set "Proxy Base URL" to: `http://localhost:3001/api`
   - **For image generation**: Set Image Generation Provider to "Gemini" and Backend Proxy URL to: `http://localhost:3001/api/generate-image`
   - Save settings

Now both text chat and image generation ("draw something") will use the backend proxy for enhanced reliability and bypassing CORS restrictions!

## Benefits of Using the Proxy

- 🚫 **No CORS Issues**: Bypass browser restrictions completely
- 🔐 **API Key Security**: Keep your API keys on the server
- ⚡ **Better Performance**: Potential for caching and optimization
- 📊 **Centralized Logging**: Monitor all API usage in one place
- 🛡️ **Enhanced Safety**: Server-side content filtering
- 🔧 **Flexibility**: Easy to add rate limiting, preprocessing, etc.

## Option 1: Custom Express.js Proxy Server

Create a simple backend server to proxy Gemini Imagen API calls:

### 1. Create a new directory for the backend:
```bash
mkdir gemini-image-proxy
cd gemini-image-proxy
npm init -y
npm install express cors axios dotenv
```

### 2. Create `server.js`:
```javascript
const express = require('express');
const cors = require('cors');
const axios = require('axios');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

app.post('/api/generate-image', async (req, res) => {
  try {
    const { prompt } = req.body;
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) {
      return res.status(500).json({ error: 'Gemini API key not configured' });
    }

    const response = await axios.post(
      `https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:generateImage?key=${apiKey}`,
      {
        prompt: { text: prompt },
        safetySettings: [
          { category: "HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold: "BLOCK_LOW_AND_ABOVE" },
          { category: "HARM_CATEGORY_HATE_SPEECH", threshold: "BLOCK_LOW_AND_ABOVE" },
          { category: "HARM_CATEGORY_HARASSMENT", threshold: "BLOCK_LOW_AND_ABOVE" },
          { category: "HARM_CATEGORY_DANGEROUS_CONTENT", threshold: "BLOCK_LOW_AND_ABOVE" }
        ],
        generationConfig: {
          aspectRatio: "SQUARE",
          negativePrompt: "blurry, low quality, distorted, ugly, watermark"
        }
      }
    );

    const candidate = response.data.candidates[0];
    if (candidate.finishReason !== 'STOP') {
      throw new Error(`Image generation failed: ${candidate.finishReason}`);
    }

    res.json({ 
      imageData: `data:image/png;base64,${candidate.image.imageBytes}` 
    });
  } catch (error) {
    console.error('Image generation error:', error);
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`Gemini Image Proxy Server running on port ${PORT}`);
});
```

### 3. Create `.env`:
```
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 4. Run the server:
```bash
node server.js
```

### 5. Update React app to use the proxy:
Update `imageGenService.ts` to call `http://localhost:3001/api/generate-image` instead of the Gemini API directly.

## Option 2: Use vLLM with Stable Diffusion

Set up a local vLLM server with Stable Diffusion:

```bash
# Install vLLM with image generation support
pip install vllm[image]

# Run vLLM with a Stable Diffusion model
vllm serve stabilityai/stable-diffusion-xl-base-1.0 --port 8001
```

Then configure the React app to use vLLM provider in the image generation settings.

## Option 3: Alternative Image Generation APIs

Use other image generation services that support CORS or have better browser support:

- OpenAI DALL-E API
- Replicate API
- Hugging Face Inference API
- Stability AI API

## Current Status

The React app currently shows placeholder images when using Gemini Imagen due to CORS restrictions. Follow one of the above options to enable real image generation.
