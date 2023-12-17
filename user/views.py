from django.shortcuts import render
from django.views import View
from django.contrib import messages

from .forms import CustomerRegistrationForm

# Create your views here.
class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'user/customerregistration.html', {'form': form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(
                request, 'Congratulations!! Registered Successfully')
            form.save()
        return render(request, 'user/customerregistration.html', {'form': form})

