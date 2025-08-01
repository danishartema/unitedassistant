#!/usr/bin/env python3
"""
Hugging Face Spaces Configuration
This file contains configuration specific to Hugging Face Spaces deployment
"""

import os
from pathlib import Path

# Hugging Face Spaces specific configuration
HF_SPACES_CONFIG = {
    "app_file": "app.py",
    "requirements_file": "requirements.txt",
    "dockerfile": "Dockerfile",
    "port": 7860,
    "host": "0.0.0.0",
    "environment": "production"
}

# Required environment variables for Hugging Face Spaces
REQUIRED_ENV_VARS = [
    "SUPABASE_DB_URL",
    "ENVIRONMENT", 
    "OPENAI_API_KEY",
    "SECRET_KEY"
]

# Optional environment variables
OPTIONAL_ENV_VARS = [
    "DEBUG",
    "HOST",
    "PORT",
    "HF_API_TOKEN"
]

def validate_hf_spaces_config():
    """Validate Hugging Face Spaces configuration."""
    print("🔧 Validating Hugging Face Spaces Configuration")
    print("=" * 50)
    
    # Check required files
    required_files = [
        "app.py",
        "requirements.txt", 
        "Dockerfile",
        "main.py",
        "config.py",
        "database.py",
        "README.md"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
    
    # Check README.md has proper frontmatter
    readme_path = Path("README.md")
    if readme_path.exists():
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if content.startswith('---'):
                print("✅ README.md has proper YAML frontmatter")
            else:
                print("❌ README.md missing YAML frontmatter")
                return False
    
    # Check environment variables
    print("\n📋 Environment Variables Check:")
    missing_vars = []
    for var in REQUIRED_ENV_VARS:
        if os.getenv(var):
            print(f"  ✅ {var}: SET")
        else:
            print(f"  ❌ {var}: NOT SET")
            missing_vars.append(var)
    
    # Check optional variables
    print("\n📋 Optional Environment Variables:")
    for var in OPTIONAL_ENV_VARS:
        if os.getenv(var):
            print(f"  ✅ {var}: SET")
        else:
            print(f"  ⚪ {var}: NOT SET (optional)")
    
    if missing_vars:
        print(f"\n❌ Missing required environment variables: {missing_vars}")
        return False
    
    return True

def get_hf_spaces_deployment_guide():
    """Get deployment guide for Hugging Face Spaces."""
    return """
🚀 Hugging Face Spaces Deployment Guide

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Choose:
   - Owner: Your username
   - Space name: unified-assistant
   - Space SDK: Docker
   - License: MIT
   - Visibility: Public or Private

4. Upload your code or connect GitHub repository

5. Set Environment Variables in Space Settings → Repository secrets:
   SUPABASE_DB_URL=postgresql+asyncpg://postgres:WiHcl5UgLmP1rLGZ@nqdhdqdtpvqfecbsjaar.supabase.co:5432/postgres
   ENVIRONMENT=production
   OPENAI_API_KEY=your_openai_api_key_here
   SECRET_KEY=Qee7sf39ipUhe_1pKCnsMLPU-aanOt-xs0gx3bsBuFo
   DEBUG=false
   HOST=0.0.0.0
   PORT=7860

6. Deploy and monitor logs

7. Test your deployment:
   - Health check: https://YOUR_SPACE_NAME.hf.space/health
   - API docs: https://YOUR_SPACE_NAME.hf.space/docs
   - Root: https://YOUR_SPACE_NAME.hf.space/
"""

def create_hf_spaces_secrets_template():
    """Create a template for Hugging Face Spaces secrets."""
    template = """# Hugging Face Spaces Secrets Template
# Copy these values to your Hugging Face Space secrets
# Go to: Your Space -> Settings -> Repository secrets

SUPABASE_DB_URL=postgresql+asyncpg://postgres:WiHcl5UgLmP1rLGZ@nqdhdqdtpvqfecbsjaar.supabase.co:5432/postgres
ENVIRONMENT=production
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=Qee7sf39ipUhe_1pKCnsMLPU-aanOt-xs0gx3bsBuFo
DEBUG=false
HOST=0.0.0.0
PORT=7860
"""
    
    with open('huggingface_secrets_template.txt', 'w') as f:
        f.write(template)
    
    print("✅ Created huggingface_secrets_template.txt")

if __name__ == "__main__":
    print("Hugging Face Spaces Configuration Check")
    print("=" * 50)
    
    # Create secrets template
    create_hf_spaces_secrets_template()
    
    is_valid = validate_hf_spaces_config()
    
    if is_valid:
        print("\n✅ Configuration is valid for Hugging Face Spaces deployment!")
        print(get_hf_spaces_deployment_guide())
    else:
        print("\n❌ Configuration needs to be fixed before deployment.")
        print("\n🔧 Quick fixes:")
        print("1. Ensure all required files are present")
        print("2. Set required environment variables")
        print("3. Check README.md has proper YAML frontmatter") 