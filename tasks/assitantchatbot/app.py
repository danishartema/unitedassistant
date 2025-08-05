#!/usr/bin/env python3
"""
Hugging Face Spaces Entry Point
This is the main entry point for Hugging Face Spaces deployment
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    # Import the FastAPI app from main.py
    from main import app
    logger.info("✅ Successfully imported FastAPI app from main.py")
except Exception as e:
    logger.error(f"❌ Failed to import FastAPI app: {e}")
    raise

# For Hugging Face Spaces, we need to expose the app directly
if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Unified Assistant on Hugging Face Spaces")
    uvicorn.run(app, host="0.0.0.0", port=7860) 