from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Video(models.Model):
    video_id = models.CharField(max_length=200)
    channel_id = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', null = True, blank = True)
    watched_date = models.DateTimeField('date watched', null = True, blank = True)
    watched = models.BooleanField(default=False)


class Channel(models.Model):
  channel_id = models.CharField(max_length=200)
  imported_date = models.DateTimeField(blank = True, null=True)