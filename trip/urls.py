from django.urls import path
from trip import views
from trip import api_views


urlpatterns = [
	path('plan/', views.TripPlannerView.as_view(), name='plan-dashboard'),
	path('saved/', api_views.saved_trips_page, name='saved-trips'),
	path('api/save/', api_views.save_trip, name='api-save-trip'),
	path('api/list/', api_views.list_trips, name='api-list-trips'),
	path('api/trip/<int:trip_id>/', api_views.get_trip, name='api-get-trip'),
	path('api/trip/<int:trip_id>/update/', api_views.update_trip, name='api-update-trip'),
	path('api/trip/<int:trip_id>/delete/', api_views.delete_trip, name='api-delete-trip'),
	# PWA support
	path('manifest.json', views.ManifestView.as_view(), name='manifest'),
	path('serviceworker.js', views.ServiceWorkerView.as_view(), name='serviceworker'),
]
