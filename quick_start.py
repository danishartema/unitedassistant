#!/usr/bin/env python3
"""
Quick Start Script for Unified Assistant
This script provides a simple way to get started with the application.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print quick start banner."""
    print("Unified Assistant - Quick Start")
    print("=" * 50)
    print("Choose an option to get started:")
    print()

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"Running {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"[OK] {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_environment():
    """Check if environment is properly configured."""
    print("Checking environment...")
    
    required_vars = ["SUPABASE_DB_URL", "OPENAI_API_KEY", "SECRET_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"[ERROR] Missing environment variables: {', '.join(missing_vars)}")
        print("Please run: python setup_supabase_complete.py")
        return False
    
    print("[OK] Environment variables are configured")
    return True

def main():
    """Main quick start function."""
    print_banner()
    
    print("1. Setup Supabase and environment variables")
    print("2. Test your configuration")
    print("3. Start the application locally")
    print("4. Run all tests")
    print("5. Check application status")
    print("6. Exit")
    print()
    
    while True:
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == "1":
            print("\n" + "="*50)
            print("Setting up Supabase and environment variables...")
            success = run_command("python setup_supabase_complete.py", "Supabase setup")
            if success:
                print("\n[OK] Setup completed! You can now test your configuration.")
            else:
                print("\n[ERROR] Setup failed. Please check the errors above.")
        
        elif choice == "2":
            print("\n" + "="*50)
            if not check_environment():
                print("Please run option 1 first to set up your environment.")
                continue
            
            print("Testing your configuration...")
            success = run_command("python test_supabase_complete.py", "Configuration testing")
            if success:
                print("\n[OK] All tests passed! Your setup is ready.")
            else:
                print("\n[ERROR] Some tests failed. Please check the errors above.")
        
        elif choice == "3":
            print("\n" + "="*50)
            if not check_environment():
                print("Please run option 1 first to set up your environment.")
                continue
            
            print("Starting the application locally...")
            print("The application will be available at: http://localhost:7860")
            print("Press Ctrl+C to stop the server")
            print()
            
            try:
                subprocess.run(["python", "main.py"], check=True)
            except KeyboardInterrupt:
                print("\n[OK] Server stopped by user")
            except subprocess.CalledProcessError as e:
                print(f"\n[ERROR] Failed to start server: {e}")
        
        elif choice == "4":
            print("\n" + "="*50)
            print("Running all tests...")
            
            tests = [
                ("python test_database_config.py", "Database configuration test"),
                ("python setup_database.py", "Database setup test"),
                ("python test_supabase_complete.py", "Complete configuration test")
            ]
            
            all_passed = True
            for command, description in tests:
                if not run_command(command, description):
                    all_passed = False
            
            if all_passed:
                print("\n[SUCCESS] All tests passed! Your setup is working perfectly.")
            else:
                print("\n[WARNING] Some tests failed. Please check the errors above.")
        
        elif choice == "5":
            print("\n" + "="*50)
            print("Checking application status...")
            
            # Check if main.py exists
            if not Path("main.py").exists():
                print("[ERROR] main.py not found. Are you in the correct directory?")
                continue
            
            # Check environment
            env_ok = check_environment()
            
            # Check if database file exists (for local development)
            db_file = Path("unified_assistant.db")
            if db_file.exists():
                print(f"[OK] Local database file exists ({db_file.stat().st_size} bytes)")
            else:
                print("[INFO] No local database file (using Supabase)")
            
            # Check requirements
            if Path("requirements.txt").exists():
                print("[OK] requirements.txt found")
            else:
                print("[ERROR] requirements.txt not found")
            
            # Check Dockerfile
            if Path("Dockerfile").exists():
                print("[OK] Dockerfile found (ready for Hugging Face deployment)")
            else:
                print("[ERROR] Dockerfile not found")
            
            print("\nStatus Summary:")
            if env_ok:
                print("  [OK] Environment: Configured")
            else:
                print("  [ERROR] Environment: Not configured")
            
            print("  Next steps:")
            if not env_ok:
                print("    - Run option 1 to set up environment")
            else:
                print("    - Run option 3 to start the application")
                print("    - Run option 4 to run all tests")
        
        elif choice == "6":
            print("\nGoodbye! Happy coding!")
            break
        
        else:
            print("[ERROR] Invalid choice. Please enter a number between 1-6.")
        
        print("\n" + "="*50)

if __name__ == "__main__":
    main() 