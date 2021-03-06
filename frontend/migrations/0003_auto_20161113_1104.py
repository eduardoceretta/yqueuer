# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-13 11:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0002_auto_20161113_1028'),
    ]

    operations = [
        migrations.CreateModel(
            name='RUserVideo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('watched_date', models.DateTimeField(blank=True, null=True, verbose_name='date watched')),
                ('watched', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='frontend.User')),
            ],
        ),
        migrations.RemoveField(
            model_name='video',
            name='watched',
        ),
        migrations.RemoveField(
            model_name='video',
            name='watched_date',
        ),
        migrations.AddField(
            model_name='ruservideo',
            name='video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='frontend.Video'),
        ),
    ]
