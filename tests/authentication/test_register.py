import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

@pytest.mark.django_db
def test_register_page_loads(api_client):
    """Test that the registration page loads successfully."""
    response = api_client.get(reverse("authentication:register"))
    assert response.status_code == 200

@pytest.mark.django_db
def test_register_success(api_client):
    """Test successful user registration."""
    data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "first_name": "New",
        "last_name": "User",
        "password1": "SecurePass123!",
        "password2": "SecurePass123!",
    }
    response = api_client.post(reverse("authentication:register"), data)
    assert response.status_code == 302
    assert response.url == reverse("authentication:activation_sent")
    assert User.objects.filter(email="newuser@example.com").exists()

@pytest.mark.django_db
def test_register_password_mismatch(api_client):
    """Test registration fails with mismatched passwords."""
    data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "first_name": "New",
        "last_name": "User",
        "password1": "SecurePass123!",
        "password2": "DifferentPass456!",
    }
    response = api_client.post(reverse("authentication:register"), data)
    assert response.status_code == 200
    assert not User.objects.filter(email="newuser@example.com").exists()

@pytest.mark.django_db
def test_register_duplicate_email(api_client, user):
    """Test registration fails with existing email."""
    data = {
        "username": "dupuser",
        "email": user.email,
        "first_name": "Dup",
        "last_name": "User",
        "password1": "SecurePass123!",
        "password2": "SecurePass123!",
    }
    response = api_client.post(reverse("authentication:register"), data)
    assert response.status_code == 200
    assert User.objects.filter(email=user.email).count() == 1
