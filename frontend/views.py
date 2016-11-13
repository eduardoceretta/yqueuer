import sys
import random
import json

from django.shortcuts import render
from django.http import Http404
from django.http import HttpResponse

def index(request):
  rand = random.randint(10,80)
  if rand == 42:
    raise Http404("The question you are looking for is not here")

  context = {
    'rand': rand
  }
  return render(request, 'frontend/index.html', context)


def player(request):
  context = {  }
  return render(request, 'frontend/player.html', context)


def getVideos(request):
  response_data = { 'videos' : [
    'Chbm84sCBAw',
    'w1feICb-HRE',
    'UfYpxF32EZo']
  }
  return HttpResponse(json.dumps(response_data), content_type = "application/json")
