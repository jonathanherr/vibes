import { useState, useCallback } from 'react';
import { speechService } from '../services/speechService';

export const useVoiceRecognition = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSupported] = useState(speechService.isRecognitionSupported());

  const startListening = useCallback(async () => {
    if (!isSupported) {
      setError('Speech recognition not supported');
      return;
    }

    try {
      setIsListening(true);
      setError(null);
      setTranscript('');
      
      const result = await speechService.startListening();
      setTranscript(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Speech recognition failed');
    } finally {
      setIsListening(false);
    }
  }, [isSupported]);

  const stopListening = useCallback(() => {
    speechService.stopListening();
    setIsListening(false);
  }, []);

  const clearTranscript = useCallback(() => {
    setTranscript('');
    setError(null);
  }, []);

  return {
    isListening,
    transcript,
    error,
    isSupported,
    startListening,
    stopListening,
    clearTranscript
  };
};