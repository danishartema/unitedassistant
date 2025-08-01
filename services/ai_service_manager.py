"""
AI Service Manager - Manages multiple AI services with OpenAI as primary.
"""
import logging
from typing import Dict, List, Optional, Any
from config import settings

from services.openai_service import OpenAIService
from services.huggingface_service import HuggingFaceService

logger = logging.getLogger(__name__)


class AIServiceManager:
    """Manages multiple AI services with OpenAI as the primary service."""
    
    def __init__(self):
        self.openai_service = None
        self.huggingface_service = None
        self.primary_service = settings.primary_ai_service.lower()
        
        # Initialize OpenAI service (primary)
        if settings.openai_api_key:
            try:
                self.openai_service = OpenAIService()
                logger.info("OpenAI service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI service: {e}")
        else:
            logger.warning("OpenAI API key not configured")
        
        # Initialize Hugging Face service
        if settings.hf_api_token:
            try:
                self.huggingface_service = HuggingFaceService()
                logger.info("Hugging Face service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Hugging Face service: {e}")
        
        logger.info(f"AI Service Manager initialized with primary service: {self.primary_service}")
    
    async def generate_content(
        self,
        prompt: str,
        context: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        service: str = "auto"
    ) -> str:
        """Generate content using the appropriate AI service."""
        try:
            # Determine which service to use
            if service == "auto":
                service = self.primary_service
            elif service == "openai" and self.openai_service:
                service = "openai"
            elif service == "huggingface" and self.huggingface_service:
                service = "huggingface"
            else:
                # Fallback to available service
                if self.openai_service:
                    service = "openai"
                elif self.huggingface_service:
                    service = "huggingface"
                else:
                    raise Exception("No AI service available")
            
            # Generate content using selected service
            if service == "openai" and self.openai_service:
                return await self.openai_service.generate_content(
                    prompt=prompt,
                    context=context,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            elif service == "huggingface" and self.huggingface_service:
                return await self.huggingface_service.generate_text(
                    prompt=prompt,
                    max_length=max_tokens,
                    temperature=temperature
                )
            else:
                raise Exception(f"Service '{service}' not available")
                
        except Exception as e:
            logger.error(f"Content generation error: {e}")
            raise Exception(f"Failed to generate content: {str(e)}")
    
    async def create_embedding(
        self,
        text: str,
        service: str = "auto"
    ) -> List[float]:
        """Create embedding using the appropriate AI service."""
        try:
            # Determine which service to use
            if service == "auto":
                # Prefer OpenAI for embeddings
                if self.openai_service:
                    service = "openai"
                elif self.huggingface_service:
                    service = "huggingface"
                else:
                    raise Exception("No AI service available")
            
            # Create embedding using selected service
            if service == "openai" and self.openai_service:
                return await self.openai_service.create_embedding(text)
            elif service == "huggingface" and self.huggingface_service:
                return await self.huggingface_service.create_embedding(text)
            else:
                raise Exception(f"Service '{service}' not available")
                
        except Exception as e:
            logger.error(f"Embedding creation error: {e}")
            raise Exception(f"Failed to create embedding: {str(e)}")
    
    async def analyze_content_structure(
        self,
        content: str,
        service: str = "auto"
    ) -> dict:
        """Analyze content structure using the appropriate AI service."""
        try:
            # OpenAI has better structure analysis, prefer it
            if service == "auto" and self.openai_service:
                service = "openai"
            elif service == "auto" and self.huggingface_service:
                service = "huggingface"
            
            if service == "openai" and self.openai_service:
                return await self.openai_service.analyze_content_structure(content)
            elif service == "huggingface" and self.huggingface_service:
                # Basic analysis for Hugging Face
                return {
                    "key_points": [],
                    "topics": [],
                    "complexity_level": "medium",
                    "word_count": len(content.split()),
                    "summary": "Analysis via Hugging Face"
                }
            else:
                raise Exception(f"Service '{service}' not available")
                
        except Exception as e:
            logger.error(f"Content analysis error: {e}")
            return {
                "key_points": [],
                "topics": [],
                "complexity_level": "medium",
                "word_count": len(content.split()),
                "summary": "Analysis failed"
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all AI services."""
        return {
            "primary_service": self.primary_service,
            "openai": {
                "available": self.openai_service is not None,
                "configured": bool(settings.openai_api_key),
                "model": settings.openai_model if self.openai_service else None
            },
            "huggingface": {
                "available": self.huggingface_service is not None,
                "configured": bool(settings.hf_api_token or settings.hf_model_name),
                "model": settings.hf_model_name if self.huggingface_service else None
            }
        }
    
    def get_available_services(self) -> List[str]:
        """Get list of available AI services."""
        services = []
        if self.openai_service:
            services.append("openai")
        if self.huggingface_service:
            services.append("huggingface")
        return services


# Global instance
ai_service_manager = AIServiceManager() 