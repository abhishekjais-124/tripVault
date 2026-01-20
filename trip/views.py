
def plan_placeholder(request):
    from django.http import HttpResponse
    return HttpResponse('<html><body><h2>Plan page placeholder</h2></body></html>')

def saved_placeholder(request):
    from django.http import HttpResponse
    return HttpResponse('<html><body><h2>Saved page placeholder</h2></body></html>')
def custom_404_view(request, exception, template_name="trip/error.html"):
    return render(request, template_name, {"error_code": 404, "error_message": "Page Not Found"}, status=404)

def custom_500_view(request, template_name="trip/error.html"):
    return render(request, template_name, {"error_code": 500, "error_message": "Internal Server Error"}, status=500)
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from user import utils as user_utils
from group_request import utils as group_request_utils
from common.redis_client import redis_client
from user import constants as user_constants


@method_decorator(login_required(login_url="/tripvault/user/login/"), name="dispatch")
class HomeView(APIView):
    def get(self, request):
        user = request.user.user
        if not user:
            return Response(
                {"error": "User Not Found!"}, status=status.HTTP_404_NOT_FOUND
            )
        request_data = {}
        pending_requests = group_request_utils.get_user_group_pending_request(user)
        if pending_requests:
            request_data = {
                "sender": pending_requests.sender.username,
                "group": pending_requests.group.name,
                "group_id": pending_requests.group.id,
                "sender_uid": pending_requests.sender.uid,
            }
            key = user_constants.SHOW_PENDING_REQUEST_REDIS_KEY.format(
                user.uid + "#" + pending_requests.sender.uid
            )
            value = redis_client.get_value(key)
            if value:
                request_data = {}
            else:
                redis_client.set_value(key, 1, 10*60)
        return render(
            request, "trip/home.html", {"user": user, "request_data": request_data}
        )


@method_decorator(login_required(login_url="/tripvault/user/login/"), name="dispatch")
class TripPlannerView(APIView):
    def get(self, request):
        user = getattr(request.user, "user", None)
        return render(request, "trip/plan_dashboard.html", {"user": user})


class ManifestView(TemplateView):
    template_name = 'trip/manifest.json'
    content_type = 'application/json'


class ServiceWorkerView(TemplateView):
    template_name = 'serviceworker.js'
    content_type = 'application/javascript'

    def get(self, request, *args, **kwargs):
        with open('trip/static/serviceworker.js', 'r') as f:
            content = f.read()
        return HttpResponse(content, content_type=self.content_type)
