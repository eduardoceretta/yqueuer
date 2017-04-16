from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class Channel(models.Model):
  y_channel_id        = models.CharField(max_length = 200, unique = True)
  playlist_uploads_id = models.CharField(max_length = 200)
  username            = models.CharField(max_length = 1024, blank = True, null = True)
  title               = models.CharField(max_length = 1024, blank = True, null = True)
  name                = models.CharField(max_length = 1024, blank = True, null = True)
  thumbnails          = models.CharField(max_length = 2048, blank = True, null = True)

  users = models.ManyToManyField(User, through = 'RUserChannel')

  def __str__(self):
    return "id: %s | Title: %s " % (self.y_channel_id, self.title)

class Video(models.Model):
  y_video_id   = models.CharField(max_length = 200, unique = True)
  published_at = models.DateTimeField(null = True, blank = True)
  title        = models.CharField(max_length = 1024, blank = True, null = True)
  thumbnails   = models.CharField(max_length = 2048, blank = True, null = True)
  description  = models.TextField(blank = True, null = True)
  position     = models.PositiveIntegerField(blank = True, null = True)

  ref_count    = models.PositiveIntegerField(blank = True, null = True, default = 0)

  channel = models.ForeignKey(Channel)
  users   = models.ManyToManyField(User, through = 'RUserVideo')

  def __str__(self):
    return "Channel: %s | id: %s | Title: %s | PublishedAt: %s" % (self.channel.title, self.y_video_id, self.title, self.published_at)

class RUserChannel(models.Model):
  user              = models.ForeignKey(User)
  channel           = models.ForeignKey(Channel)
  num_vid           = models.PositiveIntegerField(blank = True, null = True, default = 0)
  last_vid_pub_date = models.DateTimeField(null = True, blank = True)
  last_vid_y_vid_id = models.CharField(max_length = 200, blank = True, null = True)
  avg_freq_per_day  = models.DecimalField(max_digits = 5, decimal_places = 2, default = 0, blank = True, null = True)

  def __str__(self):
    return "User: %s | Channel: %s | NumVid: %d" % (self.user.username, self.channel.title, self.num_vid)


class RUserVideo(models.Model):
  user         = models.ForeignKey(User)
  video        = models.ForeignKey(Video)
  watched_date = models.DateTimeField(null = True, blank = True)
  watched      = models.BooleanField(default = False)

  def __str__(self):
    return "User: %s | Video: %s | Watched: %s" % (self.user.username, self.video.title, self.watched)

