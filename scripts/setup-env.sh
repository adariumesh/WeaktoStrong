#!/bin/bash

# Environment setup script for Weak-to-Strong platform
set -e

echo "🔧 Setting up environment for Weak-to-Strong platform..."

# Copy environment files if they don't exist
if [ ! -f .env ]; then
    echo "📋 Creating .env from template..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your actual values."
else
    echo "ℹ️  .env file already exists, skipping..."
fi

if [ ! -f backend/.env ]; then
    echo "📋 Creating backend/.env from template..."
    cp .env.example backend/.env
    echo "✅ backend/.env file created. Please edit it with your actual values."
else
    echo "ℹ️  backend/.env file already exists, skipping..."
fi

# Start external services
echo "🐳 Starting Docker services..."
docker-compose up -d postgres redis

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
timeout 60 bash -c 'until docker-compose ps | grep -q "healthy\|Up"; do sleep 2; done' || {
    echo "❌ Services failed to start properly"
    docker-compose logs
    exit 1
}

echo "✅ PostgreSQL and Redis are ready"

# Install Python dependencies if virtual environment exists
if [ -d "backend/venv" ]; then
    echo "🐍 Installing Python dependencies..."
    source backend/venv/bin/activate
    pip install -r backend/requirements.txt
    echo "✅ Python dependencies installed"
else
    echo "ℹ️  No virtual environment found. Creating one..."
    python3 -m venv backend/venv
    source backend/venv/bin/activate
    pip install -r backend/requirements.txt
    echo "✅ Virtual environment created and dependencies installed"
fi

# Test database connection
echo "🔍 Testing database connection..."
if python3 -c "
import psycopg2
try:
    conn = psycopg2.connect('postgresql://postgres:postgres@localhost:5432/weaktostrong')
    print('✅ Database connection successful')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"; then
    echo "✅ Database test passed"
else
    echo "❌ Database test failed"
    exit 1
fi

# Test Redis connection
echo "🔍 Testing Redis connection..."
if python3 -c "
import redis
try:
    r = redis.Redis(host='localhost', port=6379, password='redis_password', decode_responses=True)
    r.ping()
    print('✅ Redis connection successful')
except Exception as e:
    print(f'❌ Redis connection failed: {e}')
    exit(1)
"; then
    echo "✅ Redis test passed"
else
    echo "❌ Redis test failed"
    exit 1
fi

echo "🎉 Environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and backend/.env with your actual API keys"
echo "2. Run: npm run install:backend (to install Python dependencies)"
echo "3. Run: npm run dev:backend (to start the FastAPI server)"
echo "4. Run: npm run dev:web (to start the Next.js frontend)"
echo "5. Run: ./scripts/setup-ollama.sh (to set up local AI model)"