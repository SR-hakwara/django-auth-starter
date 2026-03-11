"""Core validators for the application."""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

AVATAR_MAX_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB
AVATAR_ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}


def validate_avatar(file) -> None:
    """Validate avatar upload: size <= 2 MB and allowed image types only."""
    if file.size > AVATAR_MAX_SIZE_BYTES:
        raise ValidationError(
            _("Avatar file size must not exceed 2 MB. Your file is %(size)s MB."),
            code="avatar_too_large",
            params={"size": round(file.size / (1024 * 1024), 1)},
        )

    # Read the first 12 bytes to detect the real MIME type (magic bytes).
    header = file.read(12)
    file.seek(0)  # reset so subsequent reads still work

    mime = _detect_mime(header)
    if mime not in AVATAR_ALLOWED_MIME_TYPES:
        raise ValidationError(
            _("Unsupported image type. Allowed formats: JPEG, PNG, WebP."),
            code="avatar_invalid_type",
        )


def _detect_mime(header: bytes) -> str:
    """Return a MIME type string based on magic bytes, or 'unknown'."""
    if header[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if header[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if header[:4] in (b"RIFF",) and header[8:12] == b"WEBP":
        return "image/webp"
    return "unknown"
