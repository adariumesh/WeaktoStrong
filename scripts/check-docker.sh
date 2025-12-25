#!/bin/bash

# Check if Docker is running
set -e

echo "🐳 Checking Docker status..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed."
    echo "   Please install Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running."
    echo "   Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running and available"

# Check if docker-compose is available
if command -v docker-compose &> /dev/null; then
    echo "✅ docker-compose is available"
elif docker compose version &> /dev/null; then
    echo "✅ docker compose (plugin) is available"
else
    echo "❌ Neither docker-compose nor docker compose plugin is available"
    exit 1
fi

echo "🎉 Docker setup is ready!"