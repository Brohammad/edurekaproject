"""
TASK 3: LangGraph Workflow Implementation
- Query classification
- Conditional routing
- RAG response or escalation
"""
import logging
from typing import Dict, Literal, TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

import config
from rag_pipeline import answer_with_rag

# Configure logging
logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    query: str
    history: str
    category: str
    response: str


class ChatbotWorkflow:
    """LangGraph workflow for TechGear chatbot."""
    
    def __init__(self):
        """Initialize the workflow with LLM for classification."""
        self.llm = ChatGoogleGenerativeAI(
            model=config.GEMINI_MODEL,
            google_api_key=config.GOOGLE_API_KEY,
            temperature=0.1,
            convert_system_message_to_human=True
        )
        self.graph = self._build_graph()
    
    def classify_query(self, state: Dict) -> Dict:
        """
        Node 1: Classifier
        Categorize the user query into one of: products, returns, general, or escalate.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with category
        """
        query = state.get("query", "")
        
        # Pre-check for out-of-scope queries using rule-based checks
        out_of_scope_keywords = [
            "lawsuit", "legal", "sue", "court", "lawyer",
            "broken screen", "repair my", "fix my device",
            "payment failed", "payment error", "charged twice",
            "spam", "abuse", "hate", "scam"
        ]
        
        query_lower = query.lower()
        for keyword in out_of_scope_keywords:
            if keyword in query_lower:
                logger.info(f"Query matched out-of-scope keyword: {keyword}")
                state["category"] = "escalate"
                return state
        
        # Classification prompt
        classification_prompt = PromptTemplate(
            template="""You are a query classifier for TechGear Electronics customer support.
Classify the following customer query into EXACTLY ONE of these categories:
- "products": Questions about product features, prices, specifications, warranty
- "returns": Questions about return policy, refunds, return process
- "general": Questions about support hours, contact information, general inquiries
- "escalate": Complex issues, complaints, payment problems, device repairs not in knowledge base, abusive messages, or unclear queries

Output ONLY the category name, nothing else.

Query: {query}

Category:""",
            input_variables=["query"]
        )
        
        prompt_text = classification_prompt.format(query=query)
        result = self.llm.invoke(prompt_text)
        category = result.content.strip().lower()
        
        # Validate category
        valid_categories = ["products", "returns", "general", "escalate"]
        if category not in valid_categories:
            # Default to escalate if unclear
            category = "escalate"
        
        logger.info(f"Classified query as: {category}")
        state["category"] = category
        return state
    
    def rag_responder(self, state: Dict) -> Dict:
        """
        Node 2: RAG Responder
        Use the RAG chain to generate a response based on retrieved context.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with response
        """
        query = state.get("query", "")
        history = state.get("history", "")
        
        logger.info("Generating response using RAG...")
        response = answer_with_rag(query, history)
        
        state["response"] = response
        return state
    
    def escalation_handler(self, state: Dict) -> Dict:
        """
        Node 3: Escalation
        Return a standardized escalation message for queries that need human support.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with escalation message
        """
        logger.info("Escalating to human support...")
        
        escalation_message = (
            "I'm not able to handle this request. "
            "Please contact support@techgear.com or call customer support for further assistance."
        )
        
        state["response"] = escalation_message
        return state
    
    def route_query(self, state: Dict) -> Literal["rag_responder", "escalation_handler"]:
        """
        Conditional routing based on classification.
        
        Args:
            state: Current workflow state
            
        Returns:
            Next node name
        """
        category = state.get("category", "escalate")
        
        if category == "escalate":
            return "escalation_handler"
        else:
            return "rag_responder"
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow with nodes and edges.
        
        Returns:
            Compiled workflow graph
        """
        # Create the graph with state schema
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("classifier", self.classify_query)
        workflow.add_node("rag_responder", self.rag_responder)
        workflow.add_node("escalation_handler", self.escalation_handler)
        
        # Set entry point
        workflow.set_entry_point("classifier")
        
        # Add conditional routing from classifier
        workflow.add_conditional_edges(
            "classifier",
            self.route_query,
            {
                "rag_responder": "rag_responder",
                "escalation_handler": "escalation_handler"
            }
        )
        
        # Both response nodes lead to END
        workflow.add_edge("rag_responder", END)
        workflow.add_edge("escalation_handler", END)
        
        # Compile the graph
        return workflow.compile()
    
    def run(self, query: str, history: Optional[List[Dict]] = None) -> Dict:
        """
        Run the workflow for a given query with optional conversation history.
        
        Args:
            query: User's question
            history: Optional list of previous messages [{"sender": "user"|"bot", "text": "..."}]
            
        Returns:
            Dict with response and category
        """
        # Format history into a string
        history_str = ""
        if history:
            history_lines = []
            for msg in history[-4:]:  # Only use last 4 messages
                sender = "User" if msg.get("sender") == "user" else "Bot"
                text = msg.get("text", "")
                history_lines.append(f"{sender}: {text}")
            history_str = "\n".join(history_lines)
            logger.info(f"Using conversation history with {len(history[-4:])} messages")
        
        # Initialize state
        initial_state = {
            "query": query,
            "history": history_str,
            "category": "",
            "response": ""
        }
        
        # Execute workflow
        final_state = self.graph.invoke(initial_state)
        
        return {
            "response": final_state.get("response", ""),
            "category": final_state.get("category", "")
        }


# Global workflow instance
_workflow = None


def get_workflow() -> ChatbotWorkflow:
    """
    Get or create the global workflow instance.
    
    Returns:
        ChatbotWorkflow instance
    """
    global _workflow
    if _workflow is None:
        logger.info("Initializing LangGraph workflow...")
        _workflow = ChatbotWorkflow()
        logger.info("Workflow initialized!")
    return _workflow


def run_chatbot_flow(query: str, history: Optional[List[Dict]] = None) -> Dict:
    """
    Convenience function to run the chatbot workflow.
    
    Args:
        query: User's question
        history: Optional conversation history
        
    Returns:
        Dict with response and category
    """
    workflow = get_workflow()
    return workflow.run(query, history)
