"""
Authentication endpoints.
"""

import logging
from datetime import timedelta, datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from app.db.mongodb.models import User, UserSettings

logger = logging.getLogger(__name__)

router = APIRouter()


class Token(BaseModel):
    """Token response model."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token payload model."""
    
    sub: Optional[str] = None
    exp: Optional[int] = None


class UserCreate(BaseModel):
    """User creation request model."""
    
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    """User response model."""
    
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account",
)
async def register_user(user_in: UserCreate) -> Any:
    """
    Register a new user.
    
    Args:
        user_in: User registration data
        
    Returns:
        UserResponse: The created user data
        
    Raises:
        HTTPException: If the email or username already exists
    """
    # Check if email already exists
    existing_email_user = await User.find_one({"email": user_in.email})
    if existing_email_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Check if username already exists
    existing_username_user = await User.find_one({"username": user_in.username})
    if existing_username_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    # Create new user
    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        settings=UserSettings(),
    )
    
    # Save user to database
    await user.save()
    
    # Return user data (without password)
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
    }


@router.post(
    "/login",
    response_model=Token,
    summary="Login",
    description="Authenticate a user and get access tokens",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    Login a user.
    
    Args:
        form_data: OAuth2 password request form
        
    Returns:
        Token: Access and refresh tokens
        
    Raises:
        HTTPException: If authentication fails
    """
    # Check if user exists by username or email
    user = await User.find_one({"username": form_data.username})
    if not user:
        user = await User.find_one({"email": form_data.username})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if password is correct
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires,
    )
    
    # Create refresh token
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": user.id},
        expires_delta=refresh_token_expires,
    )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await user.save()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    
    refresh_token: str


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh token",
    description="Get a new access token using a refresh token",
)
async def refresh_token(
    request: RefreshTokenRequest,
) -> Any:
    """
    Refresh access token.
    
    Args:
        request: Refresh token request
        
    Returns:
        Token: New access and refresh tokens
        
    Raises:
        HTTPException: If the refresh token is invalid
    """
    try:
        # Verify refresh token
        payload = verify_token(request.refresh_token)
        
        # Check token type
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user ID from token
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = await User.find_one({"_id": user_id})
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.id},
            expires_delta=access_token_expires,
        )
        
        # Create new refresh token
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = create_refresh_token(
            data={"sub": user.id},
            expires_delta=refresh_token_expires,
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) 