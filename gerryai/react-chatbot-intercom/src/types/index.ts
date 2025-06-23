export interface Message {
  id: string;
  text: string;
  timestamp: Date;
  isUser: boolean;
  type: 'text' | 'image' | 'video' | 'audio';
  mediaUrl?: string;
  deviceId?: string;
}

export interface VoiceSettings {
  language: string;
  rate: number;
  pitch: number;
  volume: number;
}

export interface SpeechRecognitionResult {
  transcript: string;
  confidence: number;
  isFinal: boolean;
}

export interface IntercomDevice {
  id: string;
  name: string;
  isOnline: boolean;
  lastSeen: Date;
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}

export interface LLMResponse {
  text: string;
  mediaUrls?: string[];
  confidence?: number;
}

export interface LLMConfig {
  provider: 'gemini' | 'vllm';
  apiKey?: string;
  baseUrl?: string;
  model?: string;
  temperature?: number;
  maxTokens?: number;
}

export interface ChatSettings {
  selectedLLM: 'gemini' | 'vllm';
  geminiConfig: {
    apiKey: string;
    model: string;
    temperature: number;
  };
  vllmConfig: {
    baseUrl: string;
    model: string;
    temperature: number;
    maxTokens: number;
  };
}