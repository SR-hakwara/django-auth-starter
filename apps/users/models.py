"""Custom User Model with username + email dual authentication."""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model replacing Django's default ``auth.User``.

    Stored in the ``users_customuser`` database table.  Inherits
    ``PermissionsMixin`` to gain the standard ``groups`` and
    ``user_permissions`` many-to-many relations.

    Authentication works via *username* **or** *email* thanks to
    ``EmailOrUsernameBackend``.  A separate email-verification flag
    (``is_email_verified``) gates access to certain features without
    disabling the account outright.

    Attributes:
        username (str): Unique login handle (max 150 chars).
        email (str): Unique email address used for notifications and
            alternative login.
        first_name (str): Optional first name.
        last_name (str): Optional last name.
        avatar (ImageField): Optional profile picture stored under
            ``MEDIA_ROOT/avatars/``.
        is_active (bool): Soft-delete flag; inactive users cannot log in.
        is_staff (bool): Grants access to the Django admin interface.
        is_email_verified (bool): Set to ``True`` after the user clicks
            the activation link sent by email.
        date_joined (datetime): UTC timestamp recorded at account creation.
    """

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    email = models.EmailField(
        _("email address"),
        unique=True,
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    avatar = models.ImageField(
        _("avatar"),
        upload_to="avatars/",
        blank=True,
        null=True,
        help_text=_("Upload a profile picture."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into the admin site."),
    )
    is_email_verified = models.BooleanField(
        _("email verified"),
        default=False,
        help_text=_("Designates whether the user has verified their email address."),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS: list[str] = ["email", "first_name", "last_name"]  # type: ignore[misc]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        """Return the username as the human-readable representation."""
        return self.username

    def get_full_name(self) -> str:
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username

    def get_short_name(self) -> str:
        """Return the short name for the user."""
        return self.first_name or self.username
