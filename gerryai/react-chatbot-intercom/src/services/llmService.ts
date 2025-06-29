import { GoogleGenerativeAI } from '@google/generative-ai';
import axios from 'axios';
import { LLMConfig, LLMResponse } from '../types';

export class LLMService {
  private geminiClient: GoogleGenerativeAI | null = null;
  private config: LLMConfig;

  constructor(config: LLMConfig) {
    this.config = config;
    
    console.log('LLMService constructor called with config:', {
      provider: config.provider,
      hasApiKey: config.provider === 'gemini' ? !!config.apiKey : 'N/A',
      apiKeyPrefix: config.provider === 'gemini' && config.apiKey ? config.apiKey.substring(0, 10) : 'none',
      baseUrl: config.provider === 'vllm' ? config.baseUrl : 'N/A'
    });
    
    if (config.provider === 'gemini' && config.apiKey) {
      try {
        this.geminiClient = new GoogleGenerativeAI(config.apiKey);
        console.log('Gemini client initialized successfully');
      } catch (error) {
        console.error('Failed to initialize Gemini client:', error);
        throw error;
      }
    } else if (config.provider === 'gemini') {
      console.warn('Gemini provider selected but no API key provided');
    }
  }

  async generateResponse(prompt: string, conversationHistory?: string[]): Promise<LLMResponse> {
    try {
      if (this.config.provider === 'gemini') {
        return await this.generateGeminiResponse(prompt, conversationHistory);
      } else if (this.config.provider === 'vllm') {
        return await this.generateVLLMResponse(prompt, conversationHistory);
      } else {
        throw new Error(`Unsupported LLM provider: ${this.config.provider}`);
      }
    } catch (error) {
      console.error('LLM generation error:', error);
      throw new Error('Failed to generate response from LLM');
    }
  }

  private async generateGeminiResponse(prompt: string, conversationHistory?: string[]): Promise<LLMResponse> {
    // Check if proxy mode is enabled
    if (this.config.proxyBaseUrl) {
      return await this.generateGeminiProxyResponse(prompt, conversationHistory);
    }

    if (!this.geminiClient) {
      throw new Error('Gemini client not initialized. Please check your API key.');
    }

    console.log('Generating Gemini response for prompt:', prompt.substring(0, 50) + '...');

    const model = this.geminiClient.getGenerativeModel({ 
      model: this.config.model || 'gemini-pro',
      generationConfig: {
        temperature: this.config.temperature || 0.7,
        maxOutputTokens: this.config.maxTokens || 1000,
      }
    });

    // Build conversation context
    let fullPrompt = prompt;
    if (conversationHistory && conversationHistory.length > 0) {
      const context = conversationHistory.slice(-10).join('\n'); // Last 10 messages for context
      fullPrompt = `Previous conversation:\n${context}\n\nCurrent message: ${prompt}`;
    }

    console.log('Sending request to Gemini with prompt length:', fullPrompt.length);

    try {
      const result = await model.generateContent(fullPrompt);
      const response = await result.response;
      const text = response.text();

      console.log('Gemini response received:', {
        length: text.length,
        preview: text.substring(0, 100) + '...'
      });

      return {
        text,
        confidence: 0.9 // Gemini doesn't provide confidence scores
      };
    } catch (error) {
      console.error('Gemini API error:', error);
      throw new Error(`Gemini API error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  private async generateGeminiProxyResponse(prompt: string, conversationHistory?: string[]): Promise<LLMResponse> {
    console.log('Using Gemini proxy for text generation:', this.config.proxyBaseUrl);

    try {
      const response = await axios.post(
        `${this.config.proxyBaseUrl}/generate-text`,
        {
          prompt,
          model: this.config.model || 'gemini-1.5-flash',
          temperature: this.config.temperature || 0.7,
          maxTokens: this.config.maxTokens || 1000,
          conversationHistory: conversationHistory || []
        },
        {
          headers: {
            'Content-Type': 'application/json',
          },
          timeout: 30000
        }
      );

      if (!response.data.text) {
        throw new Error('No text returned from proxy');
      }

      console.log('Proxy response received:', {
        length: response.data.text.length,
        preview: response.data.text.substring(0, 100) + '...'
      });

      return {
        text: response.data.text,
        confidence: 0.9
      };
    } catch (error) {
      console.error('Gemini proxy error:', error);
      if (axios.isAxiosError(error)) {
        throw new Error(`Proxy API error: ${error.response?.data?.error || error.message}`);
      }
      throw new Error(`Proxy error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  private async generateVLLMResponse(prompt: string, conversationHistory?: string[]): Promise<LLMResponse> {
    if (!this.config.baseUrl) {
      throw new Error('vLLM base URL not configured');
    }

    // Build messages array for chat completion
    const messages = [];
    
    // Add conversation history
    if (conversationHistory && conversationHistory.length > 0) {
      conversationHistory.slice(-10).forEach((msg, index) => {
        messages.push({
          role: index % 2 === 0 ? 'user' : 'assistant',
          content: msg
        });
      });
    }

    // Add current prompt
    messages.push({
      role: 'user',
      content: prompt
    });

    const requestBody = {
      model: this.config.model || 'llama-2-7b-chat',
      messages,
      temperature: this.config.temperature || 0.7,
      max_tokens: this.config.maxTokens || 1000,
      stream: false
    };

    const response = await axios.post(
      `${this.config.baseUrl}/v1/chat/completions`,
      requestBody,
      {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 30000 // 30 second timeout
      }
    );

    if (!response.data.choices || response.data.choices.length === 0) {
      throw new Error('No response from vLLM server');
    }

    const choice = response.data.choices[0];
    return {
      text: choice.message.content,
      confidence: choice.logprobs ? Math.exp(choice.logprobs) : undefined
    };
  }

  async listGeminiModels(): Promise<string[]> {
    if (!this.geminiClient) {
      throw new Error('Gemini client not initialized. Please check your API key.');
    }

    try {
      // Use the REST API to list models since the SDK doesn't have a direct method
      const response = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models?key=${this.config.apiKey}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch models: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Available Gemini models:', data);

      // Extract model names and filter for generative models
      const models = data.models
        ?.filter((model: any) => 
          model.name?.includes('gemini') && 
          model.supportedGenerationMethods?.includes('generateContent')
        )
        ?.map((model: any) => model.name.replace('models/', ''))
        ?.sort() || [];

      return models.length > 0 ? models : ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro'];
    } catch (error) {
      console.error('Error fetching Gemini models:', error);
      // Return default models if fetch fails
      return ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro'];
    }
  }

  updateConfig(newConfig: LLMConfig) {
    this.config = { ...this.config, ...newConfig };
    
    // Reinitialize Gemini client if provider or API key changed
    if (newConfig.provider === 'gemini' && newConfig.apiKey) {
      this.geminiClient = new GoogleGenerativeAI(newConfig.apiKey);
    }
  }

  getConfig(): LLMConfig {
    return { ...this.config };
  }
}

// Default configurations
export const defaultLLMConfigs = {
  gemini: {
    provider: 'gemini' as const,
    model: 'gemini-1.5-flash',
    temperature: 0.7,
    maxTokens: 1000,
    apiKey: process.env.REACT_APP_GEMINI_API_KEY || ''
  },
  vllm: {
    provider: 'vllm' as const,
    baseUrl: process.env.REACT_APP_VLLM_BASE_URL || 'http://localhost:8000',
    model: 'llama-2-7b-chat',
    temperature: 0.7,
    maxTokens: 1000
  }
};