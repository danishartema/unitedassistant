#!/usr/bin/env python3
"""
Hugging Face Spaces Entry Point
This is the main entry point for Hugging Face Spaces deployment
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import the FastAPI app from main.py
from main import app

# For Hugging Face Spaces, we need to expose the app directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860) 