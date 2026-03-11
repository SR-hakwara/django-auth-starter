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
