"""URL patterns for the profiles app."""

from django.urls import path
from apps.authentication.views import resend_activation_view
from . import views

app_name = "profiles"

urlpatterns = [
    path("profile/", views.profile_view, name="profile"),
    path("profile/update/", views.profile_update_view, name="profile_update"),
    path("profile/password/", views.password_change_view, name="password_change"),
    path("profile/resend-activation/", resend_activation_view, name="resend_activation"),
]
