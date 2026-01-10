from django.db import models
from django.contrib.auth.models import User as AuthUser

# Create your models here.
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Notification(BaseModel):
    """Model to store user notifications for various events"""
    
    NOTIFICATION_TYPES = [
        ('expense_added', 'Expense Added'),
        ('expense_deleted', 'Expense Deleted'),
        ('group_request', 'Group Request'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='other')
    metadata = models.JSONField(default=dict, blank=True)  # Store additional data like expense_id, etc.
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} - {self.user.username}"
