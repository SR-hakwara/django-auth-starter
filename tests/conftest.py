import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def user(db):
    """Fixture to create a test user."""
    return User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="SecurePass123!",
        first_name="Test",
        last_name="User"
    )

@pytest.fixture
def api_client():
    from django.test import Client
    return Client()
