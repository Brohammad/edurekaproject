import React from 'react';
import './MessageBubble.css';

function MessageBubble({ sender, text, timestamp, category }) {
  const isUser = sender === 'user';
  const label = isUser ? 'You' : 'TechGear Bot';

  // Format timestamp
  const formatTimestamp = (isoString) => {
    if (!isoString) return '';
    const date = new Date(isoString);
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
  };

  return (
    <div className={`message-bubble-container ${isUser ? 'user' : 'bot'}`}>
      <div className={`message-bubble ${isUser ? 'user' : 'bot'}`}>
        <div className="message-header">
          <div className="message-label">{label}</div>
          {timestamp && (
            <div className="message-timestamp">{formatTimestamp(timestamp)}</div>
          )}
        </div>
        <div className="message-text">{text}</div>
        {!isUser && category && (
          <div className="message-category">
            Category: {category}
          </div>
        )}
      </div>
    </div>
  );
}

export default MessageBubble;
