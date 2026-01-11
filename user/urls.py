from django.urls import path
from user.auth_views import (
    CustomerRegistrationView, UserProfileView, NotificationsView, 
    FriendsView, FriendDetailView, MarkAllNotificationsReadView, 
    SupportView, SendContactEmailView, ForgotPasswordView, ResetPasswordView
)
from group.views import GroupView, UserGroupView
from group_request.views import (
    SearchUserView, 
    RequestUserView, 
    AcceptUserRequestView, 
    DeclineUserRequestView, 
    DismissUserRequestView,
    GetPendingRequestsView
)
from django.contrib.auth import views as auth_views
from user.forms import LoginForm

urlpatterns = [
    # Authentication routes
    path('registration/', CustomerRegistrationView.as_view(), name='customerregistration'),
    path('login/', auth_views.LoginView.as_view(template_name='user/login.html', authentication_form=LoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', ResetPasswordView.as_view(), name='reset_password'),
    
    # User profile routes
    path('profile/', UserProfileView.as_view(), name='userprofile'),
    path('notifications/', NotificationsView.as_view(), name='notifications'),
    path('notifications/mark-all-read/', MarkAllNotificationsReadView.as_view(), name='mark-all-read'),
    path('friends/', FriendsView.as_view(), name='friends'),
    path('friends/<str:friend_uid>/', FriendDetailView.as_view(), name='friend_detail'),
    path('support/', SupportView.as_view(), name='support'),
    path('support/send-email/', SendContactEmailView.as_view(), name='send-contact-email'),
    
    # Group management routes
    path('groups/', GroupView.as_view(), name='group'),
    path('user_group/', UserGroupView.as_view(), name='user_group'),
    
    # Group request routes
    path('groups/search/', SearchUserView.as_view(), name='search'),
    path('groups/request/<str:user_uid>/', RequestUserView.as_view(), name='request_user'),
    path('groups/pending-requests/', GetPendingRequestsView.as_view(), name='pending-requests'),
    path('accept/', AcceptUserRequestView.as_view(), name='accept-request'),
    path('decline/', DeclineUserRequestView.as_view(), name='decline-request'),
    path('dismiss/', DismissUserRequestView.as_view(), name='dismiss-request'),
]
