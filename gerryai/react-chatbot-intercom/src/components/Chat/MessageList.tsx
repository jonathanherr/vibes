import React from 'react';
import { Message } from '../../types';

interface MessageListProps {
  messages: Message[];
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  return (
    <div className="message-list">
      {messages.length === 0 ? (
        <div className="no-messages">
          <p>No messages yet. Start a conversation!</p>
        </div>
      ) : (
        messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.isUser ? 'user-message' : 'ai-message'}`}
          >
            <div className="message-content">
              <p>{message.text}</p>
              {message.mediaUrl && (
                <div className="message-media">
                  {message.type === 'image' && (
                    <img src={message.mediaUrl} alt="Shared content" />
                  )}
                  {message.type === 'video' && (
                    <video controls>
                      <source src={message.mediaUrl} type="video/mp4" />
                    </video>
                  )}
                </div>
              )}
            </div>
            <div className="message-timestamp">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))
      )}
    </div>
  );
};

export default MessageList;