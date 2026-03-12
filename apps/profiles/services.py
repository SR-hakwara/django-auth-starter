"""Business logic layer for the profiles app."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.core.files.uploadedfile import UploadedFile

if TYPE_CHECKING:
    from apps.users.models import CustomUser

logger = logging.getLogger(__name__)


def update_profile(
    *,
    user: "CustomUser",
    username: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    avatar: UploadedFile | None = None,
    remove_avatar: bool = False,
) -> None:
    """Apply selective field updates to a user's profile in one database write.

    Only fields that have actually changed are included in the
    ``update_fields`` list, so unrelated columns are not touched and
    Django's ``pre_save`` / ``post_save`` signal overhead is minimised.

    Email changes automatically clear ``is_email_verified`` so the user
    must confirm ownership of the new address before gaining verified
    access again.

    Avatar lifecycle:
    - ``remove_avatar=True``: the existing file is deleted and the field
      is set to ``None``.
    - ``avatar`` is an ``UploadedFile``: the old file (if any) is deleted
      and replaced with the new upload.
    - Neither flag set: the avatar is left unchanged.

    Args:
        user: The ``CustomUser`` instance to update (mutated in place).
        username: New username, or ``None`` to leave unchanged.
        first_name: New first name, or ``None`` to leave unchanged.
        last_name: New last name, or ``None`` to leave unchanged.
        email: New email address, or ``None`` to leave unchanged.  When
            provided and different from the current value, resets
            ``is_email_verified`` to ``False``.
        avatar: A newly uploaded avatar file, or ``None``.
        remove_avatar: When ``True``, delete the current avatar and clear
            the field regardless of the ``avatar`` parameter.
    """
    update_fields: list[str] = []

    if username is not None and username != user.username:
        user.username = username
        update_fields.append("username")

    if first_name is not None:
        user.first_name = first_name
        update_fields.append("first_name")

    if last_name is not None:
        user.last_name = last_name
        update_fields.append("last_name")

    if email is not None and email != user.email:
        user.email = email
        user.is_email_verified = False
        update_fields.extend(["email", "is_email_verified"])

    def _safe_delete(fieldfile):
        """Attempt to delete a FieldFile while ignoring locks on Windows.

        On Windows a file may be temporarily locked by another process
        (antivirus, image viewer, the Django dev server, etc.). A
        ``PermissionError`` raised during deletion would normally bubble up
        and crash the view. We swallow that error and log a warning so the
        profile update can continue. The DB value is still cleared to
        prevent broken references.
        """

        try:
            fieldfile.delete(save=False)
        except PermissionError as exc:  # pragma: no cover - hard to force on CI
            # Windows-specific issue where the file handle is held by another
            # process; see GH#...
            logger.warning(
                "Permission denied while deleting avatar %s: %s",
                getattr(fieldfile, "name", "<unknown>"),
                exc,
            )

    if remove_avatar and user.avatar:
        _safe_delete(user.avatar)
        user.avatar = None
        update_fields.append("avatar")
    elif avatar:
        # Delete old avatar if exists
        if user.avatar:
            _safe_delete(user.avatar)
        user.avatar = avatar
        update_fields.append("avatar")

    if update_fields:
        user.save(update_fields=update_fields)


def change_password(
    *, user: "CustomUser", old_password: str, new_password: str
) -> None:
    """Change a user's password after verifying the current one.

    Only the ``password`` column is written so other fields are untouched.
    The caller is responsible for calling ``update_session_auth_hash``
    afterwards to keep the user's session valid.

    Args:
        user: The ``CustomUser`` instance whose password should change.
        old_password: The user's current plain-text password for
            verification.
        new_password: The desired new plain-text password; it will be
            hashed by Django's ``set_password`` before storage.

    Raises:
        ValueError: If ``old_password`` does not match the stored hash.
    """
    if not user.check_password(old_password):
        raise ValueError("Old password is incorrect.")

    user.set_password(new_password)
    user.save(update_fields=["password"])
