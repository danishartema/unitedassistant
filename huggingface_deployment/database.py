"""
Async database configuration and session management.
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from base import Base

DATABASE_URL = settings.database_url

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
    # PostgreSQL configuration - with pool parameters
    async_engine = create_async_engine(
        DATABASE_URL,
        echo=False,  # Set to True for debugging
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=10,
        max_overflow=20,
        future=True
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

# Import models to ensure they are registered with SQLAlchemy
# This must be done after Base is defined and engines are created
import logging
logger = logging.getLogger(__name__)

try:
    import models
    logger.info("Models imported successfully")
    logger.info(f"Number of tables in metadata: {len(Base.metadata.tables)}")
    for table_name in Base.metadata.tables.keys():
        logger.info(f"Table: {table_name}")
except Exception as e:
    logger.error(f"Failed to import models: {e}")
    raise

async def get_async_db():
    """Get async database session."""
    try:
        async with AsyncSessionLocal() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        # Return a mock session for now
        logger.warning("Using mock database session - functionality will be limited")
        yield None

def get_sync_db():
    """Get sync database session for debugging."""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

async def create_tables():
    """Create all database tables asynchronously."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Attempting to create tables with database URL: {DATABASE_URL}")
        
        # Ensure the database directory exists
        if is_sqlite and not ":memory:" in DATABASE_URL:
            db_path = DATABASE_URL.replace("sqlite:///", "")
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
                logger.info(f"Created database directory: {db_dir}")
        
        # Test database connection first
        logger.info("Testing database connection...")
        async with async_engine.begin() as conn:
            # Simple test query
            result = await conn.execute("SELECT 1")
            logger.info("Database connection test successful")
        
        # Create tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

# (Sync get_db and create_tables_sync removed for async-only migration)
