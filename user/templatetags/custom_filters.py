from django import template
import hashlib

register = template.Library()

@register.filter
def img_from_name(name):
    hash = hashlib.md5(name.lower().encode('utf-8')).hexdigest()
    num = "1"
    for i in list(hash):
        if i.isdigit() and 1 <= int(i) < 7:
            num = i
            break
    return f"https://bootdey.com/img/Content/avatar/avatar{num}.png"

@register.filter
def get_pending_requests_count(user):
    from group_request import utils as group_request_utils
    pending_requests = group_request_utils.get_user_group_all_pending_request(user)
    return len(pending_requests)


@register.filter
def get_unread_activity_count(user):
    """Total unread activities = pending requests + unread notifications."""
    from group_request import utils as group_request_utils
    from common.models import Notification

    pending_count = group_request_utils.get_user_group_all_pending_request(user, unseen_only=True)
    unread_notifs = Notification.objects.filter(user=user, is_read=False).count()
    pending_count = len(pending_count)
    return pending_count + unread_notifs

