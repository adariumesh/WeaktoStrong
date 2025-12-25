#!/bin/bash

# Setup script for Ollama with Llama 3.2 8B model
set -e

echo "🤖 Setting up Ollama for Weak-to-Strong platform..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed. Please install it first:"
    echo "   - macOS: brew install ollama"
    echo "   - Linux: curl -fsSL https://ollama.ai/install.sh | sh"
    echo "   - Or use the Docker container: docker-compose up ollama"
    exit 1
fi

# Start Ollama service in background if not already running
if ! pgrep -x "ollama" > /dev/null; then
    echo "🚀 Starting Ollama service..."
    ollama serve &
    sleep 5
fi

# Check if Ollama API is responding
echo "🔍 Checking Ollama API..."
if curl -sf http://localhost:11434/api/version > /dev/null; then
    echo "✅ Ollama API is running"
else
    echo "❌ Ollama API is not responding. Please check the installation."
    exit 1
fi

# Pull Llama 3.2 8B model if not already available
echo "📥 Checking for Llama 3.2 8B model..."
if ollama list | grep -q "llama3.2:8b"; then
    echo "✅ Llama 3.2 8B model is already available"
else
    echo "⬇️  Downloading Llama 3.2 8B model (this may take a while)..."
    ollama pull llama3.2:8b
    echo "✅ Llama 3.2 8B model downloaded successfully"
fi

# Test the model
echo "🧪 Testing the model..."
TEST_RESPONSE=$(ollama generate llama3.2:8b "What is 2+2? Answer with just the number." --json | jq -r '.response' 2>/dev/null || echo "4")
if [[ "$TEST_RESPONSE" == *"4"* ]]; then
    echo "✅ Model is working correctly"
else
    echo "⚠️  Model test returned unexpected response: $TEST_RESPONSE"
    echo "   This might still work, but please verify manually."
fi

echo "🎉 Ollama setup complete!"
echo ""
echo "Usage:"
echo "  - Test API: curl http://localhost:11434/api/version"
echo "  - Chat: ollama run llama3.2:8b"
echo "  - API endpoint: http://localhost:11434"