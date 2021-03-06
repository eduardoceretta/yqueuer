# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-15 20:02
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('frontend', '0004_auto_20161113_1353'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ruserchannel',
            name='channel',
        ),
        migrations.RemoveField(
            model_name='ruserchannel',
            name='user',
        ),
        migrations.AddField(
            model_name='channel',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='video',
            name='user_video',
            field=models.ManyToManyField(through='frontend.RUserVideo', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='RUserChannel',
        ),
    ]
