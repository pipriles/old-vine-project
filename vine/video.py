#!/usr/bin/env python2

import datetime as dt

from collections import namedtuple

import config
import youtube as yt

# Vine video struct
# I should transform this in a class
# With database methods related

fields  = "url "
fields += "id "
fields += "description "
fields += "title "
fields += "user"
VineVideo = namedtuple("VineVideo", fields)

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

class VideoData:

	# This class should like the jobs class
	# I will change this in the future

	def __init__(self, db, vid=None, conf_id=None, source=None, 
		name=None, date=None, status=None, job=None):

		self.db = db

		# If we pass just the video
		if job is None:
			self.id = vid
			self.conf_id = conf_id
			self.source = source
			self.date = date
			self.name = name

		# If we pass just the job
		else:
			self.job = job
			self.conf_id = job.settings_id
			self.source = job.url
			self.date = dt.datetime.now().strftime(config.DT_FORMAT)
			self.name = "{}_{}".format(job._id, self.date)

	def create_video(self):

		if self.id is None:

			sql  = "INSERT INTO video (`settingsID`, `source`, `name`, `date`, `status`) "
			sql += "VALUES (%s, %s, %s, %s, '00')"

			args = (self.conf_id, self.source, self.name, self.date)
			dbc = self.db.query(sql, args)
			
			self.id = dbc.lastrowid
			self.status = '00'

	def set_status(self, combined=False, uploaded=False):
		
		combine = 1 if combined else 0
		upload  = 1 if uploaded else 0
		new_status = '{}{}'.format(combine, upload)
		_change_status(new_status)

	def _change_status(self, new_status):

		sql = "UPDATE video SET status = %s WHERE id = %s"
		self.db.query(sql, (new_status, self.id))

		self.status = new_status

	def link_vine(self, vine, position):

		sql  = "INSERT INTO vine_video (`vineID`, `videoID`, `position`) "
		sql += "VALUES (%s, %s, %s)"

		args = (vine, self.id, position)
		self.db.query(sql, args)

	def link_account(self, account, title, url, description=None, 
		keywords=None, category=None, lang='EN'):

		sql  = "INSERT INTO video_account ("
		sql += " videoID, accountID,"
		sql += " title, description,"
		sql += " keywords, category,"
		sql += " url, language )"
		sql += "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

		args = (self.id, account, title, description, 
			keywords, category, url, lang)

		self.db.query(sql, args)

	@property
	def conf(self):
		# Notice that the configuration
		# should not be set manually

		if hasattr(self, '_conf'):
			return self._conf
		else:
			self._conf = fetch_conf(self.conf_id, self.db)

		self._conf = conf
		return self._conf

	def get_accounts(self):

		if self.job:
			return self.job.get_accounts(self.db)
		else:
			return None

	def set_as_used(self, vine):
		
		sql  = "UPDATE vine_job SET used = 1 "
		sql += "WHERE vine_job.jobID = %s"
		sql += " AND vine_job.vineID = %s"

		self.db.query(sql, (self.job._id, vine))


# Kind of ugly
def get_top_videos(self, db, job):
	
	# Look for videos not combined

	sql = """
		SELECT vine.url, vine.id, vine.title, user.name, 
			(vine.likes + vine.views + vine.reposts) /
    		CASE 
        		WHEN dif > 0.5 THEN 0.42 + dif * 0.01 ELSE dif 
        	END as formula
   		FROM (
    		SELECT *, 
      		TIMESTAMPDIFF(SECOND, vine.date, vine.dbdate)/86400 as dif 
    		from vine
    	) as vine
        
        INNER JOIN user
        ON vine.userID=user.id
        INNER JOIN vine_job
    	ON vine_job.vineID=vine.id
   		INNER JOIN job
    	ON job.id = vine_job.jobID
    	WHERE vine_job.jobID=%s AND vine_job.used=0 
   		AND (job.date_limit = 0 OR DATE(vine.date) > (NOW() - INTERVAL job.date_limit DAY))
    	ORDER BY formula DESC
    	LIMIT %s
    """

	result = db.query(sql, (job._id, job.combine_limit))
	return map(_make_it_pretty, result.fetchall())

def _make_it_pretty(vid):

	# I should make a column description length
	# in the settings table
	# There should not be a title field
	# - It should be just one id field

	url = vid[0]
	_id = vid[1]
	description = vid[2]
	title = str(_id)
	user = vid[3]

	return VineVideo(url, _id, description, title, user)

def get_videos(db, limit):

	# Get some videos
	# This function is mostly a helper for debug

	sql  = "SELECT vine.url, vine.id, vine.title, user.name"
	sql += " FROM vine "
	sql += "INNER JOIN user"
	sql += " ON vine.userID=user.id "
	sql += "ORDER BY RAND() "
	sql += "LIMIT %s"

	result = db.query(sql, (limit,))
	return map(_make_it_pretty, result.fetchall())