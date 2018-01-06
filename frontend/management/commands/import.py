import os
import sys
import pprint
import requests
import traceback
from cStringIO import StringIO

from django.core.management.base import BaseCommand, CommandError

from django.conf import settings
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib.auth.models import User

from frontend.forms import UserForm
from frontend.models import Channel, Video, RUserVideo, RUserChannel
from frontend.yqueuer_api import *

IMPORT_LOWER_BOUNDARY = 30
IMPORT_UPPER_BOUNDARY = 50

class Command(BaseCommand):
  help = 'Import new videos into library for all users'

  def __init__(self, *args, **kwargs):
    super(self.__class__, self).__init__(*args, **kwargs)
    self.stdout_mail = StringIO()

  def handle(self, *args, **options):
    try:
      self._dbStats()
      self._print("\n")
      self._print("Starting Populate Library")
      self._trim()
      self._import()
      self._print("Done Populate Library")
      self._print("\n")
      self._print("Starting Running Tests")
      self._runTests()
      self._print("Done Running Tests")
      self._dbStats()
    except: # catch *all* exceptions
      traceback.print_exc(30,self.stdout_mail)
      traceback.print_exc(30,self.stdout)
    self._send_mail_logs()

  def _trim(self):
    self._print("\n")
    self._print("Started Trimming", 1)

    for u in User.objects.all():
      self._print("Processing user: %s" % u.username, 2)
      videos = self._getWatchedVideos(u)
      self._print("Got %d watched videos" % len(videos), 3)
      for v in videos:
        c = v.channel
        userchannel = u.ruserchannel_set.get(channel = c)
        uservideo = u.ruservideo_set.get(video = v)

        self._print("Processing Video %s[nv%d]:%s[rc:%d] (%s) %s " % (c.title, userchannel.num_vid, v.title, v.ref_count, v.y_video_id, v.published_at), 3)
        # Delete UserVideo relation entry
        uservideo.delete()
        self._print("Deleted From RUserVideo", 4)

        # Update UserChannel counter
        userchannel.num_vid-=1
        userchannel.save()
        self._print("Updated UserChannel num_vid to %d" % userchannel.num_vid, 4)

        # Update Video Refcount and delete it if needed
        v.ref_count-=1
        if v.ref_count <= 0:
          v.delete()
          self._print("Deleted Video", 4)
        else:
          v.save()
          self._print("Updated Video ref_count to %d" % v.ref_count, 4)


  def _import(self):
    self._print("\n")
    self._print("Started Importing", 1)

    for u in User.objects.all():
      self._print("Processing user: %s" % u.username, 2)
      for u_c in u.ruserchannel_set.all():
        self._print("Processing Channel %s[nv%d/%d] last(%s)" % (u_c.channel.title, u_c.num_vid, IMPORT_LOWER_BOUNDARY, u_c.last_vid_y_vid_id), 3)
        if u_c.num_vid <= IMPORT_LOWER_BOUNDARY:
          self._print("Need to import %d new videos" % (IMPORT_UPPER_BOUNDARY - u_c.num_vid), 4)
          videos = self._fetchNewVideos(u, u_c.channel, u_c.last_vid_y_vid_id, u_c.last_vid_pub_date, IMPORT_UPPER_BOUNDARY - u_c.num_vid)
          self._print("Got %d Videos" % (len(videos)), 4)
          if len(videos) > 0:
            last_vid = videos[-1]
            u_c.num_vid += len(videos)
            u_c.last_vid_y_vid_id = last_vid.y_video_id
            u_c.last_vid_pub_date = last_vid.published_at
            u_c.save()
            self._print("Updated UserChannel. nv=%d last=%s" % (u_c.num_vid, u_c.last_vid_y_vid_id), 4)

            for v in videos:
              uservideo = u.ruservideo_set.create(video = v)
            self._print("Appended %d videos to RuserVideo" % len(videos),4)

  def _send_mail_logs(self):
    logs = self.stdout_mail.getvalue()

    api_key = settings.SECRETS['MAILGUN_API_KEY']
    domain = settings.SECRETS['MAILGUN_DOMAIN']
    log_mail = settings.SECRETS['PROJECT_EMAIL']
    response = requests.post(
      "https://api.mailgun.net/v3/" + domain + "/messages",
      auth=("api", api_key),
      data={"from": "Importer<importer@yqueuer>",
            "to": [log_mail],
            "subject": "[Importer] Importer Logs",
            "text": logs}
    )
    self._print("Sending log email, response %s." % (response), 0)

  def _getWatchedVideos(self, user):
    video_qs = Video.objects.select_related('channel').filter(users = user, ruservideo__watched = True)
    return video_qs


  def _fetchNewVideos(self, u, c, last_vid_y_vid_id, last_vid_pub_date,  n):
    videos = getVideosFromPlaylist(settings.SECRETS['YOUTUBE_API_KEY'], c.playlist_uploads_id, last_vid_y_vid_id)
    db_videos = []

    for v in videos[0:n]:
      video_qs = Video.objects.filter(y_video_id = v["id"])
      if len(video_qs) == 0 :
        self._print("Adding video: %s[rc:%d] (%s) %s" % (v["title"], 1, v["id"], v["published_at"]), 4)
        db_vid = Video.objects.create(
          y_video_id = v["id"], channel = c, published_at = v["published_at"],
          title = v["title"], thumbnails = v["thumbnails"],
          description = v["description"], position = v["position"], ref_count = 1
        )
        db_videos.append(db_vid)
      else :
        # Videos should be unique per user
        uservideo_qs = u.ruservideo_set.filter(video = video_qs[0])
        if len(uservideo_qs) == 0 :
          db_vid = video_qs[0]
          db_vid.ref_count+=1
          db_vid.save()
          db_videos.append(db_vid)
          self._print("Incrementing video: %s[rc:%d] (%s) %s" % (db_vid.title, db_vid.ref_count, db_vid.y_video_id, db_vid.published_at), 4)
        else :
          self.warn("Trying to insert an already existing video(%s) to user %s" % (video_qs[0].y_video_id, u.username))

    return db_videos

  def _runTests(self):
    self._print("Check if RUserChannel.num_vid is != than the actual relational", 1)
    channels = RUserChannel.objects.all()
    for x in channels:
      c_vids = RUserVideo.objects.filter(video__channel = x.channel, user = x.user).count()
      if x.num_vid - c_vids != 0 :
        warn("User %s - Channel %s has %d num_vids but RUserVideo.count has %d" % (x.user.username, x.channel.title, x.num_vid, c_vids))

    self._print("Check if any video has no relation in uservideo",1)
    all_vids = Video.objects.annotate(num_users=Count('users'))
    for v in all_vids:
      if (v.ref_count - v.num_users != 0):
        warn("Channel %s Video %s(%s) has ref_count %d but RUserVideo.count has %d" % (v.channel.name,v.title, v.y_video_id,v.ref_count, v.num_users))


  def _dbStats(self):
    self._print("\n")
    self._print("DB Stats", 1)

    num_users = User.objects.all().count()
    num_unique_videos = Video.objects.all().count()
    num_unique_channel = Channel.objects.all().count()
    num_unique_userchannel = RUserChannel.objects.all().count()
    num_unique_uservideo = RUserVideo.objects.all().count()
    total = num_unique_videos + num_unique_videos + num_unique_channel + num_unique_userchannel + num_unique_uservideo
    self._print("Users: %d" % num_users, 2)
    self._print("Videos: %d" % num_unique_videos, 2)
    self._print("Channel: %d" % num_unique_channel, 2)
    self._print("UserChannel: %d" % num_unique_userchannel, 2)
    self._print("UserVideo: %d" % num_unique_uservideo, 2)
    self._print("Total: %d/~10000" % total, 2)

  def warn(self, msg):
    self._print("[WARN]" + msg, 0)

  def _print(self, obj, indent_level = 0):
    u_obj = (u' '+obj).encode('ascii', 'ignore').decode('ascii')
    self.stdout_mail.write(" "*indent_level + u_obj + "\n")
    self.stdout.write(" "*indent_level + u_obj)
