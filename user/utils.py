from user import models
from common import utils as common_utils


def get_user_by_uid(user_uid):
    """Get a user by their UID."""
    return models.User.objects.filter(uid=user_uid, is_active=True).last()


def search_users_by_uid(search_term, exclude_ids):
    """Search users by UID, excluding users in the provided list."""
    return models.User.objects.filter(uid__icontains=search_term).exclude(
        id__in=exclude_ids
    )


def search_users_by_username(search_term, exclude_ids):
    """Search users by username, excluding users in the provided list."""
    return models.User.objects.filter(username__icontains=search_term).exclude(
        id__in=exclude_ids
    )


def search_users_by_name(search_term, exclude_ids):
    """Search users by name, excluding users in the provided list."""
    return models.User.objects.filter(name__icontains=search_term).exclude(
        id__in=exclude_ids
    )


def validate(full_name, email, phone_number):
    """Validate user profile information."""
    if not email:
        return False, "Email can't be empty."
    if full_name and len(full_name) > 30:
        return False, "Name is too long. Only 30 characters allowed."
    if email and not common_utils.validate_email(email):
        return False, "Email is not valid."
    if phone_number and not common_utils.validate_phone_number(phone_number):
        return False, "Phone number is not valid."
    return True, ""
