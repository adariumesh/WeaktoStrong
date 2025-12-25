#!/bin/bash

# Complete setup script for Weak-to-Strong platform
set -e

echo "🚀 Setting up Weak-to-Strong platform..."
echo "=================================="
echo ""

# Check prerequisites
echo "1. Checking prerequisites..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

echo "✅ Node.js $(node --version) and Python $(python3 --version) are available"
echo ""

# Install npm dependencies
echo "2. Installing npm dependencies..."
npm install
echo "✅ npm dependencies installed"
echo ""

# Setup environment files
echo "3. Setting up environment files..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ .env file created"
else
    echo "ℹ️  .env file already exists"
fi

if [ ! -f backend/.env ]; then
    cp .env.example backend/.env
    echo "✅ backend/.env file created"
else
    echo "ℹ️  backend/.env file already exists"
fi
echo ""

# Setup Python virtual environment
echo "4. Setting up Python environment..."
if [ ! -d "backend/venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv backend/venv
fi

echo "Activating virtual environment and installing dependencies..."
source backend/venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
echo "✅ Python environment ready"
echo ""

# Test backend configuration
echo "5. Testing backend configuration..."
cd backend && python test_connection.py && cd ..
echo "✅ Backend configuration test passed"
echo ""

# Check Docker (optional)
echo "6. Checking Docker availability..."
if command -v docker &> /dev/null && docker info &> /dev/null; then
    echo "✅ Docker is available"
    echo "ℹ️  You can run: docker-compose up -d postgres redis"
    echo "   This will start PostgreSQL and Redis for local development"
else
    echo "⚠️  Docker is not available"
    echo "   For full local development, you'll need:"
    echo "   - PostgreSQL database"
    echo "   - Redis instance"
    echo "   - Consider using cloud services instead"
fi
echo ""

# Check Ollama (optional)
echo "7. Checking Ollama availability..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is installed"
    echo "ℹ️  Run: ./scripts/setup-ollama.sh to download the AI model"
else
    echo "⚠️  Ollama is not installed (optional for local AI)"
    echo "   Install: https://ollama.ai/download"
    echo "   Or use cloud AI services only"
fi
echo ""

echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and backend/.env with your API keys and database URLs"
echo "2. Start development servers:"
echo "   - Frontend: npm run dev:web"
echo "   - Backend: source backend/venv/bin/activate && npm run dev:backend"
echo "   - Both: npm run dev:full (requires concurrently)"
echo ""
echo "For external services:"
echo "- Database: Set up Supabase or run: docker-compose up -d postgres"
echo "- Redis: Set up Upstash or run: docker-compose up -d redis"  
echo "- AI Models: Configure Claude API keys or run: ./scripts/setup-ollama.sh"