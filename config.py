"""
Configuration settings for the application.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""
    
    # Database - PostgreSQL/Supabase only
    database_url: str = Field(
        default="", 
        alias="DATABASE_URL"
    )
    
    # Supabase specific settings (for production)
    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_key: str = Field(default="", alias="SUPABASE_KEY")
    supabase_db_url: str = Field(default="", alias="SUPABASE_DB_URL")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    
    # Security
    secret_key: str = Field(default="your-secret-key-change-in-production", alias="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # OpenAI (Primary AI Service)
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = "gpt-4o"  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
    embedding_model: str = "text-embedding-3-small"
    
    # AI Service Priority (openai, huggingface, or both)
    primary_ai_service: str = Field(default="openai", alias="PRIMARY_AI_SERVICE")
    
    # Application
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=7860, alias="PORT")
    
    # File storage
    upload_dir: str = Field(default="./uploads", alias="UPLOAD_DIR")
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # Hugging Face API Key
    hf_api_token: str = Field(default="", alias="HF_API_TOKEN")
    hf_model_name: str = Field(default="", alias="HF_MODEL_NAME")
    
    # Celery
    celery_broker_url: str = Field(default="redis://localhost:6379/1", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/2", alias="CELERY_RESULT_BACKEND")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() in ["production", "prod"]
    
    @property
    def is_huggingface_deployment(self) -> bool:
        """Check if running in Hugging Face deployment environment."""
        # Check for Hugging Face specific environment variables
        return (
            os.getenv("SPACE_ID") is not None or
            os.getenv("HF_HUB_ENDPOINT") is not None or
            os.getenv("HUGGING_FACE_HUB_TOKEN") is not None or
            self.is_production or
            bool(self.supabase_db_url) or
            bool(os.getenv("SUPABASE_DB_URL"))
        )
    
    @property
    def effective_database_url(self) -> str:
        """Get the effective database URL - Supabase only."""
        # If SUPABASE_DB_URL is set (either in settings or environment), use it
        supabase_db_url = self.supabase_db_url or os.getenv("SUPABASE_DB_URL")
        if supabase_db_url:
            return supabase_db_url
        
        # Always require Supabase
        supabase_db_url = os.getenv("SUPABASE_DB_URL")
        if supabase_db_url:
            return supabase_db_url
        else:
            # If no Supabase URL is available, raise an error
            raise ValueError(
                "SUPABASE_DB_URL environment variable is required. "
                "Please set it in your environment variables or Hugging Face Space secrets."
            )
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"  # Allow extra fields to be ignored
    }


settings = Settings()
