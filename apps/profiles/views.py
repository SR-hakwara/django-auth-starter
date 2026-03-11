"""Views for the profiles app."""

from typing import cast

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from apps.emails.services import send_activation_email

from .forms import PasswordChangeForm, ProfileUpdateForm
from .services import change_password, update_profile

from django.contrib.auth import get_user_model
User = get_user_model()

@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    """Display the user's profile."""
    return render(request, "profiles/profile.html", {"user": request.user})


@login_required
def profile_update_view(request: HttpRequest) -> HttpResponse:
    """Handle profile updates including avatar and email."""
    if request.method == "POST":
        # Fetch a separate instance for the form to prevent it from mutating
        # request.user.avatar before our service handles the old vs new files.

        form_instance = User.objects.get(pk=request.user.pk)

        form = ProfileUpdateForm(request.POST, request.FILES, instance=form_instance)
        if form.is_valid():
            remove_avatar = request.POST.get("remove_avatar") == "true"

            # Only pass a new avatar if the user actually uploaded one
            new_avatar = (
                form.cleaned_data.get("avatar")
                if "avatar" in form.changed_data
                else None
            )

            update_profile(
                user=request.user,
                username=form.cleaned_data.get("username"),
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                email=form.cleaned_data["email"],
                avatar=new_avatar,
                remove_avatar=remove_avatar,
            )

            # If email was changed, it requires re-verification
            if "email" in form.changed_data:
                send_activation_email(user=request.user, request=request)
                messages.warning(
                    request,
                    _(
                        "Profile updated. A verification link has been sent to your new email address. Please verify it to regain full access."
                    ),
                )
            else:
                messages.success(request, _("Profile updated successfully."))

            return redirect("profiles:profile")
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, "profiles/profile_update.html", {"form": form})


@login_required
def password_change_view(request: HttpRequest) -> HttpResponse:
    """Handle authenticated password changes."""
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            # narrow the type so the checker knows `user` isn’t AnonymousUser
            user = cast(User, request.user)
            change_password(
                user=user,
                old_password=form.cleaned_data["old_password"],
                new_password=form.cleaned_data["new_password1"],
            )
            # Re-log the user in after password change to prevent session invalidation
            from django.contrib.auth import update_session_auth_hash

            update_session_auth_hash(request, user)
            messages.success(request, _("Your password has been successfully updated."))
            return redirect("profiles:profile")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "profiles/password_change.html", {"form": form})
