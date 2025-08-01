"""
OpenAI service for content generation and embeddings.
"""
import json
import os
from typing import List, Tuple
from openai import OpenAI
import logging

from config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for OpenAI API interactions."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    async def generate_content(
        self,
        prompt: str,
        context: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """Generate content using OpenAI GPT model."""
        try:
            # Build system message
            system_message = """You are an expert AI assistant helping users create comprehensive documents through a 14-phase structured workflow. 

Your responses should be:
- Professional and well-structured
- Comprehensive yet concise
- Tailored to the specific phase and user input
- Building upon previous phases when context is provided

Always provide actionable, detailed content that helps move the document creation process forward."""

            # Build user message
            user_message = prompt
            if context:
                user_message = f"Context from previous phases:\n{context}\n\nCurrent phase request:\n{prompt}"
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else ""
            
        except Exception as e:
            logger.error(f"OpenAI content generation error: {e}")
            raise Exception(f"Failed to generate content: {str(e)}")
    
    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding for text using OpenAI embedding model."""
        try:
            # Clean and truncate text if necessary
            cleaned_text = text.strip()
            if len(cleaned_text) > 8000:  # Rough token limit
                cleaned_text = cleaned_text[:8000]
            
            response = self.client.embeddings.create(
                model=settings.embedding_model,
                input=cleaned_text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            raise Exception(f"Failed to create embedding: {str(e)}")
    
    async def analyze_content_structure(self, content: str) -> dict:
        """Analyze content structure and extract key information."""
        try:
            prompt = f"""Analyze the following content and extract key information in JSON format:

Content:
{content}

Provide analysis in this JSON format:
{{
    "key_points": ["point1", "point2", "point3"],
    "topics": ["topic1", "topic2"],
    "complexity_level": "low|medium|high",
    "word_count": number,
    "summary": "brief summary"
}}"""

            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            response_content = response.choices[0].message.content
            return json.loads(response_content) if response_content else {}
            
        except Exception as e:
            logger.error(f"Content analysis error: {e}")
            return {
                "key_points": [],
                "topics": [],
                "complexity_level": "medium",
                "word_count": len(content.split()),
                "summary": "Analysis failed"
            }


# Global instance
openai_service = OpenAIService()
