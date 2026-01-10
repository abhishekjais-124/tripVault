"""Expense management utilities"""
from decimal import Decimal
from datetime import datetime
from django.db.models import Sum, Q

from expense.models import Expense, ExpenseSplit, Settlement
from group.models import UserGroupMapping


def create_expense(
    group,
    paid_by,
    title,
    amount,
    date,
    category="other",
    description="",
    split_type="equal",
    splits_data=None,
    split_member_ids=None,
    receipt_file=None,
):
    """Create an expense with flexible splitting.

    Args:
        group: Group instance
        paid_by: User who paid
        title: Expense title
        amount: Total amount paid (Decimal)
        date: Date of expense
        category: Category of expense
        description: Optional description
        split_type: equal | custom | percentage
        splits_data: Dict of {user_id: amount_or_percent}
        split_member_ids: Optional iterable of user_ids to include in split
        receipt_file: Optional uploaded file for receipt
    """

    # Resolve members included in split (default: all active members)
    member_qs = UserGroupMapping.objects.filter(group=group, is_active=True)
    if split_member_ids:
        member_qs = member_qs.filter(user_id__in=split_member_ids)

    members = list(member_qs.select_related("user"))
    if not members:
        raise ValueError("Group has no active members selected for split")

    expense = Expense.objects.create(
        group=group,
        paid_by=paid_by,
        title=title,
        amount=amount,
        date=date,
        category=category,
        description=description,
        receipt=receipt_file,
    )

    # Create splits based on split_type
    member_ids = {m.user_id for m in members}

    if split_type == "equal":
        per_person = (amount / Decimal(len(members))).quantize(Decimal("0.01"))
        for mapping in members:
            ExpenseSplit.objects.create(
                expense=expense,
                user=mapping.user,
                amount_owed=per_person,
            )

    elif split_type == "custom":
        if not splits_data:
            expense.delete()
            raise ValueError("No split amounts provided")
        for user_id, owed_amount in splits_data.items():
            from user.models import User

            if user_id not in member_ids:
                continue
            user = User.objects.get(id=user_id)
            ExpenseSplit.objects.create(
                expense=expense,
                user=user,
                amount_owed=Decimal(str(owed_amount)).quantize(Decimal("0.01")),
            )

    elif split_type == "percentage":
        if not splits_data:
            expense.delete()
            raise ValueError("No split percentages provided")
        total_percent = sum(Decimal(str(pct)) for pct in splits_data.values())
        if total_percent <= 0:
            expense.delete()
            raise ValueError("Percentages must sum to more than 0")
        # Allow slight rounding tolerance around 100%
        if total_percent < Decimal("99.5") or total_percent > Decimal("100.5"):
            expense.delete()
            raise ValueError("Percentages should total roughly 100%")
        for user_id, pct in splits_data.items():
            from user.models import User

            if user_id not in member_ids:
                continue
            user = User.objects.get(id=user_id)
            amount_owed = (amount * Decimal(str(pct)) / Decimal("100")).quantize(
                Decimal("0.01")
            )
            ExpenseSplit.objects.create(
                expense=expense,
                user=user,
                amount_owed=amount_owed,
            )

    else:
        expense.delete()
        raise ValueError("Invalid split type")

    return expense


def get_group_balance(group, user):
    """
    Calculate how much a user owes/is owed in a group.
    
    Returns:
        Positive: user is owed money (creditor)
        Negative: user owes money (debtor)
        Zero: settled up
    """
    # Money user paid
    paid_total = Expense.objects.filter(
        group=group,
        paid_by=user
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    # Money owed by user
    owed_total = ExpenseSplit.objects.filter(
        expense__group=group,
        user=user
    ).aggregate(total=Sum('amount_owed'))['total'] or Decimal('0')
    
    # Balance: positive means user is owed money
    balance = paid_total - owed_total
    return balance


def get_group_expenses(group, user=None):
    """Get all expenses for a group, optionally filtered by user"""
    expenses = Expense.objects.filter(group=group).select_related(
        'paid_by', 'group'
    ).prefetch_related('splits__user').order_by('-date', '-created_at')
    
    if user:
        # Filter for expenses related to this user
        expenses = expenses.filter(
            Q(paid_by=user) | Q(splits__user=user)
        ).distinct()
    
    return expenses


def get_user_balance_with_others(group, user):
    """
    Get balance between user and each other person in the group.
    
    Returns:
        Dict of {user_id: balance}
        Positive: user is owed money by that person
        Negative: user owes money to that person
    """
    balances = {}
    group_members = UserGroupMapping.objects.filter(
        group=group, is_active=True
    ).select_related('user')
    
    for member in group_members:
        other_user = member.user
        if other_user.id == user.id:
            continue
        
        # What user paid for other_user
        paid_for_other = Expense.objects.filter(
            group=group,
            paid_by=user,
            splits__user=other_user
        ).aggregate(total=Sum('splits__amount_owed'))['total'] or Decimal('0')
        
        # What other_user paid for user
        paid_by_other = Expense.objects.filter(
            group=group,
            paid_by=other_user,
            splits__user=user
        ).aggregate(total=Sum('splits__amount_owed'))['total'] or Decimal('0')
        
        # Other user paid for user
        other_user_paid = Expense.objects.filter(
            group=group,
            paid_by=other_user
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # User paid for other user
        user_paid = Expense.objects.filter(
            group=group,
            paid_by=user
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Calculate simple balance
        # Positive: user is owed money
        # Negative: user owes money
        balance = paid_for_other - paid_by_other
        
        if balance != 0:
            balances[other_user.id] = {
                'user': other_user,
                'balance': balance
            }
    
    return balances


def get_total_group_expenses(group):
    """Get total expenses for a group"""
    return Expense.objects.filter(group=group).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')


def delete_expense(expense):
    """Delete an expense and its splits"""
    expense.splits.all().delete()
    expense.delete()
