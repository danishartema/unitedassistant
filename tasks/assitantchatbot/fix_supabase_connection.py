#!/usr/bin/env python3
"""
Fix Supabase Connection for Hugging Face Deployment
This script helps diagnose and fix the network connectivity issue
"""

import os
import asyncio
import asyncpg
from urllib.parse import urlparse
import requests

def print_banner():
    """Print diagnostic banner."""
    print("🔧 Supabase Connection Diagnostic for Hugging Face Deployment")
    print("=" * 60)
    print("This script will help you fix the network connectivity issue")
    print()

def get_current_connection_string():
    """Get the current connection string from environment."""
    return os.getenv("SUPABASE_DB_URL", "")

def parse_connection_string(conn_str):
    """Parse the connection string to extract components."""
    if not conn_str:
        return None
    
    try:
        # Remove the +asyncpg part for parsing
        clean_str = conn_str.replace("+asyncpg", "")
        parsed = urlparse(clean_str)
        
        return {
            "host": parsed.hostname,
            "port": parsed.port or 5432,
            "user": parsed.username,
            "password": parsed.password,
            "database": parsed.path[1:] if parsed.path else "postgres",
            "original": conn_str
        }
    except Exception as e:
        print(f"❌ Error parsing connection string: {e}")
        return None

def check_supabase_project_status(host):
    """Check if Supabase project is accessible."""
    print("🔍 Checking Supabase Project Status...")
    
    # Extract project reference from hostname
    if host and host.endswith('.supabase.co'):
        project_ref = host.replace('.supabase.co', '')
        print(f"   Project Reference: {project_ref}")
        
        # Try to access the project status
        try:
            # This is a basic check - in reality, you'd need to use Supabase API
            print("   ⚠️  Manual check required:")
            print(f"   1. Go to https://supabase.com/dashboard/project/{project_ref}")
            print("   2. Check if project is active (not paused)")
            print("   3. Verify the project is not suspended")
            return True
        except Exception as e:
            print(f"   ❌ Error checking project status: {e}")
            return False
    else:
        print("   ❌ Invalid Supabase hostname format")
        return False

async def test_database_connection(conn_info):
    """Test the database connection."""
    print("\n🔍 Testing Database Connection...")
    
    if not conn_info:
        print("   ❌ No connection information available")
        return False
    
    try:
        print(f"   Host: {conn_info['host']}")
        print(f"   Port: {conn_info['port']}")
        print(f"   User: {conn_info['user']}")
        print(f"   Database: {conn_info['database']}")
        print(f"   Password: {'*' * len(conn_info['password'])}")
        
        # Test connection
        conn = await asyncpg.connect(
            host=conn_info['host'],
            port=conn_info['port'],
            user=conn_info['user'],
            password=conn_info['password'],
            database=conn_info['database'],
            timeout=10
        )
        
        # Test a simple query
        result = await conn.fetchval("SELECT 1 as test")
        print(f"   ✅ Connection successful! Test result: {result}")
        
        await conn.close()
        return True
        
    except asyncpg.InvalidPasswordError:
        print("   ❌ Invalid password")
        return False
    except asyncpg.InvalidAuthorizationSpecificationError:
        print("   ❌ Invalid username or database")
        return False
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False

def check_network_connectivity(host, port):
    """Check basic network connectivity."""
    print(f"\n🌐 Testing Network Connectivity to {host}:{port}...")
    
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print("   ✅ Network connectivity successful")
            return True
        else:
            print(f"   ❌ Network connectivity failed (error code: {result})")
            return False
    except Exception as e:
        print(f"   ❌ Network test error: {e}")
        return False

def generate_fix_instructions(conn_info, network_ok, db_ok):
    """Generate specific fix instructions based on the diagnosis."""
    print("\n🔧 Fix Instructions")
    print("=" * 40)
    
    if not conn_info:
        print("❌ No connection string found")
        print("\n📋 Steps to fix:")
        print("1. Go to your Hugging Face Space → Settings → Repository secrets")
        print("2. Add SUPABASE_DB_URL with your connection string")
        print("3. Format: postgresql+asyncpg://postgres:[password]@[host]:5432/postgres")
        return
    
    if not network_ok:
        print("❌ Network connectivity issue detected")
        print("\n📋 Possible solutions:")
        print("1. Check if your Supabase project is paused or suspended")
        print("2. Verify the project is in an accessible region")
        print("3. Check for IP restrictions in your Supabase project")
        print("4. Try creating a new Supabase project in a different region")
        print("5. Contact Supabase support if the issue persists")
    
    elif not db_ok:
        print("❌ Database authentication issue")
        print("\n📋 Steps to fix:")
        print("1. Go to your Supabase dashboard → Settings → Database")
        print("2. Copy the correct connection string")
        print("3. Update your Hugging Face Space secrets")
        print("4. Verify the password is correct")
        print("5. Check if the database user has proper permissions")
    
    else:
        print("✅ Connection appears to be working locally")
        print("\n📋 For Hugging Face deployment:")
        print("1. Ensure your Space secrets are correctly set")
        print("2. Check if there are any Hugging Face-specific network restrictions")
        print("3. Try redeploying your Space")
        print("4. Monitor the Space logs for any new errors")

def create_new_connection_template():
    """Create a template for new connection string."""
    print("\n📝 New Connection String Template")
    print("=" * 40)
    
    template = """# Hugging Face Space Secrets Template
# Copy these to your Space -> Settings -> Repository secrets

SUPABASE_DB_URL=postgresql+asyncpg://postgres:[YOUR_PASSWORD]@[YOUR_HOST]:5432/postgres
ENVIRONMENT=production
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here
DEBUG=false
HOST=0.0.0.0
PORT=7860

# Instructions:
# 1. Replace [YOUR_PASSWORD] with your actual Supabase database password
# 2. Replace [YOUR_HOST] with your actual Supabase host (e.g., abc123.supabase.co)
# 3. Replace your_openai_api_key_here with your actual OpenAI API key
# 4. Replace your_secret_key_here with a secure random string
"""
    
    try:
        with open('huggingface_secrets_template.txt', 'w', encoding='utf-8') as f:
            f.write(template)
        print("✅ Created huggingface_secrets_template.txt")
        print("📋 Use this template to update your Hugging Face Space secrets")
    except Exception as e:
        print(f"❌ Error creating template file: {e}")
        print("📋 Here's the template content:")
        print(template)

async def main():
    """Main diagnostic function."""
    print_banner()
    
    # Get current connection string
    conn_str = get_current_connection_string()
    if not conn_str:
        print("❌ No SUPABASE_DB_URL found in environment variables")
        print("🔧 This is expected if you're running this locally")
        print("📋 The connection string should be set in Hugging Face Space secrets")
        create_new_connection_template()
        return
    
    print(f"📋 Current connection string: {conn_str.split('@')[0]}@***")
    
    # Parse connection string
    conn_info = parse_connection_string(conn_str)
    if not conn_info:
        print("❌ Failed to parse connection string")
        return
    
    # Check Supabase project status
    project_ok = check_supabase_project_status(conn_info['host'])
    
    # Test network connectivity
    network_ok = check_network_connectivity(conn_info['host'], conn_info['port'])
    
    # Test database connection
    db_ok = await test_database_connection(conn_info)
    
    # Generate fix instructions
    generate_fix_instructions(conn_info, network_ok, db_ok)
    
    # Create template
    create_new_connection_template()
    
    print("\n🎯 Summary:")
    print(f"   Project Status: {'✅ OK' if project_ok else '❌ Check Required'}")
    print(f"   Network: {'✅ OK' if network_ok else '❌ Failed'}")
    print(f"   Database: {'✅ OK' if db_ok else '❌ Failed'}")
    
    if network_ok and db_ok:
        print("\n✅ Your connection appears to be working!")
        print("📋 The issue might be specific to Hugging Face deployment.")
        print("🔧 Try redeploying your Space after verifying the secrets.")
    else:
        print("\n❌ Connection issues detected.")
        print("📋 Follow the fix instructions above to resolve the issues.")

if __name__ == "__main__":
    asyncio.run(main()) 