from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from group_request import utils as group_request_utils
from group_request import models as group_request_models
from user import constants
from user import utils as user_utils
from common import utils as common_utils


class SearchUserView(APIView):
    """Search for users to invite to a group."""
    
    def get(self, request):
        search_type = request.GET.get("type", "id")
        search_term = request.GET.get("term", "").strip()
        group_id = request.GET.get("group", "")
        
        from group.models import UserGroupMapping
        
        user_ids = list(
            UserGroupMapping.objects.filter(
                group_id=group_id, is_active=True
            ).values_list("user_id", flat=True)
        )
        sender = request.user.user
        
        # Search by different criteria
        if search_term and search_type == "id":
            results = user_utils.search_users_by_uid(search_term, user_ids)
        elif search_term and search_type == "username":
            results = user_utils.search_users_by_username(search_term, user_ids)
        elif search_term and search_type == "name":
            results = user_utils.search_users_by_name(search_term, user_ids)
        else:
            results = []
        
        user_ids_list = [user.id for user in results]
        requests_data = set(
            group_request_models.UserGroupRequest.objects.filter(
                sender=sender,
                receiver_id__in=user_ids_list,
                group_id=group_id,
                status=constants.PENDING,
            ).values_list("receiver_id", flat=True)
        )
        
        data = [
            {
                "username": user.username,
                "uid": user.uid,
                "name": user.name,
                "icon": user.icon,
                "isRequested": user.id in requests_data,
            }
            for user in results
        ]

        return Response({"results": data})


class RequestUserView(APIView):
    """Send a group join request to another user."""
    
    def post(self, request, user_uid):
        sender = request.user.user
        role = request.data.get("role", None)
        group_id = request.data.get("groupId", None)
        
        receiver = user_utils.get_user_by_uid(user_uid)
        if not receiver:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if request already exists
        if group_request_models.UserGroupRequest.objects.filter(
            sender=sender,
            receiver=receiver,
            group_id=group_id,
            status__in=[constants.PENDING, constants.ACCEPTED],
        ).exists():
            return Response({"success": False, "message": "Request already exists"})
        
        group_request_utils.create_user_request(sender, receiver, group_id, role)
        return Response({"success": True})


@permission_classes([IsAuthenticated])
class AcceptUserRequestView(APIView):
    """Accept a group join request."""
    
    def post(self, request):
        user = request.user.user
        request_data = request.data
        sender_uid = request_data.get("sender_uid", None)
        
        if not sender_uid:
            return Response(
                {"error": "sender_uid Not Found!"}, status=status.HTTP_404_NOT_FOUND
            )
        
        group_id = request_data.get("group_id", None)
        if not group_id:
            return Response(
                {"error": "GroupId Not Found!"}, status=status.HTTP_404_NOT_FOUND
            )
        
        sender = user_utils.get_user_by_uid(sender_uid)
        request_obj = group_request_models.UserGroupRequest.objects.filter(
            group_id=group_id, receiver=user, sender=sender, status=constants.PENDING
        ).last()
        
        if request_obj:
            success, message = group_request_utils.accept_request(request_obj)
            if success:
                return Response({"message": message})
            else:
                return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"error": "Request not found"}, status=status.HTTP_404_NOT_FOUND)


@permission_classes([IsAuthenticated])
class DeclineUserRequestView(APIView):
    """Decline a group join request."""
    
    def post(self, request):
        user = request.user.user
        request_data = request.data
        sender_uid = request_data.get("sender_uid", None)
        
        if not sender_uid:
            return Response(
                {"error": "sender_uid Not Found!"}, status=status.HTTP_404_NOT_FOUND
            )
        
        group_id = request_data.get("group_id", None)
        if not group_id:
            return Response(
                {"error": "GroupId Not Found!"}, status=status.HTTP_404_NOT_FOUND
            )
        
        sender = user_utils.get_user_by_uid(sender_uid)
        request_obj = group_request_models.UserGroupRequest.objects.filter(
            group_id=group_id, receiver=user, sender=sender, status=constants.PENDING
        ).last()
        
        if request_obj:
            group_request_utils.decline_request(request_obj)
            return Response({"message": "Request declined"})
        
        return Response({"error": "Request not found"}, status=status.HTTP_404_NOT_FOUND)


class GetPendingRequestsView(APIView):
    """Get all pending requests for a group."""
    
    def get(self, request):
        group_id = request.GET.get("group_id", None)
        if not group_id:
            return Response(
                {"error": "GroupId Not Found!"}, status=status.HTTP_404_NOT_FOUND
            )
        
        sender = request.user.user
        pending_requests = group_request_utils.get_pending_requests_for_group(sender, group_id)
        
        data = [
            {
                "username": req.receiver.username,
                "uid": req.receiver.uid,
                "name": req.receiver.name,
                "icon": req.receiver.icon,
                "role": req.role_requested,
                "created_at": req.created_at.strftime("%b %d, %Y")
            }
            for req in pending_requests
        ]
        
        return Response({"pending_requests": data})
