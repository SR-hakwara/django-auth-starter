"""Tests for apps/core/validators.py — avatar upload validation."""

from unittest.mock import MagicMock

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.core.validators import AVATAR_MAX_SIZE_BYTES, validate_avatar


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_jpeg() -> SimpleUploadedFile:
    """Minimal valid JPEG file (first 4 magic bytes + padding)."""
    data = b"\xff\xd8\xff\xe0" + b"\x00" * 20
    return SimpleUploadedFile("test.jpg", data, content_type="image/jpeg")


def _make_png() -> SimpleUploadedFile:
    """Minimal valid PNG file (8-byte signature + padding)."""
    data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20
    return SimpleUploadedFile("test.png", data, content_type="image/png")


def _make_webp() -> SimpleUploadedFile:
    """Minimal valid WebP file (RIFF....WEBP magic bytes + padding)."""
    data = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 20
    return SimpleUploadedFile("test.webp", data, content_type="image/webp")


def _make_invalid() -> SimpleUploadedFile:
    """File whose magic bytes are not JPEG, PNG, or WebP (GIF header)."""
    data = b"GIF89a" + b"\x00" * 20
    return SimpleUploadedFile("test.gif", data, content_type="image/gif")


def _make_oversized():
    """Mock file object that reports a size exceeding the 2 MB limit."""
    mock = MagicMock()
    mock.size = AVATAR_MAX_SIZE_BYTES + 1
    return mock


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_validate_avatar_jpeg_accepted():
    """A JPEG file within the size limit should pass without error."""
    validate_avatar(_make_jpeg())


def test_validate_avatar_png_accepted():
    """A PNG file within the size limit should pass without error."""
    validate_avatar(_make_png())


def test_validate_avatar_webp_accepted():
    """A WebP file within the size limit should pass without error."""
    validate_avatar(_make_webp())


def test_validate_avatar_invalid_type_rejected():
    """A GIF (or any unsupported format) should raise ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        validate_avatar(_make_invalid())
    assert exc_info.value.code == "avatar_invalid_type"


def test_validate_avatar_oversized_rejected():
    """A file exceeding 2 MB should raise ValidationError before MIME check."""
    with pytest.raises(ValidationError) as exc_info:
        validate_avatar(_make_oversized())
    assert exc_info.value.code == "avatar_too_large"


def test_validate_avatar_empty_file_rejected():
    """An empty file should fail the MIME check (no magic bytes match)."""
    empty = SimpleUploadedFile("empty.jpg", b"", content_type="image/jpeg")
    with pytest.raises(ValidationError) as exc_info:
        validate_avatar(empty)
    assert exc_info.value.code == "avatar_invalid_type"
