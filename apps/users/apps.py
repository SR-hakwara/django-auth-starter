"""Users app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    """Configuration for the users application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"
    label = "users"
    verbose_name = _("Users")

    def ready(self) -> None:
        import apps.users.signals  # noqa: F401
