from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class Channel(models.Model):
  y_channel_id = models.CharField(max_length = 200, unique = True)
  imported_date = models.DateTimeField(blank = True, null = True)

  users = models.ManyToManyField(User)

  def __str__(self):
    return self.y_channel_id

class Video(models.Model):
  y_video_id = models.CharField(max_length = 200, unique = True)
  channel = models.ForeignKey(Channel)
  pub_date = models.DateTimeField('date published', null = True, blank = True)

  user_video = models.ManyToManyField(User, through='RUserVideo')

  def __str__(self):
    return self.y_video_id

# class RUserChannel(models.Model):
#   user = models.ForeignKey(User)
#   channel = models.ForeignKey(Channel)

class RUserVideo(models.Model):
  user = models.ForeignKey(User)
  video = models.ForeignKey(Video)
  watched_date = models.DateTimeField('date watched', null = True, blank = True)
  watched = models.BooleanField(default = False)

