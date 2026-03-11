"""Business logic layer for the emails app."""

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.authentication.tokens import email_verification_token

def send_activation_email(*, user, request: HttpRequest) -> None:
    """
    Send an email with an activation link to the user.
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

    subject = render_to_string(
        "emails/activation_subject.txt", context
    ).strip()
    message = render_to_string(
        "emails/activation_email.html", context
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=message,
    )

def send_password_reset_email(*, user, request: HttpRequest) -> None:
    """
    Send a password reset email to the user.
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

    subject = render_to_string(
        "emails/password_reset_subject.txt", context
    ).strip()
    message = render_to_string(
        "emails/password_reset_email.html", context
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=message,
    )
