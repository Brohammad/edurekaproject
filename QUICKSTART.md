# TechGear Chatbot - Quick Start Guide

## 🎯 Complete Setup Instructions

### Step 1: Start the Backend

```bash
# Navigate to project root
cd /home/labuser/edurekaproject

# Start the FastAPI backend
./venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

The backend will be available at `http://127.0.0.1:8000`

### Step 2: Install Frontend Dependencies (First Time Only)

```bash
# Open a new terminal and navigate to frontend
cd /home/labuser/edurekaproject/frontend

# Install dependencies
npm install
```

### Step 3: Start the Frontend

```bash
# From the frontend directory
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Step 4: Test the Application

1. Open your browser to `http://localhost:5173`
2. You should see the TechGear Support Chatbot interface
3. Try asking questions like:
   - "What is the price of SmartWatch Pro X?"
   - "What is your return policy?"
   - "Tell me about the gaming laptop"

## 🔍 Verify Everything is Working

### Check Backend Health
```bash
curl http://127.0.0.1:8000/health
```

Should return: `{"status":"ok","message":"TechGear Support Chatbot is running"}`

### Check API Endpoint
```bash
curl -X POST "http://127.0.0.1:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"query": "What products do you have?"}'
```

## 🎨 What You Get

### Frontend Features:
- ✅ Modern, gradient-based UI
- ✅ Real-time chat interface
- ✅ Typing indicators
- ✅ Error handling and display
- ✅ Responsive design (mobile-friendly)
- ✅ Smooth animations
- ✅ Auto-scrolling chat
- ✅ Keyboard shortcuts (Enter to send)

### Backend Features:
- ✅ RAG pipeline with ChromaDB
- ✅ LangGraph workflow
- ✅ Gemini Flash 2.5 AI
- ✅ Product information retrieval
- ✅ Returns policy handling
- ✅ CORS enabled for frontend

## 🐛 Troubleshooting

### Backend won't start?
- Check if the virtual environment is activated
- Verify all dependencies are installed: `./venv/bin/pip install -r requirements.txt`
- Check if port 8000 is available: `lsof -i:8000`

### Frontend won't start?
- Ensure Node.js is installed: `node --version`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check if port 5173 is available: `lsof -i:5173`

### CORS errors in browser?
- Backend CORS middleware is already configured for `http://localhost:5173`
- Make sure the backend started successfully before opening the frontend

### Chat not working?
- Open browser DevTools (F12) and check Console for errors
- Verify backend is responding: `curl http://127.0.0.1:8000/health`
- Check Network tab to see API calls

## 📁 Project Structure

```
edurekaproject/
├── backend (Python)
│   ├── main.py              # FastAPI app with CORS
│   ├── rag_pipeline.py      # RAG implementation
│   ├── graph_workflow.py    # LangGraph workflow
│   ├── config.py            # Configuration
│   └── requirements.txt     # Python dependencies
│
└── frontend (React)
    ├── src/
    │   ├── components/
    │   │   ├── ChatWindow.jsx    # Main chat UI
    │   │   └── MessageBubble.jsx # Message component
    │   ├── App.jsx               # Root component
    │   └── main.jsx              # Entry point
    ├── package.json              # Node dependencies
    └── vite.config.js           # Vite config
```

## 🚀 Development Tips

### Run both servers simultaneously:

**Terminal 1 (Backend):**
```bash
cd /home/labuser/edurekaproject
./venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 (Frontend):**
```bash
cd /home/labuser/edurekaproject/frontend
npm run dev
```

### Hot Reload
- Backend: `--reload` flag enables auto-restart on code changes
- Frontend: Vite automatically hot-reloads on file changes

## 🎉 You're All Set!

Visit `http://localhost:5173` and start chatting with your TechGear Support Bot!
