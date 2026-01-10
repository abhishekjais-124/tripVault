from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from .forms import CustomerRegistrationForm
from user import utils
from user import models
from common import utils as common_utils


class CustomerRegistrationView(APIView):
    """Handle user registration."""
    
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, "user/customerregistration.html", {"form": form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto-login the user after registration
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            authenticated_user = authenticate(username=username, password=password)
            if authenticated_user is not None:
                login(request, authenticated_user)
            return redirect("group")
        return render(request, "user/customerregistration.html", {"form": form})


@method_decorator(login_required(login_url="/user/login/"), name="dispatch")
class UserProfileView(APIView):
    """Handle user profile viewing and updates."""
    
    def get(self, request):
        user = request.user.user
        if not user:
            return Response(
                {"error": "User Not Found!"}, status=status.HTTP_404_NOT_FOUND
            )
        
        from group_request import utils as group_request_utils
        
        requests = []
        pending_requests = group_request_utils.get_user_group_all_pending_request(user)
        for req in pending_requests:
            r = {
                'id': req.id,
                'role': req.role_requested.capitalize(),
                'requested_by': req.sender.username,
                'group_name': req.group.name,
                'time': common_utils.format_time_difference(req.created_at),
                'sender_uid': req.sender.uid,
                'group_id': req.group.id
            }
            requests.append(r.copy())
        return render(request, "user/user_profile.html", {"user": user, 'requests': requests})

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
class NotificationsView(View):
    """Display user notifications for pending group requests and expense activities."""
    
    def get(self, request):
        user = request.user.user
        if not user:
            return redirect('login')
        
        from group_request import utils as group_request_utils
        from common.models import Notification
        
        # Get all pending requests for the current user
        pending_requests = group_request_utils.get_user_group_all_pending_request(user)
        requests = []
        for req in pending_requests:
            r = {
                'id': req.id,
                'role': req.role_requested.capitalize(),
                'requested_by': req.sender.username,
                'sender_name': req.sender.name or req.sender.username,
                'sender_icon': req.sender.icon,
                'group_name': req.group.name,
                'group_id': req.group.id,
                'time': common_utils.format_time_difference(req.created_at),
                'sender_uid': req.sender.uid,
                'type': 'group_request',
            }
            requests.append(r.copy())
        
        # Get expense notifications
        expense_notifications = Notification.objects.filter(user=user).select_related('user')[:50]
        for notif in expense_notifications:
            r = {
                'id': notif.id,
                'title': notif.title,
                'message': notif.message,
                'notification_type': notif.notification_type,
                'time': common_utils.format_time_difference(notif.created_at),
                'type': 'activity',
                'is_read': notif.is_read,
            }
            requests.append(r)
        
        # Sort all notifications by date (most recent first)
        requests.sort(key=lambda x: x.get('time', ''), reverse=True)
        
        return render(request, "user/notifications.html", {"user": user, 'requests': requests})
