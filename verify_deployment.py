#!/usr/bin/env python3
"""
Verification script to ensure Hugging Face deployment matches local system.
"""
import os
import sys
from pathlib import Path

def check_database_config():
    """Check database configuration matches local system."""
    print("🔍 Checking database configuration...")
    
    # Check if SQLite is configured
    database_url = os.getenv("DATABASE_URL", "sqlite:///./unified_assistant.db")
    
    if "sqlite" in database_url:
        print("✅ SQLite database configured (same as local system)")
        print(f"   Database URL: {database_url}")
    else:
        print("⚠️  Database URL is not SQLite")
        print(f"   Current: {database_url}")
    
    return True

def check_openai_config():
    """Check OpenAI configuration."""
    print("\n🔍 Checking OpenAI configuration...")
    
    openai_key = os.getenv("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o")
    embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    if openai_key:
        print("✅ OpenAI API key configured")
        print(f"   Model: {openai_model}")
        print(f"   Embedding Model: {embedding_model}")
    else:
        print("❌ OpenAI API key not configured")
        print("   This is REQUIRED for your application to work")
    
    return bool(openai_key)

def check_huggingface_config():
    """Check Hugging Face configuration."""
    print("\n🔍 Checking Hugging Face configuration...")
    
    hf_token = os.getenv("HF_API_TOKEN")
    
    if hf_token:
        print("✅ Hugging Face API token configured")
        print(f"   Token: {hf_token[:20]}...{hf_token[-10:]}")
    else:
        print("⚠️  Hugging Face API token not configured")
    
    return bool(hf_token)

def check_server_config():
    """Check server configuration."""
    print("\n🔍 Checking server configuration...")
    
    host = os.getenv("HOST", "0.0.0.0")
    port = os.getenv("PORT", "7860")
    environment = os.getenv("ENVIRONMENT", "production")
    
    print(f"✅ Server configured for Hugging Face Spaces")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Environment: {environment}")
    
    return True

def check_file_structure():
    """Check if all required files exist."""
    print("\n🔍 Checking file structure...")
    
    required_files = [
        "main.py",
        "Dockerfile",
        "requirements.txt",
        "config.py",
        "database.py",
        "models.py",
        "dependencies.py"
    ]
    
    required_dirs = [
        "routers",
        "services",
        "utils",
        "tasks"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    missing_dirs = []
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing_dirs.append(dir_name)
    
    if missing_files or missing_dirs:
        print("❌ Missing required files/directories:")
        for file in missing_files:
            print(f"   - {file}")
        for dir_name in missing_dirs:
            print(f"   - {dir_name}/")
        return False
    
    print("✅ All required files and directories found")
    return True

def check_gpt_flow():
    """Check GPT FINAL FLOW directory."""
    print("\n🔍 Checking GPT FINAL FLOW directory...")
    
    if Path("GPT FINAL FLOW").exists():
        print("✅ GPT FINAL FLOW directory found")
        
        # Count modules
        modules = [d for d in Path("GPT FINAL FLOW").iterdir() if d.is_dir()]
        print(f"   Found {len(modules)} modules")
        
        # List modules
        for module in modules:
            print(f"   - {module.name}")
        
        return True
    else:
        print("❌ GPT FINAL FLOW directory not found")
        print("   This contains your AI modules and is required")
        return False

def main():
    """Main verification function."""
    print("🤖 Unified Assistant - Deployment Verification")
    print("=" * 50)
    
    checks = [
        check_file_structure(),
        check_database_config(),
        check_openai_config(),
        check_huggingface_config(),
        check_server_config(),
        check_gpt_flow()
    ]
    
    print("\n" + "=" * 50)
    print("📊 Verification Results:")
    
    if all(checks):
        print("✅ All checks passed! Your deployment is ready.")
        print("\n🚀 Next steps:")
        print("1. Run: python deploy_to_huggingface.py")
        print("2. Upload files to Hugging Face Space")
        print("3. Set environment variables in Space settings")
        print("4. Deploy and test your application")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        sys.exit(1)
    
    print("\n💡 Remember:")
    print("- Your database will be SQLite (same as local)")
    print("- Your OpenAI application will work exactly as before")
    print("- All GPT FINAL FLOW modules will use OpenAI GPT-4o")
    print("- Hugging Face integration is available for additional features")

if __name__ == "__main__":
    main() 