import React from 'react';
import './MessageBubble.css';

function MessageBubble({ sender, text }) {
  const isUser = sender === 'user';
  const label = isUser ? 'You' : 'TechGear Bot';

  return (
    <div className={`message-bubble-container ${isUser ? 'user' : 'bot'}`}>
      <div className={`message-bubble ${isUser ? 'user' : 'bot'}`}>
        <div className="message-label">{label}</div>
        <div className="message-text">{text}</div>
      </div>
    </div>
  );
}

export default MessageBubble;
