from django.contrib import admin
from .models import Expense, ExpenseSplit, Settlement


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'paid_by', 'amount', 'category', 'date', 'created_at')
    list_filter = ('category', 'date', 'group', 'created_at')
    search_fields = ('title', 'paid_by__username', 'group__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'group', 'paid_by', 'amount', 'category')
        }),
        ('Dates', {
            'fields': ('date', 'created_at', 'updated_at')
        }),
    )


@admin.register(ExpenseSplit)
class ExpenseSplitAdmin(admin.ModelAdmin):
    list_display = ('expense', 'user', 'amount_owed', 'is_settled')
    list_filter = ('is_settled', 'created_at')
    search_fields = ('user__username', 'expense__title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'group', 'amount', 'created_at')
    list_filter = ('group', 'created_at')
    search_fields = ('from_user__username', 'to_user__username')
    readonly_fields = ('created_at', 'updated_at')
