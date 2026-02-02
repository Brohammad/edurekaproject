"""
TASK 4: FastAPI Endpoint Implementation

TechGear Electronics RAG Chatbot API

SETUP INSTRUCTIONS:
===================
1. Install dependencies:
   pip install -r requirements.txt

2. Set environment variable:
   export GOOGLE_API_KEY="your-google-api-key-here"
   
   Or create a .env file with:
   GOOGLE_API_KEY=your-google-api-key-here

3. Run the FastAPI app:
   uvicorn main:app --reload
   
   Or:
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

4. Test the endpoint:
   
   Example curl command:
   curl -X POST "http://localhost:8000/chat" \
        -H "Content-Type: application/json" \
        -d '{"query": "What is the price of SmartWatch Pro X?"}'
   
   Example with returns policy:
   curl -X POST "http://localhost:8000/chat" \
        -H "Content-Type: application/json" \
        -d '{"query": "What is your return policy?"}'
   
   Example escalation:
   curl -X POST "http://localhost:8000/chat" \
        -H "Content-Type: application/json" \
        -d '{"query": "I want to file a complaint about my order"}'

5. Access API docs:
   http://localhost:8000/docs (Swagger UI)
   http://localhost:8000/redoc (ReDoc)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn

from graph_workflow import run_chatbot_flow
from rag_pipeline import get_rag_pipeline

# Initialize FastAPI app
app = FastAPI(
    title="TechGear Electronics Support Chatbot",
    description="RAG-powered customer support chatbot using ChromaDB, LangChain, LangGraph, and Gemini Flash 2.5",
    version="1.0.0"
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    query: str = Field(..., description="Customer's question or query", min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the price of SmartWatch Pro X?"
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="Chatbot's response to the query")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "The SmartWatch Pro X is priced at ₹15,999."
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str
    message: str


# Startup event to initialize RAG pipeline
@app.on_event("startup")
async def startup_event():
    """Initialize the RAG pipeline on app startup."""
    print("Starting up TechGear Support Chatbot...")
    try:
        # Initialize RAG pipeline (this loads documents and creates vector store)
        get_rag_pipeline()
        print("RAG pipeline initialized successfully!")
    except Exception as e:
        print(f"Error initializing RAG pipeline: {e}")
        raise


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check."""
    return HealthResponse(
        status="ok",
        message="TechGear Electronics Support Chatbot API is running. Visit /docs for API documentation."
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="All systems operational"
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint that processes customer queries using the LangGraph workflow.
    
    The workflow:
    1. Classifies the query (products, returns, general, or escalate)
    2. Routes to RAG responder or escalation handler
    3. Returns the appropriate response
    
    Args:
        request: ChatRequest with user query
        
    Returns:
        ChatResponse with chatbot answer
    """
    try:
        print(f"\nReceived query: {request.query}")
        
        # Run the LangGraph workflow
        response = run_chatbot_flow(request.query)
        
        print(f"Generated response: {response[:100]}...")
        
        return ChatResponse(response=response)
    
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing your query: {str(e)}"
        )


# Optional: Direct RAG endpoint (bypasses classification)
@app.post("/chat/direct", response_model=ChatResponse)
async def chat_direct(request: ChatRequest):
    """
    Direct RAG endpoint that bypasses the classification step.
    Useful for debugging or when you want to force RAG retrieval.
    
    Args:
        request: ChatRequest with user query
        
    Returns:
        ChatResponse with RAG-generated answer
    """
    try:
        from rag_pipeline import answer_with_rag
        
        print(f"\nDirect RAG query: {request.query}")
        response = answer_with_rag(request.query)
        
        return ChatResponse(response=response)
    
    except Exception as e:
        print(f"Error in direct RAG: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing your query: {str(e)}"
        )


if __name__ == "__main__":
    # Run with: python main.py
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
