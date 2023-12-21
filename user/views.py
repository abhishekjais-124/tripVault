from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from .forms import CustomerRegistrationForm
from user import utils


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


@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class UserProfile(APIView):
    def get(self, request):
        # user_uid = request.query_params.get("user_uid", None)
        # if not user_uid:
        #     return Response(
        #         {"error": "Missing user uid"},
        #         status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #     )
        # user = utils.get_user_by_uid(user_uid)
        user = request.user.user
        if not user:
            return Response(
                {"error": "User Not Found!"}, status=status.HTTP_404_NOT_FOUND
            )
        return render(request, "user/user_profile.html", {"user": user})

    def post(self, request):
        full_name = request.POST.get('fullName').strip()
        email = request.POST.get('eMail').strip()
        phone_number = request.POST.get('phone').strip()

        user_instance = request.user.user

        valid, msg = utils.validate(full_name, email, phone_number)
        if not valid:
            messages.add_message(request, messages.ERROR, msg, extra_tags='danger')
            return render(request, "user/user_profile.html", {"user": user_instance})

        # Update user details
        user_instance.name = full_name
        user_instance.auth_user.email = email
        user_instance.email = email
        user_instance.phone_number = phone_number

        # Save changes
        user_instance.save()
        user_instance.auth_user.save()

        messages.success(request, 'User details updated successfully.')

        return render(request, "user/user_profile.html", {"user": user_instance})
    

@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class GroupView(APIView):
    def get(self, request):
        user = request.user.user
        if not user:
            return Response(
                {"error": "User Not Found!"}, status=status.HTTP_404_NOT_FOUND
            )
        return render(request, "user/group_table.html", {"user": user})
        
        return render(request, "user/group.html", {"user": user})
        

    # def post(self, request):
    #     # Extract data from the request
    #     uid = request.POST.get('uid')
    #     name = request.POST.get('name')
    #     is_active = request.POST.get('is_active')
    #     created_by = request.POST.get('created_by')
    #     users_count = request.POST.get('users_count')

    #     # Use the utility function to fetch and set data
    #     fetch_and_set_data(uid, name, is_active, created_by, users_count)

    #     return JsonResponse({'message': 'Data successfully saved'})