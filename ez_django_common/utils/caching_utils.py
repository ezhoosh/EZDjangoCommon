"""
Versioned caching utilities for API responses.
Provides automatic cache invalidation based on Redis version counters.
"""

import hashlib
import json
from typing import Any, Optional, Callable
from functools import wraps

from django.core.cache import cache
from django.conf import settings


# Cache key prefix for version counters``
VERSION_KEY_PREFIX = "cache_version:"


def get_version(version_key: str) -> int:
    """
    Get current version from Redis for a cache key.
    Creates the key with version 1 if it doesn't exist.

    Args:
        version_key: Identifier for the version counter (e.g., 'product_list')

    Returns:
        Current version number
    """
    redis_key = f"{VERSION_KEY_PREFIX}{version_key}"
    version = cache.get(redis_key)

    if version is None:
        # Initialize version to 1
        cache.set(redis_key, 1, timeout=None)  # Never expire version counters
        return 1

    return int(version)


def increment_version(version_key: str) -> int:
    """
    Atomically increment version counter in Redis.

    Args:
        version_key: Identifier for the version counter

    Returns:
        New version number after increment
    """
    redis_key = f"{VERSION_KEY_PREFIX}{version_key}"

    try:
        # Try atomic increment (works with Redis backend)
        new_version = cache.incr(redis_key)
    except (ValueError, AttributeError):
        # Fallback for non-Redis backends or if key doesn't exist
        current = get_version(version_key)
        new_version = current + 1
        cache.set(redis_key, new_version, timeout=None)

    return new_version


def get_cache_key_with_version(base_key: str, version_key: str, **kwargs) -> str:
    """
    Generate a versioned cache key.

    Args:
        base_key: Base identifier for the cache (e.g., 'product_list')
        version_key: Key to look up version counter in Redis
        **kwargs: Additional parameters to include in cache key (e.g., filters, page)

    Returns:
        Versioned cache key string
    """
    version = get_version(version_key)

    # Sort kwargs for consistent key generation
    if kwargs:
        params_str = json.dumps(kwargs, sort_keys=True, default=str)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"{base_key}:v{version}:{params_hash}"

    return f"{base_key}:v{version}"


def get_cache_timeout() -> int:
    """Get cache timeout from settings or use default."""
    return getattr(settings, "API_CACHE_TIMEOUT", 3600)  # 1 hour default


def invalidate_cache(version_key: str) -> int:
    """
    Invalidate all caches associated with a version key by incrementing the version.

    Args:
        version_key: Version counter key in Redis to increment

    Returns:
        New version number
    """
    return increment_version(version_key)


def versioned_cache(version_key: str, timeout: Optional[int] = None):
    """
    Decorator for caching function results with version-based invalidation.

    Usage:
        @versioned_cache('product_list')
        def get_products(filters):
            return expensive_query()

    Args:
        version_key: Version counter key in Redis for tracking this cache
        timeout: Cache timeout in seconds (uses setting default if None)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            func_key = f"{func.__module__}.{func.__name__}"
            cache_key = get_cache_key_with_version(
                func_key, version_key, args=str(args), kwargs=kwargs
            )

            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result

            # Cache miss - compute result
            result = func(*args, **kwargs)

            # Store in cache
            cache_timeout = timeout if timeout is not None else get_cache_timeout()
            cache.set(cache_key, result, cache_timeout)

            return result

        return wrapper

    return decorator


class CachedQuerySet:
    """
    Helper for caching QuerySet results with versioning.
    """

    def __init__(
        self,
        queryset,
        version_key: str,
        cache_key_base: str,
        timeout: Optional[int] = None,
    ):
        self.queryset = queryset
        self.version_key = version_key
        self.cache_key_base = cache_key_base
        self.timeout = timeout if timeout is not None else get_cache_timeout()

    def get_or_set(self, serializer_class=None, **filters) -> Any:
        """
        Get cached results or compute and cache them.

        Args:
            serializer_class: Optional serializer to apply to queryset
            **filters: Additional filters for cache key generation

        Returns:
            Cached or freshly computed data
        """
        cache_key = get_cache_key_with_version(
            self.cache_key_base, self.version_key, **filters
        )

        # Try cache first
        result = cache.get(cache_key)
        if result is not None:
            return result

        # Cache miss - compute
        if serializer_class:
            result = serializer_class(self.queryset, many=True).data
        else:
            result = list(self.queryset.values())

        # Store in cache
        cache.set(cache_key, result, self.timeout)

        return result


def get_request_cache_key(request, base_key: str, version_key: str) -> str:
    """
    Generate cache key from DRF request parameters.

    Args:
        request: DRF Request object
        base_key: Base cache key
        version_key: Version key to look up

    Returns:
        Versioned cache key including query parameters
    """
    query_params = dict(request.query_params)
    # Remove sensitive/variable params
    query_params.pop("timestamp", None)
    query_params.pop("_", None)

    return get_cache_key_with_version(
        base_key, version_key, path=request.path, **query_params
    )
