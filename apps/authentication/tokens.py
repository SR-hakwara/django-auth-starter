"""Email token generator extending PasswordResetTokenGenerator."""

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.models import AbstractBaseUser
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from apps.users.models import CustomUser  # custom user


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """One-time token generator for email address verification.

    Extends Django's ``PasswordResetTokenGenerator`` so tokens are:
    - Time-limited (expire according to ``PASSWORD_RESET_TIMEOUT``).
    - Single-use: the token is invalidated as soon as ``is_email_verified``
      transitions from ``False`` to ``True``.
    - Bound to the account: changing the password also invalidates any
      outstanding verification tokens.
    """

    def _make_hash_value(self, user: AbstractBaseUser, timestamp: int) -> str:
        """Build the string that is hashed to create the token.

        Including ``is_email_verified`` in the hash ensures the token is
        invalidated the moment the flag flips to ``True``, so clicking the
        same activation link a second time yields an "invalid token" page
        instead of silently succeeding.

        ``last_login`` (stripped of microseconds and timezone) is also
        included so that logging in after receiving the email — but before
        clicking the link — does not invalidate the token.

        Args:
            user: The ``CustomUser`` instance for whom the token is made.
            timestamp: Integer timestamp (seconds since a fixed epoch)
                encoded in the token to enable expiry checks.

        Returns:
            A plain-text string that is subsequently HMAC-hashed by the
            parent class.
        """
        login_timestamp = (
            ""
            if user.last_login is None
            else user.last_login.replace(microsecond=0, tzinfo=None)
        )
        user = cast("CustomUser", user)
        return f"{user.pk}{user.password}{login_timestamp}{timestamp}{user.is_email_verified}"


email_verification_token = EmailVerificationTokenGenerator()
