from django.contrib import admin

# Register your models here.
from .models import Channel, Video

admin.site.register(Channel)
admin.site.register(Video)
