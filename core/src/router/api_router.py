"""
API endpoints for router functionality.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def router_info():
    """Get router information."""
    return {"message": "Router API", "status": "stub"}
