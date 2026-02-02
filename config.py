"""
Configuration module for the RAG chatbot.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set!")

# Model Configuration
GEMINI_MODEL = "gemini-2.0-flash-exp"  # Gemini Flash 2.5 model
EMBEDDING_MODEL = "models/embedding-001"  # Google's embedding model

# Document Configuration
KNOWLEDGE_BASE_PATH = "product_info.txt"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# ChromaDB Configuration
CHROMA_COLLECTION_NAME = "techgear_support"
CHROMA_PERSIST_DIRECTORY = "./chroma_db"
