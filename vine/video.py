#!/usr/bin/env python2

from collections import namedtuple

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

DEFAULT_SETTINGS = ("0", "1280:720", "720:720",
	"(main_w/2-text_w/2)", "(main_h)-50",
	"Text here please", "32", "black@1", "white@0.7", 
	"FreeSerif.ttf", "Vine_Numbers.jpg")

class VideoData:

	def __init__(self, job, db):
		self.db = db
		self.job = job
		self.job_settings = None

	def get_settings(self):
		sql = "SELECT * FROM settings WHERE id = %s;"
		dbc = self.db.query(sql % job.settingsID)
		conf = dbc.fetchone()
		if conf is None: 
			self.job_settings = Settings(*DEFAULT_SETTINGS)
		else:
			self.job_settings = Settings(*conf)
		
		return self.job_settings

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
		return result.fetchall()