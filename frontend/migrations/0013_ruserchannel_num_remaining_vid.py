# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2021-01-18 22:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0012_userpreferences'),
    ]

    operations = [
        migrations.AddField(
            model_name='ruserchannel',
            name='num_remaining_vid',
            field=models.IntegerField(blank=True, default=-1, null=True),
        ),
    ]
