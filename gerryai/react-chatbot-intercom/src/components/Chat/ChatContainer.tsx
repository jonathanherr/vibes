import React, { useState, useCallback } from 'react';
import { Message } from '../../types';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import LLMSettings from './LLMSettings';
import { useSpeechSynthesis } from '../../hooks/useSpeechSynthesis';
import { useLLM } from '../../hooks/useLLM';

const ChatContainer: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      text: 'Hello! I\'m your AI assistant. Try typing a message or click the microphone button to use voice input. Configure your AI provider in the settings above for better responses!',
      timestamp: new Date(),
      isUser: false,
      type: 'text'
    }
  ]);
  const [conversationHistory, setConversationHistory] = useState<string[]>([]);
  const { speak, isSpeaking } = useSpeechSynthesis();
  const { generateResponse, isLoading, error: llmError, isConfigured, settings, currentProvider } = useLLM();

  const handleSendMessage = useCallback(async (text: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      text,
      timestamp: new Date(),
      isUser: true,
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);
    
    // Update conversation history
    const newHistory = [...conversationHistory, text];
    setConversationHistory(newHistory);

    try {
      let aiResponseText: string;
      
      const configStatus = isConfigured();
      const apiKey = settings.geminiConfig.apiKey;
      console.log('Configuration check:', {
        isConfigured: configStatus,
        provider: currentProvider,
        hasApiKey: !!apiKey,
        apiKeyLength: apiKey?.length || 0
      });
      
      if (configStatus) {
        // Use configured LLM
        console.log('Using configured LLM...');
        const aiResponse = await generateResponse(text, conversationHistory);
        aiResponseText = aiResponse.text;
      } else {
        // Use mock response when not configured
        console.log('Using mock response...');
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate delay
        const mockResponses = [
          `I received your message: "${text}". Please configure an LLM in the settings to get AI responses.`,
          "To get started, click the settings button and add your Gemini API key or vLLM server URL.",
          `You said: "${text}". I'm using mock responses since no LLM is configured yet.`,
          "Great question! Configure your AI provider in the settings panel above to get real responses.",
          "Hello! I'm working with mock responses. Configure a real LLM in the settings for better answers."
        ];
        aiResponseText = mockResponses[Math.floor(Math.random() * mockResponses.length)];
      }
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: aiResponseText,
        timestamp: new Date(),
        isUser: false,
        type: 'text'
      };

      setMessages(prev => [...prev, aiMessage]);
      
      // Update conversation history with AI response
      setConversationHistory(prev => [...prev, aiResponseText]);
      
      // Speak the AI response
      try {
        await speak(aiResponseText);
      } catch (speechError) {
        console.log('Speech synthesis not available or failed:', speechError);
      }
      
    } catch (error) {
      console.error('Error getting AI response:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Using mock response instead.`,
        timestamp: new Date(),
        isUser: false,
        type: 'text'
      };
      
      setMessages(prev => [...prev, errorMessage]);
    }
  }, [generateResponse, conversationHistory, speak, isConfigured, settings, currentProvider]);

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>AI Chatbot</h2>
        <div className="header-controls">
          <LLMSettings />
          {(isLoading || isSpeaking) && (
            <div className="status-indicator">
              {isLoading && <span>🤔 Thinking...</span>}
              {isSpeaking && <span>🔊 Speaking...</span>}
            </div>
          )}
        </div>
      </div>
      
      {llmError && (
        <div className="error-banner">
          <span>⚠️ {llmError}</span>
        </div>
      )}
      
      <MessageList messages={messages} />
      
      <MessageInput 
        onSendMessage={handleSendMessage}
        disabled={isLoading}
      />
    </div>
  );
};

export default ChatContainer;