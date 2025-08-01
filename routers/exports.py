"""
Export router for async document generation and downloads.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
import logging

from database import get_async_db
from models import User, Project, ExportTask, ExportStatus
from schemas import ExportRequest, ExportTaskResponse, APIResponse
from dependencies import get_current_active_user, check_project_access
from tasks.export_tasks import generate_export
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/projects/{project_id}/export", response_model=ExportTaskResponse)
async def create_export_task(
    project_id: str,
    export_request: ExportRequest,
    project: Project = Depends(check_project_access),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Create an export task for a project (async)."""
    # Create export task
    export_task = ExportTask(
        project_id=project_id,
        user_id=current_user.id,
        format=export_request.format,
        status=ExportStatus.PENDING
    )
    
    db.add(export_task)
    await db.commit()
    await db.refresh(export_task)
    
    # Try to start background task, fallback to immediate processing if Redis unavailable
    try:
        from tasks.celery_app import celery_app
        celery_task = celery_app.send_task('tasks.export_tasks.generate_export', args=[export_task.id])
        
        # Update with Celery task ID
        export_task.celery_task_id = celery_task.id
        await db.commit()
        
        logger.info(f"Export task created: {export_task.id} for project {project_id}")
        
        return export_task
        
    except Exception as e:
        logger.warning(f"Redis/Celery unavailable, processing export immediately: {e}")
        
        # Fallback: Process export immediately
        try:
            from tasks.export_tasks import generate_export
            await generate_export(export_task.id)
            
            # Refresh the task to get updated status
            await db.refresh(export_task)
            
            logger.info(f"Export completed immediately: {export_task.id} for project {project_id}")
            return export_task
            
        except Exception as export_error:
            logger.error(f"Export processing failed: {export_error}")
            export_task.status = ExportStatus.FAILED
            export_task.error_message = f"Export processing failed: {str(export_error)}"
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process export"
            )


@router.get("/projects/{project_id}/exports", response_model=List[ExportTaskResponse])
async def get_project_exports(
    project_id: str,
    project: Project = Depends(check_project_access),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all export tasks for a project."""
    result = await db.execute(
        select(ExportTask)
        .where(ExportTask.project_id == project_id)
        .order_by(ExportTask.created_at.desc())
    )
    export_tasks = result.scalars().all()
    
    return export_tasks


@router.get("/exports/{export_id}", response_model=ExportTaskResponse)
async def get_export_status(
    export_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get status of an export task."""
    result = await db.execute(
        select(ExportTask).where(ExportTask.id == export_id)
    )
    export_task = result.scalar_one_or_none()
    
    if not export_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export task not found"
        )
    
    # Check if user has access to this export
    if export_task.user_id != current_user.id:
        # Check if user has access to the project
        project_result = await db.execute(
            select(Project).where(Project.id == export_task.project_id)
        )
        project = project_result.scalar_one_or_none()
        
        if not project or project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this export"
            )
    
    return export_task


@router.get("/exports/{export_id}/download")
async def download_export(
    export_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Download a completed export file."""
    result = await db.execute(
        select(ExportTask).where(ExportTask.id == export_id)
    )
    export_task = result.scalar_one_or_none()
    
    if not export_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export task not found"
        )
    
    # Check if user has access to this export
    if export_task.user_id != current_user.id:
        # Check if user has access to the project
        project_result = await db.execute(
            select(Project).where(Project.id == export_task.project_id)
        )
        project = project_result.scalar_one_or_none()
        
        if not project or project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this export"
            )
    
    if export_task.status != ExportStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Export is not completed yet"
        )
    
    if not export_task.file_path or not os.path.exists(export_task.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export file not found"
        )
    
    # Determine filename based on format
    filename = f"project_export_{export_task.project_id}.{export_task.format.value}"
    
    return FileResponse(
        export_task.file_path,
        filename=filename,
        media_type='application/octet-stream'
    )


@router.delete("/exports/{export_id}", response_model=APIResponse)
async def delete_export(
    export_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Delete an export task and its associated file."""
    result = await db.execute(
        select(ExportTask).where(ExportTask.id == export_id)
    )
    export_task = result.scalar_one_or_none()
    
    if not export_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export task not found"
        )
    
    # Check if user has access to this export
    if export_task.user_id != current_user.id:
        # Check if user has access to the project
        project_result = await db.execute(
            select(Project).where(Project.id == export_task.project_id)
        )
        project = project_result.scalar_one_or_none()
        
        if not project or project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this export"
            )
    
    # Delete associated file if it exists
    if export_task.file_path and os.path.exists(export_task.file_path):
        try:
            os.remove(export_task.file_path)
        except Exception as e:
            logger.warning(f"Failed to delete export file {export_task.file_path}: {e}")
    
    # Delete the export task
    await db.delete(export_task)
    await db.commit()
    
    logger.info(f"Export task deleted: {export_id} by {current_user.email}")
    return APIResponse(success=True, message="Export task deleted successfully")
