"""
Hugging Face API router for model inference endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import logging

from services.huggingface_service import HuggingFaceService
from dependencies import get_current_user
from models import User

logger = logging.getLogger(__name__)

router = APIRouter()
hf_service = HuggingFaceService()


class TextGenerationRequest(BaseModel):
    prompt: str
    model_name: Optional[str] = None
    max_length: int = 2048
    temperature: float = 0.7
    use_local: bool = False


class EmbeddingRequest(BaseModel):
    text: str
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"


class ClassificationRequest(BaseModel):
    text: str
    model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"


class TranslationRequest(BaseModel):
    text: str
    source_lang: str = "en"
    target_lang: str = "es"
    model_name: str = "Helsinki-NLP/opus-mt-en-es"


@router.get("/status")
async def get_hf_status(current_user: User = Depends(get_current_user)):
    """Get Hugging Face service status."""
    try:
        status = hf_service.get_service_status()
        return {
            "success": True,
            "status": status
        }
    except Exception as e:
        logger.error(f"Error getting HF status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def get_available_models(current_user: User = Depends(get_current_user)):
    """Get available Hugging Face models."""
    try:
        models = hf_service.get_available_models()
        return {
            "success": True,
            "models": models
        }
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_text(
    request: TextGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate text using Hugging Face models."""
    try:
        result = await hf_service.generate_text(
            prompt=request.prompt,
            model_name=request.model_name,
            max_length=request.max_length,
            temperature=request.temperature,
            use_local=request.use_local
        )
        
        return {
            "success": True,
            "generated_text": result,
            "prompt": request.prompt,
            "model_used": request.model_name or "default"
        }
    except Exception as e:
        logger.error(f"Error generating text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/embed")
async def create_embedding(
    request: EmbeddingRequest,
    current_user: User = Depends(get_current_user)
):
    """Create embedding using Hugging Face models."""
    try:
        embedding = await hf_service.create_embedding(
            text=request.text,
            model_name=request.model_name
        )
        
        return {
            "success": True,
            "embedding": embedding,
            "text": request.text,
            "model_used": request.model_name,
            "embedding_dimension": len(embedding)
        }
    except Exception as e:
        logger.error(f"Error creating embedding: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify")
async def classify_text(
    request: ClassificationRequest,
    current_user: User = Depends(get_current_user)
):
    """Classify text using Hugging Face models."""
    try:
        result = await hf_service.classify_text(
            text=request.text,
            model_name=request.model_name
        )
        
        return {
            "success": True,
            "classification": result,
            "text": request.text,
            "model_used": request.model_name
        }
    except Exception as e:
        logger.error(f"Error classifying text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate")
async def translate_text(
    request: TranslationRequest,
    current_user: User = Depends(get_current_user)
):
    """Translate text using Hugging Face models."""
    try:
        result = await hf_service.translate_text(
            text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            model_name=request.model_name
        )
        
        return {
            "success": True,
            "translation": result,
            "original_text": request.text,
            "source_language": request.source_lang,
            "target_language": request.target_lang,
            "model_used": request.model_name
        }
    except Exception as e:
        logger.error(f"Error translating text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def hf_health_check():
    """Health check for Hugging Face service."""
    try:
        status = hf_service.get_service_status()
        return {
            "status": "healthy" if (status["client_initialized"] or status["local_model_loaded"]) else "unhealthy",
            "service": "huggingface",
            "details": status
        }
    except Exception as e:
        logger.error(f"HF health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "huggingface",
            "error": str(e)
        } 