"""Views for expense management"""
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from group.models import Group, UserGroupMapping
from expense import utils as expense_utils
from expense.models import Expense, ExpenseSplit


@method_decorator(login_required(login_url="/user/login/"), name="dispatch")
class GroupExpensesView(APIView):
    """Display all expenses for a group with balance information"""
    
    def get(self, request, group_id):
        user = request.user.user
        if not user:
            return Response(
                {"error": "User Not Found!"}, status=status.HTTP_404_NOT_FOUND
            )
        
        # Get group and verify user is a member
        group = get_object_or_404(Group, id=group_id, is_active=True)
        is_member = UserGroupMapping.objects.filter(
            user=user, group=group, is_active=True
        ).exists()
        
        if not is_member:
            return Response(
                {"error": "You are not a member of this group"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get expenses
        expenses = expense_utils.get_group_expenses(group)
        
        # Calculate balances
        overall_balance = expense_utils.get_group_balance(group, user)
        total_group_expenses = expense_utils.get_total_group_expenses(group)
        
        # Format expenses for template
        formatted_expenses = []
        for expense in expenses:
            # Get user's split for this expense
            user_split = expense.splits.filter(user=user).first()
            amount_owed = user_split.amount_owed if user_split else None
            
            formatted_expenses.append({
                'id': expense.id,
                'title': expense.title,
                'paid_by': expense.paid_by,
                'amount': expense.amount,
                'amount_owed': amount_owed,
                'date': expense.date,
                'category': expense.get_category_display(),
                'description': expense.description,
                'is_paid_by_user': expense.paid_by.id == user.id,
                'is_owed_by_user': amount_owed and amount_owed > 0,
            })
        
        context = {
            'user': user,
            'group': group,
            'expenses': formatted_expenses,
            'overall_balance': overall_balance,
            'total_expenses': total_group_expenses,
            'user_is_debtor': overall_balance < 0,
        }
        
        return render(request, 'expense/group_expenses.html', context)


@method_decorator(login_required(login_url="/user/login/"), name="dispatch")
class AddExpenseView(APIView):
    """Add a new expense to a group"""
    
    def get(self, request, group_id):
        user = request.user.user
        if not user:
            return Response(
                {"error": "User Not Found!"}, status=status.HTTP_404_NOT_FOUND
            )
        
        group = get_object_or_404(Group, id=group_id, is_active=True)
        is_member = UserGroupMapping.objects.filter(
            user=user, group=group, is_active=True
        ).exists()
        
        if not is_member:
            return Response(
                {"error": "You are not a member of this group"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get group members for split options
        group_members = UserGroupMapping.objects.filter(
            group=group, is_active=True
        ).select_related('user')
        
        context = {
            'user': user,
            'group': group,
            'group_members': group_members,
            'categories': Expense._meta.get_field('category').choices,
        }
        
        return render(request, 'expense/add_expense.html', context)
    
    def post(self, request, group_id):
        user = request.user.user
        if not user:
            return Response(
                {"error": "User Not Found!"}, status=status.HTTP_404_NOT_FOUND
            )
        
        group = get_object_or_404(Group, id=group_id, is_active=True)
        is_member = UserGroupMapping.objects.filter(
            user=user, group=group, is_active=True
        ).exists()
        
        if not is_member:
            return Response(
                {"error": "You are not a member of this group"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get form data
        title = request.POST.get('title', '').strip()
        amount_raw = request.POST.get('amount', '').strip()
        date = request.POST.get('date', '').strip()
        category = request.POST.get('category', 'other')
        description = request.POST.get('description', '').strip()
        split_type = request.POST.get('split_type', 'equal')
        paid_by_id = request.POST.get('paid_by') or None
        receipt_file = request.FILES.get('receipt')

        # Validation
        if not all([title, amount_raw, date]):
            messages.error(request, "Title, amount, and date are required.")
            return redirect('group_expenses', group_id=group_id)

        # Amount validation
        from decimal import Decimal, InvalidOperation

        try:
            amount = Decimal(amount_raw)
            if amount <= 0:
                raise InvalidOperation("Amount must be positive")
        except (InvalidOperation, TypeError):
            messages.error(request, "Invalid amount.")
            return redirect('group_expenses', group_id=group_id)

        # Resolve paid_by (defaults to current user)
        paid_by_user = user
        if paid_by_id:
            try:
                paid_by_user = UserGroupMapping.objects.get(
                    group=group, user_id=paid_by_id, is_active=True
                ).user
            except UserGroupMapping.DoesNotExist:
                messages.error(request, "Selected payer is not in the group.")
                return redirect('group_expenses', group_id=group_id)

        # Determine members included in split
        selected_member_ids = request.POST.getlist('split_member')
        if not selected_member_ids:
            # default to all active members
            selected_member_ids = list(
                UserGroupMapping.objects.filter(group=group, is_active=True).values_list('user_id', flat=True)
            )

        # Parse splits
        splits_data = {}
        if split_type == 'custom':
            for member_id in selected_member_ids:
                member_amount_raw = request.POST.get(f'split_amount_{member_id}', '').strip()
                if not member_amount_raw:
                    continue
                try:
                    splits_data[int(member_id)] = float(member_amount_raw)
                except (ValueError, TypeError):
                    continue

        elif split_type == 'percentage':
            for member_id in selected_member_ids:
                pct_raw = request.POST.get(f'split_percent_{member_id}', '').strip()
                if not pct_raw:
                    continue
                try:
                    splits_data[int(member_id)] = float(pct_raw)
                except (ValueError, TypeError):
                    continue

            # Basic sum validation
            total_pct = sum(splits_data.values())
            if total_pct <= 0:
                messages.error(request, "Please provide percentages greater than 0.")
                return redirect('group_expenses', group_id=group_id)

        # Create expense
        try:
            expense_utils.create_expense(
                group=group,
                paid_by=paid_by_user,
                title=title,
                amount=amount,
                date=date,
                category=category,
                description=description,
                split_type=split_type,
                splits_data=splits_data or None,
                split_member_ids=[int(mid) for mid in selected_member_ids],
                receipt_file=receipt_file,
            )

            # Create a notification for the expense creation
            try:
                from common.models import Notification
                
                # Notify all group members about the new expense
                group_members = UserGroupMapping.objects.filter(
                    group=group, is_active=True
                ).values_list('user_id', flat=True)
                
                notification_message = f"{user.username} added expense '{title}' (₹{amount}) to the group"
                
                for member_id in group_members:
                    Notification.objects.create(
                        user_id=member_id,
                        title="New Expense",
                        message=notification_message,
                        notification_type="expense_added",
                        metadata={"expense_title": title, "amount": str(amount), "added_by": user.username}
                    )
            except Exception as e:
                # Log but don't fail if notification creation fails
                print(f"Error creating notification: {str(e)}")

            messages.success(request, f"Expense '{title}' added successfully!")
            return redirect('group_expenses', group_id=group_id)

        except Exception as e:
            messages.error(request, f"Error creating expense: {str(e)}")
            return redirect('group_expenses', group_id=group_id)


@method_decorator(login_required(login_url="/user/login/"), name="dispatch")
class DeleteExpenseView(APIView):
    """Delete an expense (only by person who created it)"""
    
    def post(self, request, expense_id):
        user = request.user.user
        if not user:
            return Response(
                {"error": "User Not Found!"}, status=status.HTTP_404_NOT_FOUND
            )
        
        expense = get_object_or_404(Expense, id=expense_id)
        
        # Only the person who paid can delete
        if expense.paid_by.id != user.id:
            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return Response(
                    {"success": False, "error": "You can only delete expenses you created."},
                    status=status.HTTP_403_FORBIDDEN
                )
            messages.error(request, "You can only delete expenses you created.")
            return redirect('group_expenses', group_id=expense.group_id)
        
        group_id = expense.group_id
        expense_title = expense.title
        
        # Delete the expense
        expense_utils.delete_expense(expense)
        
        # Create a notification for the expense deletion
        try:
            from common.models import Notification
            from django.utils import timezone
            from datetime import datetime
            
            # Notify all group members about the deletion
            group_members = UserGroupMapping.objects.filter(
                group_id=group_id, is_active=True
            ).values_list('user_id', flat=True)
            
            notification_message = f"{user.username} deleted expense '{expense_title}' from the group"
            
            for member_id in group_members:
                Notification.objects.create(
                    user_id=member_id,
                    title="Expense Deleted",
                    message=notification_message,
                    notification_type="expense_deleted",
                    metadata={"expense_title": expense_title, "deleted_by": user.username}
                )
        except Exception as e:
            # Log but don't fail if notification creation fails
            print(f"Error creating notification: {str(e)}")
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return Response(
                {"success": True, "message": f"Expense '{expense_title}' deleted successfully!"},
                status=status.HTTP_200_OK
            )
        
        messages.success(request, f"Expense '{expense_title}' deleted successfully!")
        return redirect('group_expenses', group_id=group_id)


@method_decorator(login_required(login_url="/user/login/"), name="dispatch")
class ExpenseDetailView(APIView):
    """Display detailed information about a single expense"""
    
    def get(self, request, expense_id):
        user = request.user.user
        if not user:
            return Response(
                {"error": "User Not Found!"}, status=status.HTTP_404_NOT_FOUND
            )
        
        expense = get_object_or_404(Expense, id=expense_id)
        group = expense.group
        
        # Verify user is a member of the group
        is_member = UserGroupMapping.objects.filter(
            user=user, group=group, is_active=True
        ).exists()
        
        if not is_member:
            return Response(
                {"error": "You are not a member of this group"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get user's split for this expense
        user_split = expense.splits.filter(user=user).first()
        
        # Get all splits for the expense
        all_splits = []
        for split in expense.splits.all():
            all_splits.append({
                'username': split.user.username,
                'user_icon': split.user.icon,
                'amount_owed': float(split.amount_owed),
            })
        
        context = {
            'user': user,
            'expense': {
                'id': expense.id,
                'title': expense.title,
                'amount': float(expense.amount),
                'date': expense.date,
                'category': expense.get_category_display(),
                'description': expense.description,
                'receipt': expense.receipt,
                'paid_by': expense.paid_by,
                'group': group,
                'is_paid_by_user': expense.paid_by.id == user.id,
                'user_amount_owed': float(user_split.amount_owed) if user_split else 0,
            },
            'all_splits': all_splits,
        }
        
        return render(request, 'expense/expense_detail.html', context)
