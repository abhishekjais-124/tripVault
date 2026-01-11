from django.shortcuts import render

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from user import utils as user_utils
from group_request import utils as group_request_utils
from common.redis_client import redis_client
from user import constants as user_constants


@method_decorator(login_required(login_url="/user/login/"), name="dispatch")
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


@method_decorator(login_required(login_url="/user/login/"), name="dispatch")
class TripPlannerView(APIView):
    def get(self, request):
        user = getattr(request.user, "user", None)
        return render(request, "trip/plan_dashboard.html", {"user": user})
