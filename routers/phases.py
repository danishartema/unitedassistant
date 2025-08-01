"""
Phase management router for the 14-phase workflow system.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_db
from models import User, Project, Phase, PhaseDraft, PhaseStatus
from schemas import (
    PhaseResponse, PhaseUpdate, PhaseGenerateRequest, PhaseGenerateResponse,
    PhaseDraftResponse, APIResponse
)
from dependencies import get_current_active_user, check_project_access
from services.phase_service import PhaseService
from services.rag_service import RAGService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/projects/{project_id}/phases", response_model=List[PhaseResponse])
async def get_project_phases(
    project_id: str,
    project: Project = Depends(check_project_access),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all phases for a project (async)."""
    result = await db.execute(select(Phase).where(Phase.project_id == project_id).order_by(Phase.phase_number))
    phases = result.scalars().all()
    return phases


@router.get("/projects/{project_id}/phases/{phase_number}", response_model=PhaseResponse)
async def get_phase(
    project_id: str,
    phase_number: int,
    project: Project = Depends(check_project_access),
    db: AsyncSession = Depends(get_async_db)
):
    """Get a specific phase."""
    if not (1 <= phase_number <= 14):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phase number must be between 1 and 14"
        )
    
    result = await db.execute(select(Phase).where(Phase.project_id == project_id, Phase.phase_number == phase_number))
    phase = result.scalar_one_or_none()
    
    if not phase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phase not found"
        )
    
    return phase


@router.put("/projects/{project_id}/phases/{phase_number}", response_model=PhaseResponse)
async def update_phase(
    project_id: str,
    phase_number: int,
    phase_data: PhaseUpdate,
    project: Project = Depends(check_project_access),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Update a phase."""
    if not (1 <= phase_number <= 14):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phase number must be between 1 and 14"
        )
    
    # Get phase
    result = await db.execute(select(Phase).where(Phase.project_id == project_id, Phase.phase_number == phase_number))
    phase = result.scalar_one_or_none()
    
    if not phase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phase not found"
        )
    
    # Save current state as draft if there's content
    if phase.ai_response and phase.user_input:
        await PhaseService.save_draft(db, phase.id, phase.user_input, phase.ai_response)
    
    # Update phase
    update_data = {}
    if phase_data.title is not None:
        update_data["title"] = phase_data.title
    if phase_data.description is not None:
        update_data["description"] = phase_data.description
    if phase_data.user_input is not None:
        update_data["user_input"] = phase_data.user_input
    if phase_data.prompt_template is not None:
        update_data["prompt_template"] = phase_data.prompt_template
    
    if update_data:
        await db.execute(
            update(Phase)
            .where(Phase.id == phase.id)
            .values(**update_data)
        )
        
        # Mark subsequent phases as stale if this phase was completed
        if phase.status == PhaseStatus.COMPLETED:
            await PhaseService.mark_subsequent_phases_stale(db, project_id, phase_number)
    
    await db.commit()
    
    # Return updated phase
    result = await db.execute(
        select(Phase)
        .where(Phase.id == phase.id)
    )
    updated_phase = result.scalar_one()
    
    logger.info(f"Phase {phase_number} updated in project {project_id} by {current_user.email}")
    
    return updated_phase


@router.post("/projects/{project_id}/phases/{phase_number}/generate", response_model=PhaseGenerateResponse)
async def generate_phase_content(
    project_id: str,
    phase_number: int,
    request: PhaseGenerateRequest,
    project: Project = Depends(check_project_access),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Generate AI content for a phase."""
    if not (1 <= phase_number <= 14):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phase number must be between 1 and 14"
        )
    
    # Get phase
    result = await db.execute(select(Phase).where(Phase.project_id == project_id, Phase.phase_number == phase_number))
    phase = result.scalar_one_or_none()
    
    if not phase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phase not found"
        )
    
    try:
        # Save current state as draft if there's content
        if phase.ai_response and phase.user_input:
            # TODO: Implement sync version of save_draft
            pass
        
        # Generate content using PhaseService
        ai_response, context_used = await PhaseService.generate_content(
            db, phase, request.user_input, request.use_rag, request.temperature
        )
        
        # Update phase
        await db.execute(
            update(Phase)
            .where(Phase.id == phase.id)
            .values(
                user_input=request.user_input,
                ai_response=ai_response,
                status=PhaseStatus.COMPLETED
            )
        )
        
        # Create embedding for RAG
        if request.use_rag:
            await RAGService.create_embedding(db, phase.id, ai_response)
        
        # Mark subsequent phases as stale
        await PhaseService.mark_subsequent_phases_stale(db, project_id, phase_number)
        
        await db.commit()
        
        logger.info(f"Content generated for phase {phase_number} in project {project_id}")
        
        return PhaseGenerateResponse(
            phase_id=phase.id,
            ai_response=ai_response,
            status=PhaseStatus.COMPLETED,
            context_used=context_used
        )
        
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate content: {str(e)}"
        )


@router.post("/projects/{project_id}/phases/{phase_number}/reconstruct-context", response_model=PhaseGenerateResponse)
async def reconstruct_phase_context(
    project_id: str,
    phase_number: int,
    project: Project = Depends(check_project_access),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Reconstruct context for a phase and regenerate content."""
    if not (1 <= phase_number <= 14):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phase number must be between 1 and 14"
        )
    
    # Get phase
    result = await db.execute(select(Phase).where(Phase.project_id == project_id, Phase.phase_number == phase_number))
    phase = result.scalar_one_or_none()
    
    if not phase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phase not found"
        )
    
    if not phase.user_input:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phase has no user input to reconstruct from"
        )
    
    try:
        # Save current state as draft
        if phase.ai_response:
            await PhaseService.save_draft(db, phase.id, phase.user_input, phase.ai_response)
        
        # Reconstruct context and regenerate
        ai_response, context_used = await PhaseService.generate_content(
            db, phase, phase.user_input, use_rag=True, temperature=0.7
        )
        
        # Update phase
        await db.execute(
            update(Phase)
            .where(Phase.id == phase.id)
            .values(
                ai_response=ai_response,
                status=PhaseStatus.COMPLETED
            )
        )
        
        # Update embedding
        await RAGService.create_embedding(db, phase.id, ai_response)
        
        await db.commit()
        
        logger.info(f"Context reconstructed for phase {phase_number} in project {project_id}")
        
        return PhaseGenerateResponse(
            phase_id=phase.id,
            ai_response=ai_response,
            status=PhaseStatus.COMPLETED,
            context_used=context_used
        )
        
    except Exception as e:
        logger.error(f"Error reconstructing context: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reconstruct context: {str(e)}"
        )


@router.get("/projects/{project_id}/phases/{phase_number}/drafts", response_model=List[PhaseDraftResponse])
async def get_phase_drafts(
    project_id: str,
    phase_number: int,
    project: Project = Depends(check_project_access),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all drafts for a phase."""
    # Get phase
    result = await db.execute(select(Phase).where(Phase.project_id == project_id, Phase.phase_number == phase_number))
    phase = result.scalar_one_or_none()
    
    if not phase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phase not found"
        )
    
    # Get drafts
    drafts_result = await db.execute(
        select(PhaseDraft)
        .where(PhaseDraft.phase_id == phase.id)
        .order_by(PhaseDraft.version.desc())
    )
    drafts = drafts_result.scalars().all()
    
    return drafts


@router.post("/projects/{project_id}/phases/{phase_number}/drafts/{version}/restore", response_model=PhaseResponse)
async def restore_phase_draft(
    project_id: str,
    phase_number: int,
    version: int,
    project: Project = Depends(check_project_access),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Restore a phase from a specific draft version."""
    # Get phase
    result = await db.execute(select(Phase).where(Phase.project_id == project_id, Phase.phase_number == phase_number))
    phase = result.scalar_one_or_none()
    
    if not phase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phase not found"
        )
    
    # Get draft
    draft_result = await db.execute(
        select(PhaseDraft).where(
            PhaseDraft.phase_id == phase.id,
            PhaseDraft.version == version
        )
    )
    draft = draft_result.scalar_one_or_none()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found"
        )
    
    # Save current state as new draft
    if phase.ai_response and phase.user_input:
        await PhaseService.save_draft(db, phase.id, phase.user_input, phase.ai_response)
    
    # Restore from draft
    await db.execute(
        update(Phase)
        .where(Phase.id == phase.id)
        .values(
            user_input=draft.user_input,
            ai_response=draft.ai_response
        )
    )
    
    # Mark subsequent phases as stale
    await PhaseService.mark_subsequent_phases_stale(db, project_id, phase_number)
    
    await db.commit()
    
    # Return updated phase
    result = await db.execute(
        select(Phase)
        .where(Phase.id == phase.id)
    )
    updated_phase = result.scalar_one()
    
    logger.info(f"Phase {phase_number} restored to version {version} in project {project_id}")
    
    return updated_phase
