"""Signal handlers for the users app."""

import logging

from django.db.models.signals import post_delete
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_delete, sender="users.CustomUser")
def delete_avatar_on_user_delete(sender, instance, **kwargs):
    """Delete the avatar file from storage when a CustomUser is deleted.

    Prevents orphaned media files accumulating on disk after account deletion.
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
