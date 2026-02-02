"""
TASK 1 & 2: RAG Pipeline Implementation
- Document loading and vector store creation
- RAG chain for question answering
"""
# Fix for SQLite version compatibility on Linux
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
import logging
from typing import List, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

import config

# Configure logging
logger = logging.getLogger(__name__)

# Relevance threshold for retrieved documents
RELEVANCE_THRESHOLD = 0.4  # Adjust based on your embedding model's score range


class RAGPipeline:
    """RAG Pipeline for TechGear Electronics customer support."""
    
    def __init__(self):
        self.vectorstore = None
        self.retriever = None
        self.rag_chain = None
        self.llm = None
        
    def load_documents(self) -> List[Document]:
        """
        Load documents from the knowledge base file.
        
        Returns:
            List of Document objects
        """
        logger.info(f"Loading documents from {config.KNOWLEDGE_BASE_PATH}...")
        
        if not os.path.exists(config.KNOWLEDGE_BASE_PATH):
            raise FileNotFoundError(f"Knowledge base file not found: {config.KNOWLEDGE_BASE_PATH}")
        
        with open(config.KNOWLEDGE_BASE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create a single document
        documents = [Document(page_content=content, metadata={"source": config.KNOWLEDGE_BASE_PATH})]
        logger.info(f"Loaded {len(documents)} document(s)")
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks for better retrieval.
        
        Args:
            documents: List of documents to split
            
        Returns:
            List of chunked documents
        """
        logger.info("Splitting documents into chunks...")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
    
    def create_vector_store(self, chunks: List[Document]) -> Chroma:
        """
        Create a ChromaDB vector store from document chunks.
        
        Args:
            chunks: List of document chunks
            
        Returns:
            ChromaDB vector store
        """
        logger.info("Creating embeddings and vector store...")
        
        # Initialize Google embeddings
        embeddings = GoogleGenerativeAIEmbeddings(
            model=config.EMBEDDING_MODEL,
            google_api_key=config.GOOGLE_API_KEY
        )
        
        # Create ChromaDB vector store
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=config.CHROMA_COLLECTION_NAME,
            persist_directory=config.CHROMA_PERSIST_DIRECTORY
        )
        
        logger.info("Vector store created successfully")
        return vectorstore
    
    def setup_rag_chain(self):
        """
        Set up the complete RAG chain with retriever and LLM.
        """
        logger.info("Setting up RAG chain...")
        
        # Load and process documents
        documents = self.load_documents()
        chunks = self.split_documents(documents)
        self.vectorstore = self.create_vector_store(chunks)
        
        # Create retriever - we'll use similarity_score_threshold for relevance filtering
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": 3,  # Retrieve top 3 relevant chunks
                "score_threshold": RELEVANCE_THRESHOLD
            }
        )
        
        # Initialize Gemini Flash 2.5 LLM
        self.llm = ChatGoogleGenerativeAI(
            model=config.GEMINI_MODEL,
            google_api_key=config.GOOGLE_API_KEY,
            temperature=0.3
        )
        
        # Create custom prompt for RAG
        prompt_template = """You are a helpful customer support assistant for TechGear Electronics.
Use the following context to answer the customer's question accurately and professionally.
If you don't know the answer based on the context, say so politely.

Context: {context}

Question: {question}

Answer:"""
        
        self.prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        logger.info("RAG chain setup complete!")
    
    def retrieve_with_scores(self, question: str) -> Tuple[List[Document], bool]:
        """
        Retrieve documents and determine if context is sufficient.
        
        Args:
            question: User's question
            
        Returns:
            Tuple of (documents, has_reliable_context)
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized.")
        
        # Get documents with similarity scores
        docs_with_scores = self.vectorstore.similarity_search_with_relevance_scores(
            question, k=3
        )
        
        logger.info(f"Retrieved {len(docs_with_scores)} documents")
        
        # Check if we have reliable context
        has_reliable_context = (
            len(docs_with_scores) > 0 and 
            docs_with_scores[0][1] >= RELEVANCE_THRESHOLD
        )
        
        if has_reliable_context:
            logger.info(f"Found reliable context with score: {docs_with_scores[0][1]:.3f}")
        else:
            best_score = docs_with_scores[0][1] if docs_with_scores else 0.0
            logger.warning(f"No reliable context found. Best score: {best_score:.3f}")
        
        # Extract just the documents
        docs = [doc for doc, score in docs_with_scores]
        
        return docs, has_reliable_context
    
    def answer_with_rag(self, question: str, history: str = "") -> str:
        """
        Answer a question using the RAG chain with conversation history support.
        
        Args:
            question: User's question
            history: Optional conversation history context
            
        Returns:
            Generated answer or fallback message
        """
        if self.llm is None:
            raise ValueError("RAG chain not initialized. Call setup_rag_chain() first.")
        
        # Retrieve documents and check relevance
        docs, has_reliable_context = self.retrieve_with_scores(question)
        
        # If no reliable context, return fallback message
        if not has_reliable_context:
            logger.info("Using fallback response due to insufficient context")
            return (
                "I don't have specific information about that in TechGear's knowledge base. "
                "Please contact support@techgear.com for more details."
            )
        
        # Format context
        context = "\n\n".join(doc.page_content for doc in docs)
        
        # Include history if provided
        if history:
            enhanced_question = f"Conversation history:\n{history}\n\nCurrent question: {question}"
            logger.info(f"Using conversation history (length: {len(history)} chars)")
        else:
            enhanced_question = question
        
        # Generate response using LLM
        prompt_text = self.prompt.format(context=context, question=enhanced_question)
        result = self.llm.invoke(prompt_text)
        
        return result.content


# Global instance
_rag_pipeline = None


def get_rag_pipeline() -> RAGPipeline:
    """
    Get or create the global RAG pipeline instance.
    
    Returns:
        RAGPipeline instance
    """
    global _rag_pipeline
    if _rag_pipeline is None:
        logger.info("Initializing RAG pipeline...")
        _rag_pipeline = RAGPipeline()
        _rag_pipeline.setup_rag_chain()
    return _rag_pipeline


def answer_with_rag(question: str, history: str = "") -> str:
    """
    Convenience function to answer questions using RAG.
    
    Args:
        question: User's question
        history: Optional conversation history
        
    Returns:
        Generated answer
    """
    pipeline = get_rag_pipeline()
    return pipeline.answer_with_rag(question, history)
