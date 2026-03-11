"""Tests for the Custom User model."""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_create_user():
    """Test creating a regular user with email and username."""
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123!",
        first_name="Test",
        last_name="User",
    )
    assert user.email == "test@example.com"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_superuser is False
    assert user.is_email_verified is False
    assert user.check_password("testpass123!")

@pytest.mark.django_db
def test_create_user_without_email_raises():
    """Test that creating a user without email raises ValueError."""
    with pytest.raises(ValueError):
        User.objects.create_user(username="testuser", email="", password="testpass123!")

@pytest.mark.django_db
def test_create_superuser():
    """Test creating a superuser."""
    user = User.objects.create_superuser(
        username="adminuser",
        email="admin@example.com",
        password="adminpass123!",
    )
    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.is_email_verified is True

@pytest.mark.django_db
def test_email_normalization():
    """Test that email is normalized (lowered domain)."""
    user = User.objects.create_user(
        username="testuser",
        email="test@EXAMPLE.COM",
        password="testpass123!",
    )
    assert user.email == "test@example.com"

@pytest.mark.django_db
def test_user_str():
    """Test the string representation of a user."""
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123!",
    )
    assert str(user) == "testuser"

@pytest.mark.django_db
def test_get_full_name():
    """Test get_full_name returns first + last name."""
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123!",
        first_name="John",
        last_name="Doe",
    )
    assert user.get_full_name() == "John Doe"

@pytest.mark.django_db
def test_get_short_name():
    """Test get_short_name returns first name."""
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123!",
        first_name="John",
    )
    assert user.get_short_name() == "John"
