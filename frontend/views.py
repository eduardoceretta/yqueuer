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

from frontend.yqueuer_api import searchChannel


##################################
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
    videos.append(video.y_video_id)

  response_data = { 'videos' : videos }
  return HttpResponse(json.dumps(response_data), content_type = "application/json")


##################################
@login_required
def markWatched(request):
  y_video_id = request.POST['y_video_id']
  user = request.user

  video = Video.objects.get(y_video_id = y_video_id)
  uservideo, created = user.ruservideo_set.get_or_create(video = video)
  uservideo.watched = True
  uservideo.watched_date = timezone.now()
  uservideo.save()

  response_data = {'success': True}
  return HttpResponse(json.dumps(response_data), content_type = "application/json")


##################################
# @login_required
# def updateLibrary(request):
#   user = request.user

#   # Move to Constants
#   date_format = '%Y-%m-%d %H:%M:%S'
#   for c in user.channel_set.all():
#     # CALL retrieve videos from c
#     #HARDCODED
#     video_list = (('Chbm84sCBAw', '2016-01-01 01:00:00'), ('w1feICb-HRE', '2016-01-01 01:00:00'), ('UfYpxF32EZo', '2016-01-01 01:00:00')) #HARDCODED
#     #Insert Videos into VideoTable
#     for v in video_list:
#       published_at = pytz.utc.localize(datetime.datetime.strptime(v[1], date_format))
#       video = Video.objects.update_or_create(y_video_id = v[0], channel = c, published_at = published_at)

#   response_data = {'success': True}
#   return HttpResponse(json.dumps(response_data), content_type = "application/json")


##################################
@login_required
def addChannel(request):
  # print >>sys.stderr, request.user, request.POST.has_key('channel_name'), request.GET.has_key('channel_name')

  response_data = {'error' : "can't find channel"}
  channel = None

  user = request.user
  channel_name = request.GET['channel_name']
  channel_qs = Channel.objects.filter(name = channel_name)

  if len(channel_qs) > 0 :
    channel = channel_qs[0]
  else :
    result = searchChannel(settings.SECRETS['YOUTUBE_API_KEY'], request.GET['channel_name'])
    channel = Channel.objects.create(
      y_channel_id = result['id'],
      playlist_uploads_id = result['playlist_uploads_id'],
      title = result['title'],
      name = result['name'],
      thumbnails = result['thumbnails']
    )

  if channel :
    user.channel_set.add(channel)
    user.save()
    response_data = {'success': True}

  return HttpResponse(json.dumps(response_data), content_type = "application/json")

##################################
@login_required
def bulkMarkWatched(request):
  print >>sys.stderr, request.user
    ,request.POST.has_key('channel_name'), request.GET.has_key('channel_name')
    ,request.POST.has_key('until_y_video_id'), request.GET.has_key('until_y_video_id')

  # response_data = {'error' : "error"}
  # channel = None

  # user = request.user
  # channel_name = request.GET['channel_name']
  # until_y_video_id = request.GET('until_y_video_id')

  # channel_qs = Channel.objects.filter(name = channel_name)

  # if len(channel_qs) > 0 :
  #   channel = channel_qs[0]
  # else :
  #   response_data = {'error' : "can't find channel"}
  #   return HttpResponse(json.dumps(response_data), content_type = "application/json")

  # until_video = Video.objects.get(y_video_id = until_y_video_id)
  # user.ruservideo_set.filter(published_at__lte = until_video.published_at)

  # return HttpResponse(json.dumps(response_data), content_type = "application/json")