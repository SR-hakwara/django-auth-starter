import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


@pytest.mark.django_db
def test_avatar_deleted_on_user_delete(monkeypatch):
    called = False

    from django.db.models.fields.files import FieldFile

    def fake_delete(self, save=False):
        nonlocal called
        called = True

    monkeypatch.setattr(FieldFile, "delete", fake_delete, raising=False)
    user = User.objects.create_user(username="foo", email="foo@example.com", password="pass")
    user.avatar.save(
        "pic.png", SimpleUploadedFile("pic.png", b"1", content_type="image/png")
    )
    user.save()
    user.delete()
    assert called
