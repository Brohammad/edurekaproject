import React, { useState, useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';
import './ChatWindow.css';

const API_BASE_URL = "http://127.0.0.1:8000";

function ChatWindow() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'bot',
      text: "Hi! I'm the TechGear Support Chatbot. Ask me about our products, returns, or support hours."
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const nextIdRef = useRef(2);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    const trimmedMessage = inputValue.trim();
    if (!trimmedMessage || isLoading) return;

    // Clear any previous errors
    setError(null);

    // Add user message to chat
    const userMessage = {
      id: nextIdRef.current++,
      sender: 'user',
      text: trimmedMessage
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: trimmedMessage }),
      });

      if (!response.ok) {
        throw new Error(`Server responded with status: ${response.status}`);
      }

      const data = await response.json();

      // Add bot response to chat
      const botMessage = {
        id: nextIdRef.current++,
        sender: 'bot',
        text: data.response || 'Sorry, I received an empty response.'
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      console.error('Error calling API:', err);
      setError('Failed to contact server. Please try again.');

      // Add error message to chat
      const errorMessage = {
        id: nextIdRef.current++,
        sender: 'bot',
        text: "Sorry, I couldn't reach the server. Please try again in a moment."
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-window">
      <div className="messages-container">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            sender={message.sender}
            text={message.text}
          />
        ))}
        
        {isLoading && (
          <div className="typing-indicator">
            <span>TechGear bot is typing…</span>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}

      <div className="input-area">
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message here..."
          rows="3"
          disabled={isLoading}
          className="message-input"
        />
        <button
          onClick={sendMessage}
          disabled={!inputValue.trim() || isLoading}
          className="send-button"
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatWindow;
