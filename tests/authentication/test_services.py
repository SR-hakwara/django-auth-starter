import pytest
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from apps.users.models import CustomUser
from apps.authentication import services

User = get_user_model()


@pytest.mark.django_db
def test_get_user_by_email_not_found():
    assert services.get_user_by_email("noone@example.com") is None


@pytest.mark.django_db
def test_register_user_sends_email(monkeypatch):
    called = {}

    def fake_send_activation_email(user, request):
        called["args"] = (user, request)

    monkeypatch.setattr(services, "send_activation_email", fake_send_activation_email)
    req = HttpRequest()
    req.method = "GET"
    user: CustomUser = services.register_user(
        username="foo",
        email="foo@example.com",
        password="pass",
        first_name="",
        last_name="",
        request=req,
    )  # type: ignore[assignment]
    assert user.email == "foo@example.com"
    assert not user.is_email_verified
    assert called["args"][0] is user
    assert called["args"][1] is req


@pytest.mark.django_db
def test_activate_user_sets_flag(unverified_user):
    # use fresh unverified account
    assert not unverified_user.is_email_verified
    services.activate_user(user=unverified_user)
    unverified_user.refresh_from_db()
    assert unverified_user.is_email_verified
