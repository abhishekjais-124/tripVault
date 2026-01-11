"""URL routing for expense app"""
from django.urls import path
from . import views

urlpatterns = [
    path('group/<int:group_id>/expenses/', views.GroupExpensesView.as_view(), name='group_expenses'),
    path('group/<int:group_id>/expenses/add/', views.AddExpenseView.as_view(), name='add_expense'),
    path('group/<int:group_id>/settlements/add/', views.AddSettlementView.as_view(), name='add_settlement'),
    path('expense/<int:expense_id>/detail/', views.ExpenseDetailView.as_view(), name='expense_detail'),
    path('expense/<int:expense_id>/delete/', views.DeleteExpenseView.as_view(), name='delete_expense'),
]
