#!/bin/bash

# NQL Movie Chatbot Production Startup Script

echo "🚀 Starting NQL Movie Chatbot in Production Mode..."

# Check if production config exists
if [ ! -f "production/config/production.env" ]; then
    echo "❌ Production config not found!"
    echo "   Please copy production/config/production.env to .env and configure it"
    exit 1
fi

# Copy production config to .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📋 Copying production configuration..."
    cp production/config/production.env .env
    echo "⚠️  Please edit .env file with your production settings before continuing"
    exit 1
fi

# Check if database connection works
echo "🔍 Testing database connection..."
uv run python production/scripts/analyze_database.py

if [ $? -ne 0 ]; then
    echo "❌ Database connection failed. Please check your configuration."
    exit 1
fi

echo "✅ Database connection successful!"

# Start production server
echo "🌐 Starting production server..."
echo "   API will be available at: http://localhost:8000"
echo "   API docs will be available at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"

uv run python production/scripts/start_production.py
