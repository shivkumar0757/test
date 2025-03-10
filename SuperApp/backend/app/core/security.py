"""
Security utilities for authentication and encryption.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

import jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from jose import jwt, JWTError

from app.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# API key encryption
try:
    fernet_key = Fernet(settings.API_KEY_ENCRYPTION_SECRET.encode())
except Exception as e:
    logger.warning(f"Failed to initialize Fernet for API key encryption: {e}")
    logger.warning("API keys will not be encrypted properly!")
    fernet_key = None


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create an access token.
    
    Args:
        data (Dict[str, Any]): The data to encode in the token
        expires_delta (Optional[timedelta], optional): The expiration time. Defaults to None.
        
    Returns:
        str: The encoded token
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    # Add token type and expiration time to payload
    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    
    # Encode token
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a refresh token.
    
    Args:
        data (Dict[str, Any]): The data to encode in the token
        expires_delta (Optional[timedelta], optional): The expiration time. Defaults to None.
        
    Returns:
        str: The encoded token
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
    # Add token type and expiration time to payload
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })
    
    # Encode token
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password (str): The plain password
        hashed_password (str): The hashed password
        
    Returns:
        bool: True if the password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Get the password hash.
    
    Args:
        password (str): The password to hash
        
    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt API key.
    
    Args:
        api_key: Plain API key
        
    Returns:
        Encrypted API key
    """
    if not fernet_key:
        logger.warning("API key encryption not available. Using fallback method.")
        # Simple fallback encryption (not secure)
        return f"mock_encrypted_{api_key[-8:]}"
    
    return fernet_key.encrypt(api_key.encode()).decode()


def decrypt_api_key(encrypted_api_key: str) -> Optional[str]:
    """
    Decrypt API key.
    
    Args:
        encrypted_api_key: Encrypted API key
        
    Returns:
        Decrypted API key or None on failure
    """
    if not fernet_key:
        logger.warning("API key decryption not available. Using fallback method.")
        # Simple fallback decryption (not secure)
        if encrypted_api_key.startswith("mock_encrypted_"):
            return f"decrypted_key_ending_with_{encrypted_api_key[-8:]}"
        return None
    
    try:
        return fernet_key.decrypt(encrypted_api_key.encode()).decode()
    except Exception as e:
        logger.error(f"Failed to decrypt API key: {e}")
        return None


def create_masked_key(api_key: str) -> str:
    """
    Create a masked version of an API key for display purposes.
    
    Args:
        api_key: Full API key
        
    Returns:
        Masked API key (e.g., "sk-...ABCD")
    """
    if len(api_key) < 8:
        return "***" + api_key[-2:] if len(api_key) > 2 else "***"
    
    prefix = api_key[:3]
    suffix = api_key[-4:]
    return f"{prefix}...{suffix}"


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify a token.
    
    Args:
        token (str): The token to verify
        
    Returns:
        Dict[str, Any]: The token payload
        
    Raises:
        JWTError: If the token is invalid
    """
    try:
        # Decode token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        return payload
    except JWTError as e:
        logger.error(f"Error verifying token: {e}")
        raise 