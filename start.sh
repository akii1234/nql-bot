#!/bin/bash

# NQL Movie Chatbot Startup Script

echo "🎬 Starting NQL Movie Chatbot..."

# Check if .env file exists, if not create one with defaults
# Note: API keys will be entered in the app UI, not in .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env.example .env
    echo "✅ Created .env file with default settings"
    echo "📝 Note: You'll enter your API key in the app UI at http://localhost:8501"
fi

# Check if database exists, if not populate it
if [ ! -f "data/movies.db" ]; then
    echo "📊 Database not found. Creating and populating with sample data..."
    uv run python scripts/populate_sample_data.py
fi

echo "🚀 Starting FastAPI backend..."
echo "   API will be available at: http://localhost:8000"
echo "   API docs will be available at: http://localhost:8000/docs"
echo ""
echo "🌐 Starting Streamlit frontend..."
echo "   Web interface will be available at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop both services"

# Start both services in parallel
uv run python main.py &
BACKEND_PID=$!

sleep 3  # Give backend time to start

uv run streamlit run frontend/app.py &
FRONTEND_PID=$!

# Wait for user to stop
wait

# Cleanup on exit
echo "🛑 Stopping services..."
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
echo "✅ Services stopped"
