"""
API endpoint for testing API key authentication.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..app.security import require_api_key

router = APIRouter()


class SelftestRequest(BaseModel):
    """Selftest request model."""
    test_name: str
    parameters: dict = {}


class SelftestResponse(BaseModel):
    """Selftest response model."""
    status: str
    message: str
    test_name: str
    timestamp: float


@router.post("/run", response_model=SelftestResponse)
async def run_selftest(
    request: SelftestRequest,
    api_key: str = Depends(require_api_key)
) -> SelftestResponse:
    """Run selftest with API key authentication."""
    import time
    
    return SelftestResponse(
        status="success",
        message=f"Selftest '{request.test_name}' executed successfully",
        test_name=request.test_name,
        timestamp=time.time()
    )


@router.get("/status")
async def selftest_status() -> dict:
    """Get selftest status (no auth required)."""
    return {"status": "ready", "message": "Selftest endpoint available"}
