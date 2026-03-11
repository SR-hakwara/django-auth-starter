import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_login_page_loads(api_client):
    """Test that the login page loads successfully."""
    response = api_client.get(reverse("authentication:login"))
    assert response.status_code == 200

@pytest.mark.django_db
def test_login_success(api_client, user):
    """Test successful login redirects to profile."""
    data = {"username": "testuser@example.com", "password": "SecurePass123!"}
    response = api_client.post(reverse("authentication:login"), data)
    assert response.status_code == 302
    assert response.url == reverse("profiles:profile")

@pytest.mark.django_db
def test_login_failure(api_client, user):
    """Test failed login re-renders form."""
    data = {"username": "testuser@example.com", "password": "WrongPass!"}
    response = api_client.post(reverse("authentication:login"), data)
    assert response.status_code == 200

@pytest.mark.django_db
def test_logout(api_client, user):
    """Test logout redirects to login."""
    api_client.login(username="testuser@example.com", password="SecurePass123!")
    response = api_client.get(reverse("authentication:logout"))
    assert response.status_code == 302
    assert response.url == reverse("authentication:login")
