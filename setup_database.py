#!/usr/bin/env python3
"""
Database setup and migration script for Unified Assistant.
This script helps set up the database connection and create tables.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from database import create_tables, async_engine, DATABASE_URL
from config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_database_connection():
    """Test the database connection."""
    try:
        # Test connection
        async with async_engine.begin() as conn:
            if DATABASE_URL.startswith("sqlite"):
                result = await conn.execute("SELECT 1")
            else:
                result = await conn.execute("SELECT 1")
            await result.fetchone()
        
        logger.info("✅ Database connection successful!")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

async def setup_database():
    """Set up the database tables."""
    try:
        logger.info("🔄 Setting up database...")
        
        # Test connection first
        if not await test_database_connection():
            return False
        
        # Create tables
        await create_tables()
        logger.info("✅ Database setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        return False

async def show_database_info():
    """Show current database configuration."""
    logger.info("📊 Database Configuration:")
    logger.info(f"   Environment: {settings.environment}")
    logger.info(f"   Is Production: {settings.is_production}")
    logger.info(f"   Database Type: {'PostgreSQL' if not DATABASE_URL.startswith('sqlite') else 'SQLite'}")
    
    # Mask sensitive information in the URL
    masked_url = DATABASE_URL
    if '@' in masked_url:
        # Mask password in PostgreSQL URL
        parts = masked_url.split('@')
        if ':' in parts[0]:
            protocol_user = parts[0].split(':')
            if len(protocol_user) >= 3:
                masked_url = f"{protocol_user[0]}:{protocol_user[1]}:***@{parts[1]}"
    
    logger.info(f"   Database URL: {masked_url}")
    
    if settings.supabase_db_url:
        logger.info("   Supabase URL configured: Yes")
    else:
        logger.info("   Supabase URL configured: No")

async def main():
    """Main function."""
    logger.info("🚀 Unified Assistant Database Setup")
    logger.info("=" * 50)
    
    # Show current configuration
    await show_database_info()
    logger.info("")
    
    # Setup database
    success = await setup_database()
    
    if success:
        logger.info("")
        logger.info("🎉 Database is ready to use!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Start your application")
        logger.info("2. Create your first user account")
        logger.info("3. Begin using the Unified Assistant!")
    else:
        logger.error("")
        logger.error("💥 Database setup failed!")
        logger.error("")
        logger.error("Troubleshooting:")
        logger.error("1. Check your database connection string")
        logger.error("2. Verify network connectivity")
        logger.error("3. Ensure database credentials are correct")
        logger.error("4. Check the SUPABASE_SETUP.md guide for help")
        
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 