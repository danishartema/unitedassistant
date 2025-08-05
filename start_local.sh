#!/bin/bash

echo "🚀 Unified Assistant - Local Development"
echo "================================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    echo "   Please install Python 3.11+ from https://python.org"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found"
    echo "   Please run this script from the project directory"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found"
    echo "   Creating template..."
    python3 start_local.py
    exit 0
fi

# Start the application
echo "🚀 Starting Unified Assistant..."
echo "   The application will be available at: http://localhost:7860"
echo "   Press Ctrl+C to stop the server"
echo

python3 main.py

echo
echo "👋 Server stopped" 