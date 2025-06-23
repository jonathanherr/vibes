import React, { useEffect } from 'react';
import { useVoiceRecognition } from '../../hooks/useVoiceRecognition';

interface VoiceInputProps {
  onTranscript: (text: string) => void;
  disabled?: boolean;
}

const VoiceInput: React.FC<VoiceInputProps> = ({ onTranscript, disabled = false }) => {
  const { isListening, transcript, error, isSupported, startListening, stopListening } = useVoiceRecognition();

  useEffect(() => {
    if (transcript) {
      onTranscript(transcript);
    }
  }, [transcript, onTranscript]);

  const handleVoiceToggle = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  if (!isSupported) {
    return (
      <div className="voice-input-unsupported">
        <span>Voice input not supported in this browser</span>
      </div>
    );
  }

  return (
    <div className="voice-input">
      <button
        onClick={handleVoiceToggle}
        disabled={disabled}
        className={`voice-button ${isListening ? 'listening' : ''}`}
        type="button"
      >
        {isListening ? '🛑' : '🎤'}
      </button>
      
      {isListening && (
        <div className="listening-indicator">
          <span>Listening...</span>
          <div className="pulse-animation"></div>
        </div>
      )}
      
      {error && (
        <div className="voice-error">
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};

export default VoiceInput;