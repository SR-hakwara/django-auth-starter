import pytest
from django.contrib.auth import get_user_model

from apps.users.models import CustomUserManager
from typing import cast

User = get_user_model()
manager = cast(CustomUserManager, User.objects)


@pytest.fixture
def user(db):
    """Verified user fixture for tests that require an authenticated user."""
    return manager.create_user(
        username="testuser",
        email="testuser@example.com",
        password="SecurePass123!",
        first_name="Test",
        last_name="User",
        is_email_verified=True,
    )


@pytest.fixture
def unverified_user(db):
    """Unverified user fixture for testing email verification flows."""
    return manager.create_user(
        username="unverifieduser",
        email="unverified@example.com",
        password="SecurePass123!",
        first_name="Unverified",
        last_name="User",
        is_email_verified=False,
    )


@pytest.fixture
def client():
    """Standard Django test client."""
    from django.test import Client

    return Client()
