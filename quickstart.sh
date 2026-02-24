#!/bin/bash
# Quick Start Guide for Complete Pipeline

echo "=== Kids Content Engine - Complete Pipeline Setup ==="
echo ""

# 1. Check if server is running
echo "1️⃣  Checking if server is running..."
if curl -s http://127.0.0.1:8000/ > /dev/null; then
    echo "✅ Server is running on http://127.0.0.1:8000"
else
    echo "❌ Server not running. Starting..."
    cd /workspaces/kids-content-engine
    uvicorn app.main:app --reload &
    sleep 3
    echo "✅ Server started"
fi

echo ""

# 2. Build index
echo "2️⃣  Building FAISS index..."
RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/rag/build-index)
echo "   $RESPONSE"

echo ""

# 3. Show example request
echo "3️⃣  Example: Generate complete content"
echo ""
echo "cURL:"
echo "curl -X POST http://127.0.0.1:8000/rag/generate-complete \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"query\": \"Tell me a story about animals\", \"k\": 3}'"

echo ""
echo "Python:"
echo "import requests"
echo "response = requests.post('http://127.0.0.1:8000/rag/generate-complete',"
echo "    json={'query': 'Tell me a story about animals', 'k': 3})"
echo "result = response.json()"
echo "print(result['outputs']['video'])  # Path to generated video"

echo ""
echo "✅ Setup complete! Start generating content 🎬"
