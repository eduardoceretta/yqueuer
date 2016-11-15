import sys
import random
import json

from django.conf import settings
from django.http import Http404
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

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

# @login_required
# def markWatched(request):

# @login_required
# def updateLibrary(request):

@login_required
def addChannel(request):
  print >>sys.stderr, request.user, request.POST.has_key('channel_name'), request.GET.has_key('channel_name')
  result = searchChannel(settings.SECRETS['YOUTUBE_API_KEY'], request.GET['channel_name'])
  y_channel_id = 'UCZYTClx2T1of7BRZ86-8fow'
  # channel = Channel(y_channel_id = y_channel_id)
  # channel.save()
  response_data = {'t':'oi', 'y_channel_id': y_channel_id, 'res' : result}
  return HttpResponse(json.dumps(response_data), content_type = "application/json")
