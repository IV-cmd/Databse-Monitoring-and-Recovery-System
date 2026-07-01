#!/bin/bash

# Database Monitoring System Startup Script
# Simple, clean, purposeful - first principles

set -e

echo "🚀 Starting Database Monitoring System..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start with Docker Compose
if [ -f "docker-compose.yml" ]; then
    echo "🐳 Starting services with Docker Compose..."
    docker-compose up -d
else
    echo "❌ docker-compose.yml not found."
    exit 1
fi

echo "✅ System started successfully!"
