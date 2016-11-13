from django.contrib import admin

# Register your models here.
from .models import Channel, Video, RUserChannel, RUserVideo

admin.site.register(Channel)
admin.site.register(Video)
admin.site.register(RUserChannel)
admin.site.register(RUserVideo)

