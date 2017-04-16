import os
import sys
import pprint

from django.core.management.base import BaseCommand, CommandError

from django.conf import settings
from django.db.models import Q
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
    self.pp = pprint.PrettyPrinter(stream = self.stdout)


  def add_arguments(self, parser):
    parser.add_argument('channel_name', nargs='*', type=str)
    parser.add_argument('--user', nargs='*', type=str)

  def handle(self, *args, **options):
    self._dbStats()
    self._print("\n")
    self._print("Starting Populate Library")

    self._parseOptions(**options)
    self._trim()
    self._import()
    self._print("Done Populate Library")
    # self._repopulate()
    self._dbStats()


  def _parseOptions(self, **options):
    self._print("_parseOptions", 1)
    channel_names = options['channel_name']
    usernames = options['user']

    self._print(pprint.pformat(channel_names), 2)
    self._print(pprint.pformat(usernames), 2)
    self._print("!!Ignoring Options!", 2)

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
          videos = self._fetchNewVideos(u_c.channel, u_c.last_vid_y_vid_id, IMPORT_UPPER_BOUNDARY - u_c.num_vid)
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



  def _print(self, obj, indent_level = 0):
    self.stdout.write(" "*indent_level + obj)


  def _getWatchedVideos(self, user):
    video_qs = Video.objects.select_related('channel').filter(users = user, ruservideo__watched = True)
    return video_qs


  def _fetchNewVideos(self, c, last_vid_y_vid_id, n):
    videos = getVideosFromPlaylist(settings.SECRETS['YOUTUBE_API_KEY'], c.playlist_uploads_id, last_vid_y_vid_id)
    db_videos = []
    videos.sort(key=lambda x: x["published_at"])
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
        db_vid = video_qs[0]
        db_vid.ref_count+=1
        db_vid.save()
        db_videos.append(db_vid)
        self._print("Incrementing video: %s[rc:%d] (%s) %s" % (db_vid.title, db_vid.ref_count, db_vid.y_video_id, db_vid.published_at), 4)

    return db_videos


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
    self._print("Total: %d" % total, 2)



  # def _repopulate(self):
  #   s = User.objects.get(username = 'slart')
  #   self._print(pprint.pformat(s))
  #   # self._addChannel(s, 'UC2C_jShtL725hvbm1arSV9w', 'G3wLQz-LgrM')   # channel_name = 'greymatter'
  #   # self._addChannel(s, 'UC6nSFpj9HTCZ5t-N3Rm3-HA', 'VhVtK7UhKbI')   # channel_name = 'vsauce1'
  #   # self._addChannel(s, 'UC7_gcs09iThXybpVgjHZ_7g', 'mht-1c4wc0Q')   # channel_name = 'pbsspacetime'
  #   # self._addChannel(s, 'UCAuUUnT6oDeKwE6v1NGQxug', 'hLltkC-G5dY')   # channel_name = 'ted'
  #   # self._addChannel(s, 'UCC552Sd-3nyi_tk2BudLUzA', 'zTeaOTkjut0')   # channel_name = 'AsapSCIENCE'
  #   # self._addChannel(s, 'UCeiYXex_fwgYDonaTcSIk6w', 'oaOfeSJZ3lY')   # channel_name = 'minuteearth'
  #   # self._addChannel(s, 'UCrMePiHCWG4Vwqv3t7W9EFg', 'kpF2ruHcpDM')   # channel_name = 'scishowspace'
  #   # self._addChannel(s, 'UCsXVk37bltHxD1rDPwtNM8Q', 'czgOWmtGVGs')   # channel_name = 'inanutshell'
  #   # self._addChannel(s, 'UCUHW94eEFW7hkUMVaZz4eDg', 'lHaX9asEXIo')   # channel_name = 'minutephysics'
  #   # self._addChannel(s, 'UCUL-pmhmDcZDwsA4cX2HO5w', 'GYOe13IXO80')   # channel_name = 'phd'
  #   # self._addChannel(s, 'UCZYTClx2T1of7BRZ86-8fow', 'GP-YJbGxe20')   # channel_name = 'scishow'

  #   a = User.objects.get(username = 'alexandre.ceretta')
  #   self._print(pprint.pformat(a))
  #   # self._addChannel(a, 'UCB_zuUSmh_PVkqwkaDT-thA', 'D_bfwNwGx-o') #CEN
  #   # self._addChannel(a, 'UCEWHPFNilsT0IfQfutVzsag', '1Eta61j0uTs') #portadosfundos
  #   # self._addChannel(a, 'UCGozdt7Wbd15k7dWhvlmLUw', 'poQ_ILxvXbY') #cleanmyspace
  #   # self._addChannel(a, 'UCI4I6ldZ0jWe7vXpUVeVcpg', 'kO8fZcO-458') #householdhackertv
  #   # self._addChannel(a, 'UCOClvgLYa7g75eIaTdwj_vg', '1l97wjymVJU') #Consumer
  #   # self._addChannel(a, 'UCWXCrItCF6ZgXrdozUS-Idw', 'oJ92tfQDnS4') #explosmentertainment


  # def _addChannel(self, user, c_y_id, last_vid_y_vid_id):
  #   self._print("Adding for user %s channel %s (%s)" % (user.username, c_y_id, last_vid_y_vid_id), 2)
  #   channel_qs = Channel.objects.filter(name = c_y_id)

  #   if len(channel_qs) > 0 :
  #     channel = channel_qs[0]
  #   else :
  #     result = searchChannelById(settings.SECRETS['YOUTUBE_API_KEY'], c_y_id)
  #     if result :
  #       channel = Channel.objects.create(
  #         y_channel_id = result['id'],
  #         playlist_uploads_id = result['playlist_uploads_id'],
  #         title = result['title'],
  #         name = result['name'],
  #         thumbnails = result['thumbnails']
  #       )
  #     else :
  #       self._print("No channel found", 3)

  #   if channel :
  #     uc = user.ruserchannel_set.create(channel = channel)
  #     uc.last_vid_y_vid_id = last_vid_y_vid_id
  #     uc.save()
  #     self._print("Added", 3)