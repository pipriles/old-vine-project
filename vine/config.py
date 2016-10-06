#!/usr/bin/env python2

import os
from collections import namedtuple

# Control varibles

SCRIPT_STATUS = 1
DIRTY_JOBS = 0

# Listener 

CONFIGURE_SCRIPT =  '/home/oswald/Documents/Work'
CONFIGURE_SCRIPT += '/Vine Scraper/script/configure.sh'

SOCKET_FOLDER = '/tmp/SCRAPE'
SOCKET_PATH = SOCKET_FOLDER + '/SCRAPE_SOCKET'

MAX_CLIENTS = 1

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

# Video default settings
# I will move this to the video module

DEFAULT_SETTINGS = ("0", "1280:720", "720:720",
	"(main_w/2-text_w/2)", "(main_h)-50",
	"Text here please", "26", "black@1", "white@0.7", 
	"SuperFont.ttf", "Vine_Numbers.jpg")

# Settings struct

fields  = "id "
fields += "scale_1 "
fields += "scale_2 "
fields += "text_x "
fields += "text_y "
fields += "text_size "
fields += "font_size "
fields += "font_color "
fields += "font_background_color "
fields += "font "
fields += "image"
Settings = namedtuple("Settings", fields)

def get_settings(conf_id, db):
	if conf_id is None:
		conf = DEFAULT_SETTINGS
		return Settings(*conf)
	else:
		sql = "SELECT * FROM settings WHERE id = %s;"
		dbc = db.query(sql, (conf_id,))
		conf = dbc.fetchone()
		return Settings(*conf)
