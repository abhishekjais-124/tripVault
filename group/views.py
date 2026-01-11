from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from group import utils as group_utils
from group import models as group_models
from user import constants
from expense import utils as expense_utils
from decimal import Decimal


@method_decorator(login_required(login_url="/tripvault/user/login/"), name="dispatch")
class GroupView(APIView):
    """Handle group listing and creation."""
    
    def get(self, request):
        user = request.user.user
        if not user:
            return Response(
                {"error": "User Not Found!"}, status=status.HTTP_404_NOT_FOUND
            )
        group_ids = group_utils.get_user_groups(user)
        if not group_ids:
            return render(request, "user/group.html", {"user": user, "overall_balance": Decimal("0"), "overall_is_debtor": False})
        group_user_mapping = group_utils.create_group_user_mapping(
            list(set(group_ids)), user
        ).values()

        # Compute overall balance across all groups for this user
        overall_balance = Decimal("0")
        for grp in group_models.Group.objects.filter(id__in=list(set(group_ids)), is_active=True):
            overall_balance += expense_utils.get_group_balance(grp, user)
        overall_is_debtor = overall_balance < 0
        return render(
            request,
            "user/group_table.html",
            {"user": user, "group_user_mapping": group_user_mapping, "overall_balance": overall_balance, "overall_is_debtor": overall_is_debtor},
        )

    def post(self, request):
        user = request.user.user
        name = request.POST.get("groupName")
        description = request.POST.get("groupDescription", "").strip()
        if not name:
            return redirect("group")
        group_utils.create_user_group(name, user, description or None)
        return redirect("group")


@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
class UserGroupView(APIView):
    """Handle user removal from groups."""
    
    def delete(self, request):
        request_data = request.data
        user_id = request_data.get("user_id", None)
        if not user_id:
            return Response(
                {"error": "UserId Not Found!"}, status=status.HTTP_404_NOT_FOUND
            )
        group_id = request_data.get("group_id", None)
        if not group_id:
            return Response(
                {"error": "GroupId Not Found!"}, status=status.HTTP_404_NOT_FOUND
            )
        group_models.UserGroupMapping.objects.filter(
            user_id=user_id, group_id=group_id
        ).update(is_active=False)
        return Response({"message": "DELETE request processed successfully"})
