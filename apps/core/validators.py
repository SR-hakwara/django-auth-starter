"""Core validators for the application."""

import re
from typing import cast

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import gettext_lazy as _

# Maximum permitted avatar file size.  2 MB is a reasonable upper bound that
# accommodates high-resolution profile pictures while protecting against
# trivially large uploads clogging storage.
AVATAR_MAX_SIZE_BYTES: int = 2 * 1024 * 1024  # 2 MB

# MIME types accepted for avatar uploads.  Validation is performed against
# magic bytes (not the Content-Type header) to prevent extension spoofing.
AVATAR_ALLOWED_MIME_TYPES: frozenset[str] = frozenset(
    {"image/jpeg", "image/png", "image/webp"}
)


def validate_avatar(file: UploadedFile) -> None:
    """Validate an uploaded avatar file for size and image type.

    Performs two checks:
    1. **Size**: the file must not exceed ``AVATAR_MAX_SIZE_BYTES`` (2 MB).
    2. **Type**: the real MIME type is inferred from the first 12 magic bytes
       of the file content, *not* the ``Content-Type`` header or the file
       extension — both of which can be trivially spoofed by an attacker.

    After reading the magic bytes the file cursor is reset to position 0 so
    subsequent reads by Django's storage backend work correctly.

    Args:
        file: An ``UploadedFile``-like object exposing ``size``, ``read(n)``,
            and ``seek(0)`` attributes.

    Raises:
        ValidationError: If the file exceeds 2 MB or is not a JPEG, PNG,
            or WebP image.
    """
    # file.size is int | None per Django stubs; treat None as 0 (can't happen
    # for an in-memory upload, but the guard keeps the type-checker happy).
    file_size: int = file.size or 0
    if file_size > AVATAR_MAX_SIZE_BYTES:
        raise ValidationError(
            _("Avatar file size must not exceed 2 MB. Your file is %(size)s MB."),
            code="avatar_too_large",
            params={"size": round(file_size / (1024 * 1024), 1)},
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
    """Identify a MIME type from the leading magic bytes of a file.

    Checks against known byte signatures ("magic numbers") for JPEG, PNG,
    and WebP.  This approach is intentionally conservative: only formats
    explicitly listed in ``AVATAR_ALLOWED_MIME_TYPES`` can be approved; any
    unrecognised header returns ``'unknown'`` which will fail validation.

    Args:
        header: The first 12 bytes of the file content.

    Returns:
        One of ``'image/jpeg'``, ``'image/png'``, ``'image/webp'``, or
        ``'unknown'`` if the signature is not recognised.
    """
    if header[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if header[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if header[:4] in (b"RIFF",) and header[8:12] == b"WEBP":
        return "image/webp"
    return "unknown"


class PasswordComplexityValidator:
    """Enforce that passwords contain at least one uppercase letter, one
    lowercase letter, one digit, and one special character.

    This validator is intended to be listed in ``AUTH_PASSWORD_VALIDATORS``
    so it is applied automatically by Django's ``validate_password`` helper,
    covering both the registration form and the password-change flow.
    """

    def validate(self, password: str, user: object = None) -> None:
        errors: list[ValidationError] = []
        if not re.search(r"[A-Z]", password):
            errors.append(
                ValidationError(
                    _("Password must contain at least one uppercase letter."),
                    code="password_no_upper",
                )
            )
        if not re.search(r"[a-z]", password):
            errors.append(
                ValidationError(
                    _("Password must contain at least one lowercase letter."),
                    code="password_no_lower",
                )
            )
        if not re.search(r"\d", password):
            errors.append(
                ValidationError(
                    _("Password must contain at least one digit."),
                    code="password_no_digit",
                )
            )
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;'/`~]", password):
            errors.append(
                ValidationError(
                    _("Password must contain at least one special character."),
                    code="password_no_special",
                )
            )
        if errors:
            raise ValidationError(errors)

    def get_help_text(self) -> str:
        return cast(
            str,
            _(
                "Your password must contain at least one uppercase letter, one lowercase "
                "letter, one digit, and one special character."
            ),
        )
