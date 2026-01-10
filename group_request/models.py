from django.db import models

from common.models import BaseModel
from user import constants


class UserGroupRequest(BaseModel):
    """Model for group join requests between users."""
    sender = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name="sent_requests")
    receiver = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name="received_requests")
    group = models.ForeignKey("group.Group", on_delete=models.CASCADE, related_name="requests")
    role_requested = models.CharField(
        max_length=10, choices=constants.ROLE_CHOICES, default="Member"
    )
    status = models.IntegerField(choices=constants.REQUEST_CHOICES, default=constants.PENDING)
    # When true, the receiver dismissed the request notification
    is_dismissed = models.BooleanField(default=False)
    # Tracks if the receiver has opened the activities page and seen this request
    is_seen = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Group Request"
        verbose_name_plural = "Group Requests"

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.group.name})"
