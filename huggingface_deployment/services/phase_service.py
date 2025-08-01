"""
Phase service for managing the 14-phase workflow system.
"""
from typing import Tuple, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timezone
import logging

from models import Phase, PhaseDraft, PhaseStatus
from services.openai_service import openai_service
from services.rag_service import RAGService

logger = logging.getLogger(__name__)


class PhaseService:
    """Service for phase management and content generation."""
    
    @staticmethod
    async def generate_content(
        db: AsyncSession,
        phase: Phase,
        user_input: str,
        use_rag: bool = True,
        temperature: float = 0.7
    ) -> Tuple[str, List[str]]:
        """Generate AI content for a phase with context."""
        try:
            # Build context using RAG if enabled
            context = ""
            context_sources = []
            
            if use_rag:
                context, context_sources = await RAGService.get_context_for_phase(
                    db, phase.project_id, phase.phase_number, user_input
                )
            
            # Build prompt
            prompt = await PhaseService._build_prompt(phase, user_input, context)
            
            # Generate content
            ai_response = await openai_service.generate_content(
                prompt=prompt,
                context=context,
                temperature=temperature
            )
            
            logger.info(f"Generated content for phase {phase.phase_number} in project {phase.project_id}")
            return ai_response, context_sources
            
        except Exception as e:
            logger.error(f"Content generation error: {e}")
            raise Exception(f"Failed to generate content: {str(e)}")
    
    @staticmethod
    async def _build_prompt(phase: Phase, user_input: str, context: str) -> str:
        """Build prompt for content generation."""
        # Base prompt template
        if phase.prompt_template:
            prompt = phase.prompt_template
        else:
            prompt = f"""
Phase {phase.phase_number}: {phase.title}

{phase.description or ""}

Please provide a comprehensive response based on the user's input.
"""
        
        # Add user input
        prompt += f"\n\nUser Input:\n{user_input}"
        
        # Add context if available
        if context:
            prompt += f"\n\nRelevant Context from Previous Phases:\n{context}"
        
        prompt += "\n\nPlease provide a detailed, professional response that builds upon the context and addresses the user's input:"
        
        return prompt
    
    @staticmethod
    async def save_draft(
        db: AsyncSession,
        phase_id: str,
        user_input: str,
        ai_response: str
    ) -> PhaseDraft:
        """Save a draft version of phase content."""
        try:
            # Get current highest version number
            version_result = await db.execute(
                select(PhaseDraft.version)
                .where(PhaseDraft.phase_id == phase_id)
                .order_by(PhaseDraft.version.desc())
                .limit(1)
            )
            current_version = version_result.scalar_one_or_none()
            next_version = (current_version or 0) + 1
            
            # Create draft
            draft = PhaseDraft(
                phase_id=phase_id,
                version=next_version,
                content=f"User Input: {user_input}\n\nAI Response: {ai_response}",
                user_input=user_input,
                ai_response=ai_response
            )
            
            db.add(draft)
            await db.commit()
            await db.refresh(draft)
            
            logger.info(f"Saved draft version {next_version} for phase {phase_id}")
            return draft
            
        except Exception as e:
            logger.error(f"Failed to save draft: {e}")
            raise Exception(f"Failed to save draft: {str(e)}")
    
    @staticmethod
    async def mark_subsequent_phases_stale(
        db: AsyncSession,
        project_id: str,
        current_phase_number: int
    ):
        """Mark all subsequent phases as stale when a phase is updated."""
        try:
            await db.execute(
                update(Phase)
                .where(
                    Phase.project_id == project_id,
                    Phase.phase_number > current_phase_number,
                    Phase.status == PhaseStatus.COMPLETED
                )
                .values(status=PhaseStatus.STALE)
            )
            
            logger.info(f"Marked phases {current_phase_number + 1}+ as stale in project {project_id}")
            
        except Exception as e:
            logger.error(f"Failed to mark phases as stale: {e}")
            raise Exception(f"Failed to mark phases as stale: {str(e)}")
    
    @staticmethod
    async def get_phase_dependencies(
        db: AsyncSession,
        project_id: str,
        phase_number: int
    ) -> List[Phase]:
        """Get phases that the current phase depends on."""
        try:
            # For now, assume linear dependency (each phase depends on all previous phases)
            # This can be enhanced with more complex dependency mapping
            result = await db.execute(
                select(Phase)
                .where(
                    Phase.project_id == project_id,
                    Phase.phase_number < phase_number,
                    Phase.status == PhaseStatus.COMPLETED
                )
                .order_by(Phase.phase_number)
            )
            
            return list(result.scalars().all())
            
        except Exception as e:
            logger.error(f"Failed to get phase dependencies: {e}")
            return []
    
    @staticmethod
    async def validate_phase_progression(
        db: AsyncSession,
        project_id: str,
        phase_number: int
    ) -> bool:
        """Validate that prerequisites for a phase are met."""
        try:
            # Check if previous phase is completed (simple linear validation)
            if phase_number > 1:
                prev_phase_result = await db.execute(
                    select(Phase)
                    .where(
                        Phase.project_id == project_id,
                        Phase.phase_number == phase_number - 1
                    )
                )
                prev_phase = prev_phase_result.scalar_one_or_none()
                
                if not prev_phase or prev_phase.status != PhaseStatus.COMPLETED:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Phase validation error: {e}")
            return False
    
    @staticmethod
    async def get_project_progress(db: AsyncSession, project_id: str) -> dict:
        """Get overall project progress statistics."""
        try:
            # Get all phases for the project
            phases_result = await db.execute(
                select(Phase).where(Phase.project_id == project_id)
            )
            phases = phases_result.scalars().all()
            
            # Calculate statistics
            total_phases = len(phases)
            completed_phases = len([p for p in phases if p.status == PhaseStatus.COMPLETED])
            stale_phases = len([p for p in phases if p.status == PhaseStatus.STALE])
            in_progress_phases = len([p for p in phases if p.status == PhaseStatus.IN_PROGRESS])
            
            progress_percentage = (completed_phases / total_phases * 100) if total_phases > 0 else 0
            
            return {
                "total_phases": total_phases,
                "completed_phases": completed_phases,
                "stale_phases": stale_phases,
                "in_progress_phases": in_progress_phases,
                "progress_percentage": round(progress_percentage, 2),
                "current_phase": completed_phases + 1 if completed_phases < total_phases else total_phases
            }
            
        except Exception as e:
            logger.error(f"Failed to get project progress: {e}")
            return {
                "total_phases": 0,
                "completed_phases": 0,
                "stale_phases": 0,
                "in_progress_phases": 0,
                "progress_percentage": 0,
                "current_phase": 1
            }
