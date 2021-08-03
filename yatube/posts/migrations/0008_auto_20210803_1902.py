# Generated by Django 2.2.6 on 2021-08-03 19:02

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_auto_20210803_1847'),
    ]

    operations = [
        migrations.AlterField(
            model_name='follow',
            name='user',
            field=models.ForeignKey(blank=True, default=django.contrib.auth.models.User, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='follower', to=settings.AUTH_USER_MODEL),
        ),
    ]
