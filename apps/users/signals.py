"""Signal handlers for the users app."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db.models.signals import post_delete
from django.dispatch import receiver

if TYPE_CHECKING:
    from apps.users.models import CustomUser

logger = logging.getLogger(__name__)


@receiver(post_delete, sender="users.CustomUser")
def delete_avatar_on_user_delete(
    sender: type,
    instance: "CustomUser",
    **kwargs: object,
) -> None:
    """Delete the avatar file from storage when a ``CustomUser`` is deleted.

    Connected to the ``post_delete`` signal so the physical file is removed
    from ``MEDIA_ROOT`` immediately after the database row is gone, preventing
    orphaned media files from accumulating on disk.

    Deletion errors (e.g. file already missing, permission denied) are caught
    and logged at ``WARNING`` level rather than raised, since the database
    record has already been removed and rolling back is not possible.

    Args:
        sender: The model class that sent the signal (``CustomUser``).
        instance: The ``CustomUser`` instance that was just deleted.
        **kwargs: Extra keyword arguments forwarded by Django's signal
            dispatcher (e.g. ``using``, ``origin``).
    """
    if instance.avatar:
        try:
            instance.avatar.delete(save=False)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Could not delete avatar for deleted user pk=%s: %s",
                instance.pk,
                exc,
            )
