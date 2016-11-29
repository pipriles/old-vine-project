#!/usr/bin/env python2

# This module should be about the final video
# Any special class like VineVideo or VineData
# Should be moved

import re
import datetime as dt

import props
from vine import VineVideo
from .. import util
from .. import config
from .. import youtube as yt
from .. import jobs

class VideoData:

	# This class should like the jobs class
	# I will change this in the future

	def __init__(self, db, vid=None, conf_id=None, source=None, 
		name=None, date=None, job=None):

		self.db  = db
		self.id  = vid
		self.job = job

		# If we pass just the video
		if job is None:
			args = (conf_id, source, name, date, 0)
			self.set_info(*args)

		# If we pass just the job
		else:
			args = (job.settings_id, job.url, job.name,
				dt.datetime.now().strftime(config.DT_FORMAT), 0)
			self.set_info(*args)

	def fetch_info(self):

		if self.id:
			sql = "SELECT * FROM video WHERE id = %s"
			query = self.db.query(sql, (self.id,))
			args = query.fetchone()
			self.set_info(*args)

	def set_info(self, conf_id, source, name, date, status):

		self.conf_id = conf_id
		self.source  = source
		self.name    = name
		self.date    = date
		self.status  = status

	def get_videos(self):

		ret = []
		db  = self.db
		job = self.job

		vids = self._get_linked()
		if vids is None:
			vids = get_top_videos(db, job)

		for x in vids:
			url, vid, description, user = x[:4]
			if self.id:
				title = "{}_Vid_{}".format(vid, self.id)
			elif job:
				title = "{}_Job_{}".format(vid, job._id)
			else:
				title = vid

			ret.append(VineVideo(url, vid, description, title, user))

		return ret

	def _get_linked(self):
		result = None
		if self.id:
			sql  = 'SELECT vine.url, vine.id, vine.title, user.name'
			sql += ' FROM `vine_video` '
			sql += 'INNER JOIN vine'
			sql += ' ON vine_video.vineID=vine.id '
			sql += 'INNER JOIN user'
			sql += ' ON vine.userID=user.id '
			sql += 'WHERE vine_video.videoID=%s'
			sql += " ORDER BY vine_video.position ASC"
			query = self.db.query(sql, (self.id,))
			result = query.fetchall()
		return result

	def create_video(self):

		if self.id is None:
			sql  = "INSERT INTO video (`settingsID`, `source`, `name`, `date`, `status`) "
			sql += "VALUES (%s, %s, %s, %s, '00')"

			args = (self.conf_id, self.source, self.name, self.date)
			dbc = self.db.query(sql, args)
			
			self.id = dbc.lastrowid
			self.status = 0

	def set_status(self, stat):

		if not self.id is None:
			sql = "UPDATE video SET status = %s WHERE id = %s"
			self.db.query(sql, (stat, self.id))

			self.status = stat

	def link_vine(self, vine_id, position):

		sql  = "INSERT INTO vine_video (`vineID`, `videoID`, `position`) "
		sql += "VALUES (%s, %s, %s)"

		args = (vine_id, self.id, position)
		self.db.query(sql, args)

	def link_account(self, account, title, url, lang='EN'):

		sql  = "INSERT INTO video_account ("
		sql += " url, videoID, accountID,"
		sql += " title, language )"
		sql += "VALUES (%s, %s, %s, %s, %s)"

		args = (url, self.id, account, title, lang)

		self.db.query(sql, args)

	@property
	def conf(self):
		# Notice that the configuration
		# should not be set manually

		if not hasattr(self, '_conf'):
			self._conf = props.fetch_conf(self.conf_id, self.db)

		return self._conf

	def get_accounts(self):

		if self.job:
			data = jobs.JobData(self.job, self.db)
			return data.get_accounts()
		else:
			return None

	def set_as_used(self, vine_id):
		
		if self.job:
			sql  = "UPDATE vine_job SET used = 1 "
			sql += "WHERE vine_job.jobID = %s"
			sql += " AND vine_job.vineID = %s"

			self.db.query(sql, (self.job._id, vine_id))

	# Removed the info of the video
	# to youtube generator

# Kind of ugly
def get_top_videos(db, job):
	
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
	return result.fetchall()

def _make_it_pretty(vid):

	# This is not useful anymore

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
