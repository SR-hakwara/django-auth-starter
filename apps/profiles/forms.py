"""Forms for the profiles app."""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from django.utils.translation import gettext_lazy as _

from apps.core.constants import INPUT_CSS
from apps.core.validators import validate_avatar

User = get_user_model()


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile: name, email, and avatar."""

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "avatar")
        widgets = {
            "username": forms.TextInput(attrs={"class": INPUT_CSS}),
            "first_name": forms.TextInput(attrs={"class": INPUT_CSS}),
            "last_name": forms.TextInput(attrs={"class": INPUT_CSS}),
            "email": forms.EmailInput(attrs={"class": INPUT_CSS}),
            "avatar": forms.FileInput(
                attrs={
                    "class": "hidden",
                    "accept": "image/*",
                    "id": "avatar-input",
                }
            ),
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialise the form and annotate the email field with a help text.

        The help text reminds users that changing their email will trigger
        a new verification flow, so the change is not silently applied.
        """
        super().__init__(*args, **kwargs)
        self.fields["email"].help_text = _(
            "Changing your email will require re-verification."
        )

    def clean_avatar(self):
        """Validate avatar file size and type — only for newly uploaded files."""
        from django.core.files.uploadedfile import UploadedFile

        avatar = self.cleaned_data.get("avatar")
        # Only run validation on a *new* upload (UploadedFile).
        # When no new file is chosen, cleaned_data contains either None or the
        # existing FieldFile.  Calling validate_avatar() on an existing FieldFile
        # would open a file handle on the current avatar *before* _safe_delete
        # runs, which on Windows prevents os.remove() from succeeding.
        if isinstance(avatar, UploadedFile):
            validate_avatar(avatar)
        return avatar

    def clean_email(self) -> str:
        """Validate email uniqueness excluding current user."""
        email = self.cleaned_data.get("email", "").lower().strip()
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                _("A user with that email already exists."),
                code="email_exists",
            )
        return email

    def clean_username(self) -> str:
        """Validate username uniqueness excluding current user."""
        username = self.cleaned_data.get("username", "").strip()
        qs = User.objects.filter(username__iexact=username).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                _("A user with that username already exists."),
                code="username_exists",
            )
        return username


class PasswordChangeForm(DjangoPasswordChangeForm):
    """Styled password change form."""

    old_password = forms.CharField(
        label=_("Current password"),
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CSS,
                "placeholder": _("••••••••"),
                "autocomplete": "current-password",
            }
        ),
    )
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
