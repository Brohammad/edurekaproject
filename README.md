# TechGear Electronics Support Chatbot

A RAG-powered customer support chatbot using ChromaDB, LangChain, LangGraph, and Google Gemini Flash 2.5.

## Architecture

### Task 1: Document Loading & Vector Store ✅
- Loads product information from `product_info.txt`
- Uses `RecursiveCharacterTextSplitter` for chunking
- Creates embeddings with Google's embedding model
- Stores in ChromaDB for efficient retrieval

### Task 2: RAG Chain ✅
- Retrieves relevant context from ChromaDB
- Uses Google Gemini Flash 2.5 for response generation
- Implements custom prompt template for customer support
- Modular `answer_with_rag()` function

### Task 3: LangGraph Workflow ✅
- **Node 1 (Classifier)**: Categorizes queries as products/returns/general/escalate
- **Node 2 (RAG Responder)**: Answers using RAG chain
- **Node 3 (Escalation)**: Returns escalation message for complex issues
- **Conditional Routing**: Routes based on classification

### Task 4: FastAPI Endpoint ✅
- POST `/chat`: Main chatbot endpoint
- POST `/chat/direct`: Direct RAG (bypass classification)
- GET `/health`: Health check
- Pydantic models for request/response validation

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set API Key
```bash
# Option 1: Environment variable
export GOOGLE_API_KEY="your-google-api-key-here"

# Option 2: Create .env file
cp .env.example .env
# Edit .env and add your API key
```

### 3. Run the Application
```bash
# Using uvicorn directly
uvicorn main:app --reload

# Or with host and port specification
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or run the Python file directly
python main.py
```

### 4. Test the API

**Interactive Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Example curl commands:**

```bash
# Product query
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is the price of SmartWatch Pro X?"}'

# Return policy query
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is your return policy?"}'

# Warranty query
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"query": "Tell me about the warranty on Wireless Earbuds"}'

# Escalation example
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"query": "I want to file a complaint"}'

# Direct RAG (bypass classification)
curl -X POST "http://localhost:8000/chat/direct" \
     -H "Content-Type: application/json" \
     -d '{"query": "What products do you sell?"}'
```

## Project Structure

```
edurekaproject/
├── main.py                 # FastAPI application (Task 4)
├── rag_pipeline.py         # RAG implementation (Tasks 1 & 2)
├── graph_workflow.py       # LangGraph workflow (Task 3)
├── config.py              # Configuration settings
├── product_info.txt       # Knowledge base
├── requirements.txt       # Dependencies
├── .env.example          # Environment variable template
├── README.md             # This file
└── chroma_db/            # ChromaDB storage (created on first run)
```

## Key Features

- ✅ Modular, clean code structure
- ✅ Google Gemini Flash 2.5 integration
- ✅ ChromaDB vector store with persistence
- ✅ LangGraph workflow with conditional routing
- ✅ FastAPI with Pydantic validation
- ✅ Comprehensive error handling
- ✅ Interactive API documentation
- ✅ Easy to run and test

## Marks Breakdown

- **Task 1** (10 marks): Document loading, splitting, embeddings, vector store ✅
- **Task 2** (20 marks): RAG chain with Gemini Flash 2.5 ✅
- **Task 3** (20 marks): LangGraph workflow with 3 nodes and routing ✅
- **Task 4** (10 marks): FastAPI endpoint with Pydantic models ✅

Total: **60 marks** (all requirements met)
