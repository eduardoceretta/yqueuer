# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-04-15 17:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0009_auto_20170415_1719'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='channel',
            name='users',
        ),
    ]
