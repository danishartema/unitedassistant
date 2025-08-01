"""
Hugging Face service for model inference and API integration.
"""
import os
import logging
from typing import Dict, List, Optional, Any

# Optional imports - handle missing dependencies gracefully
try:
    from huggingface_hub import InferenceClient
    HUGGINGFACE_HUB_AVAILABLE = True
except ImportError:
    HUGGINGFACE_HUB_AVAILABLE = False
    InferenceClient = None

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    AutoTokenizer = None
    AutoModelForCausalLM = None
    pipeline = None

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None

from config import settings

logger = logging.getLogger(__name__)


class HuggingFaceService:
    """Service for Hugging Face model interactions."""
    
    def __init__(self):
        self.client = None
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        
        # Check if dependencies are available
        if not HUGGINGFACE_HUB_AVAILABLE:
            logger.warning("huggingface_hub not available. Hugging Face API features will be disabled.")
        
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("transformers not available. Local model features will be disabled.")
        
        if not TORCH_AVAILABLE:
            logger.warning("torch not available. Local model features will be disabled.")
        
        # Initialize Hugging Face client if API token is provided and dependencies are available
        if settings.hf_api_token and HUGGINGFACE_HUB_AVAILABLE:
            try:
                self.client = InferenceClient(token=settings.hf_api_token)
                logger.info("Hugging Face Inference Client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Hugging Face client: {e}")
        
        # Load local model if specified and dependencies are available
        if settings.hf_model_name and TRANSFORMERS_AVAILABLE and TORCH_AVAILABLE:
            self._load_local_model()
    
    def _load_local_model(self):
        """Load a local Hugging Face model."""
        if not TRANSFORMERS_AVAILABLE or not TORCH_AVAILABLE:
            logger.error("Cannot load local model: transformers or torch not available")
            return
            
        try:
            logger.info(f"Loading local model: {settings.hf_model_name}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(settings.hf_model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                settings.hf_model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            
            # Create pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_length=2048,
                temperature=0.7,
                do_sample=True
            )
            
            logger.info("Local model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load local model: {e}")
    
    async def generate_text(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        max_length: int = 2048,
        temperature: float = 0.7,
        use_local: bool = False
    ) -> str:
        """Generate text using Hugging Face models."""
        try:
            if use_local and self.pipeline and TRANSFORMERS_AVAILABLE:
                # Use local model
                result = self.pipeline(
                    prompt,
                    max_length=max_length,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                return result[0]['generated_text']
            
            elif self.client and model_name and HUGGINGFACE_HUB_AVAILABLE:
                # Use Hugging Face Inference API
                result = self.client.text_generation(
                    prompt,
                    model=model_name,
                    max_new_tokens=max_length,
                    temperature=temperature,
                    do_sample=True
                )
                return result
            
            else:
                raise Exception("No model available. Please configure HF_API_TOKEN or HF_MODEL_NAME, or install required dependencies")
                
        except Exception as e:
            logger.error(f"Hugging Face text generation error: {e}")
            raise
    
    async def create_embedding(
        self,
        text: str,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ) -> List[float]:
        """Create embedding using Hugging Face models."""
        try:
            if self.client:
                # Use Hugging Face Inference API
                result = self.client.feature_extraction(
                    text,
                    model=model_name
                )
                return result[0] if isinstance(result, list) else result
            else:
                raise Exception("Hugging Face client not initialized")
                
        except Exception as e:
            logger.error(f"Hugging Face embedding error: {e}")
            raise Exception(f"Failed to create embedding: {str(e)}")
    
    async def classify_text(
        self,
        text: str,
        model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"
    ) -> Dict[str, Any]:
        """Classify text using Hugging Face models."""
        try:
            if self.client:
                result = self.client.text_classification(
                    text,
                    model=model_name
                )
                return result
            else:
                raise Exception("Hugging Face client not initialized")
                
        except Exception as e:
            logger.error(f"Hugging Face classification error: {e}")
            raise Exception(f"Failed to classify text: {str(e)}")
    
    async def translate_text(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "es",
        model_name: str = "Helsinki-NLP/opus-mt-en-es"
    ) -> str:
        """Translate text using Hugging Face models."""
        try:
            if self.client:
                result = self.client.translation(
                    text,
                    model=model_name
                )
                return result
            else:
                raise Exception("Hugging Face client not initialized")
                
        except Exception as e:
            logger.error(f"Hugging Face translation error: {e}")
            raise Exception(f"Failed to translate text: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """Get list of available models for the service."""
        models = []
        
        if self.client and HUGGINGFACE_HUB_AVAILABLE:
            models.append("Hugging Face Inference API (remote)")
        
        if self.pipeline and TRANSFORMERS_AVAILABLE:
            models.append(f"Local model: {settings.hf_model_name}")
        
        return models
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status and configuration."""
        return {
            "client_initialized": self.client is not None,
            "local_model_loaded": self.pipeline is not None,
            "local_model_name": settings.hf_model_name if self.pipeline else None,
            "api_token_configured": bool(settings.hf_api_token),
            "available_models": self.get_available_models()
        } 