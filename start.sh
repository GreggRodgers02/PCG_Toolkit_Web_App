#!/bin/bash

# Function to handle script exit
cleanup() {
    echo "Stopping servers..."
    kill 0
}

# Trap SIGINT and SIGTERM to run cleanup
trap cleanup EXIT

echo "🚀 Starting PCG Toolkit..."

# Start Backend (from root)
echo "🔌 Starting Backend (Port 8000)..."
uvicorn main:app --reload --port 8000 &

# Start Frontend (from frontend dir)
echo "💻 Starting Frontend (Port 5173)..."
cd frontend
npm run dev &

# Wait for all background processes
wait
