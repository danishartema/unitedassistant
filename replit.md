# Unified Assistant Backend

## Overview

This is the backend API for the Unified Assistant, an AI-powered document creation platform that guides users through a structured 14-phase workflow. The system combines modern web technologies with advanced AI capabilities to help users create comprehensive documents collaboratively.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

### January 21, 2025 - Application Debugging and Fixes
- Fixed database connection issues with asyncpg SSL configuration
- Resolved import conflicts with routers package
- Fixed all 14 LSP type errors across multiple files
- Removed conflicting django-routers dependency
- Application now running successfully on port 8000
- All API endpoints properly registered and accessible

## System Architecture

### Backend Framework
- **FastAPI**: Modern, fast web framework for building APIs with Python 3.11+
- **Async/Await**: Fully asynchronous architecture for high performance
- **Pydantic**: Data validation and serialization using Python type hints

### Database Architecture
- **PostgreSQL 16+**: Primary relational database with pgvector extension
- **SQLAlchemy**: Async ORM for database operations
- **Alembic**: Database migration management
- **pgvector**: Vector storage for AI embeddings and semantic search

### AI Integration
- **OpenAI GPT-4o**: Latest model for content generation (released May 13, 2024)
- **text-embedding-3-small**: Embedding model for semantic search
- **RAG (Retrieval Augmented Generation)**: Context-aware content generation

### Background Processing
- **Celery**: Distributed task queue for async operations
- **Redis**: Message broker and caching layer
- **Export Tasks**: Async document generation (PDF, Word, JSON)

### Authentication & Security
- **JWT Tokens**: Access and refresh token system
- **bcrypt**: Password hashing
- **Role-based Access Control**: User and project-level permissions

## Key Components

### User Management
- User registration and authentication
- JWT-based session management
- Role-based access control (Admin, User)
- Password strength validation

### Project Management
- Multi-user collaborative projects
- Project ownership and member roles (Owner, Editor)
- Project-level access controls
- Invitation system for collaboration

### 14-Phase Workflow System
- Structured document creation process
- Each phase builds upon previous phases
- AI-generated content with context awareness
- Phase status tracking (Not Started, In Progress, Completed, Stale)
- Draft management with version history

### AI Content Generation
- OpenAI GPT-4o integration for content creation
- Context-aware prompts using RAG
- Temperature-controlled generation
- Embedding-based semantic search

### Export System
- Async document generation
- Multiple formats: PDF, Word, JSON
- Background task processing with Celery
- Download management and cleanup

### RAG Service
- Semantic search across project content
- Context retrieval for AI generation
- Vector embeddings storage
- Cross-phase content relationships

## Data Flow

### Content Generation Flow
1. User provides input for a specific phase
2. System retrieves relevant context from previous phases using RAG
3. AI generates content using OpenAI GPT-4o with context
4. Content is stored as a draft with embeddings
5. System updates phase status and triggers cascade updates if needed

### Export Flow
1. User requests document export in specific format
2. System creates export task and queues it with Celery
3. Background worker processes all phases into document
4. Generated file is stored and download link provided
5. Cleanup occurs after expiration period

### Authentication Flow
1. User login generates JWT access and refresh tokens
2. API requests include Bearer token in Authorization header
3. Token validation extracts user identity and permissions
4. Database session provides user context for operations

## External Dependencies

### Required Services
- **PostgreSQL 16+**: Database with pgvector extension
- **Redis 7+**: Caching and message broker
- **OpenAI API**: Content generation and embeddings

### Python Packages
- **FastAPI**: Web framework
- **SQLAlchemy**: Database ORM
- **Celery**: Task queue
- **OpenAI**: AI service client
- **Pydantic**: Data validation
- **passlib**: Password hashing
- **python-jose**: JWT handling
- **reportlab**: PDF generation
- **python-docx**: Word document generation

### Environment Configuration
- Database connection strings
- OpenAI API keys
- Redis URLs
- JWT secret keys
- File storage paths

## Deployment Strategy

### Development Environment
- Local PostgreSQL with pgvector
- Local Redis instance
- Environment variables in .env file
- Hot reload with uvicorn

### Production Considerations
- Containerized deployment (Docker)
- AWS RDS for PostgreSQL
- AWS ElastiCache for Redis
- EKS for container orchestration
- Environment-specific configuration
- SSL/TLS termination
- Rate limiting and monitoring

### Database Schema
- Users table with authentication data
- Projects table with ownership and metadata
- Phases table for workflow management
- Phase drafts for version control
- Embeddings table for RAG functionality
- Export tasks for async processing
- Project members for collaboration

The system is designed for scalability and maintainability, with clear separation of concerns between authentication, business logic, AI services, and data persistence.