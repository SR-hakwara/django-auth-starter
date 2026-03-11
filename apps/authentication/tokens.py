"""Email token generator extending PasswordResetTokenGenerator."""

from django.contrib.auth.tokens import PasswordResetTokenGenerator

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Generate a token for email verification.
    """
    def _make_hash_value(self, user, timestamp: int) -> str:
        # We append is_email_verified to ensure token invalidates when verified.
        login_timestamp = (
            "" if user.last_login is None else user.last_login.replace(microsecond=0, tzinfo=None)
        )
        return f"{user.pk}{user.password}{login_timestamp}{timestamp}{user.is_email_verified}"

email_verification_token = EmailVerificationTokenGenerator()
