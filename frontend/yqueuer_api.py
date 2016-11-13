import sys
import random
import json

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

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
  print >>sys.stderr, channel_name, search_response
  for search_result in search_response.get("items", []):
    print >>sys.stderr, search_result
    _id = search_result.get("id", None)
    _name = search_result["snippet"]["customUrl"]
    channels.append([_id, _name])

  return channels