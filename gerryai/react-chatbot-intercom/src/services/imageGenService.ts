import axios from 'axios';
import { ImageGenConfig } from '../types';

export class ImageGenService {
  private config: ImageGenConfig;

  constructor(config: ImageGenConfig) {
    this.config = config;
  }

  async generateImage(prompt: string): Promise<string> {
    try {
      console.log('Generating image with prompt:', prompt);
      
      if (this.config.provider === 'gemini') {
        return await this.generateWithGemini(prompt);
      } else if (this.config.provider === 'vllm') {
        return await this.generateWithVLLM(prompt);
      } else {
        throw new Error(`Unsupported image generation provider: ${this.config.provider}`);
      }
    } catch (error) {
      console.error('Image generation error:', error);
      throw new Error('Failed to generate image');
    }
  }

  private async generateWithGemini(prompt: string): Promise<string> {
    // Try to use backend proxy first, fall back to placeholder if not available
    try {
      return await this.generateWithGeminiProxy(prompt);
    } catch (error) {
      console.log('Backend proxy not available, using placeholder:', error);
      return this.generatePlaceholderImage(prompt);
    }
  }

  private async generateWithGeminiProxy(prompt: string): Promise<string> {
    // Try to use a local backend proxy server
    const proxyUrl = this.config.proxyUrl || 
                    process.env.REACT_APP_GEMINI_IMAGE_PROXY_URL || 
                    (process.env.REACT_APP_GEMINI_PROXY_BASE_URL ? 
                     `${process.env.REACT_APP_GEMINI_PROXY_BASE_URL}/generate-image` : 
                     'http://localhost:3001/api/generate-image');
    
    console.log('Attempting to use Gemini proxy at:', proxyUrl);
    
    const response = await axios.post(
      proxyUrl,
      { prompt },
      {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 30000 // 30 second timeout
      }
    );

    if (!response.data.imageUrl) {
      throw new Error('No image URL returned from proxy');
    }

    return response.data.imageUrl;
  }

  private generatePlaceholderImage(prompt: string): string {
    // Create a simple SVG placeholder with the prompt text
    const width = this.config.width || 512;
    const height = this.config.height || 512;
    
    const svg = `
      <svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
          </linearGradient>
        </defs>
        <rect width="100%" height="100%" fill="url(#grad1)"/>
        <foreignObject x="20" y="20" width="${width - 40}" height="${height - 40}">
          <div xmlns="http://www.w3.org/1999/xhtml" style="
            color: white; 
            font-family: Arial, sans-serif; 
            font-size: 16px; 
            text-align: center; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            height: 100%; 
            padding: 20px; 
            box-sizing: border-box;
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
          ">
            <div>
              <div style="font-size: 24px; margin-bottom: 10px;">🎨</div>
              <div style="font-weight: bold; margin-bottom: 10px;">Image Requested:</div>
              <div style="font-style: italic;">"${prompt.length > 100 ? prompt.substring(0, 100) + '...' : prompt}"</div>
              <div style="font-size: 12px; margin-top: 15px; opacity: 0.8;">
                Placeholder image - Set up a backend proxy for real Gemini Imagen generation
              </div>
              <div style="font-size: 11px; margin-top: 5px; opacity: 0.7;">
                Or configure proxy URL in settings panel
              </div>
            </div>
          </div>
        </foreignObject>
      </svg>
    `;
    
    // Convert SVG to base64 data URL
    const base64 = btoa(unescape(encodeURIComponent(svg)));
    return `data:image/svg+xml;base64,${base64}`;
  }

  private async generateWithVLLM(prompt: string): Promise<string> {
    if (!this.config.baseUrl) {
      throw new Error('vLLM base URL not configured for image generation');
    }

    // Prepare the request for vLLM image generation
    const requestBody = {
      model: this.config.model || 'flux-1-schnell',
      prompt: prompt,
      steps: this.config.steps || 20,
      width: this.config.width || 512,
      height: this.config.height || 512,
      guidance_scale: 7.5,
      negative_prompt: "blurry, low quality, distorted, ugly"
    };

    console.log('Sending image generation request to vLLM:', requestBody);

    try {
      const response = await axios.post(
        `${this.config.baseUrl}/v1/images/generations`,
        requestBody,
        {
          headers: {
            'Content-Type': 'application/json',
          },
          timeout: 60000 // 60 second timeout for image generation
        }
      );

      if (!response.data.data || response.data.data.length === 0) {
        throw new Error('No image data returned from vLLM server');
      }

      // Return the base64 image or URL
      const imageData = response.data.data[0];
      if (imageData.b64_json) {
        return `data:image/png;base64,${imageData.b64_json}`;
      } else if (imageData.url) {
        return imageData.url;
      } else {
        throw new Error('No image URL or base64 data in response');
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error('vLLM API error:', error.response?.data || error.message);
        throw new Error(`vLLM API error: ${error.response?.data?.error?.message || error.message}`);
      }
      throw error;
    }
  }

  updateConfig(newConfig: Partial<ImageGenConfig>) {
    this.config = { ...this.config, ...newConfig };
  }

  getConfig(): ImageGenConfig {
    return { ...this.config };
  }
}

// Default image generation configuration
export const defaultImageGenConfig = {
  provider: 'gemini' as const,
  apiKey: process.env.REACT_APP_GEMINI_API_KEY || '',
  model: 'imagen-3.0-generate-001',
  steps: 20,
  width: 512,
  height: 512
};
