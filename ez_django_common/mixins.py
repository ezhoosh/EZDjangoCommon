"""
Mixins for Django models and DRF ViewSets with declarative caching.

Provides automatic caching for DRF list/retrieve actions and
model-level cache invalidation on save/delete.
"""

from functools import wraps
from logging import getLogger

from django.core.cache import cache
from rest_framework.response import Response

from ez_django_common.utils.caching_utils import (
    get_cache_key_with_version,
    invalidate_cache,
)

logger = getLogger(__name__)


# =============================================================================
# MODEL MIXINS
# =============================================================================


class CacheInvalidationMixin:
    """
    Model mixin that automatically invalidates cache version on save() and delete().

    This replaces the need for Django signals by directly hooking into
    model lifecycle methods.

    Supports both single and multiple cache keys:
    - cache_version_key: str - single cache key (backward compatible)
    - cache_version_keys: list - multiple cache keys (new feature)

    Usage:
        # Single key (backward compatible):
        class Category(CacheInvalidationMixin, models.Model):
            cache_version_key = 'category_list'

        # Multiple keys (new feature):
        class Product(CacheInvalidationMixin, models.Model):
            cache_version_keys = ['product_list', 'product_detail']

        # Or both (for backward compatibility):
        class Product(CacheInvalidationMixin, models.Model):
            cache_version_key = 'product_list'  # For backward compatibility
            cache_version_keys = ['product_list', 'product_detail']
    """

    # Cache version key to invalidate (must be set in subclass)
    cache_version_key = None
    cache_version_keys = None  # New: support multiple keys

    def _get_cache_keys(self):
        """Get all cache keys to invalidate."""
        keys = []

        # Add multiple keys if defined
        if self.cache_version_keys:
            if isinstance(self.cache_version_keys, (list, tuple)):
                keys.extend(self.cache_version_keys)
            else:
                keys.append(self.cache_version_keys)

        # Add single key if defined (and not already in keys)
        if self.cache_version_key and self.cache_version_key not in keys:
            keys.append(self.cache_version_key)

        return keys

    def save(self, *args, **kwargs):
        """Override save to invalidate cache after saving."""
        # Call parent save first
        result = super().save(*args, **kwargs)

        # Invalidate all cache versions
        for key in self._get_cache_keys():
            invalidate_cache(key)

        return result

    def delete(self, *args, **kwargs):
        """Override delete to invalidate cache after deletion."""
        # Invalidate all cache versions first (before object is gone)
        for key in self._get_cache_keys():
            invalidate_cache(key)

        # Call parent delete
        return super().delete(*args, **kwargs)


# =============================================================================
# DRF VIEWSET MIXINS
# =============================================================================


class CachedListMixin:
    """
    Mixin for caching list() responses in DRF viewsets.

    Usage:
        class MyViewSet(CachedListMixin, viewsets.ModelViewSet):
            cache_key_prefix = "my_model"
            cache_version_key = "my_model_list"
            cache_timeout = 60 * 15  # 15 minutes
            cache_hit_message = "Cache hit for list"  # optional
    """

    cache_key_prefix = None
    cache_version_key = None
    cache_timeout = 60 * 15  # 15 minutes default
    cache_hit_message = None

    def list(self, request, *args, **kwargs):
        """Override list to add caching."""
        if not self.cache_key_prefix or not self.cache_version_key:
            # If not configured, fallback to default behavior
            return super().list(request, *args, **kwargs)

        # Build cache key from query params
        query_params = dict(request.query_params)
        cache_key = get_cache_key_with_version(
            base_key=self.cache_key_prefix,
            version_key=self.cache_version_key,
            params=query_params,
        )

        # Try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            if self.cache_hit_message:
                logger.info(self.cache_hit_message)
            return Response(cached_data)

        # Get fresh data
        response = super().list(request, *args, **kwargs)

        # Cache the response data
        if response.status_code == 200:
            cache.set(cache_key, response.data, self.cache_timeout)

        return response


class CachedRetrieveMixin:
    """
    Mixin for caching retrieve() responses in DRF viewsets.

    Usage:
        class MyViewSet(CachedRetrieveMixin, viewsets.ModelViewSet):
            cache_key_prefix = "my_model"
            cache_detail_version_key = "my_model_detail"
            cache_timeout = 60 * 15  # 15 minutes
            cache_hit_message = "Cache hit for detail"  # optional
    """

    cache_key_prefix = None
    cache_detail_version_key = None
    cache_timeout = 60 * 15  # 15 minutes default
    cache_hit_message = None

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to add caching."""
        if not self.cache_key_prefix or not self.cache_detail_version_key:
            # If not configured, fallback to default behavior
            return super().retrieve(request, *args, **kwargs)

        # Build cache key from pk and query params
        pk = kwargs.get("pk")
        query_params = dict(request.query_params)
        query_params["pk"] = pk

        cache_key = get_cache_key_with_version(
            base_key=f"{self.cache_key_prefix}_detail",
            version_key=self.cache_detail_version_key,
            params=query_params,
        )

        # Try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            if self.cache_hit_message:
                logger.info(self.cache_hit_message)
            return Response(cached_data)

        # Get fresh data
        response = super().retrieve(request, *args, **kwargs)

        # Cache the response data
        if response.status_code == 200:
            cache.set(cache_key, response.data, self.cache_timeout)

        return response


class CachedViewSetMixin(CachedListMixin, CachedRetrieveMixin):
    """
    Combined mixin for caching both list() and retrieve() in DRF viewsets.

    Usage:
        class MyViewSet(CachedViewSetMixin, viewsets.ModelViewSet):
            cache_key_prefix = "my_model"
            cache_list_version_key = "my_model_list"
            cache_detail_version_key = "my_model_detail"
            cache_timeout = 60 * 15  # 15 minutes
            cache_list_hit_message = "Cache hit for list"  # optional
            cache_detail_hit_message = "Cache hit for detail"  # optional
    """

    cache_list_version_key = None
    cache_detail_version_key = None
    cache_list_hit_message = None
    cache_detail_hit_message = None

    @property
    def cache_version_key(self):
        """Provide cache_version_key for CachedListMixin."""
        return self.cache_list_version_key

    def list(self, request, *args, **kwargs):
        """Override list with custom hit message."""
        # Temporarily set cache_hit_message for list
        original_message = getattr(self, "cache_hit_message", None)
        if self.cache_list_hit_message:
            self.cache_hit_message = self.cache_list_hit_message

        result = super().list(request, *args, **kwargs)

        # Restore original message
        self.cache_hit_message = original_message
        return result

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve with custom hit message."""
        # Temporarily set cache_hit_message for retrieve
        original_message = getattr(self, "cache_hit_message", None)
        if self.cache_detail_hit_message:
            self.cache_hit_message = self.cache_detail_hit_message

        result = super().retrieve(request, *args, **kwargs)

        # Restore original message
        self.cache_hit_message = original_message
        return result


def cached_action(version_key, timeout=60 * 15, key_prefix=None):
    """
    Decorator for caching custom DRF actions.

    Usage:
        @cached_action(version_key="my_custom_action", timeout=60*30)
        @action(detail=False, methods=['get'])
        def custom_action(self, request):
            # Your action logic
            return Response(data)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # Build cache key
            base_key = key_prefix or f"{self.cache_key_prefix}_{func.__name__}"
            query_params = dict(request.query_params)

            cache_key = get_cache_key_with_version(
                base_key=base_key, version_key=version_key, params=query_params
            )

            # Try to get from cache
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return Response(cached_data)

            # Get fresh data
            response = func(self, request, *args, **kwargs)

            # Cache the response data
            if isinstance(response, Response) and response.status_code == 200:
                cache.set(cache_key, response.data, timeout)

            return response

        return wrapper

    return decorator
