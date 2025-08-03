from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_async_db
from models import Project, GPTModeSession, ProjectMemory, ProjectSummary
from dependencies import get_current_active_user, check_project_access
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
import logging
from services.chatbot_service import chatbot_service

logger = logging.getLogger(__name__)
router = APIRouter()

class StartModeRequest(BaseModel):
    mode_name: str

class AnswerRequest(BaseModel):
    answer: str
    skip: bool = False  # Allow skipping questions

class SkipQuestionRequest(BaseModel):
    reason: Optional[str] = None

class ModuleTransitionRequest(BaseModel):
    confirm_completion: bool
    next_module_id: Optional[str] = None

class ChatMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class SummaryRequest(BaseModel):
    session_id: str

class EditSummaryRequest(BaseModel):
    session_id: str
    edited_summary: str

class ChatResponse(BaseModel):
    message: str
    session_id: str
    is_question: bool = False
    current_question: Optional[str] = None
    question_number: Optional[int] = None
    total_questions: Optional[int] = None
    module_complete: bool = False
    summary: Optional[str] = None

@router.get("/modes")
async def list_modes():
    """List all available assistant modes with enhanced information."""
    try:
        modules = chatbot_service.get_available_modules()
        return {
            "success": True,
            "modules": modules,
            "total_modules": len(modules)
        }
    except Exception as e:
        logger.error(f"Error listing modes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list modes: {str(e)}")

@router.get("/modules/{module_id}/info")
async def get_module_info(module_id: str):
    """Get detailed information about a specific module."""
    try:
        if module_id not in chatbot_service.modules:
            raise HTTPException(status_code=404, detail="Module not found")
        
        module = chatbot_service.modules[module_id]
        questions = chatbot_service.get_module_questions(module_id)
        
        return {
            "module_id": module_id,
            "name": module["name"],
            "description": module["description"],
            "question_count": len(questions),
            "questions": questions,
            "has_system_prompt": bool(module["system_prompt"]),
            "has_output_template": bool(module["output_template"]),
            "has_rag_content": bool(module["rag_content"])
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting module info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get module info: {str(e)}")

@router.post("/projects/{project_id}/modes/start")
async def start_mode_session(
    project_id: str,
    req: StartModeRequest,
    db: AsyncSession = Depends(get_async_db),
    user=Depends(get_current_active_user)
):
    """Start a new mode session for a project with enhanced chatbot functionality."""
    try:
        logger.info(f"Starting mode session for project {project_id}, mode {req.mode_name}")
        
        if db is None:
            logger.error("Database session is None!")
            raise HTTPException(status_code=500, detail="Database connection error")
        
        # Check project access
        result = await db.execute(select(Project).where(Project.id == project_id, Project.is_active == True))
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Find the module ID based on mode name
        module_id = None
        for mid, module in chatbot_service.modules.items():
            if module["name"] == req.mode_name:
                module_id = mid
                break
        
        if not module_id:
            raise HTTPException(status_code=404, detail=f"Mode '{req.mode_name}' not found")
        
        # Check for existing session
        result = await db.execute(select(GPTModeSession).where(GPTModeSession.project_id == project_id, GPTModeSession.mode_name == req.mode_name))
        session = result.scalar_one_or_none()
        if session:
            return {
                "session_id": session.id, 
                "current_question": session.current_question, 
                "answers": session.answers,
                "module_id": module_id,
                "module_info": chatbot_service.modules[module_id]
            }
        
        # Create new session
        new_session = GPTModeSession(
            id=str(uuid.uuid4()),
            project_id=project_id,
            mode_name=req.mode_name,
            current_question=0,
            answers={},
            checkpoint_json={}
        )
        
        logger.info(f"Adding new session to database: {new_session.id}")
        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)
        
        logger.info(f"Mode session created successfully: {new_session.id}")
        return {
            "session_id": new_session.id, 
            "current_question": 0, 
            "answers": {},
            "module_id": module_id,
            "module_info": chatbot_service.modules[module_id]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in start_mode_session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start mode session: {str(e)}")

@router.get("/projects/{project_id}/modes/{mode_name}/next-question")
async def get_next_question(
    project_id: str,
    mode_name: str,
    db: AsyncSession = Depends(get_async_db),
    user=Depends(get_current_active_user)
):
    """Get the next question for a mode session with enhanced chatbot functionality."""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection error")
            
        # Find the module ID
        module_id = None
        for mid, module in chatbot_service.modules.items():
            if module["name"] == mode_name:
                module_id = mid
                break
        
        if not module_id:
            raise HTTPException(status_code=404, detail=f"Mode '{mode_name}' not found")
        
        result = await db.execute(select(GPTModeSession).where(GPTModeSession.project_id == project_id, GPTModeSession.mode_name == mode_name))
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Mode session not found")
        
        # Get enhanced question from chatbot service
        question_data = await chatbot_service.get_next_question(
            module_id, 
            session.current_question, 
            session.answers
        )
        
        # Add module information
        question_data["module_id"] = module_id
        question_data["module_name"] = mode_name
        
        return question_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_next_question: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get next question: {str(e)}")

@router.post("/projects/{project_id}/modes/{mode_name}/answer")
async def submit_answer(
    project_id: str,
    mode_name: str,
    req: AnswerRequest,
    db: AsyncSession = Depends(get_async_db),
    user=Depends(get_current_active_user)
):
    """Submit an answer for a mode session with enhanced chatbot functionality and validation."""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection error")
        
        # Find the module ID
        module_id = None
        for mid, module in chatbot_service.modules.items():
            if module["name"] == mode_name:
                module_id = mid
                break
        
        if not module_id:
            raise HTTPException(status_code=404, detail=f"Mode '{mode_name}' not found")
            
        result = await db.execute(select(GPTModeSession).where(GPTModeSession.project_id == project_id, GPTModeSession.mode_name == mode_name))
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Mode session not found")
        
        # Check if module is complete
        is_complete = await chatbot_service.check_module_completion_ready(module_id, session.current_question)
        if is_complete:
            return {"done": True, "message": "All questions answered.", "module_complete": True}
        
        # Handle skip request
        if req.skip or not req.answer.strip():
            # Mark question as skipped
            session.answers[str(session.current_question)] = "[SKIPPED]"
            session.current_question += 1
            await db.commit()
            await db.refresh(session)
            
            # Check if module is now complete
            is_complete = await chatbot_service.check_module_completion_ready(module_id, session.current_question)
            if is_complete:
                return {"done": True, "message": "All questions answered.", "module_complete": True}
            
            # Get next question
            next_question_data = await chatbot_service.get_next_question(
                module_id, 
                session.current_question, 
                session.answers
            )
            
            next_question_data["module_id"] = module_id
            next_question_data["module_name"] = mode_name
            next_question_data["message"] = "Question skipped successfully. Here's the next question:"
            
            return next_question_data
        
        # Validate answer
        validation_result = chatbot_service.validate_answer(module_id, session.current_question, req.answer)
        if not validation_result["valid"]:
            return {
                "valid": False,
                "error": validation_result["message"],
                "question_number": session.current_question,
                "can_retry": True
            }
        
        # Store valid answer
        session.answers[str(session.current_question)] = req.answer
        session.current_question += 1
        await db.commit()
        await db.refresh(session)
        
        # Check if module is now complete
        is_complete = await chatbot_service.check_module_completion_ready(module_id, session.current_question)
        if is_complete:
            return {"done": True, "message": "All questions answered.", "module_complete": True}
        
        # Get next question
        next_question_data = await chatbot_service.get_next_question(
            module_id, 
            session.current_question, 
            session.answers
        )
        
        next_question_data["module_id"] = module_id
        next_question_data["module_name"] = mode_name
        next_question_data["message"] = "Answer submitted successfully. Here's the next question:"
        
        return next_question_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in submit_answer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to submit answer: {str(e)}")

@router.get("/projects/{project_id}/modes/{mode_name}/summary")
async def get_mode_summary(
    project_id: str,
    mode_name: str,
    db: AsyncSession = Depends(get_async_db),
    user=Depends(get_current_active_user)
):
    """Get comprehensive summary for a completed mode session."""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection error")
        
        # Find the module ID
        module_id = None
        for mid, module in chatbot_service.modules.items():
            if module["name"] == mode_name:
                module_id = mid
                break
        
        if not module_id:
            raise HTTPException(status_code=404, detail=f"Mode '{mode_name}' not found")
            
        result = await db.execute(select(GPTModeSession).where(GPTModeSession.project_id == project_id, GPTModeSession.mode_name == mode_name))
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Mode session not found")
        
        # Generate comprehensive summary (even if not all questions answered)
        summary_data = await chatbot_service.generate_module_summary(module_id, session.answers)
        
        # Update session with summary
        session.checkpoint_json = summary_data
        await db.commit()
        
        return summary_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_mode_summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get mode summary: {str(e)}")

@router.post("/projects/{project_id}/modes/{mode_name}/complete")
async def complete_module(
    project_id: str,
    mode_name: str,
    req: ModuleTransitionRequest,
    db: AsyncSession = Depends(get_async_db),
    user=Depends(get_current_active_user)
):
    """Complete a module and optionally transition to the next module."""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection error")
        
        # Find the module ID
        module_id = None
        for mid, module in chatbot_service.modules.items():
            if module["name"] == mode_name:
                module_id = mid
                break
        
        if not module_id:
            raise HTTPException(status_code=404, detail=f"Mode '{mode_name}' not found")
        
        result = await db.execute(select(GPTModeSession).where(GPTModeSession.project_id == project_id, GPTModeSession.mode_name == mode_name))
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Mode session not found")
        
        # Check if module is complete
        is_complete = await chatbot_service.check_module_completion_ready(module_id, session.current_question)
        if not is_complete:
            raise HTTPException(status_code=400, detail="Module not yet complete. Please answer all questions first.")
        
        # Generate summary if not already done
        if not session.checkpoint_json:
            summary_data = await chatbot_service.generate_module_summary(module_id, session.answers)
            session.checkpoint_json = summary_data
            await db.commit()
        
        # Get next module information
        next_module_id = chatbot_service.get_next_module(module_id)
        next_module_info = None
        if next_module_id:
            next_module_info = {
                "module_id": next_module_id,
                "name": chatbot_service.modules[next_module_id]["name"],
                "description": chatbot_service.modules[next_module_id]["description"]
            }
        
        return {
            "module_completed": True,
            "current_module": {
                "module_id": module_id,
                "name": mode_name,
                "summary": session.checkpoint_json
            },
            "next_module": next_module_info,
            "message": f"Congratulations! You've completed {mode_name}. Ready for the next module?"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in complete_module: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to complete module: {str(e)}")

@router.get("/projects/{project_id}/progress")
async def get_project_progress(
    project_id: str,
    db: AsyncSession = Depends(get_async_db),
    user=Depends(get_current_active_user)
):
    """Get overall progress for a project across all modules."""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection error")
        
        # Get all sessions for this project
        result = await db.execute(select(GPTModeSession).where(GPTModeSession.project_id == project_id))
        sessions = result.scalars().all()
        
        # Build progress data
        progress_data = []
        total_modules = len(chatbot_service.modules)
        completed_modules = 0
        
        for module_id, module_info in chatbot_service.modules.items():
            session = next((s for s in sessions if s.mode_name == module_info["name"]), None)
            
            if session:
                questions = chatbot_service.get_module_questions(module_id)
                progress_percentage = (session.current_question / len(questions)) * 100
                is_complete = session.current_question >= len(questions)
                
                if is_complete:
                    completed_modules += 1
                
                progress_data.append({
                    "module_id": module_id,
                    "name": module_info["name"],
                    "description": module_info["description"],
                    "current_question": session.current_question,
                    "total_questions": len(questions),
                    "progress_percentage": round(progress_percentage, 1),
                    "is_complete": is_complete,
                    "has_summary": bool(session.checkpoint_json)
                })
            else:
                progress_data.append({
                    "module_id": module_id,
                    "name": module_info["name"],
                    "description": module_info["description"],
                    "current_question": 0,
                    "total_questions": len(chatbot_service.get_module_questions(module_id)),
                    "progress_percentage": 0,
                    "is_complete": False,
                    "has_summary": False
                })
        
        overall_progress = (completed_modules / total_modules) * 100
        
        return {
            "project_id": project_id,
            "overall_progress": round(overall_progress, 1),
            "completed_modules": completed_modules,
            "total_modules": total_modules,
            "modules": progress_data
        }
        
    except Exception as e:
        logger.error(f"Error in get_project_progress: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get project progress: {str(e)}") 

@router.post("/projects/{project_id}/modes/{mode_name}/skip")
async def skip_question(
    project_id: str,
    mode_name: str,
    req: SkipQuestionRequest,
    db: AsyncSession = Depends(get_async_db),
    user=Depends(get_current_active_user)
):
    """Skip the current question and move to the next one."""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection error")
        
        # Find the module ID
        module_id = None
        for mid, module in chatbot_service.modules.items():
            if module["name"] == mode_name:
                module_id = mid
                break
        
        if not module_id:
            raise HTTPException(status_code=404, detail=f"Mode '{mode_name}' not found")
            
        result = await db.execute(select(GPTModeSession).where(GPTModeSession.project_id == project_id, GPTModeSession.mode_name == mode_name))
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Mode session not found")
        
        # Check if module is complete
        is_complete = await chatbot_service.check_module_completion_ready(module_id, session.current_question)
        if is_complete:
            return {"done": True, "message": "All questions answered.", "module_complete": True}
        
        # Check if question can be skipped
        validation_rules = chatbot_service._get_validation_rules(module_id, session.current_question)
        if not validation_rules.get("allow_skip", True):
            raise HTTPException(status_code=400, detail="This question cannot be skipped.")
        
        # Mark question as skipped
        skip_reason = req.reason if req.reason else "User chose to skip"
        session.answers[str(session.current_question)] = f"[SKIPPED: {skip_reason}]"
        session.current_question += 1
        await db.commit()
        await db.refresh(session)
        
        # Check if module is now complete
        is_complete = await chatbot_service.check_module_completion_ready(module_id, session.current_question)
        if is_complete:
            return {"done": True, "message": "All questions answered.", "module_complete": True}
        
        # Get next question
        next_question_data = await chatbot_service.get_next_question(
            module_id, 
            session.current_question, 
            session.answers
        )
        
        next_question_data["module_id"] = module_id
        next_question_data["module_name"] = mode_name
        next_question_data["message"] = f"Question skipped successfully. Here's the next question:"
        
        return next_question_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in skip_question: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to skip question: {str(e)}")

@router.get("/projects/{project_id}/modes/{mode_name}/validation-rules")
async def get_question_validation_rules(
    project_id: str,
    mode_name: str,
    question_number: int,
    db: AsyncSession = Depends(get_async_db),
    user=Depends(get_current_active_user)
):
    """Get validation rules for a specific question."""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection error")
        
        # Find the module ID
        module_id = None
        for mid, module in chatbot_service.modules.items():
            if module["name"] == mode_name:
                module_id = mid
                break
        
        if not module_id:
            raise HTTPException(status_code=404, detail=f"Mode '{mode_name}' not found")
        
        # Get validation rules
        validation_rules = chatbot_service._get_validation_rules(module_id, question_number)
        
        return {
            "module_id": module_id,
            "module_name": mode_name,
            "question_number": question_number,
            "validation_rules": validation_rules
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting validation rules: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get validation rules: {str(e)}")

@router.post("/projects/{project_id}/combined-summary")
async def get_combined_summary(
    project_id: str, 
    completed_modules: dict = Body(...),
    db: AsyncSession = Depends(get_async_db),
    user=Depends(get_current_active_user)
):
    """Generate a combined summary for all completed modules for a project."""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection error")
        
        # Check project access
        result = await db.execute(select(Project).where(Project.id == project_id, Project.is_active == True))
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Generate combined summary
        summary = await chatbot_service.generate_combined_summary(completed_modules)
        
        # Save the summary to database
        project_summary = ProjectSummary(
            id=str(uuid.uuid4()),
            project_id=project_id,
            summary_type="combined",
            module_answers=completed_modules,
            combined_summary=summary,
            modules_processed=len(completed_modules)
        )
        
        db.add(project_summary)
        await db.commit()
        await db.refresh(project_summary)
        
        return {
            "success": True,
            "summary": summary,
            "project_id": project_id,
            "modules_processed": len(completed_modules),
            "summary_id": project_summary.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating combined summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate combined summary: {str(e)}")

@router.get("/projects/{project_id}/summaries")
async def get_project_summaries(
    project_id: str,
    db: AsyncSession = Depends(get_async_db),
    user=Depends(get_current_active_user)
):
    """Get all saved summaries for a project."""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection error")
        
        # Check project access
        result = await db.execute(select(Project).where(Project.id == project_id, Project.is_active == True))
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get all summaries for this project
        result = await db.execute(select(ProjectSummary).where(ProjectSummary.project_id == project_id))
        summaries = result.scalars().all()
        
        return {
            "success": True,
            "project_id": project_id,
            "summaries": [
                {
                    "id": summary.id,
                    "summary_type": summary.summary_type,
                    "modules_processed": summary.modules_processed,
                    "created_at": summary.created_at.isoformat(),
                    "updated_at": summary.updated_at.isoformat()
                }
                for summary in summaries
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project summaries: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get project summaries: {str(e)}")

@router.get("/projects/{project_id}/summaries/{summary_id}")
async def get_project_summary(
    project_id: str,
    summary_id: str,
    db: AsyncSession = Depends(get_async_db),
    user=Depends(get_current_active_user)
):
    """Get a specific saved summary for a project."""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection error")
        
        # Check project access
        result = await db.execute(select(Project).where(Project.id == project_id, Project.is_active == True))
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get the specific summary
        result = await db.execute(select(ProjectSummary).where(ProjectSummary.id == summary_id, ProjectSummary.project_id == project_id))
        summary = result.scalar_one_or_none()
        if not summary:
            raise HTTPException(status_code=404, detail="Summary not found")
        
        return {
            "success": True,
            "summary_id": summary.id,
            "summary_type": summary.summary_type,
            "module_answers": summary.module_answers,
            "combined_summary": summary.combined_summary,
            "modules_processed": summary.modules_processed,
            "created_at": summary.created_at.isoformat(),
            "updated_at": summary.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get project summary: {str(e)}")

# New conversational chat endpoints
@router.post("/projects/{project_id}/chat/start")
async def start_conversational_chat(
    project_id: str,
    req: StartModeRequest,
    db: AsyncSession = Depends(get_async_db),
    user=Depends(get_current_active_user)
):
    """Start a conversational chat session for a specific mode."""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection error")
        
        # Check project access
        result = await db.execute(select(Project).where(Project.id == project_id, Project.is_active == True))
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Find the module ID based on mode name
        module_id = None
        for mid, module in chatbot_service.modules.items():
            if module["name"] == req.mode_name:
                module_id = mid
                break
        
        if not module_id:
            raise HTTPException(status_code=404, detail=f"Mode '{req.mode_name}' not found")
        
        # Check for existing session
        result = await db.execute(select(GPTModeSession).where(GPTModeSession.project_id == project_id, GPTModeSession.mode_name == req.mode_name))
        session = result.scalar_one_or_none()
        
        if not session:
            # Create new session
            session = GPTModeSession(
                id=str(uuid.uuid4()),
                project_id=project_id,
                mode_name=req.mode_name,
                current_question=0,
                answers={},
                checkpoint_json={}
            )
            db.add(session)
            await db.commit()
            await db.refresh(session)
        
        # Generate welcome message
        welcome_message = await chatbot_service.generate_welcome_message(module_id)
        
        return {
            "session_id": session.id,
            "message": welcome_message,
            "module_id": module_id,
            "module_name": req.mode_name,
            "is_question": False,
            "current_question": 0,
            "total_questions": len(chatbot_service.get_module_questions(module_id))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting conversational chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start conversational chat: {str(e)}")

@router.post("/projects/{project_id}/chat/message")
async def send_chat_message(
    project_id: str,
    req: ChatMessageRequest,
    db: AsyncSession = Depends(get_async_db),
    user=Depends(get_current_active_user)
):
    """Send a message in the conversational chat and get response."""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection error")
        
        if not req.session_id:
            raise HTTPException(status_code=400, detail="Session ID is required")
        
        # Get session
        result = await db.execute(select(GPTModeSession).where(GPTModeSession.id == req.session_id, GPTModeSession.project_id == project_id))
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Find the module ID
        module_id = None
        for mid, module in chatbot_service.modules.items():
            if module["name"] == session.mode_name:
                module_id = mid
                break
        
        if not module_id:
            raise HTTPException(status_code=404, detail=f"Module not found for mode '{session.mode_name}'")
        
        # Process the message and get response
        response = await chatbot_service.process_conversational_message(
            module_id, 
            session.current_question, 
            session.answers, 
            req.message
        )
        
        # Update session if answer was provided
        if response.get("answer_provided"):
            session.answers[str(session.current_question)] = req.message
            session.current_question += 1
            await db.commit()
            await db.refresh(session)
        
        # Check if module is complete
        is_complete = await chatbot_service.check_module_completion_ready(module_id, session.current_question)
        
        return {
            "session_id": session.id,
            "message": response.get("message", ""),
            "is_question": response.get("is_question", False),
            "current_question": response.get("current_question"),
            "question_number": session.current_question + 1,
            "total_questions": len(chatbot_service.get_module_questions(module_id)),
            "module_complete": is_complete,
            "summary": response.get("summary")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process chat message: {str(e)}")

@router.post("/projects/{project_id}/chat/summary")
async def get_chat_summary(
    project_id: str,
    req: SummaryRequest,
    db: AsyncSession = Depends(get_async_db),
    user=Depends(get_current_active_user)
):
    """Get summary for the current chat session."""
    try:
        logger.info(f"Getting chat summary for session: {req.session_id}")
        
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection error")
        
        # Get session
        result = await db.execute(select(GPTModeSession).where(GPTModeSession.id == req.session_id, GPTModeSession.project_id == project_id))
        session = result.scalar_one_or_none()
        if not session:
            logger.error(f"Session not found: {req.session_id}")
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger.info(f"Found session: {session.id}, mode: {session.mode_name}, answers: {len(session.answers)}")
        
        # Find the module ID
        module_id = None
        for mid, module in chatbot_service.modules.items():
            if module["name"] == session.mode_name:
                module_id = mid
                break
        
        if not module_id:
            logger.error(f"Module not found for mode: {session.mode_name}")
            raise HTTPException(status_code=404, detail=f"Module not found for mode '{session.mode_name}'")
        
        logger.info(f"Generating summary for module: {module_id}, answers: {session.answers}")
        
        # Generate summary
        try:
            summary_data = await chatbot_service.generate_module_summary(module_id, session.answers)
            logger.info(f"Summary generated successfully: {summary_data.get('summary', '')[:100]}...")
        except Exception as e:
            logger.error(f"Error generating summary: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")
        
        # Update session with summary
        session.checkpoint_json = summary_data
        await db.commit()
        
        return {
            "session_id": req.session_id,
            "summary": summary_data.get("summary", ""),
            "module_name": session.mode_name,
            "answers": session.answers
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get chat summary: {str(e)}")

@router.post("/projects/{project_id}/chat/edit-summary")
async def edit_chat_summary(
    project_id: str,
    req: EditSummaryRequest,
    db: AsyncSession = Depends(get_async_db),
    user=Depends(get_current_active_user)
):
    """Edit the summary for the current chat session."""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection error")
        
        # Get session
        result = await db.execute(select(GPTModeSession).where(GPTModeSession.id == req.session_id, GPTModeSession.project_id == project_id))
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update summary
        if session.checkpoint_json:
            session.checkpoint_json["summary"] = req.edited_summary
        else:
            session.checkpoint_json = {"summary": req.edited_summary}
        
        await db.commit()
        await db.refresh(session)
        
        return {
            "session_id": req.session_id,
            "message": "Summary updated successfully!",
            "summary": req.edited_summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error editing chat summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to edit chat summary: {str(e)}")