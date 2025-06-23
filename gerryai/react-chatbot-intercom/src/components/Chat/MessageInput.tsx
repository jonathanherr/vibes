import React, { useState } from 'react';
import VoiceInput from './VoiceInput';

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

const MessageInput: React.FC<MessageInputProps> = ({ onSendMessage, disabled = false }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleVoiceTranscript = (transcript: string) => {
    if (transcript.trim()) {
      setMessage(transcript);
      // Optionally auto-send voice messages
      // onSendMessage(transcript.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="message-input-form">
      <div className="input-container">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message or use voice input..."
          disabled={disabled}
          className="message-input"
        />
        
        <VoiceInput 
          onTranscript={handleVoiceTranscript}
          disabled={disabled}
        />
        
        <button 
          type="submit" 
          disabled={!message.trim() || disabled}
          className="send-button"
        >
          Send
        </button>
      </div>
    </form>
  );
};

export default MessageInput;