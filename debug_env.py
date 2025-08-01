#!/usr/bin/env python3
"""
Debug script to check environment variables.
"""
import os
from config import settings

def main():
    print("🔍 Environment Variable Debug")
    print("=" * 50)
    
    # Check raw environment variables
    print("Raw Environment Variables:")
    print(f"  SUPABASE_DB_URL: {'SET' if os.getenv('SUPABASE_DB_URL') else 'NOT SET'}")
    print(f"  ENVIRONMENT: {'SET' if os.getenv('ENVIRONMENT') else 'NOT SET'}")
    print(f"  SECRET_KEY: {'SET' if os.getenv('SECRET_KEY') else 'NOT SET'}")
    print(f"  OPENAI_API_KEY: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
    
    print("\nSettings Configuration:")
    print(f"  settings.environment: {settings.environment}")
    print(f"  settings.is_production: {settings.is_production}")
    print(f"  settings.supabase_db_url: {'SET' if settings.supabase_db_url else 'NOT SET'}")
    print(f"  settings.effective_database_url: {settings.effective_database_url.split('@')[0]}@***" if '@' in settings.effective_database_url else f"  settings.effective_database_url: {settings.effective_database_url}")
    
    print("\nDatabase Type:")
    if settings.effective_database_url.startswith("sqlite"):
        print("  ❌ Still using SQLite!")
    else:
        print("  ✅ Using PostgreSQL/Supabase!")

if __name__ == "__main__":
    main() 