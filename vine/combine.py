#!/usr/bin/env python2

import logging
import datetime as dt

from subprocess import call
from functools import partial
from datetime import datetime
from multiprocessing import Process, Pool

import config
import download as dl
from database import Database
from video import VideoData, VineVideo

DT_FORMAT = "%Y-%m-%d_%H:%M:%S"

logger = logging.getLogger(__name__)

class CombineProcess(Process):

	def __init__(self, job):
		name = "Combine Process %s" % job._id
		super(CombineProcess, self).__init__(name=name)
		self.job = job
		self.db = Database()
		self.db.connect()
		self.data = VideoData(self.job, self.db)
		
		self.job.start_combine(self.db)

	def run(self):
		cast = VideosSpell(self.data)
		cast.prepare_videos()
		try:
			# Combine all the videos
			self.combine_all(cast)

			# Here we are gonna upload
			#
		finally:
			self.job.finish_combine(self.db)
			logger.info("Finished combine process")

	def combine_all(self, cast):

		survivors = cast.convert_video_list()
		
		if survivors:
			now = dt.datetime.now().strftime(DT_FORMAT)
			name = str(self.job._id) + "_" + now
			combine_videos(survivors, name)
			change_group(name)
		else:
			logger.warning("Could not convert all the videos")

		cast.clean_videos()

class VideosSpell:

	def __init__(self, vd):
		self.data = vd
		self.vids = []

	def prepare_videos(self):

		result = self.data.get_top_videos()
		self.vids = map(self._make_it_pretty, result)
		
		# I should check if the videos
		# already exists

		self.vids = dl.download_videos(self.vids)
		logger.debug(self.vids)

	def _make_it_pretty(self, vid):
		
		# I should make a column description length
		# in the settings table

		logger.debug(vid)

		url = vid[0]
		_id = vid[1]
		description = vid[2][:100] + '...' if len(vid[2]) > 100 else vid[2]
		title = "%s_%s" % (_id, self.data.job._id)

		return VineVideo(url, _id, description, title)

	def convert_video_list(self):

		conf = self.data.get_settings()
		converted = []
		for vid in self.vids:
			# Should i Pool?
			ret = convert_video(vid.title, vid.description, conf)
			if ret != "":
				self.data.set_as_used(vid.id)
				converted.append(ret)

		return converted

	def clean_videos(self):

		# Delete videos used
		for vid in self.vids:
			temp = config.video_path + vid.title
			command = ['rm', '-rf', temp + ".mp4", temp + ".mpg"]
			call(command)

def combine_videos(vids, name):

	videos = "|".join(vids)
	
 	command = [
 		config.ffmpeg_bin, '-y', '-i', 
 		'concat:%s' % videos, 
 		'-c', 'copy',
 		config.video_path + '%s.mp4' % name
 	]
	call(command)

def convert_video(title, sub, conf):

	result = ""

	cfilter  = "[0:v]scale=%s[scaled];" % conf.scale_1
	cfilter += "[1:v]scale=%s[scaled2];" % conf.scale_2
	cfilter += " [scaled][scaled2]overlay=(main_w-overlay_w)/2:0:shortest=1[res];"
	cfilter += " [res]drawtext=fontfile=%s" % config.font_path + conf.font
	cfilter += ":text='%s':x=%s: y=%s:" % (sub, conf.text_x, conf.text_y)
	cfilter += " fontsize=%s:fontcolor=%s" % (conf.font_size, conf.font_color)
	cfilter += ":box=1:boxcolor=%s[out]" % conf.font_background_color

	# Horrible magic ffmpeg command
	command = [
		config.ffmpeg_bin, 
		'-loop', '1', 
		'-i', config.image_path + '%s' % conf.image, 
		'-i', config.video_path + "%s.mp4" % (title), 
		'-filter_complex', 
		cfilter,
		'-map', '[out]', 
		'-map', '1:a',
		'-y', '-qscale:v', '1',
		config.video_path + '%s.mpg' % title
	]

	if call(command) == 0:
		result = config.video_path + "%s.mpg" % title

	return result

def change_group(name):
	command = ['chgrp', config.WEB_GROUP, config.video_path + '%s.mp4' % name]
	call(command)

# Not completed
if __name__ == '__main__':
	main()