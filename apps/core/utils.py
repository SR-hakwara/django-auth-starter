"""Core utilities for the application.

Currently provides an IP-based rate-limiting facility backed by Django's
cache framework.  All helpers are intentionally stateless so they can be
reused by any view without importing app-specific models.
"""

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest
from ipware import get_client_ip


def get_rate_limit_key(request: HttpRequest, key_prefix: str = "login_attempts") -> str:
    """Build a cache key for rate limiting based on real client IP.

    Uses ``django-ipware`` so the correct IP is extracted even behind a reverse
    proxy that sets ``X-Forwarded-For`` (e.g. Nginx, AWS ALB, Cloudflare).
    Falls back to ``'unknown'`` when no IP can be determined.
    """
    ip, _ = get_client_ip(request)
    return f"{key_prefix}_{ip or 'unknown'}"


def is_rate_limited(request: HttpRequest, key_prefix: str = "login_attempts") -> bool:
    """Check if the current IP has exceeded the allowed number of attempts."""
    key = get_rate_limit_key(request, key_prefix)
    attempts = cache.get(key, 0)
    max_attempts = getattr(settings, "LOGIN_RATE_LIMIT_MAX_ATTEMPTS", 5)
    return bool(attempts >= max_attempts)


def record_failed_attempt(
    request: HttpRequest, key_prefix: str = "login_attempts"
) -> None:
    """Atomically increment the failed attempt counter for this IP.

    Uses cache.add() + cache.incr() to avoid the read-then-write race condition
    that would occur with cache.get() + cache.set().
    """
    key = get_rate_limit_key(request, key_prefix)
    timeout = getattr(settings, "LOGIN_RATE_LIMIT_TIMEOUT", 300)
    # add() only sets the key if it does not already exist (atomic).
    # Initial value is 1 so the first call already counts as one attempt.
    added = cache.add(key, 1, timeout)
    if not added:
        try:
            cache.incr(key)
        except ValueError:
            # Key expired between add() check and incr() — start fresh.
            cache.add(key, 1, timeout)


def clear_failed_attempts(
    request: HttpRequest, key_prefix: str = "login_attempts"
) -> None:
    """Clear the failed attempt counter on successful action."""
    key = get_rate_limit_key(request, key_prefix)
    cache.delete(key)
