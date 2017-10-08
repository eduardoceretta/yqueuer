from frontend.models import Channel, Video, RUserVideo, RUserChannel
from django.contrib.auth.models import User
from django.db.models import Max, Min, Avg, Count
import pprint

def removeVideo(u_username,v_id):
  u = User.objects.get(username = u_username)
  v = Video.objects.get(id = v_id)
  c = v.channel
  userchannel = u.ruserchannel_set.get(channel = c)
  uservideo_qs = u.ruservideo_set.filter(video = v)
  if (len(uservideo_qs) > 1):
    uservideo = uservideo_qs[0]
    print("Processing Video %s[nv%d]:%s[rc:%d] (%s) %s " % (c.title, userchannel.num_vid, v.title, v.ref_count, v.y_video_id, v.published_at), 3)
    # Delete UserVideo relation entry
    uservideo.delete()
    print("Deleted From RUserVideo", 4)
    # Update UserChannel counter
    userchannel.num_vid-=1
    userchannel.save()
    print("Updated UserChannel num_vid to %d" % userchannel.num_vid, 4)
    # Update Video Refcount and delete it if needed
    v.ref_count-=1
    if v.ref_count <= 0:
      v.delete()
      print("Deleted Video", 4)
    else:
      v.save()
      print("Updated Video ref_count to %d" % v.ref_count, 4)

problems_qs = RUserVideo.objects.all().values('user','video','video__channel__name', 'video__title','user__username', 'video__ref_count').annotate(Count('video')).filter(video__count__gt = 1)
pprint.pprint([(x["user__username"],x["video__channel__name"],x["video__title"], x["video__count"]) for x in problems_qs

for v in problems_qs:
  removeVideo(v["user__username"], v["video"])
