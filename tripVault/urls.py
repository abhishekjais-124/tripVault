from django.contrib import admin
from django.urls import path, include

from user import urls as user_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('user/', include(user_urls)),
]
