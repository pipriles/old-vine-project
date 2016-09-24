#!/usr/bin/env python2

from collections import namedtuple

WORDS_DIR = "./vine/stopwords/"

# Web groub for permissions

WEB_GROUP = "http"

# Sleep interval time

sleep_time = 1

# Combine settings

ffmpeg_bin = "ffmpeg"
video_path = "./res/videos/"
image_path = "./res/images/"
font_path  = "./res/fonts/"

# Job settings

MAX_SCRAPE = 1
MAX_COMBINE = 1

# Video default settings

DEFAULT_SETTINGS = ("0", "1280:720", "720:720",
	"(main_w/2-text_w/2)", "(main_h)-50",
	"Text here please", "32", "black@1", "white@0.7", 
	"FreeSerif.ttf", "Vine_Numbers.jpg")

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
		dbc = db.query(sql % conf_id)
		conf = dbc.fetchone()
		return Settings(*conf)
