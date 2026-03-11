"""Core utilities for the application."""

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest

# Rate Limiting Helpers moved from views.py

def get_rate_limit_key(request: HttpRequest) -> str:
    """Build a cache key for login rate limiting based on IP."""
    ip = request.META.get("REMOTE_ADDR", "unknown")
    return f"login_attempts_{ip}"

def is_rate_limited(request: HttpRequest) -> bool:
    """Check if the current IP has exceeded login attempts."""
    key = get_rate_limit_key(request)
    attempts = cache.get(key, 0)
    max_attempts = getattr(settings, "LOGIN_RATE_LIMIT_MAX_ATTEMPTS", 5)
    return attempts >= max_attempts

def record_failed_attempt(request: HttpRequest) -> None:
    """Increment failed login counter for this IP."""
    key = get_rate_limit_key(request)
    timeout = getattr(settings, "LOGIN_RATE_LIMIT_TIMEOUT", 300)
    attempts = cache.get(key, 0)
    cache.set(key, attempts + 1, timeout)

def clear_failed_attempts(request: HttpRequest) -> None:
    """Clear failed login counter on successful login."""
    key = get_rate_limit_key(request)
    cache.delete(key)
