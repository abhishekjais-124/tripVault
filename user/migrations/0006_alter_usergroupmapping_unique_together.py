# Generated by Django 5.0 on 2024-01-04 18:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_usergrouprequests'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='usergroupmapping',
            unique_together={('user', 'group')},
        ),
    ]