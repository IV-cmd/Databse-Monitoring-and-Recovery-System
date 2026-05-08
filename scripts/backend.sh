#!/bin/bash

# Backend Development Script
# Python FastAPI backend

set -e

echo "🔧 Starting Backend Development Server..."

# Navigate to backend directory
cd "$(dirname "$0")/../src/backend"

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Backend directory not found. requirements.txt not found."
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed (simplified check)
if [ ! -f "venv/.deps_installed" ] || [ requirements.txt -nt "venv/.deps_installed" ]; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
    touch venv/.deps_installed
fi

# Check for environment file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env 2>/dev/null || echo "DATABASE_URL=postgresql://localhost:5432/db_monitor\nPORT=8000" > .env
fi

# Start development server
echo "🚀 Starting FastAPI development server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
