"""
Demo script to test the TechGear Support Chatbot with representative queries.

This script demonstrates the chatbot's capabilities across different categories:
- Products
- Returns
- General support
- Escalation

Run this script directly without starting the FastAPI server:
    python demo_queries.py
"""

import logging
from graph_workflow import run_chatbot_flow

# Configure logging for demo
logging.basicConfig(
    level=logging.WARNING,  # Suppress most logs for cleaner demo output
    format='%(message)s'
)

# Demo queries covering different categories
DEMO_QUERIES = [
    {
        "category": "Products",
        "query": "What is the price of SmartWatch Pro X?",
        "expected": "products"
    },
    {
        "category": "Products",
        "query": "Tell me about the laptop warranty",
        "expected": "products"
    },
    {
        "category": "Returns",
        "query": "What is your return policy?",
        "expected": "returns"
    },
    {
        "category": "Returns",
        "query": "How do I return a product?",
        "expected": "returns"
    },
    {
        "category": "General Support",
        "query": "When is customer support available?",
        "expected": "general"
    },
    {
        "category": "General Support",
        "query": "What are your support hours?",
        "expected": "general"
    },
    {
        "category": "Escalation",
        "query": "My laptop screen is broken, what should I do?",
        "expected": "escalate"
    },
    {
        "category": "Escalation",
        "query": "I want to file a complaint about my order",
        "expected": "escalate"
    },
    {
        "category": "Out of Scope (Escalation)",
        "query": "What's the weather like today?",
        "expected": "escalate"
    },
    {
        "category": "Follow-up with History",
        "query": "What is its price?",
        "expected": "products",
        "history": [
            {"sender": "user", "text": "Tell me about SmartWatch Pro X"},
            {"sender": "bot", "text": "The SmartWatch Pro X is a premium fitness tracker..."}
        ]
    }
]


def print_separator():
    """Print a visual separator."""
    print("\n" + "=" * 80 + "\n")


def run_demo():
    """Run the demo queries and display results."""
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║           TechGear Support Chatbot - Demo Queries Test                    ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    
    print("\nInitializing chatbot system...")
    print("(This may take a moment on first run to load documents and create embeddings)")
    print_separator()
    
    for i, demo in enumerate(DEMO_QUERIES, 1):
        print(f"Test {i}/{len(DEMO_QUERIES)}: {demo['category']}")
        print(f"Query: \"{demo['query']}\"")
        
        # Check if history is provided
        history = demo.get("history")
        if history:
            print(f"History: {len(history)} previous messages")
        
        print()
        
        try:
            # Run the chatbot flow
            result = run_chatbot_flow(demo["query"], history)
            
            response = result.get("response", "")
            category = result.get("category", "unknown")
            
            # Display results
            print(f"Category: {category}")
            print(f"Expected: {demo['expected']}")
            print(f"Match: {'✓' if category == demo['expected'] else '✗'}")
            print()
            print(f"Response:")
            print(f"  {response}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print_separator()
    
    print("Demo completed!")
    print("\nNote: You can run this script anytime to test the chatbot without the web interface.")


if __name__ == "__main__":
    run_demo()
