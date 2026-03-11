import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_profile_requires_login(client):
    """Test that profile page redirects unauthenticated users."""
    response = client.get(reverse("profiles:profile"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_profile_loads_for_authenticated_user(client, user):
    """Test that profile page loads for authenticated users."""
    client.login(username=user.username, password="SecurePass123!")
    response = client.get(reverse("profiles:profile"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_profile_update_name(client, user):
    """Test updating first name and last name."""
    client.login(username=user.username, password="SecurePass123!")
    response = client.post(
        reverse("profiles:profile_update"),
        {
            "username": user.username,
            "first_name": "Updated",
            "last_name": "Name",
            "email": user.email,
        },
    )
    assert response.status_code == 302
    user.refresh_from_db()
    assert user.first_name == "Updated"
    assert user.last_name == "Name"


@pytest.mark.django_db
def test_profile_update_username(client, user):
    """Test updating username."""
    client.login(username=user.username, password="SecurePass123!")
    response = client.post(
        reverse("profiles:profile_update"),
        {
            "username": "newprofilename",
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        },
    )
    assert response.status_code == 302
    user.refresh_from_db()
    assert user.username == "newprofilename"


@pytest.mark.django_db
def test_profile_update_email_triggers_reverification(client, user):
    """Test that changing email sets is_email_verified to False."""
    client.login(username=user.username, password="SecurePass123!")
    client.post(
        reverse("profiles:profile_update"),
        {
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": "newemail@example.com",
        },
    )
    user.refresh_from_db()
    assert user.email == "newemail@example.com"
    assert not user.is_email_verified


@pytest.mark.django_db
def test_profile_update_requires_login(client):
    """Test that profile update page redirects unauthenticated users."""
    response = client.post(reverse("profiles:profile_update"), {})
    assert response.status_code == 302


@pytest.mark.django_db
def test_password_change_success(client, user):
    """Test successful password change keeps user logged in."""
    client.login(username=user.username, password="SecurePass123!")
    response = client.post(
        reverse("profiles:password_change"),
        {
            "old_password": "SecurePass123!",
            "new_password1": "NewSecureXyz789@",
            "new_password2": "NewSecureXyz789@",
        },
    )
    assert response.status_code == 302
    user.refresh_from_db()
    assert user.check_password("NewSecureXyz789@")


@pytest.mark.django_db
def test_password_change_wrong_old_password(client, user):
    """Test password change fails with incorrect old password."""
    client.login(username=user.username, password="SecurePass123!")
    response = client.post(
        reverse("profiles:password_change"),
        {
            "old_password": "WrongOldPassword!",
            "new_password1": "NewSecureXyz789@",
            "new_password2": "NewSecureXyz789@",
        },
    )
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.check_password("SecurePass123!")
