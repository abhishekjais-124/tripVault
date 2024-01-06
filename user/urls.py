from django.urls import path
from user import views
from django.contrib.auth import views as auth_views
from user.forms import LoginForm

urlpatterns = [
    path('registration/', views.CustomerRegistrationView.as_view(), name='customerregistration'),  # for the registration
    path('login/', auth_views.LoginView.as_view(template_name='user/login.html',authentication_form=LoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', views.UserProfile.as_view(), name='userprofile'),
    path('groups/request/<str:user_uid>/', views.RequestUserView.as_view(), name='request_user'),
    path('groups/search/',views.SearchUser.as_view(), name='search'),  # for the registration
    path('groups/', views.GroupView.as_view(), name='group'),
    path('user_group/', views.UserGroupView.as_view(), name='user_group'),
    path('accept/', views.AcceptUserView.as_view(), name='accept-request'),
    path('decline/', views.DeclineUserView.as_view(), name='decline-request'),
    path('update_user_role/', views.UpdateUserRole.as_view(), name='update-user-role'),
]
