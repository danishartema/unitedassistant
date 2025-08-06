#!/usr/bin/env python3
"""
Database setup and migration script for the Assistant Chatbot application.
Handles database initialization, table creation, and user isolation migration.
"""

import asyncio
import logging
from sqlalchemy import text
from database import create_async_engine, get_async_db
from models import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_database_connection():
    """Test database connection."""
    try:
        engine = create_async_engine()
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

async def setup_database():
    """Create all database tables."""
    try:
        logger.info("🚀 Starting database setup...")
        
        # Test connection first
        if not await test_database_connection():
            return False
        
        # Create tables
        engine = create_async_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # List created tables
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
        
        logger.info("✅ All database tables created successfully")
        logger.info(f"📋 Available tables: {', '.join(tables)}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        return False

async def show_database_info():
    """Show database statistics and information."""
    try:
        engine = create_async_engine()
        async with engine.begin() as conn:
            # Get record counts for each table
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
                    logger.info(f" {table}: {count} records")
                except Exception as e:
                    logger.info(f" {table}: Error getting count - {e}")
                    
    except Exception as e:
        logger.error(f"❌ Error showing database info: {e}")

async def migrate_user_isolation():
    """Migrate existing data to support user isolation."""
    try:
        from sqlalchemy import text
        from database import create_async_engine
        
        engine = create_async_engine()
        
        print("🔄 Starting user isolation migration...")
        
        # Add user_id columns if they don't exist
        print("📝 Adding user_id columns...")
        async with engine.begin() as conn:
            await conn.execute(text("""
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'gpt_mode_sessions' AND column_name = 'user_id') THEN
                        ALTER TABLE gpt_mode_sessions ADD COLUMN user_id VARCHAR(36);
                    END IF;
                    
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'conversation_memory' AND column_name = 'user_id') THEN
                        ALTER TABLE conversation_memory ADD COLUMN user_id VARCHAR(36);
                    END IF;
                    
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'cross_module_memory' AND column_name = 'user_id') THEN
                        ALTER TABLE cross_module_memory ADD COLUMN user_id VARCHAR(36);
                    END IF;
                END $$;
            """))
        print("✅ User ID columns added successfully")
        
        # Update existing records
        print("🔄 Updating existing records...")
        async with engine.begin() as conn:
            await conn.execute(text("""
                UPDATE gpt_mode_sessions 
                SET user_id = (
                    SELECT owner_id 
                    FROM projects 
                    WHERE projects.id = gpt_mode_sessions.project_id
                )
                WHERE user_id IS NULL
            """))
        print("✅ Updated gpt_mode_sessions")
        
        async with engine.begin() as conn:
            await conn.execute(text("""
                UPDATE conversation_memory 
                SET user_id = (
                    SELECT owner_id 
                    FROM projects 
                    WHERE projects.id = conversation_memory.project_id
                )
                WHERE user_id IS NULL
            """))
        print("✅ Updated conversation_memory")
        
        async with engine.begin() as conn:
            await conn.execute(text("""
                UPDATE cross_module_memory 
                SET user_id = (
                    SELECT owner_id 
                    FROM projects 
                    WHERE projects.id = cross_module_memory.project_id
                )
                WHERE user_id IS NULL
            """))
        print("✅ Updated cross_module_memory")
        
        # Make user_id columns NOT NULL
        print("🔒 Making user_id columns NOT NULL...")
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE gpt_mode_sessions ALTER COLUMN user_id SET NOT NULL"))
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE conversation_memory ALTER COLUMN user_id SET NOT NULL"))
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE cross_module_memory ALTER COLUMN user_id SET NOT NULL"))
        print("✅ User ID columns are now NOT NULL")
        
        # Add foreign key constraints
        print("🔗 Adding foreign key constraints...")
        
        # Check and add foreign key for gpt_mode_sessions
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'gpt_mode_sessions' 
                AND constraint_type = 'FOREIGN KEY' 
                AND constraint_name = 'fk_gpt_mode_sessions_user'
            """))
            if not result.fetchone():
                await conn.execute(text("""
                    ALTER TABLE gpt_mode_sessions 
                    ADD CONSTRAINT fk_gpt_mode_sessions_user 
                    FOREIGN KEY (user_id) REFERENCES users(id)
                """))
                print("✅ Added foreign key for gpt_mode_sessions")
            else:
                print("ℹ️  Foreign key for gpt_mode_sessions already exists")
        
        # Check and add foreign key for conversation_memory
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'conversation_memory' 
                AND constraint_type = 'FOREIGN KEY' 
                AND constraint_name = 'fk_conversation_memory_user'
            """))
            if not result.fetchone():
                await conn.execute(text("""
                    ALTER TABLE conversation_memory 
                    ADD CONSTRAINT fk_conversation_memory_user 
                    FOREIGN KEY (user_id) REFERENCES users(id)
                """))
                print("✅ Added foreign key for conversation_memory")
            else:
                print("ℹ️  Foreign key for conversation_memory already exists")
        
        # Check and add foreign key for cross_module_memory
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'cross_module_memory' 
                AND constraint_type = 'FOREIGN KEY' 
                AND constraint_name = 'fk_cross_module_memory_user'
            """))
            if not result.fetchone():
                await conn.execute(text("""
                    ALTER TABLE cross_module_memory 
                    ADD CONSTRAINT fk_cross_module_memory_user 
                    FOREIGN KEY (user_id) REFERENCES users(id)
                """))
                print("✅ Added foreign key for cross_module_memory")
            else:
                print("ℹ️  Foreign key for cross_module_memory already exists")
        
        # Add unique constraints
        print("🔐 Adding unique constraints...")
        
        # Check and add unique constraint for gpt_mode_sessions
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'gpt_mode_sessions' 
                AND constraint_type = 'UNIQUE' 
                AND constraint_name = 'uq_project_user_mode'
            """))
            if not result.fetchone():
                await conn.execute(text("""
                    ALTER TABLE gpt_mode_sessions 
                    ADD CONSTRAINT uq_project_user_mode 
                    UNIQUE (project_id, user_id, mode_name)
                """))
                print("✅ Added unique constraint for gpt_mode_sessions")
            else:
                print("ℹ️  Unique constraint for gpt_mode_sessions already exists")
        
        # Check and add unique constraint for cross_module_memory
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'cross_module_memory' 
                AND constraint_type = 'UNIQUE' 
                AND constraint_name = 'uq_project_user_cross_module'
            """))
            if not result.fetchone():
                await conn.execute(text("""
                    ALTER TABLE cross_module_memory 
                    ADD CONSTRAINT uq_project_user_cross_module 
                    UNIQUE (project_id, user_id)
                """))
                print("✅ Added unique constraint for cross_module_memory")
            else:
                print("ℹ️  Unique constraint for cross_module_memory already exists")
        
        print("✅ User isolation migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during user isolation migration: {e}")
        raise

async def fix_enum_types():
    """Fix enum type issues in the database."""
    try:
        from sqlalchemy import text
        from database import create_async_engine
        
        engine = create_async_engine()
        
        async with engine.begin() as conn:
            print("🔧 Fixing enum types...")
            
            # Check if the enum type exists and has the correct values
            await conn.execute(text("""
                DO $$ 
                BEGIN 
                    -- Check if phasestatus enum exists and has correct values
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'phasestatus') THEN
                        CREATE TYPE phasestatus AS ENUM ('not_started', 'in_progress', 'completed', 'stale');
                    ELSE
                        -- Add missing enum values if they don't exist
                        BEGIN
                            ALTER TYPE phasestatus ADD VALUE IF NOT EXISTS 'not_started';
                        EXCEPTION
                            WHEN duplicate_object THEN
                                NULL;
                        END;
                        
                        BEGIN
                            ALTER TYPE phasestatus ADD VALUE IF NOT EXISTS 'in_progress';
                        EXCEPTION
                            WHEN duplicate_object THEN
                                NULL;
                        END;
                        
                        BEGIN
                            ALTER TYPE phasestatus ADD VALUE IF NOT EXISTS 'completed';
                        EXCEPTION
                            WHEN duplicate_object THEN
                                NULL;
                        END;
                        
                        BEGIN
                            ALTER TYPE phasestatus ADD VALUE IF NOT EXISTS 'stale';
                        EXCEPTION
                            WHEN duplicate_object THEN
                                NULL;
                        END;
                    END IF;
                    
                    -- Check if exportstatus enum exists and has correct values
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'exportstatus') THEN
                        CREATE TYPE exportstatus AS ENUM ('pending', 'in_progress', 'completed', 'failed');
                    ELSE
                        -- Add missing enum values if they don't exist
                        BEGIN
                            ALTER TYPE exportstatus ADD VALUE IF NOT EXISTS 'pending';
                        EXCEPTION
                            WHEN duplicate_object THEN
                                NULL;
                        END;
                        
                        BEGIN
                            ALTER TYPE exportstatus ADD VALUE IF NOT EXISTS 'in_progress';
                        EXCEPTION
                            WHEN duplicate_object THEN
                                NULL;
                        END;
                        
                        BEGIN
                            ALTER TYPE exportstatus ADD VALUE IF NOT EXISTS 'completed';
                        EXCEPTION
                            WHEN duplicate_object THEN
                                NULL;
                        END;
                        
                        BEGIN
                            ALTER TYPE exportstatus ADD VALUE IF NOT EXISTS 'failed';
                        EXCEPTION
                            WHEN duplicate_object THEN
                                NULL;
                        END;
                    END IF;
                    
                    -- Check if exportformat enum exists and has correct values
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'exportformat') THEN
                        CREATE TYPE exportformat AS ENUM ('pdf', 'word', 'json');
                    ELSE
                        -- Add missing enum values if they don't exist
                        BEGIN
                            ALTER TYPE exportformat ADD VALUE IF NOT EXISTS 'pdf';
                        EXCEPTION
                            WHEN duplicate_object THEN
                                NULL;
                        END;
                        
                        BEGIN
                            ALTER TYPE exportformat ADD VALUE IF NOT EXISTS 'word';
                        EXCEPTION
                            WHEN duplicate_object THEN
                                NULL;
                        END;
                        
                        BEGIN
                            ALTER TYPE exportformat ADD VALUE IF NOT EXISTS 'json';
                        EXCEPTION
                            WHEN duplicate_object THEN
                                NULL;
                        END;
                    END IF;
                    
                    -- Check if userrole enum exists and has correct values
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN
                        CREATE TYPE userrole AS ENUM ('admin', 'user');
                    ELSE
                        -- Add missing enum values if they don't exist
                        BEGIN
                            ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'admin';
                        EXCEPTION
                            WHEN duplicate_object THEN
                                NULL;
                        END;
                        
                        BEGIN
                            ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'user';
                        EXCEPTION
                            WHEN duplicate_object THEN
                                NULL;
                        END;
                    END IF;
                    
                    -- Check if projectrole enum exists and has correct values
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'projectrole') THEN
                        CREATE TYPE projectrole AS ENUM ('owner', 'editor');
                    ELSE
                        -- Add missing enum values if they don't exist
                        BEGIN
                            ALTER TYPE projectrole ADD VALUE IF NOT EXISTS 'owner';
                        EXCEPTION
                            WHEN duplicate_object THEN
                                NULL;
                        END;
                        
                        BEGIN
                            ALTER TYPE projectrole ADD VALUE IF NOT EXISTS 'editor';
                        EXCEPTION
                            WHEN duplicate_object THEN
                                NULL;
                        END;
                    END IF;
                END $$;
            """))
            
            print("✅ Enum types fixed successfully!")
            
    except Exception as e:
        print(f"❌ Error fixing enum types: {e}")
        raise

async def main():
    """Main setup function."""
    try:
        # Setup database
        if await setup_database():
            logger.info("✅ Database setup completed successfully")
            
            # Fix enum types
            await fix_enum_types()
            
            # Run user isolation migration
            await migrate_user_isolation()
            
            # Show database info
            await show_database_info()
        else:
            logger.error("❌ Database setup failed")
            
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 