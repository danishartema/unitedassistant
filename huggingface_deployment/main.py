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
    logger.info(f"Database URL: {settings.database_url}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    # Try to create database tables, but don't fail if it doesn't work
    try:
        await create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        logger.error(f"Exception type: {type(e)}")
        logger.error(f"Exception details: {str(e)}")
        logger.warning("Continuing startup without database - some features may be limited")
        # Continue startup even if database creation fails
        # The application can still run with limited functionality
    
    logger.info("Unified Assistant backend startup completed")
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
        "docs": "/docs",
        "openapi": "/openapi.json",
        "health": "/health",
        "status": "running"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "unified-assistant-backend"}


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
