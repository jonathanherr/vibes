import React from 'react';
import { Message } from '../../types';
import ImageViewer from '../Media/ImageViewer';
import VideoPlayer from '../Media/VideoPlayer';

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
                    <ImageViewer 
                      src={message.mediaUrl} 
                      alt="Generated image" 
                      width={300}
                      height={300}
                    />
                  )}
                  {message.type === 'video' && (
                    <VideoPlayer videoUrl={message.mediaUrl} />
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