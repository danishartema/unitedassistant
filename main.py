"""
Main FastAPI application for the Unified Assistant backend.
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging

from database import async_engine, create_tables, get_async_db
from routers import auth as auth_router, projects as projects_router, phases as phases_router, exports as exports_router
from routers import assistant as assistant_router, huggingface as huggingface_router, ai_status as ai_status_router
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info("Starting up Unified Assistant backend...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Is Production: {settings.is_production}")
    logger.info(f"Is Hugging Face Deployment: {settings.is_huggingface_deployment}")
    
    try:
        # Always require Supabase
        if not settings.supabase_db_url and not os.getenv("SUPABASE_DB_URL"):
            logger.error("❌ SUPABASE_DB_URL environment variable is required")
            logger.error("🔧 Please set SUPABASE_DB_URL in your environment variables or Hugging Face Space secrets")
            raise ValueError("SUPABASE_DB_URL environment variable is required")
        else:
            logger.info("✅ Supabase database configuration detected")
        
        # Try to create tables with better error handling
        try:
            await create_tables()
            logger.info("✅ Database tables created successfully")
        except Exception as db_error:
            logger.error(f"❌ Database connection failed: {db_error}")
            
            # Provide specific guidance for Hugging Face deployment
            if settings.is_huggingface_deployment:
                logger.error("🔧 Hugging Face Deployment Database Issues:")
                logger.error("1. Check if your Supabase project is active (not paused)")
                logger.error("2. Verify your Supabase project is not suspended")
                logger.error("3. Check if there are IP restrictions on your Supabase project")
                logger.error("4. Verify the database credentials in your Space secrets")
                logger.error("5. Try accessing your Supabase dashboard to confirm project status")
                
                # For Hugging Face deployment, we can continue without database
                # The app will show appropriate error messages to users
                logger.warning("⚠️  Continuing without database connection for debugging purposes")
            else:
                # For local development, fail fast
                raise db_error
                
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        if settings.is_huggingface_deployment:
            logger.error("🔧 Hugging Face Deployment Issues:")
            logger.error("1. Check your Space secrets configuration")
            logger.error("2. Verify all required environment variables are set")
            logger.error("3. Check the Space logs for detailed error messages")
        raise e
    
    yield
    
    # Shutdown
    logger.info("Shutting down Unified Assistant backend...")


# Create FastAPI app
app = FastAPI(
    title="Unified Assistant API",
    description="AI-powered document creation platform with 14-phase workflows",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred"}
    )


# Root endpoint with API information
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Unified Assistant API",
        "version": "1.0.0",
        "description": "AI-powered document creation platform with 14-phase workflows",
        "environment": settings.environment,
        "is_production": settings.is_production,
        "is_huggingface_deployment": settings.is_huggingface_deployment,
        "docs": "/docs",
        "openapi": "/openapi.json",
        "health": "/health",
        "status": "running"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        from database import async_engine
        async with async_engine.begin() as conn:
            await conn.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        db_status = "disconnected"
    
    return {
        "status": "healthy", 
        "service": "unified-assistant-backend",
        "environment": settings.environment,
        "database": db_status,
        "is_huggingface_deployment": settings.is_huggingface_deployment
    }


# Include routers
# All routers are now expected to be async/await compatible with async DB
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(projects_router.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(phases_router.router, prefix="/api/v1/phases", tags=["phases"])
app.include_router(exports_router.router, prefix="/api/v1/exports", tags=["exports"])
app.include_router(assistant_router.router, prefix="/api/v1/assistant", tags=["assistant"])
app.include_router(huggingface_router.router, prefix="/api/v1/huggingface", tags=["huggingface"])
app.include_router(ai_status_router.router, prefix="/api/v1/ai", tags=["ai-status"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True if settings.environment == "development" else False
    )
