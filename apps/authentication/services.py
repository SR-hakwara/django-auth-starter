"""Business logic layer for the authentication app."""

from typing import cast

from django.contrib.auth import get_user_model
from django.contrib.auth.models import UserManager
from django.http import HttpRequest

from apps.emails.services import send_activation_email

User = get_user_model()


def get_user_by_email(email: str):
    try:
        return User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return None


def get_user_by_pk(pk: int):
    try:
        return User.objects.get(pk=pk)
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
) -> "User":
    """
    Register a new user and send an activation email.
    """
    usermanager = cast(UserManager, User.objects)
    user = usermanager.create_user(
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


def activate_user(*, user) -> bool:
    """
    Activate a user's email verification.
    """
    user.is_email_verified = True
    user.save(update_fields=["is_email_verified"])
    return True
