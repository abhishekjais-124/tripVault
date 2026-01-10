from django.contrib import admin
from .models import UserGroupRequest


@admin.register(UserGroupRequest)
class UserGroupRequestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'group', 'role_requested', 'status', 'created_at')
    list_filter = ('status', 'role_requested', 'created_at')
    search_fields = ('sender__username', 'receiver__username', 'group__name')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('sender', 'receiver', 'group')
        return self.readonly_fields

