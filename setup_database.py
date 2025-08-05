#!/usr/bin/env python3
"""
Database setup and migration script for the Assistant Chatbot application.
"""

import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from database import create_async_engine, get_async_db
from models import Base, User, Project, Phase, PhaseDraft, ExportTask, GPTModeSession, PhaseEmbedding, ProjectMemory, ProjectSummary, ConversationMemory, CrossModuleMemory, ConversationMessage

logger = logging.getLogger(__name__)

async def test_database_connection():
    """Test database connection and basic functionality."""
    try:
        engine = create_async_engine()
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

async def setup_database():
    """Create all database tables."""
    try:
        engine = create_async_engine()
        
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ All database tables created successfully")
            
            # Verify tables exist
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            logger.info(f"📋 Available tables: {', '.join(tables)}")
            
        return True
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        return False

async def show_database_info():
    """Show database information and table counts."""
    try:
        engine = create_async_engine()
        async with engine.begin() as conn:
            # Get table counts
            tables = [
                'users', 'projects', 'phases', 'phase_drafts', 'export_tasks',
                'gpt_mode_sessions', 'phase_embeddings', 'project_memory',
                'project_summaries', 'conversation_memory', 'cross_module_memory',
                'conversation_messages'
            ]
            
            logger.info("📊 Database Statistics:")
            for table in tables:
                try:
                    result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    logger.info(f"  {table}: {count} records")
                except Exception as e:
                    logger.warning(f"  {table}: Error getting count - {e}")
                    
    except Exception as e:
        logger.error(f"❌ Error getting database info: {e}")

async def main():
    """Main setup function."""
    logger.info("🚀 Starting database setup...")
    
    # Test connection
    if not await test_database_connection():
        logger.error("❌ Cannot proceed without database connection")
        return
    
    # Setup database
    if await setup_database():
        logger.info("✅ Database setup completed successfully")
        
        # Show database info
        await show_database_info()
    else:
        logger.error("❌ Database setup failed")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main()) 