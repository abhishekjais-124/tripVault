from django.contrib import admin
from .models import Group, UserGroupMapping


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'uid', 'created_by', 'users_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'uid', 'created_by')
    readonly_fields = ('uid', 'created_at', 'updated_at')


@admin.register(UserGroupMapping)
class UserGroupMappingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'group', 'role', 'is_active', 'is_primary', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('user__username', 'group__name')
    readonly_fields = ('created_at', 'updated_at')

