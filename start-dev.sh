#!/bin/bash

# AI Assessment Platform - Development Startup Script
# This script starts both the backend and frontend services

echo "🚀 Starting AI Assessment Platform..."
echo ""

# Check if backend .env exists
if [ ! -f "aibackend/.env" ]; then
    echo "❌ Backend .env file not found!"
    echo "Please create aibackend/.env from aibackend/.env.example and add your API keys"
    exit 1
fi

# Check if Python virtual environment exists
if [ ! -d "aibackend/venv" ]; then
    echo "📦 Creating Python virtual environment..."
    cd aibackend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

# Check if frontend node_modules exists
if [ ! -d "aifrontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd aifrontend
    npm install
    cd ..
fi

echo ""
echo "✅ All dependencies ready!"
echo ""
echo "Starting services..."
echo "  - Backend: http://localhost:8000"
echo "  - Frontend: http://localhost:5173"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup INT TERM

# Start backend
cd aibackend
source venv/bin/activate
python3 main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
cd aifrontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
