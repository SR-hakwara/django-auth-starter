import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse


@pytest.mark.django_db
def test_profile_requires_login(client):
    """Test that profile page redirects unauthenticated users."""
    response = client.get(reverse("profiles:profile"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_profile_update_get_page(client, user):
    """GETting the update page should return 200 for authenticated user."""
    client.login(username=user.username, password="SecurePass123!")
    response = client.get(reverse("profiles:profile_update"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_password_change_get_page(client, user):
    """GETting the password change page should return 200 for authenticated user."""
    client.login(username=user.username, password="SecurePass123!")
    response = client.get(reverse("profiles:password_change"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_change_password_service_raises(user):
    """change_password() should raise ValueError when old password is wrong."""
    from apps.profiles.services import change_password

    with pytest.raises(ValueError):
        change_password(user=user, old_password="incorrect", new_password="x")


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
def test_profile_update_avatar_with_lock(monkeypatch, client, user):
    """If deleting the existing avatar raises ``PermissionError`` we should
    still allow the update (Windows can lock media files).
    """
    client.login(username=user.username, password="SecurePass123!")
    # give the user an initial avatar file; the contents are not
    # important, we just need something the ImageField can reference.
    from io import BytesIO

    from PIL import Image

    buf = BytesIO()
    Image.new("RGB", (1, 1)).save(buf, format="PNG")
    buf.seek(0)
    user.avatar.save(
        "old.png", SimpleUploadedFile("old.png", buf.read(), content_type="image/png")
    )
    user.save()

    # simulate a locked file error when attempting to delete the old avatar
    def locked_delete(self, save=False):
        raise PermissionError("locked")

    # patch FieldFile.delete so that any attempt to remove a file raises
    from django.db.models.fields.files import FieldFile

    monkeypatch.setattr(FieldFile, "delete", locked_delete, raising=False)

    # create another tiny valid image for the upload
    buf = BytesIO()
    Image.new("RGB", (1, 1)).save(buf, format="PNG")
    buf.seek(0)
    old_name = user.avatar.name
    response = client.post(
        reverse("profiles:profile_update"),
        {
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            # Django test client requires ``format="multipart"`` for files
            "avatar": SimpleUploadedFile(
                "new.png", buf.read(), content_type="image/png"
            ),
        },
        format="multipart",
    )
    assert response.status_code == 302
    user.refresh_from_db()
    # the file name should change when a new avatar is uploaded
    assert user.avatar.name != old_name


@pytest.mark.django_db
def test_profile_remove_avatar_with_lock(monkeypatch, client, user):
    """Removing an avatar should not crash even if the file is locked."""
    client.login(username=user.username, password="SecurePass123!")
    from io import BytesIO

    from PIL import Image

    buf = BytesIO()
    Image.new("RGB", (1, 1)).save(buf, format="PNG")
    buf.seek(0)
    user.avatar.save(
        "old.png", SimpleUploadedFile("old.png", buf.read(), content_type="image/png")
    )
    user.save()

    def locked_delete(self, save=False):
        raise PermissionError("locked")

    from django.db.models.fields.files import FieldFile

    monkeypatch.setattr(FieldFile, "delete", locked_delete, raising=False)

    response = client.post(
        reverse("profiles:profile_update"),
        {
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "remove_avatar": "true",
        },
    )
    assert response.status_code == 302
    user.refresh_from_db()
    assert not user.avatar


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
