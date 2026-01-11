from django.db import models
from django.contrib.auth.models import User
import json
from .logger import get_logger

logger = get_logger('models')

class SavedTrip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_trips')
    name = models.CharField(max_length=255, default='Untitled Trip')
    trip_data = models.JSONField(default=dict)  # Store all trip state as JSON
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} - {self.user.username}"

    def save(self, *args, **kwargs):
        """Override save to add logging"""
        is_new = self.pk is None
        try:
            super().save(*args, **kwargs)
            action = 'created' if is_new else 'updated'
            logger.debug(f'SavedTrip {action}: {self.id} - {self.name} (user: {self.user.username})')
        except Exception as e:
            logger.error(f'Error saving SavedTrip {self.name} for user {self.user.username}: {str(e)}', exc_info=True)
            raise

    def delete(self, *args, **kwargs):
        """Override delete to add logging"""
        try:
            trip_id = self.id
            trip_name = self.name
            user_name = self.user.username
            super().delete(*args, **kwargs)
            logger.debug(f'SavedTrip deleted: {trip_id} - {trip_name} (user: {user_name})')
        except Exception as e:
            logger.error(f'Error deleting SavedTrip {self.name} for user {self.user.username}: {str(e)}', exc_info=True)
            raise

