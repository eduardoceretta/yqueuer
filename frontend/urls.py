from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^player$', views.player, name='player'),
    url(r'^api/get_videos$', views.getVideos, name='get_videos'),
]