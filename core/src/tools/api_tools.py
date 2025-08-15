"""
API endpoints for tools functionality.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def tools_info():
    """Get tools information."""
    return {"message": "Tools API", "status": "stub"}
