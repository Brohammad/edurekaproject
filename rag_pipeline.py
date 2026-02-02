"""
TASK 1 & 2: RAG Pipeline Implementation
- Document loading and vector store creation
- RAG chain for question answering
"""
import os
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

import config


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
        print(f"Loading documents from {config.KNOWLEDGE_BASE_PATH}...")
        
        if not os.path.exists(config.KNOWLEDGE_BASE_PATH):
            raise FileNotFoundError(f"Knowledge base file not found: {config.KNOWLEDGE_BASE_PATH}")
        
        with open(config.KNOWLEDGE_BASE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create a single document
        documents = [Document(page_content=content, metadata={"source": config.KNOWLEDGE_BASE_PATH})]
        print(f"Loaded {len(documents)} document(s)")
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks for better retrieval.
        
        Args:
            documents: List of documents to split
            
        Returns:
            List of chunked documents
        """
        print("Splitting documents into chunks...")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        print(f"Created {len(chunks)} chunks")
        return chunks
    
    def create_vector_store(self, chunks: List[Document]) -> Chroma:
        """
        Create a ChromaDB vector store from document chunks.
        
        Args:
            chunks: List of document chunks
            
        Returns:
            ChromaDB vector store
        """
        print("Creating embeddings and vector store...")
        
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
        
        print("Vector store created successfully")
        return vectorstore
    
    def setup_rag_chain(self):
        """
        Set up the complete RAG chain with retriever and LLM.
        """
        print("Setting up RAG chain...")
        
        # Load and process documents
        documents = self.load_documents()
        chunks = self.split_documents(documents)
        self.vectorstore = self.create_vector_store(chunks)
        
        # Create retriever
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}  # Retrieve top 3 relevant chunks
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
        
        # Create RAG chain using LCEL
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        self.rag_chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        print("RAG chain setup complete!")
    
    def answer_with_rag(self, question: str) -> str:
        """
        Answer a question using the RAG chain.
        
        Args:
            question: User's question
            
        Returns:
            Generated answer
        """
        if self.rag_chain is None:
            raise ValueError("RAG chain not initialized. Call setup_rag_chain() first.")
        
        result = self.rag_chain.invoke(question)
        return result


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
        _rag_pipeline = RAGPipeline()
        _rag_pipeline.setup_rag_chain()
    return _rag_pipeline


def answer_with_rag(question: str) -> str:
    """
    Convenience function to answer questions using RAG.
    
    Args:
        question: User's question
        
    Returns:
        Generated answer
    """
    pipeline = get_rag_pipeline()
    return pipeline.answer_with_rag(question)
