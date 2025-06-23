import { useState, useCallback } from 'react';
import { speechService } from '../services/speechService';
import { VoiceSettings } from '../types';

export const useSpeechSynthesis = () => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSupported] = useState(speechService.isSynthesisSupported());

  const speak = useCallback(async (text: string, settings?: Partial<VoiceSettings>) => {
    if (!isSupported) {
      setError('Speech synthesis not supported');
      return;
    }

    try {
      setIsSpeaking(true);
      setError(null);
      await speechService.speak(text, settings);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Speech synthesis failed');
    } finally {
      setIsSpeaking(false);
    }
  }, [isSupported]);

  const stopSpeaking = useCallback(() => {
    speechService.stopSpeaking();
    setIsSpeaking(false);
  }, []);

  const getVoices = useCallback(() => {
    return speechService.getAvailableVoices();
  }, []);

  return {
    isSpeaking,
    error,
    isSupported,
    speak,
    stopSpeaking,
    getVoices
  };
};