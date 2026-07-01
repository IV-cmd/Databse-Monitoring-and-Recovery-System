#!/bin/bash

# Database Monitoring System Stop Script
# Simple, clean, purposeful - first principles

set -e

echo "🛑 Stopping Database Monitoring System..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running."
    exit 1
fi

# Stop services
if [ -f "docker-compose.yml" ]; then
    echo "🐳 Stopping services..."
    docker-compose down
else
    echo "❌ docker-compose.yml not found."
    exit 1
fi

echo "✅ System stopped successfully!"
