from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
import os
import json
from dotenv import load_dotenv
from pathlib import Path

from .forms import CustomerRegistrationForm
from user import utils
from user import models
from common import utils as common_utils

User = get_user_model()

# Load environment variables from .env.local
env_path = Path(__file__).resolve().parent.parent / '.env.local'
load_dotenv(env_path)


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
        
        # Mark all existing activity notifications as read when landing here
        Notification.objects.filter(user=user, is_read=False).update(is_read=True)

        # Get all pending requests for the current user
        pending_requests = group_request_utils.get_user_group_all_pending_request(user)
        # Mark them as seen so navbar superscript hides until a new one arrives
        from group_request import models as group_request_models
        group_request_models.UserGroupRequest.objects.filter(
            id__in=[req.id for req in pending_requests]
        ).update(is_seen=True)
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
                'created_at': req.created_at,
            }
            requests.append(r.copy())
        
        # Get expense notifications
        expense_notifications = Notification.objects.filter(user=user).select_related('user').order_by('-created_at')[:50]
        for notif in expense_notifications:
            r = {
                'id': notif.id,
                'title': notif.title,
                'message': notif.message,
                'notification_type': notif.notification_type,
                'time': common_utils.format_time_difference(notif.created_at),
                'type': 'activity',
                'is_read': notif.is_read,
                'created_at': notif.created_at,
            }
            requests.append(r)
        
        # Sort all notifications by date (most recent first)
        requests.sort(key=lambda x: x.get('created_at'), reverse=True)
        
        return render(request, "user/notifications.html", {"user": user, 'requests': requests})


@method_decorator(login_required(login_url="/user/login/"), name="dispatch")
class MarkAllNotificationsReadView(APIView):
    """Mark all activity notifications as read for the current user."""

    def post(self, request):
        user = request.user.user
        if not user:
            return Response({"error": "User Not Found!"}, status=status.HTTP_404_NOT_FOUND)

        from common.models import Notification

        Notification.objects.filter(user=user, is_read=False).update(is_read=True)
        return Response({"success": True})


@method_decorator(login_required(login_url="/user/login/"), name="dispatch")
class FriendsView(View):
    """List friends (users who share groups with you) with balances."""

    def get(self, request):
        user = request.user.user
        if not user:
            return redirect('login')

        from decimal import Decimal
        from group.models import Group, UserGroupMapping
        from group import utils as group_utils
        from expense import utils as expense_utils

        # All active groups for current user
        group_ids = set(group_utils.get_user_groups(user))

        # Build friend mapping: friend_id -> set of shared group_ids
        friend_groups = {}
        if group_ids:
            mappings = UserGroupMapping.objects.filter(
                group_id__in=group_ids,
                is_active=True
            ).select_related('user', 'group')

            for m in mappings:
                other = m.user
                if other.id == user.id:
                    continue
                if other.id not in friend_groups:
                    friend_groups[other.id] = {
                        'user': other,
                        'groups': set()
                    }
                friend_groups[other.id]['groups'].add(m.group_id)

        # Compute per-friend aggregated balance across shared groups
        friends = []
        overall_balance = Decimal('0')
        groups_cache = {}
        for gid in group_ids:
            # Cache group instances for later lookups
            try:
                groups_cache[gid] = groups_cache.get(gid) or Group.objects.get(id=gid)
            except Group.DoesNotExist:
                continue
            # Sum overall user balance across groups (credit positive, debt negative)
            overall_balance += expense_utils.get_group_balance(groups_cache[gid], user)

        for fid, info in friend_groups.items():
            other_user = info['user']
            balance_sum = Decimal('0')
            for gid in info['groups']:
                group = groups_cache.get(gid)
                if not group:
                    try:
                        group = Group.objects.get(id=gid)
                        groups_cache[gid] = group
                    except Group.DoesNotExist:
                        continue
                # Pairwise balance in this group
                pair_balances = expense_utils.get_user_balance_with_others(group, user)
                fb = pair_balances.get(fid, {}).get('balance', Decimal('0'))
                balance_sum += fb

            friends.append({
                'uid': other_user.uid,
                'username': other_user.username,
                'name': other_user.name or other_user.username,
                'icon': other_user.icon,
                'groups_count': len(info['groups']),
                'balance': balance_sum,
                'is_debtor': balance_sum < 0,
            })

        # Optional: sort by magnitude of balance, then name
        friends.sort(key=lambda f: (abs(f['balance']), f['name'].lower()), reverse=True)

        context = {
            'user': user,
            'friends': friends,
            'overall_balance': overall_balance,
            'overall_is_debtor': overall_balance < 0,
        }
        return render(request, "user/friends.html", context)


@method_decorator(login_required(login_url="/user/login/"), name="dispatch")
class FriendDetailView(View):
    """Show detailed, per-group expenses between you and a friend."""

    def get(self, request, friend_uid):
        user = request.user.user
        if not user:
            return redirect('login')

        from decimal import Decimal
        from django.shortcuts import get_object_or_404
        from group.models import Group, UserGroupMapping
        from group import utils as group_utils
        from expense import utils as expense_utils
        from user.models import User as AppUser

        friend = get_object_or_404(AppUser, uid=friend_uid)

        # Determine shared groups
        user_group_ids = set(group_utils.get_user_groups(user))
        friend_group_ids = set(
            UserGroupMapping.objects.filter(user=friend, is_active=True).values_list('group_id', flat=True)
        )
        shared_group_ids = list(user_group_ids.intersection(friend_group_ids))

        groups = []
        overall_balance = Decimal('0')
        for gid in shared_group_ids:
            try:
                group = Group.objects.get(id=gid)
            except Group.DoesNotExist:
                continue

            # Pairwise net balance for this group
            pair_balances = expense_utils.get_user_balance_with_others(group, user)
            net = pair_balances.get(friend.id, {}).get('balance', Decimal('0'))
            overall_balance += net

            groups.append({
                'group': group,
                'net': net,
                'is_debtor': net < 0,
            })

        context = {
            'user': user,
            'friend': {
                'uid': friend.uid,
                'username': friend.username,
                'name': friend.name or friend.username,
                'icon': friend.icon,
            },
            'groups': groups,
            'overall_balance': overall_balance,
            'overall_is_debtor': overall_balance < 0,
        }

        return render(request, "user/friend_detail.html", context)


class SupportView(View):
    """Display support page with contact form."""

    def get(self, request):
        context = {
            'emailjs_public_key': os.getenv('NEXT_PUBLIC_EMAILJS_PUBLIC_KEY', ''),
            'emailjs_service_id': os.getenv('NEXT_PUBLIC_EMAILJS_SERVICE_ID', 'service_1'),
            'emailjs_template_id': os.getenv('NEXT_PUBLIC_EMAILJS_TEMPLATE_ID', 'template_lccopu4'),
        }
        return render(request, "user/support.html", context)


class SendContactEmailView(APIView):
    """Handle contact form email submission via emailJS."""

    def post(self, request):
        """
        Receives contact form data from emailJS.
        EmailJS will send the email directly, but we log it in our system.
        """
        import json
        from django.core.mail import send_mail
        from django.conf import settings

        try:
            data = json.loads(request.body)
            name = data.get('from_name', '')
            email = data.get('from_email', '')
            subject = data.get('subject', '')
            message = "TripVault Support: " + data.get('message', '')

            if not all([name, email, subject, message]):
                return Response(
                    {"error": "All fields are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Optional: Send a copy to your support email using Django's mail backend
            # Uncomment and configure if you want Django to also handle emails
            # try:
            #     send_mail(
            #         f"Support Request: {subject}",
            #         f"From: {name} ({email})\n\n{message}",
            #         settings.DEFAULT_FROM_EMAIL,
            #         ['support@tripvault.com'],
            #         fail_silently=False,
            #     )
            # except Exception as e:
            #     print(f"Error sending email: {e}")

            return Response(
                {"success": True, "message": "Email sent successfully"},
                status=status.HTTP_200_OK
            )
        except json.JSONDecodeError:
            return Response(
                {"error": "Invalid JSON"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ForgotPasswordView(View):
    """Handle forgot password - send reset email."""
    
    def get(self, request):
        return render(request, "user/forgot_password.html")
    
    def post(self, request):
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, "Please enter your email address.")
            return render(request, "user/forgot_password.html")
        
        # Find user by email
        try:
            user = User.objects.get(email=email)
            user_profile = user.user
            
            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build reset link
            reset_url = request.build_absolute_uri(
                f'/user/reset-password/{uid}/{token}/'
            )
            
            # Prepare email data for EmailJS
            email_data = {
                'to_email': email,
                'user_name': user_profile.name or user.username,
                'reset_link': reset_url,
                'site_name': 'TripVault'
            }
            
            # Return success with email data (will be sent via EmailJS on frontend)
            return render(request, "user/forgot_password.html", {
                'success': True,
                'email_data': json.dumps(email_data),
                'emailjs_public_key': os.getenv('NEXT_PUBLIC_EMAILJS_PUBLIC_KEY', ''),
                'emailjs_service_id': os.getenv('NEXT_PUBLIC_EMAILJS_SERVICE_ID', 'service_1'),
                'emailjs_template_id': 'template_password_reset'
            })
            
        except User.DoesNotExist:
            # Security best practice: Don't reveal if email exists or not
            # Show same success message to prevent email enumeration attacks
            return render(request, "user/forgot_password.html", {
                'success': True,
                'no_account': True,
                'submitted_email': email
            })
        except Exception as e:
            messages.error(request, "An error occurred. Please try again.")
            return render(request, "user/forgot_password.html")


class ResetPasswordView(View):
    """Handle password reset with token."""
    
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            if default_token_generator.check_token(user, token):
                return render(request, "user/reset_password.html", {
                    'validlink': True,
                    'uidb64': uidb64,
                    'token': token
                })
            else:
                return render(request, "user/reset_password.html", {
                    'validlink': False,
                    'error': 'Invalid or expired reset link.'
                })
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return render(request, "user/reset_password.html", {
                'validlink': False,
                'error': 'Invalid reset link.'
            })
    
    def post(self, request, uidb64, token):
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        
        if not password1 or not password2:
            messages.error(request, "Please fill in both password fields.")
            return render(request, "user/reset_password.html", {
                'validlink': True,
                'uidb64': uidb64,
                'token': token
            })
        
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "user/reset_password.html", {
                'validlink': True,
                'uidb64': uidb64,
                'token': token
            })
        
        if len(password1) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, "user/reset_password.html", {
                'validlink': True,
                'uidb64': uidb64,
                'token': token
            })
        
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            if default_token_generator.check_token(user, token):
                user.set_password(password1)
                user.save()
                messages.success(request, "Password reset successful! You can now login with your new password.")
                return redirect('login')
            else:
                return render(request, "user/reset_password.html", {
                    'validlink': False,
                    'error': 'Invalid or expired reset link.'
                })
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return render(request, "user/reset_password.html", {
                'validlink': False,
                'error': 'Invalid reset link.'
            })
