from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from user import urls as user_urls
from trip import urls as trip_urls
from expense import urls as expense_urls
from trip import views as trip_views

urlpatterns = [
    path('tripvault/admin/', admin.site.urls),
    path('tripvault/api-auth/', include('rest_framework.urls')),
    path('tripvault/', trip_views.HomeView.as_view(), name='home'),
    path('tripvault/user/', include(user_urls)),
    path('tripvault/home/', include(trip_urls)),
    path('tripvault/expense/', include(expense_urls)),
    path('expense/', include(expense_urls)),
    # PWA support - direct access to manifest and service worker
    path('tripvault/manifest.json', trip_views.ManifestView.as_view(), name='manifest'),
    path('tripvault/serviceworker.js', trip_views.ServiceWorkerView.as_view(), name='serviceworker'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Error handlers
handler404 = 'trip.views.custom_404_view'
handler500 = 'trip.views.custom_500_view'
