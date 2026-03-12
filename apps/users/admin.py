"""Admin configuration for the users app."""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):  # type: ignore[type-arg]
    """
    Admin interface for ``CustomUser``.

    Extends Django's built-in ``UserAdmin`` with:
    - The ``avatar`` image field in the *Personal info* fieldset.
    - The ``is_email_verified`` flag in the *Permissions* fieldset and
      in the list/filter panels.
    - Case-insensitive search across ``username``, ``email``,
      ``first_name``, and ``last_name``.
    """

    model = User

    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "avatar")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_email_verified",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_email_verified",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "is_email_verified")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("-date_joined",)
