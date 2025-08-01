#!/usr/bin/env python3
"""
Environment Setup Script for Unified Assistant MVP Testing
This script helps set up the environment and check for any issues.
"""

import os
import sys
import subprocess
import requests
from pathlib import Path

def check_python_version():
    """Check Python version compatibility."""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} is compatible")
    return True

def check_dependencies():
    """Check if required packages are installed."""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "streamlit",
        "requests",
        "pandas",
        "openai"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt && pip install -r streamlit_requirements.txt")
        return False
    
    return True

def check_directories():
    """Check if required directories exist."""
    print("\n📁 Checking directories...")
    
    required_dirs = [
        "GPT FINAL FLOW",
        "routers",
        "services",
        "utils"
    ]
    
    missing_dirs = []
    
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ - Missing")
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"\n⚠️ Missing directories: {', '.join(missing_dirs)}")
        return False
    
    return True

def check_database():
    """Check database configuration."""
    print("\n🗄️ Checking database...")
    
    db_file = Path("unified_assistant.db")
    if db_file.exists():
        print(f"✅ Database file exists ({db_file.stat().st_size} bytes)")
    else:
        print("⚠️ Database file doesn't exist (will be created on first run)")
    
    return True

def check_openai_config():
    """Check OpenAI configuration."""
    print("\n🤖 Checking OpenAI configuration...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("✅ OpenAI API key is set")
        return True
    else:
        print("⚠️ OpenAI API key not set")
        print("   Set it with: set OPENAI_API_KEY=your_api_key_here")
        print("   Or create a .env file with: OPENAI_API_KEY=your_api_key_here")
        return False

def check_ports():
    """Check if required ports are available."""
    print("\n🔌 Checking ports...")
    
    ports_to_check = [8000, 8501]
    
    for port in ports_to_check:
        try:
            response = requests.get(f"http://localhost:{port}", timeout=1)
            print(f"⚠️ Port {port} is in use")
        except requests.exceptions.RequestException:
            print(f"✅ Port {port} is available")
    
    return True

def create_env_file():
    """Create a .env file with default settings."""
    print("\n📝 Creating .env file...")
    
    env_content = """# Unified Assistant Environment Configuration

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///./unified_assistant.db

# Security
SECRET_KEY=your-secret-key-change-in-production

# Application
ENVIRONMENT=development
DEBUG=true

# File Storage
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760

# Redis (optional for MVP testing)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Created .env file with default settings")
        print("   Please update OPENAI_API_KEY with your actual API key")
    else:
        print("✅ .env file already exists")
    
    return True

def run_quick_test():
    """Run a quick test to verify the setup."""
    print("\n🧪 Running quick test...")
    
    try:
        # Test importing main modules
        import main
        print("✅ Main module imports successfully")
        
        # Test database connection
        from database import async_engine
        print("✅ Database engine configured")
        
        # Test chatbot service
        from services.chatbot_service import ChatbotService
        service = ChatbotService()
        print(f"✅ Chatbot service initialized with {len(service.modules)} modules")
        
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🤖 Unified Assistant - Environment Setup")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Directories", check_directories),
        ("Database", check_database),
        ("OpenAI Config", check_openai_config),
        ("Ports", check_ports),
        ("Environment File", create_env_file),
        ("Quick Test", run_quick_test)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} check failed: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 Environment setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Set your OpenAI API key in the .env file")
        print("2. Run: python start_mvp_testing.py")
        print("3. Open http://localhost:8501 in your browser")
    else:
        print("⚠️ Some checks failed. Please fix the issues above before proceeding.")
        print("\n🔧 Common fixes:")
        print("- Install missing packages: pip install -r requirements.txt")
        print("- Set OpenAI API key: set OPENAI_API_KEY=your_key")
        print("- Check if ports 8000 and 8501 are available")
    
    return all_passed

if __name__ == "__main__":
    main() 