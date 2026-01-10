from django.db import models
from common.models import BaseModel
from user.models import User
from group.models import Group


class Expense(BaseModel):
    """Model to track expenses in a group"""
    
    # Relationship fields
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='expenses')
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses_paid')
    
    # Expense details
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # How much was paid
    date = models.DateField()
    description = models.TextField(null=True, blank=True)
    receipt = models.FileField(upload_to='expense_receipts/', null=True, blank=True)
    
    # Category
    CATEGORY_CHOICES = [
        ('food', 'Food'),
        ('transport', 'Transport'),
        ('accommodation', 'Accommodation'),
        ('activity', 'Activity'),
        ('shopping', 'Shopping'),
        ('utilities', 'Utilities'),
        ('other', 'Other'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.amount} (by {self.paid_by.username})"


class ExpenseSplit(BaseModel):
    """Model to track who owes what for each expense"""
    
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='splits')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expense_splits')
    amount_owed = models.DecimalField(max_digits=10, decimal_places=2)  # How much this user owes
    is_settled = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('expense', 'user')
    
    def __str__(self):
        return f"{self.user.username} owes {self.amount_owed} for {self.expense.title}"


class Settlement(BaseModel):
    """Model to track payments/settlements between users in a group"""
    
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='settlements')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_made')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_received')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.from_user.username} paid {self.amount} to {self.to_user.username}"
