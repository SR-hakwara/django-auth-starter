"""Admin configuration for the users app."""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom User Admin. Allows setting the avatar, username, and email.
    Lists and searches correctly.
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
