"""
Pydantic schemas for request/response models.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, ConfigDict
from enum import Enum

from models import UserRole, ProjectRole, PhaseStatus, ExportStatus, ExportFormat


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    role: UserRole
    is_active: bool
    created_at: datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Token schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None


# Project schemas
class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class ProjectMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user: UserResponse
    role: ProjectRole
    invited_at: datetime


class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    owner: UserResponse
    members: List[ProjectMemberResponse]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProjectCreateResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    owner: UserResponse
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProjectInvite(BaseModel):
    email: EmailStr
    role: ProjectRole = ProjectRole.EDITOR


# Phase schemas
class PhaseBase(BaseModel):
    title: str
    description: Optional[str] = None
    prompt_template: Optional[str] = None


class PhaseCreate(PhaseBase):
    phase_number: int


class PhaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    user_input: Optional[str] = None
    prompt_template: Optional[str] = None


class PhaseDraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    version: int
    content: str
    user_input: Optional[str]
    ai_response: Optional[str]
    created_at: datetime


class PhaseResponse(PhaseBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    project_id: str
    phase_number: int
    user_input: Optional[str]
    ai_response: Optional[str]
    status: PhaseStatus
    context_data: Optional[Dict[str, Any]]
    drafts: List[PhaseDraftResponse]
    created_at: datetime
    updated_at: datetime


class PhaseGenerateRequest(BaseModel):
    user_input: str
    use_rag: bool = True
    temperature: float = 0.7


class PhaseGenerateResponse(BaseModel):
    phase_id: str
    ai_response: str
    status: PhaseStatus
    context_used: List[str]


# Export schemas
class ExportRequest(BaseModel):
    format: ExportFormat


class ExportTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    project_id: str
    format: ExportFormat
    status: ExportStatus
    file_path: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]


# RAG schemas
class RAGSearchRequest(BaseModel):
    query: str
    project_id: str
    limit: int = 5
    similarity_threshold: float = 0.7


class RAGSearchResult(BaseModel):
    phase_id: str
    phase_number: int
    content: str
    similarity_score: float


class RAGSearchResponse(BaseModel):
    results: List[RAGSearchResult]
    total_count: int


# API Response schemas
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
