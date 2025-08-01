#!/usr/bin/env python3
"""
Supabase Project Verification Script
"""

import requests
import json
from urllib.parse import urlparse

def verify_supabase_project():
    """Verify Supabase project status and get connection details."""
    
    print("Supabase Project Verification")
    print("=" * 40)
    print()
    print("This script will help you verify your Supabase project status.")
    print("You'll need your Supabase API key and project reference.")
    print()
    
    # Get user input
    api_key = input("Enter your Supabase API key (eyJ...): ").strip()
    project_ref = input("Enter your project reference (e.g., nqdhdqdtpvqfecbsjaar): ").strip()
    
    if not api_key or not project_ref:
        print("[ERROR] Both API key and project reference are required.")
        return
    
    # Test API connection
    print(f"\nTesting connection to Supabase project: {project_ref}")
    
    try:
        # Get project details
        url = f"https://api.supabase.com/v1/projects/{project_ref}"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            project_data = response.json()
            print(f"[OK] Project found: {project_data.get('name', 'Unknown')}")
            print(f"   Status: {project_data.get('status', 'Unknown')}")
            print(f"   Region: {project_data.get('region', 'Unknown')}")
            
            # Get database connection info
            db_url = f"https://api.supabase.com/v1/projects/{project_ref}/api-keys"
            db_response = requests.get(db_url, headers=headers, timeout=10)
            
            if db_response.status_code == 200:
                print(f"\n[OK] Database connection details:")
                print(f"   Host: {project_ref}.supabase.co")
                print(f"   Port: 5432")
                print(f"   Database: postgres")
                print(f"   User: postgres")
                print()
                print("Your connection string should be:")
                print(f"postgresql+asyncpg://postgres:[YOUR-PASSWORD]@{project_ref}.supabase.co:5432/postgres")
                print()
                print("Please check your Supabase dashboard for the correct password.")
                
            else:
                print(f"[ERROR] Could not get database details: {db_response.status_code}")
                
        elif response.status_code == 404:
            print(f"[ERROR] Project not found. Please check your project reference.")
        elif response.status_code == 401:
            print(f"[ERROR] Invalid API key. Please check your API key.")
        else:
            print(f"[ERROR] API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network error: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")

def get_supabase_credentials():
    """Guide user to get Supabase credentials."""
    print("\nHow to get your Supabase credentials:")
    print("1. Go to https://supabase.com/dashboard")
    print("2. Select your project")
    print("3. Go to Settings → API")
    print("4. Copy the 'anon public' key (starts with 'eyJ')")
    print("5. The project reference is in the URL: https://supabase.com/dashboard/project/[PROJECT-REF]")
    print()
    print("For database connection:")
    print("1. Go to Settings → Database")
    print("2. Copy the connection string")
    print("3. Make sure to add '+asyncpg' after 'postgresql'")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Verify project status")
    print("2. Get credentials guide")
    
    choice = input("Enter choice (1/2): ").strip()
    
    if choice == "1":
        verify_supabase_project()
    elif choice == "2":
        get_supabase_credentials()
    else:
        print("Invalid choice.") 