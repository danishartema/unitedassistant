#!/usr/bin/env python3
"""
Local Development Startup Script
Quick and easy way to start the Unified Assistant locally
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def print_banner():
    """Print startup banner."""
    print("🚀 Unified Assistant - Local Development")
    print("=" * 50)
    print()

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 11):
        print("❌ Error: Python 3.11 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_requirements():
    """Check if requirements.txt exists."""
    if not Path("requirements.txt").exists():
        print("❌ Error: requirements.txt not found")
        print("   Make sure you're in the correct directory")
        return False
    print("✅ requirements.txt found")
    return True

def check_env_file():
    """Check if .env file exists and has required variables."""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("   You'll need to create one with your configuration")
        return False
    
    # Check for required variables
    required_vars = ["SUPABASE_DB_URL", "OPENAI_API_KEY", "SECRET_KEY"]
    missing_vars = []
    
    with open(env_file, 'r') as f:
        content = f.read()
        for var in required_vars:
            if f"{var}=" not in content:
                missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ .env file configured")
    return True

def install_dependencies():
    """Install Python dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def test_database_connection():
    """Test database connection."""
    print("🔍 Testing database connection...")
    try:
        result = subprocess.run([sys.executable, "setup_database.py"], 
                              check=True, capture_output=True, text=True)
        if "✅" in result.stdout or "success" in result.stdout.lower():
            print("✅ Database connection successful")
            return True
        else:
            print("⚠️  Database connection may have issues")
            return False
    except subprocess.CalledProcessError:
        print("❌ Database connection failed")
        return False

def start_server():
    """Start the FastAPI server."""
    print("🚀 Starting server...")
    print("   The application will be available at: http://localhost:7860")
    print("   Press Ctrl+C to stop the server")
    print()
    
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")

def create_env_template():
    """Create a template .env file."""
    env_template = """# Unified Assistant Environment Configuration
# Replace these values with your actual credentials

# Database Configuration (Supabase)
SUPABASE_DB_URL=postgresql+asyncpg://postgres:your_password@your_host:5432/postgres

# OpenAI Configuration
OPENAI_API_KEY=sk-your_openai_api_key_here

# Security
SECRET_KEY=your-secret-key-change-in-production

# Application Settings
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=7860

# Optional: Redis (if you want to use Celery)
# REDIS_URL=redis://localhost:6379/0
"""
    
    with open(".env", 'w') as f:
        f.write(env_template)
    
    print("📝 Created .env template file")
    print("   Please edit .env with your actual credentials")

def main():
    """Main startup function."""
    print_banner()
    
    # Check prerequisites
    if not check_python_version():
        return
    
    if not check_requirements():
        return
    
    # Check environment configuration
    env_ok = check_env_file()
    if not env_ok:
        print("\n🔧 Environment Setup Required")
        print("You need to configure your environment variables.")
        print()
        
        choice = input("Would you like to create a .env template file? (y/N): ").strip()
        if choice.lower() == 'y':
            create_env_template()
            print("\n📋 Next steps:")
            print("1. Edit the .env file with your actual credentials")
            print("2. Run this script again")
            return
        else:
            print("\nPlease create a .env file manually and run this script again.")
            return
    
    # Install dependencies if needed
    print("\n📦 Checking dependencies...")
    try:
        import fastapi
        print("✅ Dependencies already installed")
    except ImportError:
        if not install_dependencies():
            return
    
    # Test database connection
    print("\n🔍 Running pre-flight checks...")
    db_ok = test_database_connection()
    
    if not db_ok:
        print("\n⚠️  Database connection issues detected")
        print("   The application may still work, but some features might be limited")
        
        choice = input("Continue anyway? (y/N): ").strip()
        if choice.lower() != 'y':
            return
    
    # Start the server
    print("\n" + "="*50)
    start_server()

if __name__ == "__main__":
    main() 