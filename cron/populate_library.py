import os
import sys
import pprint

sys.path.append('/webapps/server/yqueuer')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yqueuer.settings")

import django
django.setup()

from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import User

from frontend.forms import UserForm
from frontend.models import Channel, Video, RUserVideo

from frontend.yqueuer_api import *


pprint.pprint("Starting Populate Library")

# result = searchChannel(settings.SECRETS['YOUTUBE_API_KEY'], 'eduardoceretta')
# pprint.pprint(result)

result = getPlaylist(settings.SECRETS['YOUTUBE_API_KEY'], 'UUZYTClx2T1of7BRZ86-8fow') #scishow
# result = getPlaylist(settings.SECRETS['YOUTUBE_API_KEY'], 'UU3Bonye4_bxoVOKBPoq45Ng') #eduardoceretta
pprint.pprint(result)