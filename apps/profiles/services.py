"""Business logic layer for the profiles app."""

from django.core.files.uploadedfile import UploadedFile

def update_profile(
    *,
    user,
    username: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    avatar: UploadedFile | None = None,
    remove_avatar: bool = False,
) -> None:
    """
    Update user profile information including avatar and email.
    """
    update_fields: list[str] = []

    if username is not None and username != user.username:
        user.username = username
        update_fields.append("username")

    if first_name is not None:
        user.first_name = first_name
        update_fields.append("first_name")

    if last_name is not None:
        user.last_name = last_name
        update_fields.append("last_name")

    if email is not None and email != user.email:
        user.email = email
        user.is_email_verified = False
        update_fields.extend(["email", "is_email_verified"])

    if remove_avatar and user.avatar:
        user.avatar.delete(save=False)
        user.avatar = None
        update_fields.append("avatar")
    elif avatar:
        # Delete old avatar if exists
        if user.avatar:
            user.avatar.delete(save=False)
        user.avatar = avatar
        update_fields.append("avatar")

    if update_fields:
        user.save(update_fields=update_fields)


def change_password(*, user, old_password: str, new_password: str) -> bool:
    """
    Change the user's password.
    """
    if not user.check_password(old_password):
        return False

    user.set_password(new_password)
    user.save(update_fields=["password"])
    return True
