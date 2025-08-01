"""
Authentication router for user management and JWT tokens.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_async_db
from models import User
from schemas import UserCreate, UserResponse, UserLogin, Token, APIResponse
from auth import verify_password, get_password_hash, create_access_token, create_refresh_token, refresh_access_token
from dependencies import get_current_active_user
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=APIResponse, status_code=201)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Register a new user."""
    # Check if user already exists
    existing_user = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = existing_user.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    logger.info(f"User registered: {db_user.email}")
    
    return APIResponse(
        success=True,
        message="User registered successfully",
        data={"user_id": db_user.id}
    )


@router.post("/login", response_model=Token)
async def login_user(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_async_db)
):
    """Authenticate user and return JWT tokens."""
    # Get user
    user_result = await db.execute(
        select(User).where(User.email == user_credentials.email)
    )
    user = user_result.scalar_one_or_none()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    logger.info(f"User logged in: {user.email}")
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


from pydantic import BaseModel

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/refresh", response_model=dict)
async def refresh_token(
    request: RefreshTokenRequest
):
    """Refresh access token using refresh token."""
    try:
        new_access_token = refresh_access_token(request.refresh_token)
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information."""
    return current_user


@router.post("/logout", response_model=APIResponse)
async def logout_user(
    current_user: User = Depends(get_current_active_user)
):
    """Logout user (client should discard tokens)."""
    logger.info(f"User logged out: {current_user.email}")
    
    return APIResponse(
        success=True,
        message="User logged out successfully"
    )
