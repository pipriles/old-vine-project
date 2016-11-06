#!/usr/bin/env python2

from collections import namedtuple
from .. import config

# Video Settings struct
# Another thing that maybe should be a class

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

def fetch_conf(conf_id, db):
	if conf_id is None:
		conf = config.DEFAULT_SETTINGS
		return Settings(*conf)
	else:
		sql = "SELECT * FROM settings WHERE id = %s;"
		dbc = db.query(sql, (conf_id,))
		conf = dbc.fetchone()
		return Settings(*conf)