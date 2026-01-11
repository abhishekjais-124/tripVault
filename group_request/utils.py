import logging
from group import models as group_models
from group_request import models as group_request_models
from user import constants
from user.models import User
from common.models import Notification


def create_user_request(sender, receiver, group_id, role):
    """Create a new group join request."""
    request = group_request_models.UserGroupRequest.objects.create(
        sender=sender, receiver=receiver, group_id=group_id, role_requested=role
    )
    
    # Create activity notification for the sender only
    try:
        group = group_models.Group.objects.get(id=group_id)
        notification_message = f"You requested to join '{group.name}' as {role}"
        
        Notification.objects.create(
            user=sender,
            title="Group Join Request Sent",
            message=notification_message,
            notification_type="other",
            metadata={"group_name": group.name, "group_id": group_id, "receiver": receiver.username}
        )
    except Exception:
        logging.getLogger(__name__).error("Failed to create 'Group Join Request Sent' notification", exc_info=True)
    
    return request


def get_user_group_pending_request(user):
    """Get the most recent pending request for a user."""
    return group_request_models.UserGroupRequest.objects.filter(
        receiver=user, status=constants.PENDING, is_dismissed=False
    ).last()


def get_user_group_all_pending_request(user, unseen_only=False):
    """Get all pending requests for a user.

    unseen_only: when True, return only requests not yet marked as seen.
    """
    qs = group_request_models.UserGroupRequest.objects.filter(
        receiver=user, status=constants.PENDING
    )
    if unseen_only:
        qs = qs.filter(is_seen=False)
    return list(qs.order_by('-created_at'))


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
    
    # Ensure role is properly capitalized
    role = request_obj.role_requested
    if role and role.lower() == 'admin':
        role = constants.ADMIN
    else:
        role = constants.MEMBER
    
    # Check if receiver (invited person) is already in group
    user_group_obj = group_models.UserGroupMapping.objects.filter(
        user=request_obj.receiver, group_id=request_obj.group_id
    ).first()
    
    if user_group_obj:
        if user_group_obj.is_active:
            # User is already active, just update role if needed and return success
            if user_group_obj.role != role:
                user_group_obj.role = role
                user_group_obj.save()
        else:
            user_group_obj.is_active = True
            user_group_obj.role = role
            user_group_obj.save()
    else:
        mapping = group_models.UserGroupMapping.objects.create(
            user=request_obj.receiver, 
            group_id=request_obj.group_id, 
            role=role,
            is_active=True
        )
    
    # Create notification for the receiver (person who accepted the invitation)
    try:
        group = group_models.Group.objects.get(id=request_obj.group_id)
        notification_message = f"You accepted {request_obj.sender.username}'s invitation to join '{group.name}' as {role}"
        
        Notification.objects.create(
            user=request_obj.receiver,
            title="Group Invitation Accepted",
            message=notification_message,
            notification_type="other",
            metadata={"group_name": group.name, "group_id": request_obj.group_id, "status": "accepted"}
        )
    except Exception:
        logging.getLogger(__name__).error("Failed to create 'Group Invitation Accepted' notification", exc_info=True)
    
    return True, "Request accepted"


def decline_request(request_obj):
    """Decline a group join request."""
    request_obj.status = constants.DECLINED
    request_obj.save()
    
    # Create notification for the sender
    try:
        group = group_models.Group.objects.get(id=request_obj.group_id)
        notification_message = f"{request_obj.receiver.username} declined your request to join '{group.name}'"
        
        Notification.objects.create(
            user=request_obj.sender,
            title="Group Request Declined",
            message=notification_message,
            notification_type="other",
            metadata={"group_name": group.name, "group_id": request_obj.group_id, "status": "declined"}
        )
    except Exception:
        logging.getLogger(__name__).error("Failed to create 'Group Request Declined' notification", exc_info=True)
    
    return True, "Request declined"
