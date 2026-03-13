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
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from apps.users.models import CustomUser  # custom user


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
    """Handle user login with brute-force rate limiting.

    Accepts an email *or* username together with a password via
    ``LoginForm``.  On success the session is refreshed, the failed-attempt
    counter is cleared, and the user is redirected to ``next`` (if safe) or
    to ``settings.LOGIN_REDIRECT_URL``.

    Rate limiting is IP-based: once the threshold defined by
    ``LOGIN_RATE_LIMIT_MAX_ATTEMPTS`` is exceeded, every subsequent request
    is rejected until the cache key expires.

    Permissions:
        Public — no authentication required.

    Args:
        request: The incoming HTTP request.  ``GET`` renders the login form;
            ``POST`` validates credentials.

    Returns:
        - ``302`` redirect to the profile page when the user is already
          authenticated.
        - ``302`` redirect to ``next`` or ``LOGIN_REDIRECT_URL`` after a
          successful login.
        - ``200`` rendering of ``authentication/login.html`` with the form
          (includes field errors on invalid submission or rate-limit error).
    """
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
            # use a string literal with `cast` so the name is not required at
            # runtime; otherwise ``CustomUser`` would be undefined when the
            # preceding ``if TYPE_CHECKING`` block is skipped and pytest calls
            # the view.
            user = cast("CustomUser", form.get_user())  # type: ignore[redundant-cast]
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
    """Handle new user registration.

    Creates a new account via ``register_user()`` (which also sends the
    activation email) and redirects to the "check your email" confirmation
    page.  Already-authenticated users are bounced straight to their profile.

    Permissions:
        Public — no authentication required.

    Args:
        request: The incoming HTTP request.  ``GET`` renders the blank
            registration form; ``POST`` processes the submission.

    Returns:
        - ``302`` redirect to ``profiles:profile`` when already authenticated.
        - ``302`` redirect to ``authentication:activation_sent`` on success.
        - ``200`` rendering of ``authentication/register.html`` with the form
          (includes field errors on invalid submission).
    """
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
    """Log the current user out, accepting POST only.

    Restricting logout to ``POST`` prevents one-click CSRF logout attacks
    where a malicious page embeds a ``<img src="/logout/">`` or similar.
    ``GET`` requests simply redirect to the login page without logging out.

    Permissions:
        Public — no authentication is required (logging out an anonymous
        user is a valid, harmless no-op from Django's perspective).

    Args:
        request: The incoming HTTP request.

    Returns:
        ``302`` redirect to ``authentication:login`` in all cases.
    """
    if request.method == "POST":
        logout(request)
        messages.info(request, _("You have been logged out."))
    return redirect("home")


def activation_sent_view(request: HttpRequest) -> HttpResponse:
    """Render the "check your inbox" confirmation page.

    Displayed immediately after registration so the user knows an
    activation link has been dispatched.  This is a static informational
    page with no side effects.

    Permissions:
        Public.

    Args:
        request: The incoming HTTP request.

    Returns:
        ``200`` rendering of ``authentication/activation_sent.html``.
    """
    return render(request, "authentication/activation_sent.html")


def activate_account_view(
    request: HttpRequest, uidb64: str, token: str
) -> HttpResponse:
    """Activate a user account from a one-time email verification link.

    Decodes the base64 ``uidb64`` path parameter to obtain the user PK,
    then validates the ``token`` with ``EmailVerificationTokenGenerator``.
    On success the account is activated via ``activate_user()``.  On any
    failure (bad encoding, unknown PK, expired or already-used token) the
    invalid-link template is rendered instead.

    Permissions:
        Public — the token itself acts as the credential.

    Args:
        request: The incoming HTTP request.
        uidb64: URL-safe base64-encoded primary key of the user to activate.
        token: HMAC token produced by ``EmailVerificationTokenGenerator``.

    Returns:
        - ``200`` rendering of ``authentication/activation_complete.html``
          on success.
        - ``200`` rendering of ``authentication/activation_invalid.html``
          when the link is malformed, expired, or already used.
    """
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
    """Resend the email verification link to the currently logged-in user.

    Only ``POST`` is accepted to prevent accidental re-sends via browser
    pre-fetching of links.  Already-verified users receive an informational
    message instead of a duplicate email.  IP-based rate limiting (key prefix
    ``resend_activation``) prevents abuse.

    Permissions:
        Login required (``@login_required``).

    Args:
        request: The incoming HTTP request.

    Returns:
        ``302`` redirect to ``profiles:profile`` in all cases (including
        rate-limited or non-POST requests).
    """
    if request.method != "POST":
        return redirect("profiles:profile")
    if is_rate_limited(request, key_prefix="resend_activation"):
        messages.error(request, _("Too many requests. Please try again later."))
        return redirect("profiles:profile")
    # casting with a string avoids a NameError when the import above
    # is guarded by TYPE_CHECKING (which is False at runtime).
    user = cast("CustomUser", request.user)
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
    """Handle password reset requests.

    Accepts an email address via ``PasswordResetRequestForm``.  A reset
    email is dispatched **only when** an account exists for that address,
    but the response is identical regardless — this prevents email
    enumeration (an attacker cannot tell whether an address is registered
    by observing the UI behaviour).

    IP-based rate limiting (key prefix ``password_reset``) is applied
    before the form is even rendered.

    Permissions:
        Public.

    Args:
        request: The incoming HTTP request.  ``GET`` renders the request
            form; ``POST`` processes the submission.

    Returns:
        - ``302`` redirect to ``authentication:password_reset_done`` when
          rate-limited.
        - ``302`` redirect to ``authentication:password_reset_done`` after
          a valid form submission (regardless of whether the email exists).
        - ``200`` rendering of ``authentication/password_reset.html`` with
          the form on ``GET`` or invalid ``POST``.
    """
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
    """Render the password-reset confirmation page.

    Shown after the user submits the password-reset request form, whatever
    the outcome.  This is a static informational page with no side effects.

    Permissions:
        Public.

    Args:
        request: The incoming HTTP request.

    Returns:
        ``200`` rendering of ``authentication/password_reset_done.html``.
    """
    return render(request, "authentication/password_reset_done.html")


def password_reset_confirm_view(
    request: HttpRequest, uidb64: str, token: str
) -> HttpResponse:
    """Handle password reset confirmation via a one-time link.

    Decodes ``uidb64`` to retrieve the target user, then validates the
    ``token`` with Django's built-in ``default_token_generator``.  If the
    link is invalid or expired the user is redirected to the request page
    with an error message.  On ``POST`` with a valid form the new password
    is saved and the user is redirected to the login page.

    Permissions:
        Public — the token itself acts as the credential.

    Args:
        request: The incoming HTTP request.
        uidb64: URL-safe base64-encoded primary key of the target user.
        token: HMAC token produced by Django's ``PasswordResetTokenGenerator``.

    Returns:
        - ``302`` redirect to ``authentication:password_reset`` when the
          link is invalid or expired.
        - ``302`` redirect to ``authentication:login`` after a successful
          password reset.
        - ``200`` rendering of
          ``authentication/password_reset_confirm.html`` with the form on
          ``GET`` or invalid ``POST``.
    """
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
