# Generated by Django 5.0 on 2024-01-02 19:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_alter_group_name_alter_user_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserGroupRequests',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('role_requested', models.CharField(choices=[('Admin', 'Admin'), ('Member', 'Member')], default='Member', max_length=10)),
                ('status', models.IntegerField(choices=[(0, 'PENDING'), (1, 'ACCEPTED'), (2, 'DECLINED')], default=0)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.group')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to='user.user')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to='user.user')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
