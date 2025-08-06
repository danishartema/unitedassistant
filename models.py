"""
Database models for the Unified Assistant application.
"""
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, 
    ForeignKey, Enum, Float, JSON, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
import uuid
import enum

from database import Base


class UserRole(str, enum.Enum):
    """User roles in the system."""
    ADMIN = "admin"
    USER = "user"


class ProjectRole(str, enum.Enum):
    """Project member roles."""
    OWNER = "owner"
    EDITOR = "editor"


class PhaseStatus(str, enum.Enum):
    """Phase status enumeration."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    STALE = "stale"


class ExportStatus(str, enum.Enum):
    """Export task status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ExportFormat(str, enum.Enum):
    """Export format types."""
    PDF = "pdf"
    WORD = "word"
    JSON = "json"


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    owned_projects: Mapped[List["Project"]] = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    project_memberships: Mapped[List["ProjectMember"]] = relationship("ProjectMember", back_populates="user", cascade="all, delete-orphan")
    export_tasks: Mapped[List["ExportTask"]] = relationship("ExportTask", back_populates="user")


class Project(Base):
    """Project model."""
    __tablename__ = "projects"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="owned_projects")
    members: Mapped[List["ProjectMember"]] = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    phases: Mapped[List["Phase"]] = relationship("Phase", back_populates="project", cascade="all, delete-orphan")
    export_tasks: Mapped[List["ExportTask"]] = relationship("ExportTask", back_populates="project")


class ProjectMember(Base):
    """Project member model for collaboration."""
    __tablename__ = "project_members"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    role: Mapped[ProjectRole] = mapped_column(Enum(ProjectRole), nullable=False)
    invited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="project_memberships")
    
    __table_args__ = (
        Index("idx_project_member", "project_id", "user_id"),
    )


class Phase(Base):
    """Phase model for the 14-phase workflow."""
    __tablename__ = "phases"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    phase_number: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-14
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    prompt_template: Mapped[Optional[str]] = mapped_column(Text)
    user_input: Mapped[Optional[str]] = mapped_column(Text)
    ai_response: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[PhaseStatus] = mapped_column(Enum(PhaseStatus), default=PhaseStatus.NOT_STARTED)
    context_data: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="phases")
    drafts: Mapped[List["PhaseDraft"]] = relationship("PhaseDraft", back_populates="phase", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_phase_project", "project_id"),
        Index("idx_phase_number", "project_id", "phase_number"),
    )


class PhaseDraft(Base):
    """Phase draft model for version control."""
    __tablename__ = "phase_drafts"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phase_id: Mapped[str] = mapped_column(String(36), ForeignKey("phases.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_input: Mapped[Optional[str]] = mapped_column(Text)
    ai_response: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    phase: Mapped["Phase"] = relationship("Phase", back_populates="drafts")
    
    __table_args__ = (
        Index("idx_draft_phase", "phase_id"),
        Index("idx_draft_version", "phase_id", "version"),
    )


class ExportTask(Base):
    """Export task model for async document generation."""
    __tablename__ = "export_tasks"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    format: Mapped[ExportFormat] = mapped_column(Enum(ExportFormat), nullable=False)
    status: Mapped[ExportStatus] = mapped_column(Enum(ExportStatus), default=ExportStatus.PENDING)
    file_path: Mapped[Optional[str]] = mapped_column(String(500))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    celery_task_id: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="export_tasks")
    user: Mapped["User"] = relationship("User", back_populates="export_tasks")
    
    __table_args__ = (
        Index("idx_export_project", "project_id"),
        Index("idx_export_user", "user_id"),
    )


class GPTModeSession(Base):
    """Session for a specific GPT mode within a project, storing answers and checkpoints."""
    __tablename__ = "gpt_mode_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)  # Add user isolation
    mode_name: Mapped[str] = mapped_column(String(255), nullable=False)
    current_question: Mapped[int] = mapped_column(Integer, default=0)
    answers: Mapped[dict] = mapped_column(JSON, default=dict)  # {question_number: answer}
    checkpoint_json: Mapped[dict] = mapped_column(JSON, default=dict)  # JSON output after this mode
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    project: Mapped["Project"] = relationship("Project")
    user: Mapped["User"] = relationship("User")  # Add user relationship

    __table_args__ = (
        Index("idx_gpt_session_project", "project_id"),
        Index("idx_gpt_session_user", "user_id"),  # Add user index
        Index("idx_gpt_session_mode", "mode_name"),
        UniqueConstraint("project_id", "user_id", "mode_name", name="uq_project_user_mode"),  # Ensure unique sessions per user per mode
    )

class PhaseEmbedding(Base):
    """Phase embedding model for RAG functionality."""
    __tablename__ = "phase_embeddings"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phase_id: Mapped[str] = mapped_column(String(36), ForeignKey("phases.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[List[float]] = mapped_column(JSON, nullable=False)  # Vector embedding
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    phase: Mapped["Phase"] = relationship("Phase")
    
    __table_args__ = (
        Index("idx_embedding_phase", "phase_id"),
    )


class ProjectMemory(Base):
    """Central memory object for a project, storing the full JSON chain."""
    __tablename__ = "project_memory"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False, unique=True)
    memory_json: Mapped[dict] = mapped_column(JSON, default=dict)  # The full JSON chain for the project
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    project: Mapped["Project"] = relationship("Project")


class ProjectSummary(Base):
    """Model for storing combined project summaries from All GPTs mode."""
    __tablename__ = "project_summaries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    summary_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "combined", "individual"
    module_answers: Mapped[dict] = mapped_column(JSON, default=dict)  # All module answers
    combined_summary: Mapped[str] = mapped_column(Text, nullable=False)  # The generated summary
    modules_processed: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    project: Mapped["Project"] = relationship("Project")

    __table_args__ = (
        Index("idx_project_summary", "project_id"),
        Index("idx_summary_type", "project_id", "summary_type"),
    )

class ConversationMemory(Base):
    """Model for storing conversation memory and context across sessions."""
    __tablename__ = "conversation_memory"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)  # Add user isolation
    session_id: Mapped[str] = mapped_column(String(36), nullable=False)  # GPTModeSession ID
    module_id: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Conversation context
    conversation_history: Mapped[List[dict]] = mapped_column(JSON, default=list)  # List of message objects
    context_summary: Mapped[str] = mapped_column(Text, default="")  # AI-generated context summary
    user_profile: Mapped[dict] = mapped_column(JSON, default=dict)  # Extracted user information
    conversation_state: Mapped[dict] = mapped_column(JSON, default=dict)  # Current conversation state
    
    # Memory management
    memory_tokens: Mapped[int] = mapped_column(Integer, default=0)  # Token count for memory management
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    project: Mapped["Project"] = relationship("Project")
    user: Mapped["User"] = relationship("User")  # Add user relationship

    __table_args__ = (
        Index("idx_conversation_project", "project_id"),
        Index("idx_conversation_session", "session_id"),
        Index("idx_conversation_module", "module_id"),
        Index("idx_conversation_user", "user_id"),  # Add user index
    )


class CrossModuleMemory(Base):
    """Model for storing information that should be shared across GPT modules."""
    __tablename__ = "cross_module_memory"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)  # Add user isolation
    
    # Shared information across modules
    business_context: Mapped[dict] = mapped_column(JSON, default=dict)  # Business information
    user_preferences: Mapped[dict] = mapped_column(JSON, default=dict)  # User preferences and style
    project_goals: Mapped[dict] = mapped_column(JSON, default=dict)  # Project objectives
    key_insights: Mapped[List[str]] = mapped_column(JSON, default=list)  # Important insights from previous modules
    
    # Module completion tracking
    completed_modules: Mapped[List[str]] = mapped_column(JSON, default=list)  # List of completed module IDs
    module_outputs: Mapped[dict] = mapped_column(JSON, default=dict)  # Outputs from each module
    
    # Context embeddings for RAG
    context_embeddings: Mapped[List[dict]] = mapped_column(JSON, default=list)  # Vector embeddings of context
    
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    project: Mapped["Project"] = relationship("Project")
    user: Mapped["User"] = relationship("User")  # Add user relationship

    __table_args__ = (
        Index("idx_cross_module_project", "project_id"),
        Index("idx_cross_module_user", "user_id"),  # Add user index
        UniqueConstraint("project_id", "user_id", name="uq_project_user_cross_module"),  # Ensure unique cross-module memory per user per project
    )


class ConversationMessage(Base):
    """Model for storing individual conversation messages with metadata."""
    __tablename__ = "conversation_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_memory_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversation_memory.id"), nullable=False)
    
    # Message content
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # "user", "assistant", "system"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(String(50), default="text")  # "text", "question", "answer", "clarification"
    
    # Context and metadata
    context_data: Mapped[dict] = mapped_column(JSON, default=dict)  # Additional context
    intent: Mapped[str] = mapped_column(String(100), default="")  # Detected intent
    confidence: Mapped[float] = mapped_column(Float, default=0.0)  # Confidence score
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)  # Token count
    
    # Relationships
    conversation_memory: Mapped["ConversationMemory"] = relationship("ConversationMemory")
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_message_conversation", "conversation_memory_id"),
        Index("idx_message_role", "role"),
        Index("idx_message_created", "created_at"),
    )
