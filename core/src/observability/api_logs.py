"""
API endpoints for log streaming and management.
"""
import asyncio
import json
import time
import logging
from typing import AsyncGenerator, Optional
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel, Field
from .ring_buffer import log_buffer, LogEntry as BufferLogEntry

router = APIRouter()
logger = logging.getLogger(__name__)


class LogEntry(BaseModel):
    """Log entry structure."""
    timestamp: float = Field(description="Unix timestamp")
    level: str = Field(description="Log level (DEBUG, INFO, WARNING, ERROR)")
    message: str = Field(description="Log message")
    module: str = Field(description="Module name")
    function: str = Field(description="Function name")
    line: int = Field(description="Line number")
    correlation_id: Optional[str] = Field(None, description="Correlation ID for request tracking")
    user_id: Optional[str] = Field(None, description="User ID if authenticated")
    extra: dict = Field(default_factory=dict, description="Additional log data")


class LogFilter(BaseModel):
    """Log filtering options."""
    level: Optional[str] = Field(None, description="Filter by log level")
    module: Optional[str] = Field(None, description="Filter by module")
    correlation_id: Optional[str] = Field(None, description="Filter by correlation ID")
    start_time: Optional[float] = Field(None, description="Start timestamp")
    end_time: Optional[float] = Field(None, description="End timestamp")
    limit: int = Field(100, description="Maximum number of log entries")


class LogStats(BaseModel):
    """Log statistics."""
    total_entries: int = Field(description="Total log entries")
    entries_by_level: dict[str, int] = Field(description="Entry count by level")
    entries_by_module: dict[str, int] = Field(description="Entry count by module")
    oldest_entry: Optional[float] = Field(None, description="Oldest entry timestamp")
    newest_entry: Optional[float] = Field(None, description="Newest entry timestamp")


# Use ring buffer for log storage
def add_log_entry(entry: LogEntry) -> None:
    """Add a log entry to the ring buffer."""
    buffer_entry = BufferLogEntry(
        timestamp=entry.timestamp,
        level=entry.level,
        message=entry.message,
        module=entry.module,
        function=entry.function,
        line=entry.line,
        correlation_id=entry.correlation_id,
        user_id=entry.user_id,
        extra=entry.extra
    )
    asyncio.create_task(log_buffer.add(buffer_entry))


@router.get("/stream")
async def logs_stream(request: Request) -> EventSourceResponse:
    """Stream logs via Server-Sent Events (SSE)."""
    async def generate_logs() -> AsyncGenerator[dict, None]:
        """Generate log events."""
        try:
            # Send initial connection message
            yield {
                "event": "connected",
                "data": json.dumps({
                    "message": "Log stream connected",
                    "timestamp": time.time()
                })
            }
            
            # Send existing logs from ring buffer
            recent_logs = await log_buffer.get_recent(100)
            for entry in recent_logs:
                yield {
                    "event": "log",
                    "data": json.dumps({
                        "timestamp": entry.timestamp,
                        "level": entry.level,
                        "message": entry.message,
                        "module": entry.module,
                        "function": entry.function,
                        "line": entry.line,
                        "correlation_id": entry.correlation_id,
                        "user_id": entry.user_id,
                        "extra": entry.extra
                    })
                }
                await asyncio.sleep(0.1)  # Small delay to prevent flooding
            
            # Send heartbeat and wait for new logs
            while True:
                if await request.is_disconnected():
                    break
                
                # Send heartbeat
                yield {
                    "event": "heartbeat",
                    "data": json.dumps({
                        "timestamp": time.time(),
                        "status": "connected"
                    })
                }
                
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                
        except asyncio.CancelledError:
            logger.info("Log stream cancelled")
        except Exception as e:
            logger.error(f"Error in log stream: {e}")
            yield {
                "event": "error",
                "data": json.dumps({
                    "error": str(e),
                    "timestamp": time.time()
                })
            }
    
    return EventSourceResponse(generate_logs())


@router.get("/recent", response_model=list[LogEntry])
async def get_recent_logs(limit: int = 100) -> list[LogEntry]:
    """Get recent log entries."""
    if limit > 1000:
        limit = 1000
    
    recent_logs = await log_buffer.get_recent(limit)
    return [LogEntry(
        timestamp=entry.timestamp,
        level=entry.level,
        message=entry.message,
        module=entry.module,
        function=entry.function,
        line=entry.line,
        correlation_id=entry.correlation_id,
        user_id=entry.user_id,
        extra=entry.extra
    ) for entry in recent_logs]


@router.post("/search")
async def search_logs(filter_params: LogFilter) -> list[LogEntry]:
    """Search logs with filters."""
    filtered_logs = await log_buffer.search(
        level=filter_params.level,
        module=filter_params.module,
        correlation_id=filter_params.correlation_id,
        start_time=filter_params.start_time,
        end_time=filter_params.end_time,
        limit=filter_params.limit
    )
    
    return [LogEntry(
        timestamp=entry.timestamp,
        level=entry.level,
        message=entry.message,
        module=entry.module,
        function=entry.function,
        line=entry.line,
        correlation_id=entry.correlation_id,
        user_id=entry.user_id,
        extra=entry.extra
    ) for entry in filtered_logs]


@router.get("/stats", response_model=LogStats)
async def get_log_stats() -> LogStats:
    """Get log statistics."""
    buffer_stats = await log_buffer.get_stats()
    
    # Get all entries for detailed stats
    all_entries = await log_buffer.get_all()
    
    if not all_entries:
        return LogStats(
            total_entries=0,
            entries_by_level={},
            entries_by_module={}
        )
    
    # Count by level
    entries_by_level: dict[str, int] = {}
    for entry in all_entries:
        entries_by_level[entry.level] = entries_by_level.get(entry.level, 0) + 1
    
    # Count by module
    entries_by_module: dict[str, int] = {}
    for entry in all_entries:
        entries_by_module[entry.module] = entries_by_module.get(entry.module, 0) + 1
    
    return LogStats(
        total_entries=buffer_stats["current_size"],
        entries_by_level=entries_by_level,
        entries_by_module=entries_by_module,
        oldest_entry=all_entries[0].timestamp if all_entries else None,
        newest_entry=all_entries[-1].timestamp if all_entries else None
    )


@router.delete("/clear")
async def clear_logs() -> dict:
    """Clear all logs (admin only)."""
    # TODO: Add authentication/authorization
    cleared_count = await log_buffer.clear()
    
    logger.warning(f"Logs cleared by admin. {cleared_count} entries removed.")
    
    return {
        "message": f"Cleared {cleared_count} log entries",
        "timestamp": time.time()
    }


# Add some sample logs for testing
def add_sample_logs() -> None:
    """Add sample log entries for testing."""
    sample_entries = [
        LogEntry(
            timestamp=time.time() - 300,
            level="INFO",
            message="Application started",
            module="main",
            function="create_app",
            line=25
        ),
        LogEntry(
            timestamp=time.time() - 240,
            level="INFO",
            message="Database connection established",
            module="database",
            function="connect",
            line=42
        ),
        LogEntry(
            timestamp=time.time() - 180,
            level="WARNING",
            message="High memory usage detected",
            module="monitoring",
            function="check_resources",
            line=67
        ),
        LogEntry(
            timestamp=time.time() - 120,
            level="ERROR",
            message="Failed to connect to external service",
            module="api_client",
            function="make_request",
            line=89
        ),
        LogEntry(
            timestamp=time.time() - 60,
            level="INFO",
            message="Health check completed",
            module="health",
            function="check_all",
            line=15
        )
    ]
    
    for entry in sample_entries:
        add_log_entry(entry)


# Initialize with sample logs
add_sample_logs()
