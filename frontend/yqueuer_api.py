import sys
import random
import json
import pprint

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

from googleapiclient.errors import HttpError

def searchChannelById(dev_key, y_channel_id):
  DEVELOPER_KEY = dev_key
  YOUTUBE_API_SERVICE_NAME = "youtube"
  YOUTUBE_API_VERSION = "v3"
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  try:
    search_response = youtube.channels().list(
      part='contentDetails,snippet',
      id=y_channel_id
    ).execute()
  except HttpError as e:
    print ("ERROR [HttpError]: " + str(e))
    return None

  channels = []
  for search_result in search_response.get("items", []):
    channel_obj = {
      'id' : search_result["id"],
      'title' : search_result["snippet"]["title"],
      'name' : search_result["snippet"].get("customUrl", search_result["snippet"]["title"]),
      'username' : None,
      'thumbnails' : search_result["snippet"]["thumbnails"]["high"]["url"],
      'playlist_uploads_id' : search_result["contentDetails"]["relatedPlaylists"]["uploads"],
    }
    channels.append(channel_obj)

  return channels[0] if len(channels) > 0 else None

def searchChannelByUsername(dev_key, username):
  DEVELOPER_KEY = dev_key
  YOUTUBE_API_SERVICE_NAME = "youtube"
  YOUTUBE_API_VERSION = "v3"
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  try:
    search_response = youtube.channels().list(
      part='contentDetails,snippet',
      forUsername=username
    ).execute()
  except HttpError as e:
    print ("ERROR [HttpError]: " + str(e))
    return None

  channels = []
  for search_result in search_response.get("items", []):
    channel_obj = {
      'id' : search_result["id"],
      'title' : search_result["snippet"]["title"],
      'name' : search_result["snippet"].get("customUrl", search_result["snippet"]["title"]),
      'username' : username,
      'thumbnails' : search_result["snippet"]["thumbnails"]["high"]["url"],
      'playlist_uploads_id' : search_result["contentDetails"]["relatedPlaylists"]["uploads"],
    }
    channels.append(channel_obj)

  return channels[0] if len(channels) > 0 else None

def getVideosFromPlaylist(dev_key, playlist_id, last_video_id):
  DEVELOPER_KEY = dev_key
  YOUTUBE_API_SERVICE_NAME = "youtube"
  YOUTUBE_API_VERSION = "v3"
  SEARCH_EXTRA_PAGES = 3
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  videos = []
  i = 0
  max_pages = 300
  nextPageToken = None
  while max_pages > 0 and (nextPageToken or i == 0):
    try:
      search_response = youtube.playlistItems().list(
        part = 'contentDetails,snippet',
        playlistId = playlist_id,
        maxResults = 50,
        pageToken = nextPageToken,
      ).execute()
    except HttpError as e:
      print ("ERROR [HttpError]: " + str(e))
      return []

    for search_result in search_response.get("items", []):
      vid_id = search_result["contentDetails"]["videoId"]

      # Import a couple of extra pages if last_video_id was found
      #   Pages are not properly sorted but by going a couple of pages further should
      #   give a good balance between overhead and correctness
      if last_video_id and last_video_id == vid_id:
        max_pages = SEARCH_EXTRA_PAGES+1

      video_obj = {
        'id' : vid_id,
        'description' : search_result["snippet"]["description"],
        'published_at' : search_result["snippet"]["publishedAt"],
        'thumbnails' : search_result["snippet"]["thumbnails"]["high"]["url"],
        'title' : search_result["snippet"]["title"],
        'position' : search_result["snippet"]["position"],
      }
      videos.append(video_obj)

    nextPageToken = search_response.get("nextPageToken", None)
    i+=1
    max_pages-=1

  videos.sort(key=lambda x: x["published_at"])
  final_vid = []
  seen_last_vid_id = False
  for v in videos:
    if(last_video_id):
      if(v["id"]==last_video_id):
        seen_last_vid_id = True
      elif (seen_last_vid_id):
        final_vid.append(v)
    else:
      final_vid.append(v)

  return final_vid



def getVideoInfo(dev_key, y_video_id):
  DEVELOPER_KEY = dev_key
  YOUTUBE_API_SERVICE_NAME = "youtube"
  YOUTUBE_API_VERSION = "v3"
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  try:
    search_response = youtube.videos().list(
      part='snippet',
      id=y_video_id
    ).execute()
  except HttpError as e:
    print ("ERROR [HttpError]: " + str(e))
    return None

  videos = []
  for search_result in search_response.get("items", []):
    video_obj = {
      'id' : search_result["id"],
      'channel_id' : search_result["snippet"]["channelId"],
      'title' : search_result["snippet"]["title"],
      'description' : search_result["snippet"]["description"],
      'thumbnails' : search_result["snippet"]["thumbnails"]["high"]["url"],
    }
    videos.append(video_obj)

  return videos[0] if len(videos) > 0 else None

