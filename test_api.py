import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GOOGLE_API_KEY")
print(f"Testing API key: {api_key[:20]}...")

# Configure the API
genai.configure(api_key=api_key)

# Test 1: List available models
print("\n✅ Test 1: Listing available models...")
try:
    models = list(genai.list_models())
    print(f"Found {len(models)} models")
    print("✅ API key is valid for listing models!")
except Exception as e:
    print(f"❌ Error listing models: {e}")

# Test 2: Generate simple content
print("\n✅ Test 2: Generating content with Gemini...")
try:
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content("Say 'Hello, the API key works!'")
    print(f"Response: {response.text}")
    print("✅ API key works for content generation!")
except Exception as e:
    print(f"❌ Error generating content: {e}")

# Test 3: Create embeddings
print("\n✅ Test 3: Creating embeddings...")
try:
    result = genai.embed_content(
        model="models/embedding-001",
        content="This is a test sentence",
        task_type="retrieval_document"
    )
    print(f"Embedding dimension: {len(result['embedding'])}")
    print("✅ API key works for embeddings!")
except Exception as e:
    print(f"❌ Error creating embeddings: {e}")

print("\n🎉 API key validation complete!")
