from django.db import models
from django.contrib.auth.models import User as AuthUser

from common.models import BaseModel
from common import utils as common_utils
from user import constants


class User(BaseModel):
    auth_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE)
    uid = models.CharField(max_length=10, unique=True, db_index=True)
    username = models.CharField(max_length=30, unique=True, db_index=True)
    name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(max_length=254)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.uid:
            uid = common_utils.create_random_uid()
            while User.objects.filter(uid=uid).exists():
                uid = common_utils.create_random_uid()
            self.uid = uid
        return super().save(*args, **kwargs)


class Group(BaseModel):
    uid = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=30)
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
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    group = models.ForeignKey("Group", on_delete=models.CASCADE)
    role = models.CharField(
        max_length=10, choices=constants.ROLE_CHOICES, default="Member"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.group.name}"

