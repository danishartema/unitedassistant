#!/usr/bin/env python3
"""
Simple script to start the backend server.
"""

import subprocess
import sys

def start_backend():
    """Start the backend server."""
    try:
        print("🚀 Starting backend server...")
        print("📝 This will start the FastAPI server on http://localhost:7860")
        print("📝 Keep this terminal window open while using the application")
        print("📝 To stop the server, press Ctrl+C\n")
        
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", "main:app", 
            "--host", "0.0.0.0", 
            "--port", "7860",
            "--reload"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    start_backend() 