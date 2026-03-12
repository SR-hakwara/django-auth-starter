"""
Django production settings.

Extends base settings with production hardening:
- PostgreSQL database
- SMTP email
- Full security headers
- HSTS enabled
"""

from .base import *  # noqa: F401, F403
from .base import env

# ---------------------------------------------------------------------------
# Debug
# ---------------------------------------------------------------------------
DEBUG = False

# ---------------------------------------------------------------------------
# Allowed hosts (must be set in .env)
# ---------------------------------------------------------------------------
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")

# ---------------------------------------------------------------------------
# Database — PostgreSQL
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        **env.db_url("DATABASE_URL"),
        "CONN_MAX_AGE": 60,  # Reuse connections; avoids a new TCP handshake per request
    },
}

# ---------------------------------------------------------------------------
# Email — SMTP
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="smtp.example.com") #type: ignore[assignment]
EMAIL_PORT = env.int("EMAIL_PORT", default=587) #type: ignore[assignment]
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="") #type: ignore[assignment]
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="") #type: ignore[assignment]
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True) #type: ignore[assignment]
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@example.com") #type: ignore[assignment]

# ---------------------------------------------------------------------------
# Security — Hardened
# ---------------------------------------------------------------------------
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True) #type: ignore[assignment]

SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Required when the app sits behind a TLS-terminating reverse proxy.
# Django 4.0+ rejects POST/PUT requests whose Origin header doesn't match the
# Host header unless the origin is in this list.
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[]) #type: ignore[assignment]

# ---------------------------------------------------------------------------
# Cache — Redis (required for shared, atomic rate limiting across workers)
# ---------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://redis:6379/1"),#type: ignore[assignment]
    }
}
