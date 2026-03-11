"""Forms for the authentication app."""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    SetPasswordForm,
)
from django.utils.translation import gettext_lazy as _

User = get_user_model()

# Shared CSS class for TailwindCSS form inputs
INPUT_CSS = (
    "w-full px-4 py-3 rounded-lg border border-gray-300 "
    "focus:ring-2 focus:ring-indigo-500 focus:border-transparent "
    "transition duration-200"
)

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

class RegisterForm(forms.ModelForm):
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
            "username": forms.TextInput(attrs={"class": INPUT_CSS, "placeholder": _("johndoe"), "autocomplete": "username"}),
            "email": forms.EmailInput(attrs={"class": INPUT_CSS, "placeholder": _("you@example.com"), "autocomplete": "email"}),
            "first_name": forms.TextInput(attrs={"class": INPUT_CSS, "placeholder": _("John"), "autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"class": INPUT_CSS, "placeholder": _("Doe"), "autocomplete": "family-name"}),
        }

    def clean_password2(self) -> str:
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."), code="password_mismatch")
        return password2

    def clean_email(self) -> str:
        email = self.cleaned_data.get("email", "").lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("A user with that email already exists."), code="email_exists")
        return email

    def clean_username(self) -> str:
        username = self.cleaned_data.get("username", "").strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(_("A user with that username already exists."), code="username_exists")
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

class CustomSetPasswordForm(SetPasswordForm):
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
