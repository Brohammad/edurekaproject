import React from 'react';
import ChatWindow from './components/ChatWindow';
import './App.css';

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>TechGear Support Chatbot</h1>
        <p className="subtitle">Ask about products, returns, or general support.</p>
      </header>
      <main className="app-main">
        <ChatWindow />
      </main>
    </div>
  );
}

export default App;
