"""
Performance optimization utilities and middleware
"""

import asyncio
import gzip
import time
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any

from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from sqlalchemy import text
from sqlalchemy.orm import joinedload, selectinload

from app.core.config import settings
from app.core.logging import PerformanceLogger, get_logger
from app.core.monitoring import track_request_metrics

logger = get_logger(__name__)


class CompressionMiddleware(BaseHTTPMiddleware):
    """Middleware for response compression"""

    def __init__(self, app, minimum_size: int = 1024):
        super().__init__(app)
        self.minimum_size = minimum_size

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Only compress if response is large enough and client accepts gzip
        if (
            response.headers.get("content-length")
            and int(response.headers["content-length"]) > self.minimum_size
            and "gzip" in request.headers.get("accept-encoding", "")
        ):
            # Get response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            # Compress body
            compressed_body = gzip.compress(body)

            # Update response
            response.headers["content-encoding"] = "gzip"
            response.headers["content-length"] = str(len(compressed_body))

            return Response(
                content=compressed_body,
                status_code=response.status_code,
                headers=response.headers,
                media_type=response.media_type,
            )

        return response


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring and optimization"""

    def __init__(self, app):
        super().__init__(app)
        self.slow_request_threshold = 2.0  # seconds

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        response = await call_next(request)

        duration = time.perf_counter() - start_time

        # Add performance headers
        response.headers["X-Response-Time"] = f"{duration:.3f}s"

        # Log slow requests
        if duration > self.slow_request_threshold:
            logger.warning(
                "Slow request detected",
                method=request.method,
                path=request.url.path,
                duration=duration,
                threshold=self.slow_request_threshold,
            )

        # Track metrics
        track_request_metrics(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration=duration,
        )

        return response


def async_timeout(seconds: float):
    """Decorator to add timeout to async functions"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except TimeoutError:
                logger.warning(
                    f"Function {func.__name__} timed out",
                    function=func.__name__,
                    timeout=seconds,
                )
                raise

        return wrapper

    return decorator


class DatabaseOptimizer:
    """Database query optimization utilities"""

    @staticmethod
    def optimize_query(query, eager_load_relationships: list[str] = None):
        """Add eager loading to prevent N+1 queries"""
        if eager_load_relationships:
            for relationship in eager_load_relationships:
                if "." in relationship:
                    # Nested relationship
                    query = query.options(selectinload(relationship))
                else:
                    # Simple relationship
                    query = query.options(joinedload(relationship))
        return query

    @staticmethod
    async def analyze_query_performance(session, query_str: str, params: dict = None):
        """Analyze query performance using EXPLAIN"""
        if not settings.debug:
            return None

        try:
            explain_query = text(f"EXPLAIN ANALYZE {query_str}")
            result = await session.execute(explain_query, params or {})
            analysis = result.fetchall()

            logger.debug(
                "Query performance analysis",
                query=query_str,
                analysis=[row[0] for row in analysis],
            )

            return analysis

        except Exception as e:
            logger.warning(f"Query analysis failed: {e}")
            return None


class ConnectionPoolMonitor:
    """Monitor database connection pool performance"""

    def __init__(self, engine):
        self.engine = engine

    def get_pool_status(self) -> dict[str, Any]:
        """Get current connection pool status"""
        pool = self.engine.pool
        return {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid(),
        }

    @asynccontextmanager
    async def monitor_connection(self):
        """Context manager to monitor connection usage"""
        start_status = self.get_pool_status()
        start_time = time.perf_counter()

        try:
            yield
        finally:
            end_time = time.perf_counter()
            end_status = self.get_pool_status()

            duration = end_time - start_time

            logger.debug(
                "Connection pool usage",
                duration=duration,
                start_status=start_status,
                end_status=end_status,
            )


class MemoryOptimizer:
    """Memory usage optimization utilities"""

    @staticmethod
    def optimize_response_data(data: Any, max_depth: int = 10) -> Any:
        """Remove unnecessary data from responses to reduce memory"""
        if max_depth <= 0:
            return data

        if isinstance(data, dict):
            optimized = {}
            for key, value in data.items():
                # Skip internal fields
                if key.startswith("_") or key in [
                    "password",
                    "hashed_password",
                    "secret",
                ]:
                    continue
                optimized[key] = MemoryOptimizer.optimize_response_data(
                    value, max_depth - 1
                )
            return optimized

        elif isinstance(data, (list, tuple)):
            return [
                MemoryOptimizer.optimize_response_data(item, max_depth - 1)
                for item in data
            ]

        return data

    @staticmethod
    async def stream_large_response(data_generator, chunk_size: int = 1000):
        """Stream large responses to reduce memory usage"""
        chunk = []
        async for item in data_generator:
            chunk.append(item)
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []

        if chunk:
            yield chunk


class CacheOptimizer:
    """Cache optimization utilities"""

    @staticmethod
    def should_cache_response(request: Request, response: Response) -> bool:
        """Determine if response should be cached"""
        # Don't cache if:
        # - POST/PUT/DELETE requests
        # - Authentication required
        # - Error responses
        # - Large responses

        if request.method not in ["GET", "HEAD"]:
            return False

        if response.status_code >= 400:
            return False

        content_length = response.headers.get("content-length")
        if content_length and int(content_length) > 1024 * 1024:  # 1MB
            return False

        # Don't cache authenticated requests by default
        if "authorization" in request.headers:
            return False

        return True

    @staticmethod
    def get_cache_ttl(request: Request) -> int:
        """Determine appropriate cache TTL based on request"""
        path = request.url.path

        # Static data can be cached longer
        if "/health" in path or "/info" in path:
            return 300  # 5 minutes

        # Challenge data can be cached moderately
        if "/challenges" in path:
            return 1800  # 30 minutes

        # User-specific data should have short TTL
        if "/users" in path or "/me" in path:
            return 300  # 5 minutes

        # Default TTL
        return 600  # 10 minutes


class BandwidthOptimizer:
    """Optimize bandwidth usage"""

    @staticmethod
    def compress_json_response(data: dict) -> bytes:
        """Compress JSON response"""
        import json

        json_str = json.dumps(data, separators=(",", ":"))
        return gzip.compress(json_str.encode("utf-8"))

    @staticmethod
    def optimize_image_response(image_data: bytes, quality: int = 85) -> bytes:
        """Optimize image responses (if Pillow is available)"""
        try:
            import io

            from PIL import Image

            # Open image
            image = Image.open(io.BytesIO(image_data))

            # Optimize
            output = io.BytesIO()
            image.save(output, format="JPEG", quality=quality, optimize=True)

            return output.getvalue()
        except ImportError:
            logger.warning("PIL not available for image optimization")
            return image_data


class AsyncBatcher:
    """Batch async operations for better performance"""

    def __init__(self, batch_size: int = 50, flush_interval: float = 1.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.batches: dict[str, list] = {}
        self._timers: dict[str, asyncio.Task] = {}

    async def add_to_batch(self, batch_key: str, item: Any, processor: callable):
        """Add item to batch for processing"""
        if batch_key not in self.batches:
            self.batches[batch_key] = []

        self.batches[batch_key].append(item)

        # Set timer for auto-flush if not already set
        if batch_key not in self._timers:
            self._timers[batch_key] = asyncio.create_task(
                self._auto_flush(batch_key, processor)
            )

        # Flush if batch is full
        if len(self.batches[batch_key]) >= self.batch_size:
            await self._flush_batch(batch_key, processor)

    async def _auto_flush(self, batch_key: str, processor: callable):
        """Auto-flush batch after timeout"""
        await asyncio.sleep(self.flush_interval)
        await self._flush_batch(batch_key, processor)

    async def _flush_batch(self, batch_key: str, processor: callable):
        """Flush batch and process items"""
        if batch_key not in self.batches or not self.batches[batch_key]:
            return

        batch = self.batches[batch_key]
        self.batches[batch_key] = []

        # Cancel timer
        if batch_key in self._timers:
            self._timers[batch_key].cancel()
            del self._timers[batch_key]

        try:
            await processor(batch)
        except Exception as e:
            logger.error(f"Batch processing failed for {batch_key}: {e}")


# Performance monitoring decorators
def monitor_performance(operation_name: str):
    """Decorator to monitor function performance"""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with PerformanceLogger(f"{func.__name__}:{operation_name}"):
                return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with PerformanceLogger(f"{func.__name__}:{operation_name}"):
                return func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Global instances
connection_pool_monitor = None  # Will be initialized with engine
async_batcher = AsyncBatcher()


def initialize_performance_monitoring(engine):
    """Initialize performance monitoring components"""
    global connection_pool_monitor
    connection_pool_monitor = ConnectionPoolMonitor(engine)
    logger.info("Performance monitoring initialized")
