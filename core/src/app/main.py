"""
Main application entry point.
Sets up FastAPI app with all components.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time

from .settings import Settings
from .middleware import (
    RateLimitMiddleware, 
    RequestIdMiddleware, 
    TimingMiddleware, 
    SecurityHeadersMiddleware
)
from ..observability.api_metrics import router as metrics_router
from ..observability.api_logs import router as logs_router
from ..observability.ring_buffer import initialize_log_buffer
from ..router.api_router import router as router_router
from ..tools.api_tools import router as tools_router
from ..scripts.api_selftest import router as selftest_router


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Jarvis Core application...")
    logger.info(f"Environment: {app.state.settings.env}")
    logger.info(f"Debug mode: {app.state.settings.debug}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Jarvis Core application...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    # Create app
    app = FastAPI(
        title="Jarvis Core API",
        version="0.1.0",
        description="Local AI assistant with edge-first processing",
        docs_url="/docs" if Settings().debug else None,
        redoc_url="/redoc" if Settings().debug else None,
        lifespan=lifespan
    )
    
    # Load settings
    app.state.settings = Settings()
    
    # Initialize log buffer with settings
    initialize_log_buffer(
        max_size=app.state.settings.log_buffer_max,
        policy=app.state.settings.log_buffer_policy
    )
    
    # Add custom middleware
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(RateLimitMiddleware, requests_per_minute=120)  # 2 req/sec
    
    # Add middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"] if app.state.settings.is_development else ["localhost", "127.0.0.1"]
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app.state.settings.cors_origins_list,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
    
    # Add exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(exc)}
        )
    
    # Include routers
    app.include_router(metrics_router, prefix="/metrics", tags=["metrics"])
    app.include_router(logs_router, prefix="/logs", tags=["logs"])
    app.include_router(router_router, prefix="/router", tags=["router"])
    app.include_router(tools_router, prefix="/tools", tags=["tools"])
    app.include_router(selftest_router, prefix="/selftest", tags=["selftest"])
    
    return app


# Create application instance
app = create_app()


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Jarvis Core API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health/live", tags=["health"])
async def live():
    """Health check endpoint."""
    return {"status": "ok", "timestamp": time.time()}


@app.get("/health/ready", tags=["health"])
async def ready():
    """Readiness check endpoint."""
    # TODO: Add actual readiness checks (database, Redis, etc.)
    return {"ready": True, "timestamp": time.time()}


@app.get("/info", tags=["info"])
async def info():
    """Application information."""
    return {
        "name": "Jarvis Core",
        "version": "0.1.0",
        "environment": app.state.settings.env,
        "debug": app.state.settings.debug,
        "python_version": "3.11+"
    }
