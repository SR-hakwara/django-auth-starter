import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_profile_requires_login(api_client):
    """Test that profile page redirects unauthenticated users."""
    response = api_client.get(reverse("profiles:profile"))
    assert response.status_code == 302

@pytest.mark.django_db
def test_profile_loads_for_authenticated_user(api_client, user):
    """Test that profile page loads for authenticated users."""
    api_client.login(username=user.email, password="SecurePass123!")
    response = api_client.get(reverse("profiles:profile"))
    assert response.status_code == 200

@pytest.mark.django_db
def test_profile_update(api_client, user):
    """Test updating user profile."""
    api_client.login(username=user.email, password="SecurePass123!")
    response = api_client.post(
        reverse("profiles:profile_update"),
        {"username": "newprofilename", "first_name": "Updated", "last_name": "Name", "email": user.email},
    )
    assert response.status_code == 302
    user.refresh_from_db()
    assert user.username == "newprofilename"
    assert user.first_name == "Updated"
    assert user.last_name == "Name"
