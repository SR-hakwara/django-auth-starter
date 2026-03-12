"""Custom User Manager for email + username authentication."""

from __future__ import annotations
from typing import cast, TYPE_CHECKING
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from apps.users.models import CustomUser  # custom user


class CustomUserManager(BaseUserManager):
    """
    Custom user manager where email is unique and username is the login field.
    Supports creating users with both email and username.
    """

    def create_user(
        self,
        username: str,
        email: str,
        password: str | None = None,
        **extra_fields,
    ) -> CustomUser:
        """
        Create and save a regular user.

        Args:
            username: User's username.
            email: User's email address.
            password: User's password.
            **extra_fields: Additional fields.

        Returns:
            The created user instance.

        Raises:
            ValueError: If no email or username is provided.
        """
        if not email:
            raise ValueError(_("The Email field must be set"))
        if not username:
            raise ValueError(_("The Username field must be set"))

        email = self.normalize_email(email)
        username = username.strip()
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        username: str,
        email: str,
        password: str | None = None,
        **extra_fields,
    ) -> CustomUser:
        """
        Create and save a superuser.

        Args:
            username: Superuser's username.
            email: Superuser's email address.
            password: Superuser's password.
            **extra_fields: Additional fields.

        Returns:
            The created superuser instance.

        Raises:
            ValueError: If is_staff or is_superuser is not True.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_email_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(username, email, password, **extra_fields)
