import sys
import random
import json
import pytz
import datetime
import os

from urlparse import urlparse, parse_qs

from django.conf import settings
from django.http import Http404
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Q

from frontend.forms import UserForm
from frontend.models import Channel, Video, RUserVideo, RUserChannel, UserPreferences

from frontend.yqueuer_api import searchChannelByUsername, searchChannelById, getVideosFromPlaylist, getVideoInfo

def _parseYoutubeUrl(url):
  data = {}
  if not (url.startswith('http') or url.startswith('//')) :
    url = 'https://' + url

  urlp = urlparse(url)
  if urlp.netloc == 'www.youtube.com' or urlp.netloc == 'youtube.com':
    data['urlparse'] = urlp

    if urlp.path == '/watch':
      urlqs = parse_qs(urlp.query)
      video_id = urlqs['v'][0]
      video_info = getVideoInfo(settings.SECRETS['YOUTUBE_API_KEY'], video_id)
      if video_info and video_info['channel_id']:
        data['y_video_id'] = video_id
        data['y_channel_id'] = video_info['channel_id']
    else :
      split_path = os.path.split(urlp.path)
      if split_path[0] == '/user':
        data['channel_username'] = split_path[1]
      elif split_path[0] == '/channel':
        data['y_channel_id'] = split_path[1]

  return data


def _markWatched(user, video):
  uservideo, created = user.ruservideo_set.get_or_create(video = video)
  uservideo.watched = True
  uservideo.watched_date = timezone.now()
  uservideo.save()

def _getChannels(user):
  # Select videos, from user's channel list, with no entry on RUserVideo for that user or it has but watched is false
  u_channels = user.channel_set.all()

  channels = []
  for channel in u_channels:
    channels.append({
      'id': channel.y_channel_id,
      'title': channel.title,
      'name': channel.name,
      'username': channel.username,
      'thumbnails' : channel.thumbnails,
    })

  return channels

def _getUserPreferences(user):
  preferences = UserPreferences.objects.get(user = user)

  return {
    'video_playback_rate': float(preferences.video_playback_rate),
  }

##############################################
# Pages
##############################################
def index(request):
  rand = random.randint(10,80)
  if rand == 42:
    raise Http404("The question you are looking for is not here")

  context = {
    'rand': rand
  }
  return render(request, 'frontend/index.html', context)


##################################
def register(request):
  registered = False

  if request.method == 'POST':
    user_form = UserForm(data=request.POST)

    if user_form.is_valid():
      user = user_form.save()
      user.set_password(user.password)
      user.save()

      registered = True
    else:
      print user_form.errors
  else:
    user_form = UserForm()

  return render(request,
      'frontend/register.html',
      {'user_form': user_form, 'registered': registered})


##################################
def user_login(request):
  if request.method == 'POST':
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username = username, password = password)

    if user:
      if user.is_active:
        login(request, user)
        return HttpResponseRedirect('/player')
      else:
        return HttpResponse("Your Rango account is disabled.")
    else:
      print "Invalid login details: {0}".format(username)
      return HttpResponse("Invalid login details supplied.")
  else:
    return render(request, 'frontend/login.html', {})


##################################
@login_required
def user_logout(request):
  logout(request)
  return HttpResponseRedirect('/')


##################################
@login_required
def player(request):
  channel_list = None
  if request.GET.has_key('channel_list') :
    channel_list = request.GET['channel_list']
  elif request.GET.has_key('channel') :
    channel_list = ",".join(request.GET.getlist('channel'))

  all_channels = _getChannels(request.user)

  preferences = _getUserPreferences(request.user)

  context = { 'channel_list' : channel_list, 'all_channels' : all_channels, 'preferences': preferences}
  return render(request, 'frontend/player.html', context)

##################################
@login_required
def manage(request):
  context = {  }
  return render(request, 'frontend/manage.html', context)

##############################################
# API
##############################################
@login_required
def getVideos(request):
  user = request.user

  channel_list = []
  if request.GET.has_key('channel_list') :
    channel_list = request.GET['channel_list'].split(',')

  # Select videos, from user's channel list, with no entry on RUserVideo for that user or it has but watched is false
  u_channels = None
  if not channel_list:
    u_channels = user.channel_set.all()
  else :
    u_channels = user.channel_set.filter(name__in = channel_list)

  video_qs = Video.objects.select_related('channel').filter(
    channel__in = u_channels, users = user, ruservideo__watched = False
  ).order_by('published_at')

  videos = []
  for video in video_qs:
    videos.append({
      'id': video.y_video_id,
      'title': video.title,
      'channel_title': video.channel.title,
      'published_at' : str(video.published_at),
      'thumbnails' : video.thumbnails,
      'description' : video.description,
    })

  response_data = {'success': True, 'data' : {'channels' : map(lambda x: x.name, u_channels), 'videos' : videos }}
  return HttpResponse(json.dumps(response_data), content_type = "application/json")

##################################
@login_required
def getChannels(request):
  channels = _getChannels(request.user)

  response_data = {'success': True, 'data' : {'channels' : channels} }
  return HttpResponse(json.dumps(response_data), content_type = "application/json")

##################################
@login_required
def markWatched(request):
  y_video_id = request.POST['y_video_id']
  user = request.user

  video = Video.objects.get(y_video_id = y_video_id)
  _markWatched(user, video)

  response_data = {'success': True}
  return HttpResponse(json.dumps(response_data), content_type = "application/json")


##################################
# @login_required
# def updateChannelLibrary(request):
#   response_data = {'error' : "can't find channel"}
#   channel = None

#   channel_name = request.POST['channel_name']
#   channel_qs = Channel.objects.filter(name = channel_name)

#   if len(channel_qs) > 0 :
#     channel = channel_qs[0]
#   else :
#     return HttpResponse(json.dumps(response_data), content_type = "application/json")

#   videos = getVideosFromPlaylist(settings.SECRETS['YOUTUBE_API_KEY'], channel.playlist_uploads_id)

#   added = 0
#   for v in videos:
#     video_qs = Video.objects.filter(y_video_id = v["id"])
#     if len(video_qs) == 0 :
#       Video.objects.update_or_create(
#         y_video_id = v["id"], channel = channel, published_at = v["published_at"],
#         title = v["title"], thumbnails = v["thumbnails"],
#         description = v["description"], position = v["position"]
#       )
#       added+=1

#   response_data = {'success': True, 'data' : { 'channel' : channel_name, 'updated' : added }}
#   return HttpResponse(json.dumps(response_data), content_type = "application/json")


##################################
@login_required
def addChannel(request):
  response_data = {'error' : "can't find channel"}
  channel = None

  user = request.user
  url               = request.POST.get('youtube_url', None)
  y_channel_id      = request.POST.get('y_channel_id', None)
  channel_username  = request.POST.get('channel_username', None)
  last_vid_y_vid_id = request.POST.get('last_y_video_id', None)

  if url:
    parsed = _parseYoutubeUrl(url)
    y_channel_id      = parsed.get('y_channel_id', None)
    channel_username  = parsed.get('channel_username', None)
    last_vid_y_vid_id = parsed.get('y_video_id', None)

  if not y_channel_id and not channel_username:
    response_data = {'error' : "Invalid parameters"}
    return HttpResponse(json.dumps(response_data), content_type = "application/json")

  channel_qs = None
  if y_channel_id:
    channel_qs = Channel.objects.filter(y_channel_id = y_channel_id)
  elif channel_username:
    channel_qs = Channel.objects.filter(username__iexact = channel_username)

  if len(channel_qs) > 0 :
    channel = channel_qs[0]
  else :
    result = None
    if y_channel_id:
      result = searchChannelById(settings.SECRETS['YOUTUBE_API_KEY'], y_channel_id)
    elif channel_username:
      result = searchChannelByUsername(settings.SECRETS['YOUTUBE_API_KEY'], channel_username)

    if result :
      channel = Channel.objects.create(
        y_channel_id = result['id'],
        playlist_uploads_id = result['playlist_uploads_id'],
        title = result['title'],
        name = result['name'],
        username = result['username'],
        thumbnails = result['thumbnails']
      )
    else :
      return HttpResponse(json.dumps(response_data), content_type = "application/json")

  if channel :
    uc, created = user.ruserchannel_set.get_or_create(channel = channel)
    if not created:
      response_data = {'error' : "Channel already added"}
    else:
      response_data = {'success': True, 'data' : {'channel_title': channel.title, 'last_vid_id': last_vid_y_vid_id }}
      if last_vid_y_vid_id:
        uc.last_vid_y_vid_id = last_vid_y_vid_id
        uc.save()

  return HttpResponse(json.dumps(response_data), content_type = "application/json")


##################################
@login_required
def removeChannel(request):
  response_data = {'error' : "can't find channel"}

  user = request.user

  y_channel_id  = request.POST.get('y_channel_id', None)
  if not y_channel_id:
    response_data = {'error' : "Invalid parameters"}
    return HttpResponse(json.dumps(response_data), content_type = "application/json")

  channel_qs = Channel.objects.filter(y_channel_id = y_channel_id)
  if len(channel_qs) <= 0 :
    return HttpResponse(json.dumps(response_data), content_type = "application/json")

  channel = channel_qs[0]
  userchannel = user.ruserchannel_set.get(channel = channel)

  video_qs = Video.objects.filter(channel = channel, users = user)
  for v in video_qs:
    uservideo = user.ruservideo_set.get(video = v)
    uservideo.delete()

    v.ref_count-=1
    if v.ref_count <= 0:
      v.delete()
    else:
      v.save()

  userchannel.delete()
  response_data = {'success': True, 'data' : {'channel_title': channel.title}}

  if channel.users.count() <= 0:
    channel.delete()

  return HttpResponse(json.dumps(response_data), content_type = "application/json")


@login_required
def getUserPreferences(request):
  user = request.user

  preferences_data = _getUserPreferences(user)

  if not preferences_data :
    response_data = {'error' : "Non Existing User Preferences"}
    return HttpResponse(json.dumps(response_data), content_type = "application/json")

  response_data = {'success': True, 'data' : preferences_data}
  return HttpResponse(json.dumps(response_data), content_type = "application/json")


@login_required
def setUserVideoPlaybackRate(request):
  user = request.user

  video_playback_rate = request.POST['video_playback_rate']
  if not video_playback_rate:
    response_data = {'error' : "Invalid arguments"}
    return HttpResponse(json.dumps(response_data), content_type = "application/json")

  user.userpreferences.video_playback_rate = video_playback_rate
  user.save()

  data = {
    'video_playback_rate' : user.userpreferences.video_playback_rate
  }
  response_data = {'success': True, 'data' : data}
  return HttpResponse(json.dumps(response_data), content_type = "application/json")


def postJSError(request):
  print >>sys.stderr, 'JSERROR: ', request.POST['msg'], request.POST['url'], request.POST['lineNo'],request.POST['columnNo'],request.POST['error']

  response_data = {'success': True}
  return HttpResponse(json.dumps(response_data), content_type = "application/json")
