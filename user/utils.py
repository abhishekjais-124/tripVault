from user import models
from common import utils as common_utils


def get_user_by_uid(user_uid):
    return models.User.objects.filter(uid=user_uid, is_active=True).last()


def validate(full_name, email, phone_number):
    if full_name and len(full_name) > 30:
        return False, "Name is too long. Only 30 characters allowed."
    if email and not common_utils.validate_email(email):
        return False, "Email is not valid."
    if phone_number and not common_utils.validate_phone_number(phone_number):
        return False, "Phone number is not valid."
    return True, ""