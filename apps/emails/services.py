"""Business logic layer for the emails app.

This module is the single place where transactional emails are composed
and dispatched.  Keeping email construction here (rather than inline in
views) makes it easy to swap the delivery backend (SMTP, SES, Mailgun…)
without touching any view code.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.authentication.tokens import email_verification_token

if TYPE_CHECKING:
    from apps.users.models import CustomUser


def send_activation_email(*, user: "CustomUser", request: HttpRequest) -> None:
    """Compose and send the account activation (email verification) email.

    Generates a time-limited, single-use token via
    ``EmailVerificationTokenGenerator`` and encodes the user PK in URL-safe
    base64.  Both values become path parameters in the activation URL
    embedded in the email body.

    The subject line is rendered from a plain-text template to allow easy
    localisation without changing Python code.

    Args:
        user: The ``CustomUser`` instance that should receive the email.
            Must have a valid ``pk`` and ``email`` attribute.
        request: The current ``HttpRequest``; used to determine the site
            domain and protocol (HTTP vs HTTPS) for the activation link.
    """
    current_site = get_current_site(request)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    context = {
        "user": user,
        "domain": current_site.domain,
        "protocol": "https" if request.is_secure() else "http",
        "uid": uid,
        "token": token,
    }

    subject = render_to_string("emails/activation_subject.txt", context).strip()
    message = render_to_string("emails/activation_email.html", context)

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=message,
    )


def send_password_reset_email(*, user: "CustomUser", request: HttpRequest) -> None:
    """Compose and send the password reset email.

    Delegates token generation to Django's built-in
    ``default_token_generator`` (``PasswordResetTokenGenerator``) so reset
    links expire according to ``PASSWORD_RESET_TIMEOUT`` and are
    automatically invalidated after first use.

    Args:
        user: The ``CustomUser`` instance that requested the password reset.
            Must have a valid ``pk`` and ``email`` attribute.
        request: The current ``HttpRequest``; used to determine the site
            domain and protocol for the reset link.
    """
    current_site = get_current_site(request)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    context = {
        "user": user,
        "domain": current_site.domain,
        "protocol": "https" if request.is_secure() else "http",
        "uid": uid,
        "token": token,
    }

    subject = render_to_string("emails/password_reset_subject.txt", context).strip()
    message = render_to_string("emails/password_reset_email.html", context)

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=message,
    )
