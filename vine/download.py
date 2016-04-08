#!/usr/bin/env python

from database import Database
import urllib
import os
from multiprocessing import Pool
from functools import partial

video_path = "/var/www/html/res/videos/"

# Downloads a videos each CPU

def download_top_videos(job):

	db = Database().connect_db()
	dbc = db.cursor()

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

	dbc.execute(sql % (job[0], job[6]))
	results = dbc.fetchall()
	db.commit()

	if not os.path.exists(video_path):
		os.makedirs(video_path)

	pool = Pool()
	download = partial(partial(retrieve_vid, urllib.URLopener()), job) 
	vids = [x for x in pool.map(download, results) if x is not None]

	pool.close()
	pool.join()

	db.commit()
	db.close()

	return vids

def retrieve_vid(site, job, vid):
	print "Downloading %s.mp4" % vid[1]
	try:
		site.retrieve(vid[0], video_path + "%s_%s.mp4" % (vid[1], job[0]))
		
		# Max 80 characters description
		return (vid[1], vid[2][:100] + '...' if len(vid[2]) > 100 else vid[2])
	except:
		return None

# Test
if __name__ == '__main__':

	job = [3, 'test', 5, 3, 4, 5]
	download_top_videos(job)
