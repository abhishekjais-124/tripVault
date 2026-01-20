from decimal import Decimal
from expense.utils import get_group_balance
from group.models import Group, UserGroupMapping

def overall_balance_context(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'user'):
        return {}
    user = request.user.user
    # Get all groups the user is a member of
    group_ids = UserGroupMapping.objects.filter(user=user, is_active=True).values_list('group_id', flat=True)
    groups = Group.objects.filter(id__in=group_ids)
    overall_balance = Decimal('0')
    for group in groups:
        overall_balance += get_group_balance(group, user)
    overall_is_debtor = overall_balance < 0
    return {
        'overall_balance': overall_balance,
        'overall_is_debtor': overall_is_debtor,
    }
