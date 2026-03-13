"""Forms for the authentication app."""

from typing import cast

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    SetPasswordForm,
)
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from apps.core.constants import INPUT_CSS

User = get_user_model()


class LoginForm(AuthenticationForm):
    """Login form accepting email or username."""

    username = forms.CharField(
        label=_("Email or Username"),
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CSS,
                "placeholder": _("you@example.com or username"),
                "autofocus": True,
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CSS,
                "placeholder": _("••••••••"),
                "autocomplete": "current-password",
            }
        ),
    )


class RegisterForm(forms.ModelForm):  # type: ignore[type-arg]
    """User registration form with username, email, and password confirmation."""

    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CSS,
                "placeholder": _("••••••••"),
                "autocomplete": "new-password",
            }
        ),
    )
    password2 = forms.CharField(
        label=_("Confirm password"),
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CSS,
                "placeholder": _("••••••••"),
                "autocomplete": "new-password",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": INPUT_CSS,
                    "placeholder": _("johndoe"),
                    "autocomplete": "username",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": INPUT_CSS,
                    "placeholder": _("you@example.com"),
                    "autocomplete": "email",
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "class": INPUT_CSS,
                    "placeholder": _("John"),
                    "autocomplete": "given-name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": INPUT_CSS,
                    "placeholder": _("Doe"),
                    "autocomplete": "family-name",
                }
            ),
        }

    def clean_password2(self) -> str | None:
        """Verify that both password fields are identical and meet complexity rules.

        Returns:
            The confirmed password value.

        Raises:
            ValidationError: If ``password1`` and ``password2`` do not match,
                or if the password fails ``AUTH_PASSWORD_VALIDATORS``.
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                _("The two password fields didn't match."), code="password_mismatch"
            )
        if password2:
            # Build a partial user instance so UserAttributeSimilarityValidator
            # can compare the password against the form's own field values.
            user = self.instance if self.instance.pk else None
            validate_password(password2, user)
        return cast(str, password2) if password2 is not None else None

    def clean_email(self) -> str:
        """Normalise and enforce uniqueness of the email address.

        The address is lower-cased and stripped of surrounding whitespace
        before the uniqueness check so that ``User@Example.com`` and
        ``user@example.com`` are treated as the same address.

        Returns:
            The normalised email string.

        Raises:
            ValidationError: If the email is already registered.
        """
        email = cast(str, self.cleaned_data.get("email", "")).lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                _("A user with that email already exists."), code="email_exists"
            )
        return email

    def clean_username(self) -> str:
        """Normalise and enforce uniqueness of the username.

        Strips surrounding whitespace before the uniqueness check so that
        ``  johndoe  `` and ``johndoe`` are treated as the same handle.

        Returns:
            The stripped username string.

        Raises:
            ValidationError: If the username is already taken.
        """
        username = cast(str, self.cleaned_data.get("username", "")).strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(
                _("A user with that username already exists."), code="username_exists"
            )
        return username


class PasswordResetRequestForm(forms.Form):
    """Form for requesting a password reset email."""

    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={
                "class": INPUT_CSS,
                "placeholder": _("you@example.com"),
                "autocomplete": "email",
            }
        ),
    )


class CustomSetPasswordForm(SetPasswordForm):  # type: ignore[type-arg]
    """Custom set password form with styled widgets."""

    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CSS,
                "placeholder": _("••••••••"),
                "autocomplete": "new-password",
            }
        ),
    )
    new_password2 = forms.CharField(
        label=_("Confirm new password"),
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CSS,
                "placeholder": _("••••••••"),
                "autocomplete": "new-password",
            }
        ),
    )
