from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User as AuthUser
from user import models

@receiver(post_save, sender=AuthUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        models.User.objects.create(auth_user=instance, username=instance.username, email=instance.email)
    else:
        instance.user.save()
