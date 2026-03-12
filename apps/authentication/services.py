"""Business logic layer for the authentication app.

This module is the single authoritative source for user-creation and
activation operations.  Views delegate here so that the same rules apply
whether an action is triggered via the web UI or a management command.
"""

from typing import cast

from django.contrib.auth import get_user_model
from django.http import HttpRequest

from apps.emails.services import send_activation_email
from apps.users.models import CustomUser

User = get_user_model()


def get_user_by_email(email: str) -> "CustomUser | None":
    """Retrieve a user by their email address (case-insensitive).

    Args:
        email: The email address to look up.

    Returns:
        The matching ``CustomUser`` instance, or ``None`` if no account
        exists with that email.
    """
    try:
        return cast("CustomUser", User.objects.get(email__iexact=email))  # type: ignore[redundant-cast]
    except User.DoesNotExist:
        return None


def get_user_by_pk(pk: int) -> "CustomUser | None":
    """Retrieve a user by their primary key.

    Args:
        pk: The integer primary-key value of the user.

    Returns:
        The matching ``CustomUser`` instance, or ``None`` if no such
        record exists (e.g. after decoding a stale activation URL).
    """
    try:
        return cast("CustomUser", User.objects.get(pk=pk))  # type: ignore[redundant-cast]
    except User.DoesNotExist:
        return None


def register_user(
    *,
    username: str,
    email: str,
    password: str,
    first_name: str = "",
    last_name: str = "",
    request: HttpRequest | None = None,
) -> "CustomUser":
    """Create a new inactive user account and dispatch the activation email.

    Uses keyword-only arguments to prevent accidental positional mis-ordering
    of ``username`` and ``email``.

    The new account is created with ``is_email_verified=False`` so the user
    cannot gain elevated access until the activation link is clicked.  When
    ``request`` is provided the activation email is sent immediately.

    Args:
        username: Desired unique username.
        email: User's email address; used for the activation link.
        password: Plain-text password that will be hashed before storage.
        first_name: Optional first name (default: empty string).
        last_name: Optional last name (default: empty string).
        request: The current ``HttpRequest``, used to build the absolute
            activation URL.  Pass ``None`` to skip sending the email
            (useful in tests or management commands).

    Returns:
        The newly created ``CustomUser`` instance.
    """
    user = CustomUser.objects.create_user(  # pyright: ignore[reportAttributeAccessIssue]
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_email_verified=False,
    )

    if request:
        send_activation_email(user=user, request=request)

    return user


def activate_user(*, user: "CustomUser") -> bool:
    """Mark a user's email address as verified and persist the change.

    Called after the user clicks a valid activation link.  Only the
    ``is_email_verified`` column is updated to minimise the write footprint.

    Args:
        user: The ``CustomUser`` instance to activate.  Must already exist
            in the database.

    Returns:
        ``True`` on success (always, unless an exception is raised).
    """
    user.is_email_verified = True
    user.save(update_fields=["is_email_verified"])
    return True
