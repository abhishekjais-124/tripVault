from django.db import models

from common.models import BaseModel
from common import utils as common_utils
from user import constants


class Group(BaseModel):
    uid = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=30, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.CharField(max_length=30)
    users_count = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.uid:
            uid = common_utils.create_random_uid()
            while Group.objects.filter(uid=uid).exists():
                uid = common_utils.create_random_uid()
            self.uid = uid
        return super().save(*args, **kwargs)


class UserGroupMapping(BaseModel):
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    group = models.ForeignKey("Group", on_delete=models.CASCADE)
    role = models.CharField(
        max_length=10, choices=constants.ROLE_CHOICES, default="Member"
    )
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False, help_text="Mark this group as primary for the user.")

    def __str__(self):
        return f"{self.user.username} - {self.group.name}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            # Unset other primaries for this user
            UserGroupMapping.objects.filter(user=self.user, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('user', 'group')
