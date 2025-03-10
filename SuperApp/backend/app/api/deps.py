"""
Dependency injection functions for API endpoints.
"""

import logging
from typing import Optional, Union, Dict, Any

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.core.config import settings
from app.core.security import verify_token
from app.db.mongodb.models import User
from app.services.ai.gemini_service import GeminiService

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get the current user from the token.
    
    Args:
        token: JWT token
        
    Returns:
        User: The current user
        
    Raises:
        HTTPException: If the token is invalid or the user is not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token and get payload
        payload = verify_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        # Get user from database
        user = await User.find_one({"_id": user_id})
        if user is None:
            raise credentials_exception
            
        return user
    except JWTError:
        raise credentials_exception


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current active user.
    
    Args:
        current_user: The current user
        
    Returns:
        User: The current active user
        
    Raises:
        HTTPException: If the user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Get the current admin user.
    
    Args:
        current_user: The current active user
        
    Returns:
        User: The current admin user
        
    Raises:
        HTTPException: If the user is not an admin
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="The user doesn't have enough privileges"
        )
    return current_user


async def get_user_gemini_service(current_user: User = Depends(get_current_active_user)) -> GeminiService:
    """
    Get the Gemini service for the current user.
    
    Args:
        current_user: The current active user
        
    Returns:
        GeminiService: The Gemini service instance
        
    Raises:
        HTTPException: If the user doesn't have a Gemini API key
    """
    api_key = current_user.settings.get("gemini_api_key") if current_user.settings else None
    
    # Use user-specific API key if available, otherwise use the default one
    api_key = api_key or settings.GEMINI_API_KEY
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gemini API key not configured. Please update your settings.",
        )
    
    return GeminiService(api_key=api_key) 