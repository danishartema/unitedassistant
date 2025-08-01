"""
Async database configuration and session management.
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

def get_database_config():
    """Get database configuration dynamically."""
    # Use the effective database URL that prefers Supabase in production
    database_url = settings.effective_database_url
    
    # Debug logging
    print(f"🔧 Database Configuration:")
    print(f"   Environment: {settings.environment}")
    print(f"   Is Production: {settings.is_production}")
    print(f"   Supabase DB URL set: {'Yes' if settings.supabase_db_url else 'No'}")
    print(f"   Effective Database URL: {database_url.split('@')[0]}@***" if '@' in database_url else f"   Effective Database URL: {database_url}")
    
    # Determine if we're using SQLite or PostgreSQL
    is_sqlite = database_url.startswith("sqlite")
    
    return database_url, is_sqlite

# Get initial configuration
DATABASE_URL, is_sqlite = get_database_config()

def create_async_engine():
    """Create async engine with current configuration."""
    database_url, is_sqlite = get_database_config()
    
    if is_sqlite:
        # SQLite configuration - no pool_size or max_overflow
        return create_async_engine(
            database_url.replace("sqlite://", "sqlite+aiosqlite://"),
            connect_args={"check_same_thread": False},
            echo=False,  # Set to True for debugging
            pool_pre_ping=True,
            future=True
        )
    else:
        # PostgreSQL configuration - with pool parameters optimized for Supabase
        return create_async_engine(
            database_url,
            echo=False,  # Set to True for debugging
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=5,  # Reduced for Hugging Face Spaces
            max_overflow=10,  # Reduced for Hugging Face Spaces
            future=True,
            # Additional PostgreSQL-specific settings
            connect_args={
                "server_settings": {
                    "application_name": "unified_assistant"
                }
            }
        )

# Create the async engine
async_engine = create_async_engine()

AsyncSessionLocal = async_sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=async_engine,
    expire_on_commit=False,  # This helps avoid greenlet issues
    class_=AsyncSession
)

def create_sync_engine():
    """Create sync engine with current configuration."""
    database_url, is_sqlite = get_database_config()
    
    return create_engine(
        database_url,
        connect_args={"check_same_thread": False} if is_sqlite else {},
        echo=False
    )

# Sync database for debugging
sync_engine = create_sync_engine()
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

Base = declarative_base()

async def get_async_db():
    """Get async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

def get_sync_db():
    """Get sync database session for debugging."""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

async def create_tables():
    """Create all database tables asynchronously."""
    try:
        # Get current database configuration
        database_url, _ = get_database_config()
        
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print(f"✅ Database tables created successfully using: {database_url.split('@')[0]}@***")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        raise

# (Sync get_db and create_tables_sync removed for async-only migration)
