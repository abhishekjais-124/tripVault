from django.urls import path
from trip import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
]
