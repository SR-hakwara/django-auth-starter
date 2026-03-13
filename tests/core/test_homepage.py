import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_homepage_loads(client):
    """The root URL should return a homepage instead of 404."""
    response = client.get(reverse("home"))
    assert response.status_code == 200
    # some text from template
    assert "welcome to django-auth-basic" in response.content.decode().lower()
