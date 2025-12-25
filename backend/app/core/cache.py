"""
Caching layer with Redis backend for performance optimization
"""

import hashlib
import pickle
from datetime import datetime, timedelta
from functools import wraps
from typing import Any

import redis.asyncio as redis
from redis.asyncio import Redis

from app.core.config import settings
from app.core.logging import get_logger
from app.core.resilience import circuit_breaker

logger = get_logger(__name__)


class CacheManager:
    """Redis-based cache manager with fallback to in-memory cache"""

    def __init__(self):
        self.redis_client: Redis | None = None
        self._memory_cache: dict[str, dict[str, Any]] = {}
        self._memory_cache_ttl: dict[str, datetime] = {}
        self._max_memory_items = 1000

    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                settings.redis_url,
                max_connections=settings.redis_max_connections,
                decode_responses=False,  # We'll handle encoding ourselves
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30,
            )

            # Test connection
            await self.redis_client.ping()
            logger.info("Redis cache initialized successfully")

        except Exception as e:
            logger.warning(
                f"Redis initialization failed, falling back to memory cache: {e}"
            )
            self.redis_client = None

    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()

    @circuit_breaker("redis")
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        try:
            if self.redis_client:
                value = await self.redis_client.get(key)
                if value is not None:
                    return pickle.loads(value)
            else:
                # Fallback to memory cache
                if key in self._memory_cache:
                    if key in self._memory_cache_ttl:
                        if datetime.utcnow() > self._memory_cache_ttl[key]:
                            # Expired
                            del self._memory_cache[key]
                            del self._memory_cache_ttl[key]
                        else:
                            return self._memory_cache[key]["value"]
                    else:
                        return self._memory_cache[key]["value"]

            return default

        except Exception as e:
            logger.warning(f"Cache get failed for key {key}: {e}")
            return default

    @circuit_breaker("redis")
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL in seconds"""
        try:
            if self.redis_client:
                serialized = pickle.dumps(value)
                await self.redis_client.setex(key, ttl, serialized)
                return True
            else:
                # Fallback to memory cache
                self._memory_cache[key] = {"value": value}
                if ttl > 0:
                    self._memory_cache_ttl[key] = datetime.utcnow() + timedelta(
                        seconds=ttl
                    )

                # Cleanup memory cache if too large
                if len(self._memory_cache) > self._max_memory_items:
                    # Remove oldest items
                    keys_to_remove = list(self._memory_cache.keys())[:100]
                    for k in keys_to_remove:
                        del self._memory_cache[k]
                        self._memory_cache_ttl.pop(k, None)

                return True

        except Exception as e:
            logger.warning(f"Cache set failed for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if self.redis_client:
                await self.redis_client.delete(key)
            else:
                self._memory_cache.pop(key, None)
                self._memory_cache_ttl.pop(key, None)
            return True
        except Exception as e:
            logger.warning(f"Cache delete failed for key {key}: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            count = 0
            if self.redis_client:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    count = await self.redis_client.delete(*keys)
            else:
                # Memory cache doesn't support patterns efficiently
                keys_to_delete = [
                    k
                    for k in self._memory_cache.keys()
                    if pattern.replace("*", "") in k
                ]
                for key in keys_to_delete:
                    self._memory_cache.pop(key, None)
                    self._memory_cache_ttl.pop(key, None)
                count = len(keys_to_delete)

            logger.info(f"Cleared {count} keys matching pattern {pattern}")
            return count

        except Exception as e:
            logger.warning(f"Cache clear pattern failed for {pattern}: {e}")
            return 0


# Global cache manager instance
cache_manager = CacheManager()


def cache_key(*args, prefix: str = "", **kwargs) -> str:
    """Generate cache key from arguments"""
    key_data = {"args": args, "kwargs": sorted(kwargs.items())}
    key_hash = hashlib.md5(str(key_data).encode()).hexdigest()
    return f"{prefix}:{key_hash}" if prefix else key_hash


def cached(ttl: int = 3600, prefix: str = "", key_func: callable | None = None):
    """
    Caching decorator for functions

    Args:
        ttl: Time to live in seconds
        prefix: Key prefix
        key_func: Custom key generation function
    """

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = cache_key(*args, prefix=f"{prefix}:{func.__name__}", **kwargs)

            # Try to get from cache
            cached_result = await cache_manager.get(key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}", key=key)
                return cached_result

            # Execute function
            logger.debug(f"Cache miss for {func.__name__}", key=key)
            result = await func(*args, **kwargs)

            # Cache result
            await cache_manager.set(key, result, ttl)
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, we can't use async cache directly
            # This is a simplified version that could be enhanced
            import asyncio

            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = cache_key(*args, prefix=f"{prefix}:{func.__name__}", **kwargs)

            result = func(*args, **kwargs)
            # Fire-and-forget cache set
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(cache_manager.set(key, result, ttl))
            except RuntimeError:
                pass  # No event loop running

            return result

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Specific cache utilities for common use cases
class UserCache:
    """Cache utilities for user data"""

    @staticmethod
    async def get_user_profile(user_id: str) -> dict | None:
        """Get cached user profile"""
        return await cache_manager.get(f"user_profile:{user_id}")

    @staticmethod
    async def set_user_profile(user_id: str, profile: dict, ttl: int = 1800):
        """Cache user profile for 30 minutes"""
        await cache_manager.set(f"user_profile:{user_id}", profile, ttl)

    @staticmethod
    async def invalidate_user(user_id: str):
        """Invalidate all user-related cache"""
        await cache_manager.clear_pattern(f"user_*:{user_id}*")


class AICache:
    """Cache utilities for AI responses"""

    @staticmethod
    def generate_ai_key(
        prompt: str, model: str, temperature: float, max_tokens: int
    ) -> str:
        """Generate cache key for AI responses"""
        key_data = f"{prompt}:{model}:{temperature}:{max_tokens}"
        return f"ai_response:{hashlib.sha256(key_data.encode()).hexdigest()}"

    @staticmethod
    async def get_ai_response(
        prompt: str, model: str, temperature: float, max_tokens: int
    ) -> str | None:
        """Get cached AI response"""
        key = AICache.generate_ai_key(prompt, model, temperature, max_tokens)
        return await cache_manager.get(key)

    @staticmethod
    async def set_ai_response(
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        response: str,
        ttl: int = 7200,  # 2 hours
    ):
        """Cache AI response"""
        key = AICache.generate_ai_key(prompt, model, temperature, max_tokens)
        await cache_manager.set(key, response, ttl)


class ChallengeCache:
    """Cache utilities for challenge data"""

    @staticmethod
    @cached(ttl=3600, prefix="challenge")
    async def get_challenge(challenge_id: str):
        """Cached challenge lookup (decorator example)"""
        # This would be implemented in the challenge service
        pass

    @staticmethod
    async def invalidate_challenge(challenge_id: str):
        """Invalidate challenge-related cache"""
        await cache_manager.clear_pattern(f"challenge*:{challenge_id}*")


# Rate limiting cache utilities
class RateLimitCache:
    """Redis-based rate limiting"""

    @staticmethod
    async def is_rate_limited(key: str, limit: int, window: int) -> bool:
        """
        Check if key is rate limited using sliding window

        Args:
            key: Rate limit key (e.g., user_id, ip_address)
            limit: Maximum requests allowed
            window: Time window in seconds

        Returns:
            True if rate limited, False otherwise
        """
        try:
            if not cache_manager.redis_client:
                # Fallback: always allow if Redis unavailable
                return False

            now = datetime.utcnow().timestamp()
            pipeline = cache_manager.redis_client.pipeline()

            # Remove expired entries
            pipeline.zremrangebyscore(key, 0, now - window)

            # Count current requests
            pipeline.zcard(key)

            # Add current request
            pipeline.zadd(key, {str(now): now})

            # Set expiration
            pipeline.expire(key, window)

            results = await pipeline.execute()
            current_count = results[1]

            return current_count >= limit

        except Exception as e:
            logger.warning(f"Rate limit check failed for {key}: {e}")
            return False  # Fail open

    @staticmethod
    async def get_rate_limit_status(
        key: str, limit: int, window: int
    ) -> dict[str, Any]:
        """Get detailed rate limit status"""
        try:
            if not cache_manager.redis_client:
                return {
                    "requests": 0,
                    "limit": limit,
                    "remaining": limit,
                    "reset_time": datetime.utcnow().timestamp() + window,
                }

            now = datetime.utcnow().timestamp()

            # Clean and count
            await cache_manager.redis_client.zremrangebyscore(key, 0, now - window)
            current_count = await cache_manager.redis_client.zcard(key)

            return {
                "requests": current_count,
                "limit": limit,
                "remaining": max(0, limit - current_count),
                "reset_time": now + window,
            }

        except Exception as e:
            logger.warning(f"Rate limit status check failed for {key}: {e}")
            return {
                "requests": 0,
                "limit": limit,
                "remaining": limit,
                "reset_time": datetime.utcnow().timestamp() + window,
            }
