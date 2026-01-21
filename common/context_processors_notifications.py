from common.models import Notification

def unread_notifications_context(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'user'):
        return {'unread_notifications_count': 0}
    user = request.user.user
    count = Notification.objects.filter(user=user, is_read=False).count()
    return {'unread_notifications_count': count}
