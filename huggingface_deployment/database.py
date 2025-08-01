"""
Async database configuration and session management.
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

# Use the effective database URL that prefers Supabase in production
DATABASE_URL = settings.effective_database_url

# Determine if we're using SQLite or PostgreSQL
is_sqlite = DATABASE_URL.startswith("sqlite")

# Configure async engine with appropriate parameters for each database type
if is_sqlite:
    # SQLite configuration - no pool_size or max_overflow
    async_engine = create_async_engine(
        DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://"),
        connect_args={"check_same_thread": False},
        echo=False,  # Set to True for debugging
        pool_pre_ping=True,
        future=True
    )
else:
    # PostgreSQL configuration - with pool parameters optimized for Supabase
    async_engine = create_async_engine(
        DATABASE_URL,
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
        } if not is_sqlite else {}
    )

AsyncSessionLocal = async_sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=async_engine,
    expire_on_commit=False,  # This helps avoid greenlet issues
    class_=AsyncSession
)

# Sync database for debugging
sync_engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if is_sqlite else {},
    echo=False
)
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
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print(f"✅ Database tables created successfully using: {DATABASE_URL.split('@')[0]}@***")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        raise

# (Sync get_db and create_tables_sync removed for async-only migration)
