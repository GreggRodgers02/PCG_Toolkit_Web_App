#!/bin/bash

echo "🚀 preparing for deployment..."

# Build Frontend
echo "📦 Building Frontend..."
cd frontend
npm install
npm run build
cd ..

# Check if build was successful
if [ ! -d "frontend/dist" ]; then
    echo "❌ Frontend build failed!"
    exit 1
fi

echo "✅ Frontend built successfully."

# Start Backend
echo "🔌 Starting Production Server (Port 8000)..."
uvicorn main:app --host 0.0.0.0 --port 8000
