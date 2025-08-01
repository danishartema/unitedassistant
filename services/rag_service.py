"""
RAG (Retrieval Augmented Generation) service for semantic search and context retrieval.
"""
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import logging

from models import Phase, PhaseEmbedding
from services.openai_service import openai_service

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG functionality with semantic search."""
    
    @staticmethod
    async def create_embedding(db: AsyncSession, phase_id: str, content: str) -> PhaseEmbedding:
        """Create and store embedding for phase content."""
        try:
            # Generate embedding
            embedding_vector = await openai_service.create_embedding(content)
            
            # Check if embedding already exists for this phase
            existing_result = await db.execute(
                select(PhaseEmbedding).where(PhaseEmbedding.phase_id == phase_id)
            )
            existing_embedding = existing_result.scalar_one_or_none()
            
            if existing_embedding:
                # Update existing embedding
                existing_embedding.content = content
                existing_embedding.embedding = embedding_vector
                await db.commit()
                return existing_embedding
            else:
                # Create new embedding
                phase_embedding = PhaseEmbedding(
                    phase_id=phase_id,
                    content=content,
                    embedding=embedding_vector
                )
                
                db.add(phase_embedding)
                await db.commit()
                await db.refresh(phase_embedding)
                
                logger.info(f"Created embedding for phase {phase_id}")
                return phase_embedding
                
        except Exception as e:
            logger.error(f"Failed to create embedding: {e}")
            raise Exception(f"Failed to create embedding: {str(e)}")
    
    @staticmethod
    async def search_similar_content(
        db: AsyncSession,
        query: str,
        project_id: str,
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Tuple[Phase, float]]:
        """Search for similar content using semantic similarity."""
        try:
            # Generate query embedding
            query_embedding = await openai_service.create_embedding(query)
            
            # Perform similarity search using pgvector
            # Note: Using cosine distance (1 - cosine_similarity)
            search_query = text("""
                SELECT p.*, pe.content, (1 - (pe.embedding <=> :query_embedding)) as similarity
                FROM phases p
                JOIN phase_embeddings pe ON p.id = pe.phase_id
                WHERE p.project_id = :project_id
                AND (1 - (pe.embedding <=> :query_embedding)) > :threshold
                ORDER BY similarity DESC
                LIMIT :limit
            """)
            
            result = await db.execute(
                search_query,
                {
                    "query_embedding": query_embedding,
                    "project_id": project_id,
                    "threshold": similarity_threshold,
                    "limit": limit
                }
            )
            
            # Process results
            similar_phases = []
            for row in result:
                # Get the full phase object
                phase_result = await db.execute(
                    select(Phase).where(Phase.id == row.id)
                )
                phase = phase_result.scalar_one()
                similarity = row.similarity
                
                similar_phases.append((phase, similarity))
            
            logger.info(f"Found {len(similar_phases)} similar phases for query in project {project_id}")
            return similar_phases
            
        except Exception as e:
            logger.error(f"Similarity search error: {e}")
            # Return empty results instead of raising exception
            return []
    
    @staticmethod
    async def get_context_for_phase(
        db: AsyncSession,
        project_id: str,
        current_phase_number: int,
        user_input: str
    ) -> Tuple[str, List[str]]:
        """Get relevant context for a phase using RAG and previous phases."""
        try:
            context_parts = []
            context_sources = []
            
            # 1. Get previous phases in order (sequential context)
            previous_phases_result = await db.execute(
                select(Phase)
                .where(
                    Phase.project_id == project_id,
                    Phase.phase_number < current_phase_number,
                    Phase.ai_response.isnot(None)
                )
                .order_by(Phase.phase_number)
            )
            previous_phases = previous_phases_result.scalars().all()
            
            # Add sequential context from previous phases
            for phase in previous_phases[-3:]:  # Last 3 phases for immediate context
                if phase.ai_response:
                    context_parts.append(f"Phase {phase.phase_number} ({phase.title}):\n{phase.ai_response}")
                    context_sources.append(f"Phase {phase.phase_number}")
            
            # 2. Get semantically similar content using RAG
            similar_phases = await RAGService.search_similar_content(
                db, user_input, project_id, limit=3, similarity_threshold=0.6
            )
            
            # Add RAG context (avoid duplicates from sequential context)
            added_phases = {p.phase_number for p in previous_phases[-3:]}
            for phase, similarity in similar_phases:
                if phase.phase_number not in added_phases and phase.ai_response:
                    context_parts.append(
                        f"Related content from Phase {phase.phase_number} ({phase.title}) [similarity: {similarity:.2f}]:\n{phase.ai_response}"
                    )
                    context_sources.append(f"Phase {phase.phase_number} (RAG)")
                    added_phases.add(phase.phase_number)
            
            # Combine context
            full_context = "\n\n---\n\n".join(context_parts)
            
            # Truncate if too long (rough token limit)
            if len(full_context) > 6000:
                full_context = full_context[:6000] + "... [context truncated]"
            
            logger.info(f"Built context for phase {current_phase_number} with {len(context_sources)} sources")
            return full_context, context_sources
            
        except Exception as e:
            logger.error(f"Context building error: {e}")
            return "", []
    
    @staticmethod
    async def update_all_embeddings(db: AsyncSession, project_id: str):
        """Update embeddings for all phases in a project."""
        try:
            # Get all phases with content
            phases_result = await db.execute(
                select(Phase)
                .where(
                    Phase.project_id == project_id,
                    Phase.ai_response.isnot(None)
                )
            )
            phases = phases_result.scalars().all()
            
            for phase in phases:
                if phase.ai_response:
                    await RAGService.create_embedding(db, phase.id, phase.ai_response)
            
            logger.info(f"Updated embeddings for {len(phases)} phases in project {project_id}")
            
        except Exception as e:
            logger.error(f"Failed to update embeddings: {e}")
            raise Exception(f"Failed to update embeddings: {str(e)}")
