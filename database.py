"""
Async database configuration and session management.
"""
import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine as sqlalchemy_create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

def get_database_config():
    """Get database configuration dynamically."""
    try:
        # Use the effective database URL that prefers Supabase in production
        database_url = settings.effective_database_url
        
        # Debug logging
        print(f"🔧 Database Configuration:")
        print(f"   Environment: {settings.environment}")
        print(f"   Is Production: {settings.is_production}")
        print(f"   Is Hugging Face Deployment: {settings.is_huggingface_deployment}")
        print(f"   Supabase DB URL set: {'Yes' if settings.supabase_db_url else 'No'}")
        
        # Mask sensitive parts of the URL for logging
        if '@' in database_url:
            masked_url = database_url.split('@')[0] + "@***"
        else:
            masked_url = database_url
        print(f"   Effective Database URL: {masked_url}")
        
        # Always PostgreSQL/Supabase
        print(f"   Database Type: PostgreSQL/Supabase")
        
        return database_url, False  # Always return False for is_sqlite
    except Exception as e:
        print(f"❌ Error in database configuration: {e}")
        print("🔧 Please ensure SUPABASE_DB_URL is set for Hugging Face deployment")
        raise

# Get initial configuration
try:
    DATABASE_URL, is_sqlite = get_database_config()
except Exception as e:
    print(f"❌ Failed to get database configuration: {e}")
    raise

def create_async_engine(database_url=None):
    """Create async engine with current configuration."""
    try:
        if database_url is None:
            database_url, _ = get_database_config()
        
        # PostgreSQL configuration - Supabase only
        print("✅ Using PostgreSQL/Supabase configuration")
        return sqlalchemy_create_async_engine(database_url)
    except Exception as e:
        print(f"❌ Error creating async engine: {e}")
        raise

# Create the async engine
try:
    async_engine = create_async_engine()
except Exception as e:
    print(f"❌ Failed to create async engine: {e}")
    raise

AsyncSessionLocal = async_sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=async_engine,
    expire_on_commit=False,  # This helps avoid greenlet issues
    class_=AsyncSession
)

def create_sync_engine():
    """Create sync engine with current configuration."""
    try:
        database_url, _ = get_database_config()
        
        return create_engine(database_url)
    except Exception as e:
        print(f"❌ Error creating sync engine: {e}")
        raise

# Sync database for debugging
try:
    sync_engine = create_sync_engine()
    SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
except Exception as e:
    print(f"❌ Failed to create sync engine: {e}")
    raise

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
        
        print(f"🔧 Creating database tables...")
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Mask sensitive parts for logging
        if '@' in database_url:
            masked_url = database_url.split('@')[0] + "@***"
        else:
            masked_url = database_url
        print(f"✅ Database tables created successfully using: {masked_url}")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        print("🔧 Please check your database configuration and connection")
        print("🔧 For Hugging Face deployment, ensure SUPABASE_DB_URL is set")
        raise

# (Sync get_db and create_tables_sync removed for async-only migration)
