"""
Celery tasks for document export functionality.
"""
import asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import logging
import os
import json
from docx import Document
from docx.shared import Inches

from tasks.celery_app import celery_app
from database import AsyncSessionLocal
from models import ExportTask, Project, Phase, ExportStatus, ExportFormat
from services.export_service import ExportService

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def generate_export(self, export_task_id: str):
    """Generate export file for a project."""
    try:
        # Run async function in event loop
        return asyncio.run(_generate_export_async(export_task_id, self.request.id))
    except Exception as e:
        logger.error(f"Export task {export_task_id} failed: {e}")
        # Update task status to failed
        asyncio.run(_mark_export_failed(export_task_id, str(e)))
        raise


async def generate_export(export_task_id: str):
    """Simple export function that can be called directly without Celery."""
    try:
        return await _generate_export_async(export_task_id, None)
    except Exception as e:
        logger.error(f"Export task {export_task_id} failed: {e}")
        await _mark_export_failed(export_task_id, str(e))
        raise


async def _generate_export_async(export_task_id: str, celery_task_id: str = None):
    """Async function to generate export."""
    async with AsyncSessionLocal() as db:
        try:
            # Get export task
            result = await db.execute(
                select(ExportTask).where(ExportTask.id == export_task_id)
            )
            export_task = result.scalar_one_or_none()
            
            if not export_task:
                raise Exception("Export task not found")
            
            # Update status to in progress
            await db.execute(
                update(ExportTask)
                .where(ExportTask.id == export_task_id)
                .values(
                    status=ExportStatus.IN_PROGRESS,
                    celery_task_id=celery_task_id
                )
            )
            await db.commit()
            
            # Get project data manually to avoid selectinload issues
            project_result = await db.execute(
                select(Project).where(Project.id == export_task.project_id)
            )
            project = project_result.scalar_one()
            
            if not project:
                raise Exception("Project not found")
            
            # Get project owner
            owner_result = await db.execute(
                select(Project.owner).where(Project.id == project.id)
            )
            owner = owner_result.scalar_one_or_none()
            
            # Get project phases
            phases_result = await db.execute(
                select(Phase).where(Phase.project_id == project.id).order_by(Phase.phase_number)
            )
            phases = phases_result.scalars().all()
            
            # Get drafts for each phase
            for phase in phases:
                drafts_result = await db.execute(
                    select(Phase.drafts).where(Phase.id == phase.id)
                )
                phase.drafts = drafts_result.scalars().all()
            
            # Prepare project data for export
            project_data = await _prepare_project_data(project, owner, phases)
            
            # Generate file path
            file_path = ExportService.get_export_file_path(
                export_task_id, 
                export_task.format.value
            )
            
            # Export based on format
            if export_task.format == ExportFormat.PDF:
                await ExportService.export_to_pdf(project_data, file_path)
            elif export_task.format == ExportFormat.WORD:
                await ExportService.export_to_word(project_data, file_path)
            elif export_task.format == ExportFormat.JSON:
                await ExportService.export_to_json(project_data, file_path)
            else:
                raise Exception(f"Unsupported export format: {export_task.format}")
            
            # Update task as completed
            await db.execute(
                update(ExportTask)
                .where(ExportTask.id == export_task_id)
                .values(
                    status=ExportStatus.COMPLETED,
                    file_path=file_path,
                    completed_at=datetime.now(timezone.utc)
                )
            )
            await db.commit()
            
            logger.info(f"Export task {export_task_id} completed successfully")
            return {"status": "completed", "file_path": file_path}
            
        except Exception as e:
            logger.error(f"Export generation error: {e}")
            await _mark_export_failed_in_session(db, export_task_id, str(e))
            raise


async def _prepare_project_data(project: Project, owner, phases) -> dict:
    """Prepare project data for export."""
    # Sort phases by phase number
    sorted_phases = sorted(phases, key=lambda p: p.phase_number)
    
    # Prepare phases data
    phases_data = []
    for phase in sorted_phases:
        phase_data = {
            "phase_number": phase.phase_number,
            "title": phase.title,
            "description": phase.description,
            "user_input": phase.user_input,
            "ai_response": phase.ai_response,
            "status": phase.status.value,
            "created_at": phase.created_at.isoformat() if phase.created_at else None,
            "updated_at": phase.updated_at.isoformat() if phase.updated_at else None,
            "drafts": [
                {
                    "version": draft.version,
                    "content": draft.content,
                    "created_at": draft.created_at.isoformat() if draft.created_at else None
                }
                for draft in sorted(phase.drafts, key=lambda d: d.version, reverse=True)
            ]
        }
        phases_data.append(phase_data)
    
    # Prepare project data
    project_data = {
        "id": project.id,
        "title": project.title,
        "description": project.description,
        "created_at": project.created_at.isoformat() if project.created_at else None,
        "updated_at": project.updated_at.isoformat() if project.updated_at else None,
        "owner": {
            "id": owner.id,
            "full_name": owner.full_name,
            "email": owner.email
        } if owner else None,
        "phases": phases_data,
        "total_phases": len(phases_data),
        "completed_phases": len([p for p in phases_data if p["status"] == "completed"])
    }
    
    return project_data


async def _mark_export_failed(export_task_id: str, error_message: str):
    """Mark export task as failed."""
    async with AsyncSessionLocal() as db:
        await _mark_export_failed_in_session(db, export_task_id, error_message)


async def _mark_export_failed_in_session(db: AsyncSession, export_task_id: str, error_message: str):
    """Mark export task as failed within existing session."""
    try:
        await db.execute(
            update(ExportTask)
            .where(ExportTask.id == export_task_id)
            .values(
                status=ExportStatus.FAILED,
                error_message=error_message,
                completed_at=datetime.now(timezone.utc)
            )
        )
        await db.commit()
    except Exception as e:
        logger.error(f"Failed to mark export as failed: {e}")
