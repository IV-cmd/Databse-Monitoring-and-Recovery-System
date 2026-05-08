#!/bin/bash

# Frontend Development Script
# Simple, clean, purposeful - first principles

set -e

echo "🌐 Starting Frontend Development Server..."

# Navigate to frontend directory
cd "$(dirname "$0")/../src/frontend"

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    echo "❌ Frontend directory not found. package.json not found."
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start development server
echo "🚀 Starting Angular development server..."
npm start
