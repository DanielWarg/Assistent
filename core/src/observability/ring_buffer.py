"""
Ring buffer implementation with backpressure handling for logs.
"""
import asyncio
import time
from typing import Any, Dict, List, Optional
from collections import deque
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class BufferPolicy(Enum):
    """Buffer overflow policies."""
    DROP_OLDEST = "drop_oldest"
    BLOCK = "block"
    DROP_NEWEST = "drop_newest"


@dataclass
class LogEntry:
    """Log entry with metadata."""
    timestamp: float
    level: str
    message: str
    module: str
    function: str
    line: int
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    extra: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.extra is None:
            self.extra = {}


class RingBuffer:
    """Thread-safe ring buffer with configurable policies."""
    
    def __init__(
        self, 
        max_size: int = 1000,
        policy: BufferPolicy = BufferPolicy.DROP_OLDEST,
        drop_warning_threshold: float = 0.8
    ):
        self.max_size = max_size
        self.policy = policy
        self.drop_warning_threshold = drop_warning_threshold
        
        self._buffer: deque = deque(maxlen=max_size)
        self._lock = asyncio.Lock()
        self._dropped_count = 0
        self._last_warning = 0
        
        # Performance tracking
        self._add_count = 0
        self._drop_count = 0
        self._start_time = time.time()
    
    async def add(self, entry: LogEntry) -> bool:
        """Add entry to buffer with backpressure handling."""
        async with self._lock:
            if len(self._buffer) >= self.max_size:
                if self.policy == BufferPolicy.DROP_OLDEST:
                    # Oldest entry is automatically removed by deque
                    self._dropped_count += 1
                    self._drop_count += 1
                elif self.policy == BufferPolicy.BLOCK:
                    # Wait for space (with timeout)
                    return await self._wait_for_space(entry)
                elif self.policy == BufferPolicy.DROP_NEWEST:
                    # Drop this entry
                    self._drop_count += 1
                    return False
            
            self._buffer.append(entry)
            self._add_count += 1
            
            # Check if we should warn about high buffer usage
            usage_ratio = len(self._buffer) / self.max_size
            if usage_ratio >= self.drop_warning_threshold:
                await self._warn_high_usage(usage_ratio)
            
            return True
    
    async def _wait_for_space(self, entry: LogEntry, timeout: float = 1.0) -> bool:
        """Wait for space in buffer with timeout."""
        start_time = time.time()
        
        while len(self._buffer) >= self.max_size:
            if time.time() - start_time > timeout:
                logger.warning(f"Buffer full, dropping entry after {timeout}s timeout")
                self._drop_count += 1
                return False
            
            await asyncio.sleep(0.01)  # Small delay to prevent busy waiting
        
        # Add entry once space is available
        self._buffer.append(entry)
        self._add_count += 1
        return True
    
    async def _warn_high_usage(self, usage_ratio: float):
        """Warn about high buffer usage (rate limited)."""
        now = time.time()
        if now - self._last_warning > 60:  # Warn at most once per minute
            logger.warning(
                f"Buffer usage high: {usage_ratio:.1%} "
                f"({len(self._buffer)}/{self.max_size})"
            )
            self._last_warning = now
    
    async def get_recent(self, limit: int = 100) -> List[LogEntry]:
        """Get recent entries from buffer."""
        async with self._lock:
            if limit >= len(self._buffer):
                return list(self._buffer)
            return list(self._buffer)[-limit:]
    
    async def get_all(self) -> List[LogEntry]:
        """Get all entries from buffer."""
        async with self._lock:
            return list(self._buffer)
    
    async def clear(self) -> int:
        """Clear buffer and return number of entries cleared."""
        async with self._lock:
            count = len(self._buffer)
            self._buffer.clear()
            return count
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get buffer statistics."""
        async with self._lock:
            now = time.time()
            uptime = now - self._start_time
            
            return {
                "current_size": len(self._buffer),
                "max_size": self.max_size,
                "usage_ratio": len(self._buffer) / self.max_size,
                "total_added": self._add_count,
                "total_dropped": self._drop_count,
                "dropped_oldest": self._dropped_count,
                "add_rate": self._add_count / uptime if uptime > 0 else 0,
                "drop_rate": self._drop_count / uptime if uptime > 0 else 0,
                "uptime_seconds": uptime,
                "policy": self.policy.value
            }
    
    async def search(
        self,
        level: Optional[str] = None,
        module: Optional[str] = None,
        correlation_id: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: int = 100
    ) -> List[LogEntry]:
        """Search entries with filters."""
        async with self._lock:
            results = []
            
            for entry in reversed(self._buffer):  # Search from newest first
                if len(results) >= limit:
                    break
                
                # Apply filters
                if level and entry.level != level:
                    continue
                if module and entry.module != module:
                    continue
                if correlation_id and entry.correlation_id != correlation_id:
                    continue
                if start_time and entry.timestamp < start_time:
                    continue
                if end_time and entry.timestamp > end_time:
                    continue
                
                results.append(entry)
            
            return results


# Global log buffer instance - will be configured in main.py
log_buffer: RingBuffer = None


def initialize_log_buffer(max_size: int = 1000, policy: str = "drop_oldest") -> RingBuffer:
    """Initialize the global log buffer with settings."""
    global log_buffer
    
    policy_enum = BufferPolicy.DROP_OLDEST
    if policy == "block":
        policy_enum = BufferPolicy.BLOCK
    elif policy == "drop_newest":
        policy_enum = BufferPolicy.DROP_NEWEST
    
    log_buffer = RingBuffer(
        max_size=max_size,
        policy=policy_enum
    )
    
    return log_buffer
