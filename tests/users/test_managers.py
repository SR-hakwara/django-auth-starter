import pytest
from django.contrib.auth import get_user_model

from apps.users.managers import CustomUserManager

User = get_user_model()


@pytest.mark.django_db
def test_create_user_requires_email_and_username():
    mgr = CustomUserManager()
    with pytest.raises(ValueError):
        mgr.create_user(username="", email="a@example.com", password="pass")
    with pytest.raises(ValueError):
        mgr.create_user(username="foo", email="", password="pass")


@pytest.mark.django_db
def test_create_superuser_flags_validation():
    mgr = CustomUserManager()
    with pytest.raises(ValueError):
        mgr.create_superuser(
            username="admin", email="admin@example.com", password="pass", is_staff=False
        )
    with pytest.raises(ValueError):
        mgr.create_superuser(
            username="admin",
            email="admin@example.com",
            password="pass",
            is_superuser=False,
        )
