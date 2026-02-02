# Quick Testing Guide

## Backend Testing

### 1. Test Demo Script (No Server Needed)
```bash
cd /home/labuser/edurekaproject
./venv/bin/python demo_queries.py
```

This will test:
- Products category
- Returns category  
- General support category
- Escalation scenarios
- Follow-up with history

### 2. Start Backend Server
```bash
cd /home/labuser/edurekaproject
./venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. Test API Endpoints

**Basic Query (backward compatible):**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the price of SmartWatch Pro X?"}'
```

**With Conversation History:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is its price?",
    "history": [
      {"sender": "user", "text": "Tell me about SmartWatch Pro X"},
      {"sender": "bot", "text": "SmartWatch Pro X is a premium device..."}
    ]
  }'
```

**Test Weak Context (Out of KB):**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather today?"}'
```
Expected: Fallback message about contacting support

**Test Escalation:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "My laptop screen is broken"}'
```
Expected: Category "escalate" with standard escalation message

## Frontend Testing

### 1. Start Frontend Dev Server
```bash
cd /home/labuser/edurekaproject/frontend
npm run dev
```

### 2. Access Application
Open browser to: http://localhost:5173

### 3. Test Scenarios

**Test 1: Basic Product Query**
- Type: "What is the price of SmartWatch Pro X?"
- ✓ Should see category: "products"
- ✓ Should see timestamp
- ✓ Should get accurate price information

**Test 2: Follow-up Question (Context)**
- First ask: "Tell me about SmartWatch Pro X"
- Then ask: "What is its warranty?"
- ✓ Bot should understand "its" refers to SmartWatch Pro X
- ✓ Category should be "products"

**Test 3: Return Policy**
- Type: "What is your return policy?"
- ✓ Should see category: "returns"
- ✓ Should get return policy information

**Test 4: General Support**
- Type: "When is customer support available?"
- ✓ Should see category: "general"
- ✓ Should get support hours

**Test 5: Escalation**
- Type: "My device is broken and needs repair"
- ✓ Should see category: "escalate"
- ✓ Should get escalation message with contact info

**Test 6: Out of Scope (Weak Context)**
- Type: "What is the capital of France?"
- ✓ Should see fallback message
- ✓ "I don't have specific information..."

**Test 7: Clear Chat**
- Have a conversation with several messages
- Click "Clear Chat" button in header
- ✓ Should reset to welcome message
- ✓ Message count should reset

**Test 8: Timestamps**
- Send any message
- ✓ Each message should show HH:MM timestamp
- ✓ Times should be current local time

## Check Logs

Backend logs will show:
```
INFO - Received query: '...'
INFO - Classified query as: products
INFO - Found reliable context with score: 0.85
INFO - Generated response | Category: products | Response length: 123 chars
```

## Expected Responses

### Products
- Category: "products"
- Detailed product information from knowledge base

### Returns  
- Category: "returns"
- Return policy details

### General
- Category: "general"
- Support hours, contact info

### Escalate
- Category: "escalate"
- Message: "I'm not able to handle this request. Please contact support@techgear.com..."

### Weak Context
- Category: may vary
- Message: "I don't have specific information about that in TechGear's knowledge base..."

## Troubleshooting

**Backend won't start:**
```bash
# Ensure virtual environment is active
source /home/labuser/edurekaproject/venv/bin/activate

# Reinstall dependencies if needed
pip install -r requirements.txt
```

**Frontend won't start:**
```bash
cd frontend
npm install  # Install dependencies
npm run dev
```

**CORS errors:**
- Check that backend is running on port 8000
- Frontend should be on port 5173
- CORS is configured for localhost:5173 and 127.0.0.1:5173

**Import errors:**
```bash
# Make sure all packages are installed in venv
./venv/bin/pip list | grep langchain
./venv/bin/pip list | grep chroma
```
