import os
import sys
import pprint

sys.path.append('/webapps/server/yqueuer')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yqueuer.settings")

import django
django.setup()

from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User

from frontend.forms import UserForm
from frontend.models import Channel, Video, RUserVideo

from frontend.yqueuer_api import *


pprint.pprint("Starting Populate Library")

# result = searchChannel(settings.SECRETS['YOUTUBE_API_KEY'], 'scishow')
# pprint.pprint(result)

# Channel.objects.update_or_create(
#       y_channel_id = result["id"],
#       playlist_uploads_id = result["playlist_uploads_id"],
#       title = result["title"],
#       name = result["name"],
#       thumbnails = result["thumbnails"],
#       imported_date = timezone.now()
#     )

pprint.pprint(Channel.objects.all())

for c in Channel.objects.all():
  pprint.pprint("  Processing channel: %s" % c.name)
  videos = getVideosFromPlaylist(settings.SECRETS['YOUTUBE_API_KEY'], c.playlist_uploads_id)
  pprint.pprint("  Got videos: %d" % len(videos))
  for v in videos:
    pprint.pprint("  Processing video: %s (%s) %s" % (v["title"], v["id"], v["published_at"]))
    video_qs = Video.objects.filter(y_video_id = v["id"])
    if len(video_qs) == 0 :
      Video.objects.update_or_create(
        y_video_id = v["id"], channel = c, published_at = v["published_at"],
        title = v["title"], thumbnails = v["thumbnails"],
        description = v["description"], position = v["position"]
      )

pprint.pprint("Total videos: %d" %  len(Video.objects.all()))