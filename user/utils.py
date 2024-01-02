from collections import defaultdict

from user import models
from user import constants
from common import utils as common_utils


def get_user_by_uid(user_uid):
    return models.User.objects.filter(uid=user_uid, is_active=True).last()


def validate(full_name, email, phone_number):
    if not email:
        return False, "Email can't be empty."
    if full_name and len(full_name) > 30:
        return False, "Name is too long. Only 30 characters allowed."
    if email and not common_utils.validate_email(email):
        return False, "Email is not valid."
    if phone_number and not common_utils.validate_phone_number(phone_number):
        return False, "Phone number is not valid."
    return True, ""


def create_user_group(name, user):
    group = models.Group.objects.create(name=name, created_by=user.username)
    user_group_mapping = models.UserGroupMapping.objects.create(user=user, group=group, role=constants.ADMIN)
    print("Group created succesfully.")
    return group, user_group_mapping


def get_user_groups(user):
    return list(models.UserGroupMapping.objects.filter(user=user, is_active=True, group__is_active=True).order_by('-id').values_list('group_id'))


def create_group_user_mapping(group_ids):
    mapping = defaultdict(lambda:   [[], ""])
    user_groups = list(models.UserGroupMapping.objects.select_related('user', 'group').filter(group_id__in=group_ids, is_active=True))
    for user_group in user_groups:
        mapping[user_group.group.id][0].append([user_group.user, user_group.role])
        mapping[user_group.group.id][1] = user_group.group
    return dict(mapping)


def create_user_request(sender, reciever, group_id, role):
    request = models.UserGroupRequests.objects.create(sender=sender, receiver=reciever, group_id=group_id, role_requested=role)
    print("Request created succesfully.")
    return request
