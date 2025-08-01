"""
AI Service Status router for monitoring AI service configuration.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from services.ai_service_manager import ai_service_manager
from dependencies import get_current_user
from models import User

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/status")
async def get_ai_status(current_user: User = Depends(get_current_user)):
    """Get status of all AI services."""
    try:
        status = ai_service_manager.get_service_status()
        return {
            "success": True,
            "ai_services": status,
            "available_services": ai_service_manager.get_available_services()
        }
    except Exception as e:
        logger.error(f"Error getting AI status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def ai_health_check():
    """Health check for AI services."""
    try:
        status = ai_service_manager.get_service_status()
        
        # Check if primary service is available
        primary_service = status.get("primary_service", "openai")
        primary_available = status.get(primary_service, {}).get("available", False)
        
        return {
            "status": "healthy" if primary_available else "unhealthy",
            "service": "ai-services",
            "primary_service": primary_service,
            "primary_available": primary_available,
            "details": status
        }
    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "ai-services",
            "error": str(e)
        }


@router.get("/config")
async def get_ai_config(current_user: User = Depends(get_current_user)):
    """Get AI service configuration (without sensitive data)."""
    try:
        status = ai_service_manager.get_service_status()
        
        # Remove sensitive information
        config = {
            "primary_service": status.get("primary_service"),
            "openai": {
                "available": status.get("openai", {}).get("available", False),
                "configured": status.get("openai", {}).get("configured", False),
                "model": status.get("openai", {}).get("model")
            },
            "huggingface": {
                "available": status.get("huggingface", {}).get("available", False),
                "configured": status.get("huggingface", {}).get("configured", False),
                "model": status.get("huggingface", {}).get("model")
            }
        }
        
        return {
            "success": True,
            "config": config
        }
    except Exception as e:
        logger.error(f"Error getting AI config: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 