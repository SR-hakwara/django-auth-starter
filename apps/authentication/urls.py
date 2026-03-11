"""URL patterns for the authentication app."""

from django.urls import path

from . import views

app_name = "authentication"

urlpatterns = [
    # Authentication
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    # Email Activation
    path("activation-sent/", views.activation_sent_view, name="activation_sent"),
    path(
        "activate/<uidb64>/<token>/",
        views.activate_account_view,
        name="activate",
    ),
    # Password Reset
    path("password-reset/", views.password_reset_request_view, name="password_reset"),
    path("password-reset/done/", views.password_reset_done_view, name="password_reset_done"),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        views.password_reset_confirm_view,
        name="password_reset_confirm",
    ),
]
