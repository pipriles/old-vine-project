#!/usr/bin/env python

import download as vine
from database import Database
from subprocess import call
from multiprocessing import Pool
from functools import partial
from datetime import datetime

ffmpeg_bin = "ffmpeg"	# Linux
video_path = "/var/www/html/res/videos/"
image_path = "/var/www/html/res/images/"
font_path  = "/var/www/html/res/fonts/"

def convert_video(job_id, vid):

	result = ""
	db = Database().connect_db()
	dbc = db.cursor()

	dbc.execute("SELECT * FROM settings;")
	conf = dbc.fetchone()

	# Horrible magic ffmpeg command
	command = \
		[
			ffmpeg_bin, '-loop', '1', '-i', image_path + '%s' % conf[10], '-i', video_path + "%s_%s.mp4" % (vid[0], job_id), 
			'-filter_complex', "[0:v]scale=%s[scaled];[1:v]scale=%s[scaled2]; [scaled][scaled2]overlay=(main_w-overlay_w)/2:0:shortest=1[res]; [res]drawtext=fontfile=%s:text='%s':x=%s: y=%s: fontsize=%s:fontcolor=%s:box=1:boxcolor=%s[out]" % 
			(conf[1], conf[2], font_path + conf[9], vid[1], conf[3], conf[4], conf[6], conf[7], conf[8]),
			'-map', '[out]', 
			'-map', '1:a',
			'-y', '-qscale:v', '1',
			video_path + '%s_%s.mpg' % (vid[0], job_id)
		]

	if call(command) == 0:
		# Check video as used
		sql = "UPDATE video_job SET used = 1 WHERE video_job.jobID = '%s' AND video_job.videoID = '%s'"
		dbc.execute(sql % (job_id, vid[0]))
		result = video_path + "%s_%s.mpg" % (vid[0], job_id)
		db.commit()

	print conf, vid

	db.close()

	return result

def combine_top_videos(job):

	db = Database().connect_db()
	dbc = db.cursor()

	# Download videos
 	videos = vine.download_top_videos(job)

	# if there is no new videos
	if len(videos) > 0:
	 	# Combine videos
	 	pool = Pool(1)
	 	convert = partial(convert_video, job[0])
		output = pool.map(convert, videos)
		pool.close()
		pool.join()

		output = [x for x in output if x != '']
		output = '|'.join(output)

		if len(output) > 0:

			result_name = '_'.join([str(job[0])] + str(datetime.now()).split())

		 	command = [
		 		ffmpeg_bin, '-y', '-i', 
		 		'concat:%s' % output, 
		 		'-c', 'copy',
		 		video_path + '%s.mp4' % result_name]
			call(command)

			command = ['chgrp', 'www-data', video_path + '%s.mp4' % result_name]
			call(command)
			
			sql = "INSERT INTO video (name, job) VALUES ('%s', '%s')"
			dbc.execute(sql % (result_name, job[1]))

	else:
		print "No hay videos que combinar"

	# Delete videos used
	for vid in videos:
		temp = video_path + "%s_%s" % (vid[0], job[0])
		command = ['rm', '-rf', temp + ".mp4", temp + ".mpg"]
		call(command)

	db.commit()
	db.close()

# Not completed
if __name__ == '__main__':

	db = Database().connect_db()

	job = [3, 'test', 5, 3, 4, 1]
	combine_top_videos(job)
