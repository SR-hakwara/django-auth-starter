"""Custom authentication backend for email OR username login."""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.http import HttpRequest

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """
    Authentication backend that allows login with either email or username.

    The username field on the login form accepts both email and username.
    """

    def authenticate(
        self,
        request: HttpRequest | None,
        username: str | None = None,
        password: str | None = None,
        **kwargs,
    ):
        """
        Authenticate a user by email or username.

        Args:
            request: The HTTP request.
            username: The email or username entered by the user.
            password: The password.

        Returns:
            User instance if authentication succeeds, None otherwise.
        """
        if username is None or password is None:
            return None

        try:
            user = User.objects.get(
                Q(email__iexact=username) | Q(username__iexact=username)
            )
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            # Run the default password hasher to mitigate timing attacks
            User().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
