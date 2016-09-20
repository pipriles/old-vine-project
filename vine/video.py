#!/usr/bin/env python2

from collections import namedtuple

import config
import youtube as yt

# Vine video struct

fields  = "url "
fields += "id "
fields += "description "
fields += "title"
VineVideo = namedtuple("VineVideo", fields)

class VideoData:

	def __init__(self, job=None, conf_id=None, db):
		self.db = db
		self.job = job
		self.conf_id = conf_id

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

	def get_upload_info(self):
		if self.job:
			return self.job.get_accounts(self.db)
		else:
			return None

	def set_as_used(self, vine):
		sql  = "UPDATE vine_job SET used = 1 "
		sql += "WHERE vine_job.jobID = '%s'"
		sql += " AND vine_job.vineID = '%s'"

		self.db.query(sql % (self.job._id, vine))

	def insert_video(self, name):
		if self.job_settings is None:
			self.get_settings()

		sql  = "INSERT INTO video"
		sql += " (settingsID, source, name) "
		sql += "VALUES ('%s', '%s', '%s')"

		args = (self.job_settings, self.job.url, name)
		self.db.query(sql % args)

	def get_top_videos(self):
		# Look for videos not combined
		sql = """
			SELECT vine.url, vine.id, vine.title, 
				(vine.likes + vine.views + vine.reposts) /
	    		CASE 
	        		WHEN dif > 0.5 THEN 0.42 + dif * 0.01 ELSE dif 
	        	END as formula
	   		FROM (
	    		SELECT *, 
	      		TIMESTAMPDIFF(SECOND, vine.date, vine.dbdate)/86400 as dif 
	    		from vine
	    	) as vine
	        
	    	INNER JOIN vine_job
	    	ON vine_job.vineID=vine.id
	   		INNER JOIN job
	    	ON job.id = vine_job.jobID
	    	WHERE vine_job.jobID=%s AND vine_job.used=0 
	   		AND (job.date_limit = 0 OR DATE(vine.date) > (NOW() - INTERVAL job.date_limit DAY))
	    	ORDER BY formula DESC
	    	LIMIT %s
	    """

		result = self.db.query(sql % (self.job._id, self.job.combine_limit))
		return map(self._make_it_pretty, result.fetchall())

	def _make_it_pretty(self, vid):
	
		# I should make a column description length
		# in the settings table

		logger.debug(vid)

		url = vid[0]
		_id = vid[1]
		description = vid[2][:100] + '...' if len(vid[2]) > 100 else vid[2]
		title = "%s_%s" % (_id, self.job._id)

		return VineVideo(url, _id, description, title)