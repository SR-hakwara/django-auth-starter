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
    ) -> "User | None":
        """
        Authenticate a user by email or username.

        The ``username`` parameter is treated as *either* a username or an
        email address.  A case-insensitive lookup is performed on both
        fields simultaneously so "Alice", "alice", and "ALICE@example.com"
        all resolve to the same account.

        A dummy ``set_password`` call is made on every failed lookup to
        ensure constant-time behaviour and prevent user-enumeration via
        timing side-channels.

        Args:
            request: The current HTTP request (may be ``None`` in tests).
            username: The email *or* username submitted via the login form.
            password: The plain-text password to verify.
            **kwargs: Ignored extra keyword arguments forwarded by Django.

        Returns:
            The authenticated ``CustomUser`` instance, or ``None`` if
            credentials are invalid or the account cannot authenticate.
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
