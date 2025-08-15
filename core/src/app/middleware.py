"""
Custom middleware for security and observability.
"""
import uuid
import time
from typing import Dict, Tuple
from collections import defaultdict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using token bucket algorithm."""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.buckets: Dict[str, Tuple[int, float]] = defaultdict(lambda: (requests_per_minute, time.time()))
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        
        # Get current bucket state
        tokens, last_refill = self.buckets[client_ip]
        now = time.time()
        
        # Refill tokens (1 token per second)
        time_passed = now - last_refill
        tokens = min(self.requests_per_minute, tokens + time_passed)
        
        # Check if request can proceed
        if tokens < 1:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded", "retry_after": 60}
            )
        
        # Consume token
        tokens -= 1
        self.buckets[client_ip] = (tokens, now)
        
        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(int(tokens))
        response.headers["X-RateLimit-Reset"] = str(int(now + 60))
        
        return response


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware for request ID tracking and correlation."""
    
    async def dispatch(self, request: Request, call_next):
        # Get or generate request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        
        # Add request ID to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware for request timing and performance tracking."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.perf_counter() - start_time
        
        # Add timing headers
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        
        # Log performance metrics
        logger.info(
            f"Request {request.method} {request.url.path} "
            f"completed in {process_time:.4f}s "
            f"(ID: {getattr(request.state, 'request_id', 'unknown')})"
        )
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for security headers."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy (basic)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self' ws: wss:;"
        )
        
        return response
