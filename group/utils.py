from collections import defaultdict
import logging

from group import models as group_models
from user import constants
from user.models import User


def create_user_group(name, user, description=None):
    """Create a new group and add the user as admin."""
    group = group_models.Group.objects.create(name=name, description=description, created_by=user.username)
    user_group_mapping = group_models.UserGroupMapping.objects.create(
        user=user, group=group, role=constants.ADMIN
    )
    # Success path - no logging per current policy
    return group, user_group_mapping


def get_user_groups(user):
    """Get all groups for a user."""
    return list(
        group_models.UserGroupMapping.objects.filter(
            user=user, is_active=True, group__is_active=True
        )
        .order_by("-id")
        .values_list("group_id", flat=True)
    )


def create_group_user_mapping(group_ids, user):
    """Create a mapping of groups with their users and admin status."""
    mapping = defaultdict(lambda: [[], "", False])
    user_groups = list(
        group_models.UserGroupMapping.objects.select_related("user", "group").filter(
            group_id__in=group_ids, is_active=True
        )
    )
    for user_group in user_groups:
        mapping[user_group.group.id][0].append(
            [user_group.user, user_group.role.capitalize()]
        )
        mapping[user_group.group.id][1] = user_group.group
        if user.id == user_group.user.id and user_group.role == constants.ADMIN:
            mapping[user_group.group.id][2] = True
    return dict(mapping)


def get_group_by_id(group_id):
    """Get a group by ID."""
    return group_models.Group.objects.filter(id=group_id, is_active=True).first()
