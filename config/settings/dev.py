"""
Django development settings.

Extends base settings with development-friendly defaults:
- DEBUG enabled
- SQLite database
- Console email backend
"""

from .base import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Debug
# ---------------------------------------------------------------------------
DEBUG = True

# ---------------------------------------------------------------------------
# Database — SQLite for easy local dev
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# ---------------------------------------------------------------------------
# Email — Mailpit (http://localhost:8025)
# SMTP server on port 1025, web UI on port 8025
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = False

# ---------------------------------------------------------------------------
# Static & Media Files — simple in dev
# ---------------------------------------------------------------------------
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# ---------------------------------------------------------------------------
# Security — relaxed for local dev
# ---------------------------------------------------------------------------
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
