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
    logger.info(f"Temp directory exists: {os.path.exists('/tmp')}")
    logger.info(f"Temp directory writable: {os.access('/tmp', os.W_OK)}")
    logger.info(f"App directory writable: {os.access('/app', os.W_OK)}")
    
    # Skip database initialization for now to get the app running
    logger.warning("Skipping database initialization for Hugging Face Spaces deployment")
    logger.info("Application will run without database functionality")
    # TODO: Implement database solution for Hugging Face Spaces
    
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
        "status": "running",
        "database": "disabled",
        "note": "Database functionality is currently disabled for Hugging Face Spaces deployment"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "service": "unified-assistant-backend",
        "database": "disabled",
        "message": "Application is running without database functionality"
    }

# Status endpoint
@app.get("/status")
async def status():
    """Status endpoint with detailed information."""
    return {
        "status": "running",
        "service": "Unified Assistant API",
        "version": "1.0.0",
        "environment": settings.environment,
        "database": {
            "status": "disabled",
            "reason": "Hugging Face Spaces deployment - database not available"
        },
        "features": {
            "ai_services": "available",
            "file_processing": "available",
            "authentication": "disabled (requires database)",
            "project_management": "disabled (requires database)"
        },
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "status": "/status"
        }
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
