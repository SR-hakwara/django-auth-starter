import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_password_reset_request_page_loads(api_client):
    """Test that the password reset request page loads."""
    response = api_client.get(reverse("authentication:password_reset"))
    assert response.status_code == 200

@pytest.mark.django_db
def test_password_reset_request_success(api_client, user):
    """Test submitting a password reset request."""
    response = api_client.post(
        reverse("authentication:password_reset"),
        {"email": user.email},
    )
    assert response.status_code == 302
    assert response.url == reverse("authentication:password_reset_done")
