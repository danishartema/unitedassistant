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

async def migrate_user_isolation():
    """Migrate existing data to add user isolation."""
    try:
        from sqlalchemy import text
        from database import create_async_engine
        
        engine = create_async_engine()
        
        async with engine.begin() as conn:
            print("🔄 Starting user isolation migration...")
            
            # Add user_id columns if they don't exist
            print("📝 Adding user_id columns...")
            await conn.execute(text("""
                DO $$ 
                BEGIN 
                    -- Add user_id to gpt_mode_sessions if not exists
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                 WHERE table_name = 'gpt_mode_sessions' AND column_name = 'user_id') THEN
                        ALTER TABLE gpt_mode_sessions ADD COLUMN user_id VARCHAR(36);
                    END IF;
                    
                    -- Add user_id to conversation_memory if not exists
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                 WHERE table_name = 'conversation_memory' AND column_name = 'user_id') THEN
                        ALTER TABLE conversation_memory ADD COLUMN user_id VARCHAR(36);
                    END IF;
                    
                    -- Add user_id to cross_module_memory if not exists
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                 WHERE table_name = 'cross_module_memory' AND column_name = 'user_id') THEN
                        ALTER TABLE cross_module_memory ADD COLUMN user_id VARCHAR(36);
                    END IF;
                END $$;
            """))
            print("✅ User ID columns added successfully")
            
            # Update existing records to link to project owners
            print("🔄 Updating existing records...")
            
            # Update gpt_mode_sessions
            await conn.execute(text("""
                UPDATE gpt_mode_sessions 
                SET user_id = (
                    SELECT owner_id FROM projects WHERE projects.id = gpt_mode_sessions.project_id
                )
                WHERE user_id IS NULL
            """))
            print("✅ Updated gpt_mode_sessions")
            
            # Update conversation_memory
            await conn.execute(text("""
                UPDATE conversation_memory 
                SET user_id = (
                    SELECT owner_id FROM projects WHERE projects.id = conversation_memory.project_id
                )
                WHERE user_id IS NULL
            """))
            print("✅ Updated conversation_memory")
            
            # Update cross_module_memory
            await conn.execute(text("""
                UPDATE cross_module_memory 
                SET user_id = (
                    SELECT owner_id FROM projects WHERE projects.id = cross_module_memory.project_id
                )
                WHERE user_id IS NULL
            """))
            print("✅ Updated cross_module_memory")
            
            # Make user_id columns NOT NULL after populating data
            print("🔒 Making user_id columns NOT NULL...")
            await conn.execute(text("ALTER TABLE gpt_mode_sessions ALTER COLUMN user_id SET NOT NULL"))
            await conn.execute(text("ALTER TABLE conversation_memory ALTER COLUMN user_id SET NOT NULL"))
            await conn.execute(text("ALTER TABLE cross_module_memory ALTER COLUMN user_id SET NOT NULL"))
            print("✅ User ID columns are now NOT NULL")
            
            # Add foreign key constraints
            print("🔗 Adding foreign key constraints...")
            
            # Add foreign key for gpt_mode_sessions
            try:
                await conn.execute(text("""
                    ALTER TABLE gpt_mode_sessions 
                    ADD CONSTRAINT fk_gpt_mode_sessions_user 
                    FOREIGN KEY (user_id) REFERENCES users(id)
                """))
                print("✅ Added foreign key for gpt_mode_sessions")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("ℹ️  Foreign key for gpt_mode_sessions already exists")
                else:
                    raise
            
            # Add foreign key for conversation_memory
            try:
                await conn.execute(text("""
                    ALTER TABLE conversation_memory 
                    ADD CONSTRAINT fk_conversation_memory_user 
                    FOREIGN KEY (user_id) REFERENCES users(id)
                """))
                print("✅ Added foreign key for conversation_memory")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("ℹ️  Foreign key for conversation_memory already exists")
                else:
                    raise
            
            # Add foreign key for cross_module_memory
            try:
                await conn.execute(text("""
                    ALTER TABLE cross_module_memory 
                    ADD CONSTRAINT fk_cross_module_memory_user 
                    FOREIGN KEY (user_id) REFERENCES users(id)
                """))
                print("✅ Added foreign key for cross_module_memory")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("ℹ️  Foreign key for cross_module_memory already exists")
                else:
                    raise
            
            # Add unique constraints
            print("🔐 Adding unique constraints...")
            
            # Add unique constraint for gpt_mode_sessions
            try:
                await conn.execute(text("""
                    ALTER TABLE gpt_mode_sessions 
                    ADD CONSTRAINT uq_project_user_mode 
                    UNIQUE (project_id, user_id, mode_name)
                """))
                print("✅ Added unique constraint for gpt_mode_sessions")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("ℹ️  Unique constraint for gpt_mode_sessions already exists")
                else:
                    raise
            
            # Add unique constraint for cross_module_memory
            try:
                await conn.execute(text("""
                    ALTER TABLE cross_module_memory 
                    ADD CONSTRAINT uq_project_user_cross_module 
                    UNIQUE (project_id, user_id)
                """))
                print("✅ Added unique constraint for cross_module_memory")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("ℹ️  Unique constraint for cross_module_memory already exists")
                else:
                    raise
            
        print("✅ User isolation migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during user isolation migration: {e}")
        raise

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
        
        # Run user isolation migration
        await migrate_user_isolation()
        
        # Show database info
        await show_database_info()
    else:
        logger.error("❌ Database setup failed")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main()) 