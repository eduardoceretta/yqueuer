from django.contrib import admin

# Register your models here.
from .models import Channel, Video, RUserVideo

admin.site.register(Channel)
admin.site.register(Video)
admin.site.register(RUserVideo)

