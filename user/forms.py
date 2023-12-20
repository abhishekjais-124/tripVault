from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext, gettext_lazy as _
from django.core.exceptions import ValidationError


class CustomerRegistrationForm(UserCreationForm):
    username = UsernameField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'autofocus': True}))
    password1 = forms.CharField(
        label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(
        label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.CharField(required=True, widget=forms.EmailInput(
        attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {'email': 'Email'}

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered")
        return email


class LoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'autofocus': True}))
    password = forms.CharField(label=_('Password'), strip=False, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'autocomplete': 'current-password'}))

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and not self.user_cache:
            raise forms.ValidationError(
                self.error_messages["Username doesn't exist"],
                code='invalid_login',
                params={'username': self.username_field.verbose_name},
            )

        if username and self.user_cache and not self.user_cache.check_password(password):
            raise forms.ValidationError(
                self.error_messages['Invalid password'],
                code='invalid_login',
                params={'username': self.username_field.verbose_name},
            )

        return cleaned_data