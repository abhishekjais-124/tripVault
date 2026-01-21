from django import forms
from .models import Group, UserGroupMapping

class GroupEditForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description']

class UserGroupMappingForm(forms.ModelForm):
    class Meta:
        model = UserGroupMapping
        fields = ['is_primary']
