
#!/usr/bin/env python3
"""
Comprehensive Supabase Connection Diagnostic
"""

import asyncio
import asyncpg
import socket
import requests
from urllib.parse import urlparse

async def diagnose_connection():
    """Comprehensive connection diagnosis."""
    
    print("Supabase Connection Diagnostic")
    print("=" * 50)
    
    # Your connection details
    supabase_url = "postgresql+asyncpg://postgres:WiHcl5UgLmP1rLGZ@nqdhdqdtpvqfecbsjaar.supabase.co:5432/postgres"
    
    # Parse the URL
    parsed = urlparse(supabase_url)
    host = parsed.hostname
    port = parsed.port
    user = parsed.username
    password = parsed.password
    database = parsed.path[1:]
    
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"User: {user}")
    print(f"Database: {database}")
    print(f"Password: {'*' * len(password)}")
    print()
    
    # Test 1: DNS Resolution
    print("1. Testing DNS Resolution...")
    try:
        ip_address = socket.gethostbyname(host)
        print(f"   [OK] DNS resolved: {host} -> {ip_address}")
    except socket.gaierror as e:
        print(f"   [ERROR] DNS resolution failed: {e}")
        return False
    
    # Test 2: Port Connectivity
    print("\n2. Testing Port Connectivity...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"   [OK] Port {port} is reachable")
        else:
            print(f"   [ERROR] Port {port} is not reachable (error code: {result})")
            return False
    except Exception as e:
        print(f"   [ERROR] Port connectivity test failed: {e}")
        return False
    
    # Test 3: Direct asyncpg connection
    print("\n3. Testing Direct Database Connection...")
    try:
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            timeout=10
        )
        
        result = await conn.fetchval("SELECT 1 as test")
        print(f"   [OK] Database connection successful: {result}")
        
        # Test if we can create tables
        try:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS test_connection (
                    id SERIAL PRIMARY KEY,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            print(f"   [OK] Table creation test successful")
            
            # Clean up
            await conn.execute("DROP TABLE IF EXISTS test_connection")
            print(f"   [OK] Table cleanup successful")
            
        except Exception as e:
            print(f"   [WARNING] Table creation test failed: {e}")
        
        await conn.close()
        return True
        
    except asyncpg.InvalidPasswordError:
        print(f"   [ERROR] Invalid password")
        return False
    except asyncpg.InvalidAuthorizationSpecificationError:
        print(f"   [ERROR] Invalid username or database")
        return False
    except asyncpg.ConnectionDoesNotExistError:
        print(f"   [ERROR] Connection does not exist")
        return False
    except Exception as e:
        print(f"   [ERROR] Database connection failed: {e}")
        return False

def test_supabase_api():
    """Test Supabase API access."""
    print("\n4. Testing Supabase API Access...")
    
    # Try to access Supabase status
    try:
        response = requests.get("https://supabase.com", timeout=10)
        if response.status_code == 200:
            print(f"   [OK] Supabase website is accessible")
        else:
            print(f"   [WARNING] Supabase website returned status: {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] Cannot access Supabase website: {e}")

def check_common_issues():
    """Check for common issues."""
    print("\n5. Checking Common Issues...")
    
    # Get host from the connection string
    supabase_url = "postgresql+asyncpg://postgres:WiHcl5UgLmP1rLGZ@nqdhdqdtpvqfecbsjaar.supabase.co:5432/postgres"
    parsed = urlparse(supabase_url)
    host = parsed.hostname
    password = parsed.password
    
    issues = []
    
    # Check if this looks like a valid Supabase hostname
    if not host.endswith('.supabase.co'):
        issues.append("Hostname doesn't end with .supabase.co")
    
    # Check if project reference looks valid
    project_ref = host.replace('.supabase.co', '')
    if len(project_ref) < 10:
        issues.append("Project reference seems too short")
    
    # Check password length
    if len(password) < 8:
        issues.append("Password seems too short")
    
    if issues:
        print("   [WARNING] Potential issues found:")
        for issue in issues:
            print(f"      - {issue}")
    else:
        print("   [OK] No obvious issues found")

if __name__ == "__main__":
    print("Starting comprehensive connection diagnosis...")
    print()
    
    # Run all tests
    success = asyncio.run(diagnose_connection())
    test_supabase_api()
    check_common_issues()
    
    print("\n" + "=" * 50)
    if success:
        print("[SUCCESS] All connection tests passed!")
        print("\nYour Supabase connection is working correctly.")
        print("You can now proceed with your application setup.")
    else:
        print("[ERROR] Connection tests failed.")
        print("\nTroubleshooting steps:")
        print("1. Check your Supabase project status at https://supabase.com/dashboard")
        print("2. Verify your database password in Supabase dashboard")
        print("3. Make sure your project is not paused or suspended")
        print("4. Check if there are any IP restrictions on your Supabase project")
        print("5. Try accessing your Supabase dashboard to confirm project is active") 