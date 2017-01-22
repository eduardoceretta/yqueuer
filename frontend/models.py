from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class Channel(models.Model):
  y_channel_id        = models.CharField(max_length = 200, unique = True)
  playlist_uploads_id = models.CharField(max_length = 200)
  title               = models.CharField(max_length = 1024, blank = True, null = True)
  name                = models.CharField(max_length = 1024, blank = True, null = True)
  thumbnails          = models.CharField(max_length = 2048, blank = True, null = True)
  imported_date       = models.DateTimeField(blank = True, null = True)

  users = models.ManyToManyField(User)

  def __str__(self):
    return "id: %s | Title: %s | ImportedDate: %s" % (self.y_channel_id, self.title, self.imported_date)

class Video(models.Model):
  y_video_id   = models.CharField(max_length = 200, unique = True)
  published_at = models.DateTimeField(null = True, blank = True)
  title        = models.CharField(max_length = 1024, blank = True, null = True)
  thumbnails   = models.CharField(max_length = 2048, blank = True, null = True)
  description  = models.TextField(blank = True, null = True)
  position     = models.PositiveIntegerField(blank = True, null = True)

  channel = models.ForeignKey(Channel)
  users   = models.ManyToManyField(User, through = 'RUserVideo')

  def __str__(self):
    return "Channel: %s | id: %s | Title: %s | PublishedAt: %s" % (self.channel.title, self.y_video_id, self.title, self.published_at)

class RUserVideo(models.Model):
  user         = models.ForeignKey(User)
  video        = models.ForeignKey(Video)
  watched_date = models.DateTimeField(null = True, blank = True)
  watched      = models.BooleanField(default = False)

  def __str__(self):
    return "User: %s | Video: %s | Watched: %s" % (self.user.username, self.video.title, self.watched)

