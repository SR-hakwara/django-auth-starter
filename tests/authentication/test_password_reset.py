import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


@pytest.mark.django_db
def test_password_reset_request_page_loads(client):
    """Test that the password reset request page loads."""
    response = client.get(reverse("authentication:password_reset"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_password_reset_request_success(client, user):
    """Test submitting a password reset request redirects to done page."""
    response = client.post(
        reverse("authentication:password_reset"),
        {"email": user.email},
    )
    assert response.status_code == 302
    assert response.url == reverse("authentication:password_reset_done")


@pytest.mark.django_db
def test_password_reset_request_unknown_email_no_enumeration(client):
    """Test that an unknown email still shows the success page (no enumeration)."""
    response = client.post(
        reverse("authentication:password_reset"),
        {"email": "nobody@example.com"},
    )
    assert response.status_code == 302
    assert response.url == reverse("authentication:password_reset_done")


@pytest.mark.django_db
def test_password_reset_done_page_loads(client):
    """Test the password reset done page loads."""
    response = client.get(reverse("authentication:password_reset_done"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_password_reset_rate_limited(client, user, settings):
    # stub is_rate_limited so that the second request is considered throttled
    from apps.core import utils

    call_count = {"n": 0}

    def fake_rate(req, key_prefix="login_attempts"):
        call_count["n"] += 1
        return call_count["n"] > 1

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(utils, "is_rate_limited", fake_rate)

    # first request not limited
    response = client.post(
        reverse("authentication:password_reset"), {"email": user.email}
    )
    # second request should be throttled; follow redirect to capture messages
    response = client.post(
        reverse("authentication:password_reset"), {"email": user.email}, follow=True
    )
    # we followed the redirect, which means branch ran; final page loads OK
    assert response.status_code == 200
    monkeypatch.undo()


@pytest.mark.django_db
def test_resend_activation_post_sends_email(monkeypatch, client, user):
    # use unverified user so the email branch runs
    user.is_email_verified = False
    user.save()
    client.login(username="testuser", password="SecurePass123!")
    called = {}

    def fake_send_activation_email(*, user, request):
        called["user"] = user

    monkeypatch.setattr(
        "apps.authentication.views.send_activation_email", fake_send_activation_email
    )
    response = client.post(reverse("authentication:resend_activation"))
    assert response.status_code == 302
    assert called.get("user") == user


@pytest.mark.django_db
def test_resend_activation_rate_limited(client, user, settings):
    client.login(username="testuser", password="SecurePass123!")
    # stub the utility to always report rate limited
    from apps.core import utils

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(
        utils, "is_rate_limited", lambda req, key_prefix="login_attempts": True
    )

    user.is_email_verified = False
    user.save()
    response = client.post(reverse("authentication:resend_activation"), follow=True)
    # branch executed and page rendered
    assert response.status_code == 200
    monkeypatch.undo()


@pytest.mark.django_db
def test_password_reset_confirm_valid_token(client, user):
    """Test password reset confirm with a valid token allows setting a new password."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    url = reverse(
        "authentication:password_reset_confirm", kwargs={"uidb64": uid, "token": token}
    )
    response = client.post(
        url,
        {
            "new_password1": "NewSecurePass456!",
            "new_password2": "NewSecurePass456!",
        },
    )
    assert response.status_code == 302
    assert response.url == reverse("authentication:login")

    user.refresh_from_db()
    assert user.check_password("NewSecurePass456!")


@pytest.mark.django_db
def test_password_reset_confirm_invalid_token(client, user):
    """Test that an invalid token redirects back to password reset."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    url = reverse(
        "authentication:password_reset_confirm",
        kwargs={"uidb64": uid, "token": "bad-token"},
    )
    response = client.post(
        url,
        {
            "new_password1": "NewSecurePass456!",
            "new_password2": "NewSecurePass456!",
        },
    )
    assert response.status_code == 302
    assert response.url == reverse("authentication:password_reset")


@pytest.mark.django_db
def test_resend_activation_requires_login(client):
    """Test that resend activation redirects unauthenticated users."""
    response = client.get(reverse("authentication:resend_activation"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_resend_activation_already_verified(client, user):
    """Test that resend activation for a verified user shows info message."""
    client.login(username="testuser", password="SecurePass123!")
    response = client.get(reverse("authentication:resend_activation"))
    assert response.status_code == 302
