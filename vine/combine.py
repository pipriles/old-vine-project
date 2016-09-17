#!/usr/bin/env python2

from subprocess import call
from functools import partial
from datetime import datetime
from multiprocessing import Process, Pool

import download as dl
from database import Database
from video import VideoData

# Make a config file in the __init__.py 

ffmpeg_bin = "ffmpeg"	# Linux
video_path = "/var/www/html/res/videos/"
image_path = "/var/www/html/res/images/"
font_path  = "/var/www/html/res/fonts/"

def prepare_videos(vid_data):
	result = vid_data.get_top_videos()
	videos = dl.download_videos(vid_data.job, result)

	p = Pool()
	vids = [x for x in p.map(cut_description, videos)]
	p.close()
	p.join()

	return vids

class CombineProcess(Process):

	def __init__(self, job):
		name = "Combine Process %s" % job._id
		super(CombineProcess, self).__init__(name=name)
		self._job = job
		self._db = Database()
		self._db.connect()
		self._data = VideoData(self._job, self._db)
		
		self._job.start_combine(self._db)

	def close(self):
		self._db.commit()
		self._db.close()

	def run(self):
		self._data.get_settings()
		vids = prepare_videos(self._data)
		
		# Combine all the videos
		self.combine_all(vids)

		# Here we are gonna upload
		#

		self.close()

	def combine_all(vids):
		cast = VideosSpell(self._job)
		
		survivors = cast.convert_video_list(vids)
		if survivors:
			final = cast.combine_videos(survivors)
			change_group(final)
		else:
			print "Nothing to do here"

		cast.clean_videos(vids)

class VideosSpell:

	def __init__(self, job):
		self.job = job

	def convert_video_list(self, vids):
		converted = []
		for v in vids:
			title = "%s_%s" % (vid[0], self.job._id)
			ret = convert_video(title)	# Should i Pool?
			if ret != "":
				data.set_as_used(vid[0])
				converted.append(ret)

		return converted

	def combine_videos(self, vids):
		videos = "|".join(vids)
		final_name = '_'.join([str(self.job._id)] + str(datetime.now()).split())

	 	command = [
	 		ffmpeg_bin, '-y', '-i', 
	 		'concat:%s' % videos, 
	 		'-c', 'copy',
	 		video_path + '%s.mp4' % final_name
	 	]
		call(command)
		return final_name

	def clean_videos(self, vids):
		# Delete videos used
		for vid in vids:
			temp = video_path + "%s_%s" % (vid[0], self.job._id)
			command = ['rm', '-rf', temp + ".mp4", temp + ".mpg"]
			call(command)

# Helper
def cut_description(vid):
	(vid[0], vid[1][:100] + '...' if len(vid[1]) > 100 else vid[1])

def convert_video(title, conf):

	result = ""

	# Horrible magic ffmpeg command
	command = [
		ffmpeg_bin, 
		'-loop', '1', 
		'-i', image_path + '%s' % conf.image, 
		'-i', video_path + "%s_%s.mp4" % title, 
		
		'-filter_complex', 	
		"[0:v]scale=%s[scaled];" % conf.scale_1,
		"[1:v]scale=%s[scaled2];" % conf.scale_2,
		"[scaled][scaled2]overlay=(main_w-overlay_w)/2:0:shortest=1[res];",
		"[res]drawtext=fontfile=%s" % font_path + conf.font,
		":text='%s':x=%s: y=%s: " % (title, conf.text_x, conf.text_y),
		"fontsize=%s:fontcolor=%s" % (conf.font_size, conf.font_color),
		":box=1:boxcolor=%s[out]" % conf.font_background_color,

		'-map', '[out]', 
		'-map', '1:a',
		'-y', '-qscale:v', '1',
		video_path + '%s_%s.mpg' % title
	]

	if call(command) == 0:
		result = video_path + "%s_%s.mpg" % title

	return result

def change_group(name):
	command = ['chgrp', 'www-data', video_path + '%s.mp4' % name]
	call(command)

# Not completed
if __name__ == '__main__':
	main()