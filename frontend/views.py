import sys
import random
import json
import pytz
import datetime

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
from frontend.models import Channel, Video, RUserVideo

from frontend.yqueuer_api import searchChannel, getVideosFromPlaylist




def _markWatched(user, video):
  uservideo, created = user.ruservideo_set.get_or_create(video = video)
  uservideo.watched = True
  uservideo.watched_date = timezone.now()
  uservideo.save()

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
      print "Invalid login details: {0}, {1}".format(username, password)
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
  context = {  }
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

  # Select videos, from user's channel list, with no entry on RUserVideo for that user or it has but watched is false
  u_channels = user.channel_set.all()
  video_qs = Video.objects.filter(
    Q( channel__in = u_channels )
    & ( ~Q( users = user) | Q( users = user, ruservideo__watched = False))
  ).order_by('published_at')

  videos = []
  for video in video_qs:
    videos.append({
      'id': video.y_video_id,
      'title': video.title,
      'channel_name': video.channel.title,
      'published_at' : str(video.published_at),
      'thumbnails' : video.thumbnails,
      'description' : video.description,
    })

  response_data = { 'videos' : videos }
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
@login_required
def updateChannelLibrary(request):
  response_data = {'error' : "can't find channel"}
  channel = None

  channel_name = request.POST['channel_name']
  channel_qs = Channel.objects.filter(name = channel_name)

  if len(channel_qs) > 0 :
    channel = channel_qs[0]
  else :
    return HttpResponse(json.dumps(response_data), content_type = "application/json")

  videos = getVideosFromPlaylist(settings.SECRETS['YOUTUBE_API_KEY'], channel.playlist_uploads_id)

  for v in videos:
    Video.objects.update_or_create(
      y_video_id = v["id"], channel = channel, published_at = v["published_at"],
      title = v["title"], thumbnails = v["thumbnails"],
      description = v["description"], position = v["position"]
    )

  response_data = {'success': True, 'data' : { 'channel' : channel_name, 'updated' : len(videos) }}
  return HttpResponse(json.dumps(response_data), content_type = "application/json")


##################################
@login_required
def addChannel(request):
  # print >>sys.stderr, request.user, request.POST.has_key('channel_name'), request.GET.has_key('channel_name')

  response_data = {'error' : "can't find channel"}
  channel = None

  user = request.user
  channel_name = request.POST['channel_name']
  channel_qs = Channel.objects.filter(name = channel_name)

  if len(channel_qs) > 0 :
    channel = channel_qs[0]
  else :
    result = searchChannel(settings.SECRETS['YOUTUBE_API_KEY'], channel_name)
    if result :
      channel = Channel.objects.create(
        y_channel_id = result['id'],
        playlist_uploads_id = result['playlist_uploads_id'],
        title = result['title'],
        name = result['name'],
        thumbnails = result['thumbnails']
      )
    else :
      return HttpResponse(json.dumps(response_data), content_type = "application/json")

  if channel :
    user.channel_set.add(channel)
    user.save()
    response_data = {'success': True}

  return HttpResponse(json.dumps(response_data), content_type = "application/json")

##################################
@login_required
def bulkMarkWatched(request):
  # print >>sys.stderr, request.user, request.POST.has_key('channel_name'), request.GET.has_key('channel_name'), request.POST.has_key('until_y_video_id'), request.GET.has_key('until_y_video_id')

  response_data = {'error' : "error"}
  channel = None
  until_video = None

  user = request.user
  channel_name = request.POST['channel_name']
  until_y_video_id = request.POST['until_y_video_id']

  if not channel_name or not until_y_video_id:
    response_data = {'error' : "Invalid parameters"}
    return HttpResponse(json.dumps(response_data), content_type = "application/json")

  channel_qs = Channel.objects.filter(name = channel_name)

  if len(channel_qs) > 0 :
    channel = channel_qs[0]
  else :
    response_data = {'error' : "can't find channel"}
    return HttpResponse(json.dumps(response_data), content_type = "application/json")

  until_video_qs = Video.objects.filter(y_video_id = until_y_video_id)
  if len(until_video_qs) > 0 :
    until_video = until_video_qs[0]
  else :
    response_data = {'error' : "can't find video"}
    return HttpResponse(json.dumps(response_data), content_type = "application/json")

  videos = Video.objects.filter(channel = channel, published_at__lte = until_video.published_at)
  for v in videos:
    _markWatched(user, v)

  response_data = {'success' : True, 'data' : { 'channel' : channel_name, 'marked' : len(videos) }}

  return HttpResponse(json.dumps(response_data), content_type = "application/json")
