from django.urls import path
from user import views
from django.contrib.auth import views as auth_views
from user.forms import LoginForm

urlpatterns = [
    path('registration/', views.CustomerRegistrationView.as_view(), name='customerregistration'),  # for the registration
    path('login/', auth_views.LoginView.as_view(template_name='user/login.html',authentication_form=LoginForm), name='login'),  # for the login
    #path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout')
]
