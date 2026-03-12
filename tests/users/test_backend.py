import pytest
from django.contrib.auth import get_user_model

from apps.users.backends import EmailOrUsernameBackend

User = get_user_model()


@pytest.mark.django_db
def test_backend_missing_credentials():
    backend = EmailOrUsernameBackend()
    assert backend.authenticate(request=None, username=None, password="foo") is None
    assert backend.authenticate(request=None, username="foo", password=None) is None


@pytest.mark.django_db
def test_backend_multiple_objects_handle(monkeypatch):
    backend = EmailOrUsernameBackend()

    # patch User.objects.get to raise MultipleObjectsReturned
    def fake_get(*args, **kwargs):
        raise User.MultipleObjectsReturned()

    monkeypatch.setattr(User.objects, "get", fake_get)

    called = {}

    def fake_set_password(self, pwd):
        called["pwd"] = pwd

    monkeypatch.setattr(User, "set_password", fake_set_password, raising=False)

    result = backend.authenticate(request=None, username="bar", password="pw")
    assert result is None
    assert called.get("pwd") == "pw"
