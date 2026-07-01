#!/bin/bash

# Database Monitoring System Restart Script
# This script restarts the complete monitoring system

set -e

echo "🔄 Restarting Database Monitoring System..."

# Stop services
echo "🛑 Stopping services..."
./scripts/stop.sh

# Wait a moment
sleep 5

# Start services
echo "🚀 Starting services..."
./scripts/start.sh

echo "✅ Database Monitoring System restarted successfully!"
