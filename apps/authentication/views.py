"""Views for the authentication app."""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.encoding import force_str
from django.utils.http import url_has_allowed_host_and_scheme, urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _

from apps.core.utils import (
    clear_failed_attempts,
    is_rate_limited,
    record_failed_attempt,
)
from apps.emails.services import send_activation_email, send_password_reset_email

from .forms import (
    CustomSetPasswordForm,
    LoginForm,
    PasswordResetRequestForm,
    RegisterForm,
)
from .services import (
    activate_user,
    get_user_by_email,
    get_user_by_pk,
    register_user,
)
from .tokens import email_verification_token


def login_view(request: HttpRequest) -> HttpResponse:
    """Handle user login with rate limiting."""
    if request.user.is_authenticated:
        return redirect("profiles:profile")

    if is_rate_limited(request):
        messages.error(
            request,
            _("Too many login attempts. Please try again later."),
        )
        return render(request, "authentication/login.html", {"form": LoginForm()})

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            clear_failed_attempts(request)
            messages.success(
                request, _("Welcome back, %(name)s!") % {"name": user.get_short_name()}
            )
            next_url = request.GET.get("next", "")
            if next_url and url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            record_failed_attempt(request)
    else:
        form = LoginForm()

    return render(request, "authentication/login.html", {"form": form})


def register_view(request: HttpRequest) -> HttpResponse:
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect("profiles:profile")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            register_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password1"],
                first_name=form.cleaned_data.get("first_name", ""),
                last_name=form.cleaned_data.get("last_name", ""),
                request=request,
            )
            messages.success(
                request,
                _("Account created! Please check your email to activate your account."),
            )
            return redirect("authentication:activation_sent")
    else:
        form = RegisterForm()

    return render(request, "authentication/register.html", {"form": form})


def logout_view(request: HttpRequest) -> HttpResponse:
    """Log the user out. Only accepts POST to prevent CSRF logout attacks."""
    if request.method == "POST":
        logout(request)
        messages.info(request, _("You have been logged out."))
    return redirect("authentication:login")


def activation_sent_view(request: HttpRequest) -> HttpResponse:
    """Show a page telling the user to check their email."""
    return render(request, "authentication/activation_sent.html")


def activate_account_view(
    request: HttpRequest, uidb64: str, token: str
) -> HttpResponse:
    """Activate a user account from an email verification link."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_by_pk(int(uid))
    except (TypeError, ValueError, OverflowError):
        user = None

    if user is not None and email_verification_token.check_token(user, token):
        activate_user(user=user)
        messages.success(
            request, _("Your email has been verified! You can now log in.")
        )
        return render(request, "authentication/activation_complete.html")
    else:
        return render(request, "authentication/activation_invalid.html")


@login_required
def resend_activation_view(request: HttpRequest) -> HttpResponse:
    """Resend the email verification link to the current user. Accepts POST only."""
    if request.method != "POST":
        return redirect("profiles:profile")
    if is_rate_limited(request, key_prefix="resend_activation"):
        messages.error(request, _("Too many requests. Please try again later."))
        return redirect("profiles:profile")
    user = request.user
    if user.is_email_verified:
        messages.info(request, _("Your email is already verified."))
    else:
        send_activation_email(user=user, request=request)
        messages.success(
            request,
            _("A new verification email has been sent to %(email)s.")
            % {"email": user.email},
        )
    return redirect("profiles:profile")


def password_reset_request_view(request: HttpRequest) -> HttpResponse:
    """Handle password reset requests."""
    if is_rate_limited(request, key_prefix="password_reset"):
        messages.error(request, _("Too many requests. Please try again later."))
        return redirect("authentication:password_reset_done")
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = get_user_by_email(email)
            if user:
                send_password_reset_email(user=user, request=request)
            # Always show success to prevent email enumeration
            messages.success(
                request,
                _(
                    "If an account with that email exists, a password reset link has been sent."
                ),
            )
            return redirect("authentication:password_reset_done")
    else:
        form = PasswordResetRequestForm()

    return render(request, "authentication/password_reset.html", {"form": form})


def password_reset_done_view(request: HttpRequest) -> HttpResponse:
    """Show confirmation that password reset email was sent."""
    return render(request, "authentication/password_reset_done.html")


def password_reset_confirm_view(
    request: HttpRequest, uidb64: str, token: str
) -> HttpResponse:
    """Handle password reset confirmation."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_by_pk(int(uid))
    except (TypeError, ValueError, OverflowError):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(
            request, _("This password reset link is invalid or has expired.")
        )
        return redirect("authentication:password_reset")

    if request.method == "POST":
        form = CustomSetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, _("Your password has been reset. You can now log in.")
            )
            return redirect("authentication:login")
    else:
        form = CustomSetPasswordForm(user)

    return render(
        request,
        "authentication/password_reset_confirm.html",
        {"form": form},
    )
