import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
def test_register_page_loads(client):
    """Test that the registration page loads successfully."""
    response = client.get(reverse("authentication:register"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_register_redirects_authenticated_user(client, user):
    """Authenticated users should be redirected away from the register page."""
    client.login(username="testuser", password="SecurePass123!")
    response = client.get(reverse("authentication:register"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_register_success(client):
    """Test successful user registration creates user and redirects."""
    data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "first_name": "New",
        "last_name": "User",
        "password1": "SecurePass123!",
        "password2": "SecurePass123!",
    }
    response = client.post(reverse("authentication:register"), data)
    assert response.status_code == 302
    assert response.url == reverse("authentication:activation_sent")
    new_user = User.objects.get(email="newuser@example.com")
    assert not new_user.is_email_verified


@pytest.mark.django_db
def test_register_password_mismatch(client):
    """Test registration fails with mismatched passwords."""
    data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "first_name": "New",
        "last_name": "User",
        "password1": "SecurePass123!",
        "password2": "DifferentPass456!",
    }
    response = client.post(reverse("authentication:register"), data)
    assert response.status_code == 200
    assert not User.objects.filter(email="newuser@example.com").exists()


@pytest.mark.django_db
def test_register_duplicate_email(client, user):
    """Test registration fails with an existing email."""
    data = {
        "username": "dupuser",
        "email": user.email,
        "first_name": "Dup",
        "last_name": "User",
        "password1": "SecurePass123!",
        "password2": "SecurePass123!",
    }
    response = client.post(reverse("authentication:register"), data)
    assert response.status_code == 200
    assert User.objects.filter(email=user.email).count() == 1


@pytest.mark.django_db
def test_register_duplicate_username(client, user):
    """Test registration fails with an existing username."""
    data = {
        "username": user.username,
        "email": "different@example.com",
        "first_name": "Dup",
        "last_name": "User",
        "password1": "SecurePass123!",
        "password2": "SecurePass123!",
    }
    response = client.post(reverse("authentication:register"), data)
    assert response.status_code == 200
    assert User.objects.filter(username=user.username).count() == 1


@pytest.mark.django_db
def test_register_activation_sent_page_loads(client):
    """Test the activation-sent confirmation page loads."""
    response = client.get(reverse("authentication:activation_sent"))
    assert response.status_code == 200
