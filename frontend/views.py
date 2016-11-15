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


from .forms import UserForm
from .models import Channel, Video, RUserVideo

from frontend.yqueuer_api import searchChannel

def index(request):
  rand = random.randint(10,80)
  if rand == 42:
    raise Http404("The question you are looking for is not here")

  context = {
    'rand': rand
  }
  return render(request, 'frontend/index.html', context)

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

@login_required
def user_logout(request):
  logout(request)

  return HttpResponseRedirect('/')


@login_required
def player(request):
  context = {  }
  return render(request, 'frontend/player.html', context)

@login_required
def getVideos(request):
  print >>sys.stderr, request.user
  response_data = { 'videos' : [
    'Chbm84sCBAw',
    'w1feICb-HRE',
    'UfYpxF32EZo']
  }
  return HttpResponse(json.dumps(response_data), content_type = "application/json")

@login_required
def markWatched(request):
  y_video_id = request.POST['y_video_id']
  user = request.user

  uservideo = user.ruservideo_set.get(video__y_video_id = y_video_id)
  uservideo.watched = True
  uservideo.watched_date = timezone.now()
  uservideo.save()

  response_data = {success: True}
  return HttpResponse(json.dumps(response_data), content_type = "application/json")


@login_required
def updateLibrary(request):
  user = request.user

  # Move to Constants
  date_format = '%Y-%m-%d %H:%M:%S'
  for c in user.channel_set.all():
    # CALL retrieve videos from c
    #HARDCODED
    video_list = (('Chbm84sCBAw', '2016-01-01 01:00:00'), ('w1feICb-HRE', '2016-01-01 01:00:00'), ('UfYpxF32EZo', '2016-01-01 01:00:00')) #HARDCODED
    #Insert Videos into VideoTable
    for v in video_list:
      pub_date = pytz.utc.localize(datetime.datetime.strptime(v[1], date_format))
      video = Video.objects.update_or_create(y_video_id = v[0], channel = c, pub_date = pub_date)

  response_data = {success: True}
  return HttpResponse(json.dumps(response_data), content_type = "application/json")

@login_required
def addChannel(request):
  # print >>sys.stderr, request.user, request.POST.has_key('channel_name'), request.GET.has_key('channel_name')

  user = request.user
  channel_name = request.POST['channel_name']

  # result = searchChannel(settings.SECRETS['YOUTUBE_API_KEY'], request.GET['channel_name'])
  y_channel_id = 'UCZYTClx2T1of7BRZ86-8fow' #HARDCODED

  channel = Channel.objects.get_or_create(y_channel_id = y_channel_id)
  channel.save()
  user.channel_set.add(channel)
  user.save()

  response_data = {success: True}
  return HttpResponse(json.dumps(response_data), content_type = "application/json")
