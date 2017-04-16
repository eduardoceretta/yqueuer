from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url(r'^player/$', views.player, name = 'player'),
    url(r'^manage/$', views.manage, name = 'manage'),
    # APIS
    url(r'^api/get_videos/$', views.getVideos, name = 'get_videos'),
    url(r'^api/get_channels/$', views.getChannels, name = 'get_channels'),
    url(r'^api/mark_watched/$', views.markWatched, name = 'mark_watched'),
    # url(r'^api/update_channel_library/$', views.updateChannelLibrary, name = 'update_channel_library'),
    url(r'^api/add_channel/$', views.addChannel, name = 'add_channel'),
    url(r'^api/post_jserror/$', views.postJSError, name = 'post_jserror'),
    # Authentication
    url(r'^register/$', views.register, name = 'register'),
    url(r'^login/$', views.user_login, name = 'login'),
    url(r'^logout/$', views.user_logout, name = 'logout'),
]