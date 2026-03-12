import pytest
from django.contrib.auth import get_user_model

from apps.profiles.forms import ProfileUpdateForm

User = get_user_model()


@pytest.mark.django_db
def test_profile_update_form_email_conflict(user):
    # create a second account, then try to update the first user to that email
    from django.contrib.auth import get_user_model

    User = get_user_model()
    other = User.objects.create_user(username="other", email="other@example.com", password="x")

    form = ProfileUpdateForm(
        data={
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": other.email,
        },
        instance=user,
    )
    assert not form.is_valid()
    assert "email" in form.errors


@pytest.mark.django_db
def test_profile_update_form_username_conflict(user):
    other = User.objects.create_user(
        username="other", email="other@example.com", password="x"
    )
    form = ProfileUpdateForm(
        data={
            "username": other.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        },
        instance=user,
    )
    assert not form.is_valid()
    assert "username" in form.errors
