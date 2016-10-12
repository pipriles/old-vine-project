#!/usr/bin/env python2

# Configuration module of the vine scraper

# Notes:
# - Change the client_id and the client_secret
# - Change the web group 
# - Change the video, image and font path

import os
from collections import namedtuple

# Control varibles

SCRIPT_STATUS = 1
DIRTY_JOBS = 0

# Listener 

SOCKET_FOLDER = '/tmp/SCRAPE'
SOCKET_PATH = SOCKET_FOLDER + '/SCRAPE_SOCKET'

MAX_CLIENTS = 1

# Youtube module

CLIENT_ID = "892925157774-u9l5kehvb7fgnqnb86rdoj0a3ek6ktd0.apps.googleusercontent.com"
CLIENT_SECRET = "k52sVi1FQCr4rj-NOICvSDDZ"
TOKEN_URI = "https://accounts.google.com/o/oauth2/token"

YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Stopwords

path = os.path.dirname(os.path.realpath(__file__))
WORDS_DIR = path + "/stopwords/"

# Web groub for permissions

WEB_GROUP = "http"

# Sleep interval time

sleep_time = 1

# Combine settings

ffmpeg_bin = "ffmpeg"
video_path = "res/videos/"
image_path = "res/images/"
font_path  = "res/fonts/"

# Job settings

MAX_SCRAPE = 1
MAX_COMBINE = 1

# Datetime format

DT_FORMAT = "%Y-%m-%d %H:%M:%S"

# Video default settings
# I will move this to the video module

DEFAULT_SETTINGS = ("0", "1280:720", "720:720",
	"(main_w/2-text_w/2)", "(main_h)-50",
	"Text here please", "26", "black@1", "white@0.7", 
	"default.ttf", "default.jpg")
