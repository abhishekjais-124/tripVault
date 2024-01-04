import json

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


from .forms import CustomerRegistrationForm
from user import utils
from user import models
from user import constants


# Create your views here.
class CustomerRegistrationView(APIView):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, "user/customerregistration.html", {"form": form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
        return render(request, "user/customerregistration.html", {"form": form})


@method_decorator(login_required(login_url="/user/login/"), name="dispatch")
class UserProfile(APIView):
    def get(self, request):
        user = request.user.user
        if not user:
            return Response(
                {"error": "User Not Found!"}, status=status.HTTP_404_NOT_FOUND
            )
        dummy_requests = [
            {'id': 1, 'requested_by': 'User1', 'group_name': 'GroupA', 'time': '2024-01-01 12:00:00'},
            {'id': 2, 'requested_by': 'User2', 'group_name': 'GroupB', 'time': '2024-01-02 14:30:00'},
            {'id': 2, 'requested_by': 'User2', 'group_name': 'GroupB', 'time': '2024-01-02 14:30:00'},
            {'id': 2, 'requested_by': 'User2', 'group_name': 'GroupB', 'time': '2024-01-02 14:30:00'},
            {'id': 2, 'requested_by': 'User2', 'group_name': 'GroupB', 'time': '2024-01-02 14:30:00'},
            {'id': 2, 'requested_by': 'User2', 'group_name': 'GroupB', 'time': '2024-01-02 14:30:00'},
            {'id': 2, 'requested_by': 'User2', 'group_name': 'GroupB', 'time': '2024-01-02 14:30:00'},
            {'id': 2, 'requested_by': 'User2', 'group_name': 'GroupB', 'time': '2024-01-02 14:30:00'},
            # Add more dummy entries as needed
        ]
        return render(request, "user/user_profile.html", {"user": user, 'requests': dummy_requests})

    def post(self, request):
        full_name = request.POST.get("fullName").strip()
        email = request.POST.get("eMail").strip()
        phone_number = request.POST.get("phone").strip()

        user_instance = request.user.user

        valid, msg = utils.validate(full_name, email, phone_number)
        if not valid:
            messages.add_message(request, messages.ERROR, msg, extra_tags="danger")
            return render(request, "user/user_profile.html", {"user": user_instance})

        # Update user details
        user_instance.name = full_name
        user_instance.auth_user.email = email
        user_instance.email = email
        user_instance.phone_number = phone_number

        # Save changes
        user_instance.save()
        user_instance.auth_user.save()

        messages.success(request, "User details updated successfully.")

        return render(request, "user/user_profile.html", {"user": user_instance})


@method_decorator(login_required(login_url="/user/login/"), name="dispatch")
class GroupView(APIView):
    def get(self, request):
        user = request.user.user
        if not user:
            return Response(
                {"error": "User Not Found!"}, status=status.HTTP_404_NOT_FOUND
            )
        group_ids = utils.get_user_groups(user)
        if not group_ids:
            return render(request, "user/group.html", {"user": user})
        group_user_mapping = utils.create_group_user_mapping(
            list(set(group_ids)), user
        ).values()
        return render(
            request,
            "user/group_table.html",
            {"user": user, "group_user_mapping": group_user_mapping},
        )

    def post(self, request):
        user = request.user.user
        name = request.POST.get("groupName")
        if not name:
            return redirect("group")
        utils.create_user_group(name, user)
        return redirect("group")


@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
class UserGroupView(APIView):
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
        models.UserGroupMapping.objects.filter(
            user_id=user_id, group_id=group_id
        ).update(is_active=False)
        return Response({"message": "DELETE request processed successfully"})


class SearchUser(APIView):
    def get(self, request):
        search_type = request.GET.get("type", "id")
        search_term = request.GET.get("term", "").strip()
        group_id = request.GET.get("group", "")
        user_ids = list(
            models.UserGroupMapping.objects.filter(
                group_id=group_id, is_active=True
            ).values_list("user_id", flat=True)
        )
        sender = request.user.user
        if search_term and search_type == "id":
            results = models.User.objects.filter(uid=search_term).exclude(
                id__in=user_ids
            )
        elif search_term and search_type == "username":
            results = models.User.objects.filter(username=search_term).exclude(
                id__in=user_ids
            )
        elif search_term and search_type == "name":
            results = models.User.objects.filter(name__icontains=search_term).exclude(
                id__in=user_ids
            )
        else:
            results = []
        user_ids_list = [user.id for user in results]
        requests_data = set(
            models.UserGroupRequests.objects.filter(
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
    def post(self, request, user_uid):
        sender = request.user.user
        role = request.data.get("role", None)
        groupId = request.data.get("groupId", None)
        print(groupId, role)
        receiver = utils.get_user_by_uid(user_uid)
        if models.UserGroupRequests.objects.filter(
            sender=sender,
            receiver=receiver,
            group_id=groupId,
            status__in=[constants.PENDING, constants.ACCEPTED],
        ).exists():
            return Response({"success": False})
        utils.create_user_request(sender, receiver, groupId, role)
        return Response({"success": True})


@permission_classes([IsAuthenticated])
class AcceptUserView(APIView):
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
        sender = utils.get_user_by_uid(sender_uid)
        request = models.UserGroupRequests.objects.filter(
            group_id=group_id, receiver=user, sender=sender, status=constants.PENDING
        ).last()
        if request:
            request.status = constants.ACCEPTED
            request.save()
            models.UserGroupMapping.objects.create(
                user=sender, group_id=group_id, role=request.role_requested
            )
        return Response({"message": "POST request processed successfully"})


@permission_classes([IsAuthenticated])
class DeclineUserView(APIView):
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
        sender = utils.get_user_by_uid(sender_uid)
        request = models.UserGroupRequests.objects.filter(
            group_id=group_id, receiver=user, sender=sender, status=constants.PENDING
        ).last()
        if request:
            request.status = constants.DECLINED
            request.save()
        return Response({"message": "POST request processed successfully"})
