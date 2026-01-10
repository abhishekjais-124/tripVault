"""
User authentication and profile views.

For group and request-related views, see:
- group/views.py for group management
- group_request/views.py for group join requests
"""

from .auth_views import CustomerRegistrationView, UserProfileView, NotificationsView

__all__ = [
    'CustomerRegistrationView',
    'UserProfileView',
    'NotificationsView',
]

        
        return render(request, "user/notifications.html", {"user": user, 'requests': requests})


