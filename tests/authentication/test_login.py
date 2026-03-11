import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_login_page_loads(client):
    """Test that the login page loads successfully."""
    response = client.get(reverse("authentication:login"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_success_with_email(client, user):
    """Test successful login using email redirects to profile."""
    data = {"username": "testuser@example.com", "password": "SecurePass123!"}
    response = client.post(reverse("authentication:login"), data)
    assert response.status_code == 302
    assert response.url == reverse("profiles:profile")


@pytest.mark.django_db
def test_login_success_with_username(client, user):
    """Test successful login using username redirects to profile."""
    data = {"username": "testuser", "password": "SecurePass123!"}
    response = client.post(reverse("authentication:login"), data)
    assert response.status_code == 302
    assert response.url == reverse("profiles:profile")


@pytest.mark.django_db
def test_login_failure(client, user):
    """Test failed login re-renders the form with error."""
    data = {"username": "testuser@example.com", "password": "WrongPass!"}
    response = client.post(reverse("authentication:login"), data)
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_redirects_authenticated_user(client, user):
    """Test that an already-authenticated user is redirected away from login."""
    client.login(username="testuser", password="SecurePass123!")
    response = client.get(reverse("authentication:login"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_logout_post(client, user):
    """Test POST logout redirects to login page."""
    client.login(username="testuser", password="SecurePass123!")
    response = client.post(reverse("authentication:logout"))
    assert response.status_code == 302
    assert response.url == reverse("authentication:login")


@pytest.mark.django_db
def test_logout_get_does_not_log_out(client, user):
    """Test that a GET request to logout does NOT log the user out (CSRF protection)."""
    client.login(username="testuser", password="SecurePass123!")
    client.get(reverse("authentication:logout"))
    # User should still be able to access protected pages
    response = client.get(reverse("profiles:profile"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_next_param_safe_redirect(client, user):
    """Test that a safe ?next= URL is honoured after login."""
    next_url = reverse("profiles:profile_update")
    data = {"username": "testuser", "password": "SecurePass123!"}
    response = client.post(f"{reverse('authentication:login')}?next={next_url}", data)
    assert response.status_code == 302
    assert response.url == next_url


@pytest.mark.django_db
def test_login_next_param_open_redirect_blocked(client, user):
    """Test that an external ?next= URL is rejected (open redirect blocked)."""
    data = {"username": "testuser", "password": "SecurePass123!"}
    response = client.post(
        f"{reverse('authentication:login')}?next=https://evil.com", data
    )
    assert response.status_code == 302
    assert "evil.com" not in response.url


@pytest.mark.django_db
def test_rate_limiting_blocks_after_max_attempts(client, user, settings):
    """Test that login is blocked after exceeding max attempts."""
    settings.LOGIN_RATE_LIMIT_MAX_ATTEMPTS = 3
    settings.LOGIN_RATE_LIMIT_TIMEOUT = 60

    bad_data = {"username": "testuser", "password": "WrongPass!"}
    login_url = reverse("authentication:login")

    for _ in range(3):
        client.post(login_url, bad_data)

    # 4th attempt — should be rate limited
    response = client.post(login_url, bad_data)
    assert response.status_code == 200
    assert "Too many login attempts" in response.content.decode()
