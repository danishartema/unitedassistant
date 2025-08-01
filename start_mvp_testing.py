#!/usr/bin/env python3
"""
MVP Testing Startup Script for Unified Assistant
This script helps you start both the FastAPI backend and Streamlit frontend for testing.
"""

import subprocess
import sys
import time
import requests
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected")
    return True

def install_requirements():
    """Install required packages."""
    print("📦 Installing requirements...")
    
    # Install backend requirements
    if os.path.exists("requirements.txt"):
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         check=True, capture_output=True)
            print("✅ Backend requirements installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install backend requirements: {e}")
            return False
    
    # Install Streamlit requirements
    if os.path.exists("streamlit_requirements.txt"):
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "streamlit_requirements.txt"], 
                         check=True, capture_output=True)
            print("✅ Streamlit requirements installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Streamlit requirements: {e}")
            return False
    
    return True

def check_backend_health():
    """Check if the backend is running and healthy."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        pass
    return False

def start_backend():
    """Start the FastAPI backend server."""
    print("🚀 Starting FastAPI backend...")
    
    # Check if backend is already running
    if check_backend_health():
        print("✅ Backend is already running!")
        return True
    
    try:
        # Start the backend server
        backend_process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for backend to start
        print("⏳ Waiting for backend to start...")
        for i in range(30):  # Wait up to 30 seconds
            if check_backend_health():
                print("✅ Backend started successfully!")
                return True
            time.sleep(1)
        
        print("❌ Backend failed to start within 30 seconds")
        return False
        
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def start_streamlit():
    """Start the Streamlit frontend."""
    print("🎨 Starting Streamlit frontend...")
    
    try:
        # Start Streamlit
        streamlit_process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port", "8501"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("✅ Streamlit started successfully!")
        print("🌐 Frontend URL: http://localhost:8501")
        print("🔧 Backend URL: http://localhost:8000")
        print("📚 API Documentation: http://localhost:8000/docs")
        
        return streamlit_process
        
    except Exception as e:
        print(f"❌ Failed to start Streamlit: {e}")
        return None

def main():
    """Main function to start MVP testing environment."""
    print("🤖 Unified Assistant - MVP Testing Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements. Please check the error messages above.")
        return
    
    # Start backend
    if not start_backend():
        print("❌ Failed to start backend. Please check the error messages above.")
        return
    
    # Start Streamlit
    streamlit_process = start_streamlit()
    if not streamlit_process:
        print("❌ Failed to start Streamlit. Please check the error messages above.")
        return
    
    print("\n🎉 MVP Testing Environment is ready!")
    print("\n📋 Next Steps:")
    print("1. Open http://localhost:8501 in your browser")
    print("2. Register a new account or login")
    print("3. Create a project")
    print("4. Test the chatbot functionality")
    print("5. Use the API testing features")
    
    print("\n🛑 To stop the servers, press Ctrl+C")
    
    try:
        # Keep the script running
        streamlit_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        streamlit_process.terminate()
        print("✅ Servers stopped")

if __name__ == "__main__":
    main() 