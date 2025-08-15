"""
Security utilities and dependencies.
"""
from typing import Optional
from fastapi import Header, HTTPException, Request, Depends
from .settings import Settings


def get_api_key(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")) -> str:
    """Validate API key from header."""
    if not x_api_key:
        raise HTTPException(
            status_code=401, 
            detail="Missing API key",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    # Validate against configured API keys (supports multiple keys)
    settings = Settings()
    valid_keys = [key.strip() for key in settings.api_keys.split(",") if key.strip()]
    
    if x_api_key not in valid_keys:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    return x_api_key


def require_api_key() -> str:
    """Dependency for endpoints that require API key authentication."""
    return Depends(get_api_key)


def get_authenticated_user(request: Request, api_key: str = Depends(get_api_key)) -> dict:
    """Get authenticated user information."""
    # TODO: Implement user lookup based on API key
    # For now, return basic user info
    return {
        "user_id": "api_user",
        "permissions": ["read", "write"],
        "api_key": api_key[:8] + "..."  # Truncate for security
    }
