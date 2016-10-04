#!/usr/bin/env python2

from collections import namedtuple

import config
import youtube as yt

# Vine video struct

fields  = "url "
fields += "id "
fields += "description "
fields += "title "
fields += "user"
VineVideo = namedtuple("VineVideo", fields)

class VideoData:

	# This class should like the jobs class
	# I will change this in the future

	def __init__(self, db, job=None, conf_id=None):
		self.db = db
		self.job = job
		self.conf_id = conf_id

	def create_video(self, name):

		sql  = "INSERT INTO video (`settingsID`, `source`, `name`, `date`, `status`) "
		sql += "VALUES (%s, %s, %s, NOW(), '00')"

		args = (self.job.settings_id, self.job.url, name)
		dbc = self.db.query(sql, args)
		self._id = dbc.lastrowid

	# I have to make a function 
	# to set as combined or uploaded

	def change_status(self, status):
		sql = "UPDATE video SET status = %s WHERE id = %s"
		self.db.query(sql, (status, self._id))

	def link_vine(self, vine, position):
		# Video should have a id attribute
		sql  = "INSERT INTO vine_video (`vineID`, `videoID`, `position`) "
		sql += "VALUES (%s, %s, %s)"

		args = (vine, self._id, position)
		self.db.query(sql, args)

	def link_account(self, account, title, url, lang='EN'):

		sql  = "INSERT INTO video_account (videoID, accountID, title, language, url) "
		sql += "VALUES (%s, %s, %s, %s, %s)"

		args = (self._id, account, title, lang, url)
		self.db.query(sql, args)

	def get_settings(self):

		if hasattr(self, 'conf'):
			return self.conf
		else:
			if self.job is None:
				conf = config.get_settings(self.conf_id, self.db)
			else:
				conf = self.job.get_settings(self.db)

		self.conf = conf
		return conf

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

	def insert_video(self, name):
		if self.job_settings is None:
			self.get_settings()

		sql  = "INSERT INTO video"
		sql += " (settingsID, source, name) "
		sql += "VALUES (%s, %s, %s)"

		args = (self.job_settings, self.job.url, name)
		self.db.query(sql, args)

	def get_top_videos(self):
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

		result = self.db.query(sql, (self.job._id, self.job.combine_limit))
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
	sql  = "SELECT vine.url, vine.id, vine.title, user.name"
	sql += " FROM vine "
	sql += "INNER JOIN user"
	sql += " ON vine.userID=user.id "
	sql += "ORDER BY RAND() "
	sql += "LIMIT %s"

	result = db.query(sql, (limit,))
	return map(_make_it_pretty, result.fetchall())