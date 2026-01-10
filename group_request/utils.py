from group import models as group_models
from group_request import models as group_request_models
from user import constants
from user.models import User


def create_user_request(sender, receiver, group_id, role):
    """Create a new group join request."""
    request = group_request_models.UserGroupRequest.objects.create(
        sender=sender, receiver=receiver, group_id=group_id, role_requested=role
    )
    print("Request created successfully.")
    return request


def get_user_group_pending_request(user):
    """Get the most recent pending request for a user."""
    return group_request_models.UserGroupRequest.objects.filter(
        receiver=user, status=constants.PENDING
    ).last()


def get_user_group_all_pending_request(user):
    """Get all pending requests for a user."""
    return list(group_request_models.UserGroupRequest.objects.filter(
        receiver=user, status=constants.PENDING
    ))


def get_pending_requests_for_group(user, group_id):
    """Get all pending requests sent by user for a specific group."""
    return group_request_models.UserGroupRequest.objects.filter(
        sender=user,
        group_id=group_id,
        status=constants.PENDING
    ).select_related('receiver')


def accept_request(request_obj):
    """Accept a group join request and add user to group."""
    request_obj.status = constants.ACCEPTED
    request_obj.save()
    
    # Check if user already in group
    user_group_obj = group_models.UserGroupMapping.objects.filter(
        user=request_obj.sender, group_id=request_obj.group_id
    ).first()
    
    if user_group_obj:
        if user_group_obj.is_active:
            return False, "User is already in the group"
        else:
            user_group_obj.is_active = True
            user_group_obj.save()
    else:
        group_models.UserGroupMapping.objects.create(
            user=request_obj.sender, 
            group_id=request_obj.group_id, 
            role=request_obj.role_requested
        )
    return True, "Request accepted"


def decline_request(request_obj):
    """Decline a group join request."""
    request_obj.status = constants.DECLINED
    request_obj.save()
    return True, "Request declined"
