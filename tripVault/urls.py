from django.contrib import admin
from django.urls import path, include

from user import urls as user_urls
from trip import urls as trip_urls
from expense import urls as expense_urls
from trip import views as trip_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('', trip_views.HomeView.as_view(), name='home'),
    path('user/', include(user_urls)),
    path('home/', include(trip_urls)),
    path('expense/', include(expense_urls)),
]
