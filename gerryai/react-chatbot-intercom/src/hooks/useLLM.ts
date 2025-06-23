import { useState, useCallback, useEffect } from 'react';
import { LLMService } from '../services/llmService';
import { LLMConfig, LLMResponse, ChatSettings } from '../types';

export const useLLM = () => {
  console.log('useLLM hook initializing, environment variables:', {
    geminiKey: process.env.REACT_APP_GEMINI_API_KEY ? `${process.env.REACT_APP_GEMINI_API_KEY.substring(0, 10)}...` : 'NOT SET',
    vllmUrl: process.env.REACT_APP_VLLM_BASE_URL || 'NOT SET'
  });
  const [llmService, setLLMService] = useState<LLMService | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [settings, setSettings] = useState<ChatSettings>(() => {
    const geminiApiKey = process.env.REACT_APP_GEMINI_API_KEY || '';
    const vllmBaseUrl = process.env.REACT_APP_VLLM_BASE_URL || 'http://localhost:8000';
    
    console.log('Initial environment variables:', {
      geminiApiKey: geminiApiKey ? `${geminiApiKey.substring(0, 10)}...` : 'none',
      vllmBaseUrl
    });
    
    return {
      selectedLLM: 'gemini',
      geminiConfig: {
        apiKey: geminiApiKey,
        model: 'gemini-pro',
        temperature: 0.7
      },
      vllmConfig: {
        baseUrl: vllmBaseUrl,
        model: 'llama-2-7b-chat',
        temperature: 0.7,
        maxTokens: 1000
      }
    };
  });

  // Initialize LLM service when settings change
  useEffect(() => {
    const config: LLMConfig = settings.selectedLLM === 'gemini' 
      ? {
          provider: 'gemini',
          apiKey: settings.geminiConfig.apiKey,
          model: settings.geminiConfig.model,
          temperature: settings.geminiConfig.temperature
        }
      : {
          provider: 'vllm',
          baseUrl: settings.vllmConfig.baseUrl,
          model: settings.vllmConfig.model,
          temperature: settings.vllmConfig.temperature,
          maxTokens: settings.vllmConfig.maxTokens
        };

    console.log('Initializing LLM service with config:', {
      provider: config.provider,
      hasApiKey: config.provider === 'gemini' ? !!config.apiKey : 'N/A',
      baseUrl: config.provider === 'vllm' ? config.baseUrl : 'N/A'
    });

    try {
      const service = new LLMService(config);
      setLLMService(service);
      setError(null);
      console.log('LLM service initialized successfully');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to initialize LLM service';
      console.error('LLM service initialization error:', errorMessage);
      setError(errorMessage);
      setLLMService(null);
    }
  }, [settings]);

  const generateResponse = useCallback(async (
    prompt: string, 
    conversationHistory?: string[]
  ): Promise<LLMResponse> => {
    if (!llmService) {
      throw new Error('LLM service not initialized');
    }

    console.log('Generating response with LLM service...', {
      provider: settings.selectedLLM,
      prompt: prompt.substring(0, 50) + '...'
    });

    setIsLoading(true);
    setError(null);

    try {
      const response = await llmService.generateResponse(prompt, conversationHistory);
      console.log('LLM response received:', {
        length: response.text.length,
        confidence: response.confidence
      });
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate response';
      console.error('LLM generation error:', err);
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [llmService, settings.selectedLLM]);

  const switchLLM = useCallback((provider: 'gemini' | 'vllm') => {
    setSettings(prev => ({
      ...prev,
      selectedLLM: provider
    }));
  }, []);

  const updateGeminiConfig = useCallback((config: Partial<ChatSettings['geminiConfig']>) => {
    setSettings(prev => ({
      ...prev,
      geminiConfig: { ...prev.geminiConfig, ...config }
    }));
  }, []);

  const updateVLLMConfig = useCallback((config: Partial<ChatSettings['vllmConfig']>) => {
    setSettings(prev => ({
      ...prev,
      vllmConfig: { ...prev.vllmConfig, ...config }
    }));
  }, []);

  const isConfigured = useCallback(() => {
    const configured = settings.selectedLLM === 'gemini' 
      ? !!settings.geminiConfig.apiKey
      : !!settings.vllmConfig.baseUrl;
    
    console.log('isConfigured check:', {
      provider: settings.selectedLLM,
      geminiApiKey: settings.geminiConfig.apiKey ? `${settings.geminiConfig.apiKey.substring(0, 10)}...` : 'none',
      vllmBaseUrl: settings.vllmConfig.baseUrl,
      configured
    });
    
    return configured;
  }, [settings.selectedLLM, settings.geminiConfig.apiKey, settings.vllmConfig.baseUrl]);

  return {
    generateResponse,
    isLoading,
    error,
    settings,
    switchLLM,
    updateGeminiConfig,
    updateVLLMConfig,
    isConfigured,
    currentProvider: settings.selectedLLM
  };
};