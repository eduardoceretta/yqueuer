import sys
import random
import json
import pprint

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

def searchChannelById(dev_key, y_channel_id):
  DEVELOPER_KEY = dev_key
  YOUTUBE_API_SERVICE_NAME = "youtube"
  YOUTUBE_API_VERSION = "v3"
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)
  search_response = youtube.channels().list(
    part='contentDetails,snippet',
    id=y_channel_id
  ).execute()

  channels = []
  for search_result in search_response.get("items", []):
    channel_obj = {
      'id' : search_result["id"],
      'title' : search_result["snippet"]["title"],
      'name' : search_result["snippet"].get("customUrl", search_result["snippet"]["title"]),
      'thumbnails' : search_result["snippet"]["thumbnails"]["high"]["url"],
      'playlist_uploads_id' : search_result["contentDetails"]["relatedPlaylists"]["uploads"],
    }
    channels.append(channel_obj)

  return channels[0] if len(channels) > 0 else None

def searchChannel(dev_key, channel_name):
  DEVELOPER_KEY = dev_key
  YOUTUBE_API_SERVICE_NAME = "youtube"
  YOUTUBE_API_VERSION = "v3"
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)
  search_response = youtube.channels().list(
    part='contentDetails,snippet',
    forUsername=channel_name
  ).execute()

  channels = []
  for search_result in search_response.get("items", []):
    channel_obj = {
      'id' : search_result["id"],
      'title' : search_result["snippet"]["title"],
      'name' : search_result["snippet"].get("customUrl", search_result["snippet"]["title"]),
      'thumbnails' : search_result["snippet"]["thumbnails"]["high"]["url"],
      'playlist_uploads_id' : search_result["contentDetails"]["relatedPlaylists"]["uploads"],
    }
    channels.append(channel_obj)

  return channels[0] if len(channels) > 0 else None

def getVideosFromPlaylist(dev_key, playlist_id, last_video_id):
  DEVELOPER_KEY = dev_key
  YOUTUBE_API_SERVICE_NAME = "youtube"
  YOUTUBE_API_VERSION = "v3"
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  videos = []
  i = 0
  nextPageToken = None
  while nextPageToken or i == 0:
    search_response = youtube.playlistItems().list(
      part = 'contentDetails,snippet',
      playlistId = playlist_id,
      maxResults = 50,
      pageToken = nextPageToken,
    ).execute()

    for search_result in search_response.get("items", []):
      vid_id = search_result["contentDetails"]["videoId"]

      # Stop importing if reached last_video_id
      if last_video_id and last_video_id == vid_id:
        return videos

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

  return videos