#!/usr/bin/env python2

import logging
import datetime as dt

from subprocess import call
from functools import partial
from datetime import datetime
from multiprocessing import Process, Pool

import config
import download as dl
import youtube as yt
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
		
		self.data = VideoData(self.db, self.job)
		self.job.start_combine(self.db)

	def run(self):
		cast = VideosSpell(self.data)
		try:
			# Combine all the videos
			cast.download_videos()
			cast.convert_videos()
			cast.combine_videos()
		finally:
			cast.clean_videos()
			self.job.finish_combine(self.db)
			logger.info("Finished combine process")

		try:
			# If autoupload flag is set
			self.job.start_upload(self.db)
			cast.upload_video()
		finally:
			self.job.finish_upload(self.db)
			logger.info("Finished upload process")

# Maybe this class should have inside
# a VideoData initialization and not 
# in the process

class VideosSpell:

	def __init__(self, vd):
		self.data = vd
		self.downloaded = []
		self.converted = []

	def download_videos(self):

		top = self.data.get_top_videos()

		# I should check if the videos
		# already exists

		self.downloaded = dl.download_videos(top)
		logger.debug(self.downloaded)

	def convert_videos(self):

		conf = self.data.get_settings()
		
		# Should i Pool?

		for vid in self.downloaded:
			ret = convert_video(vid, conf)
			if ret != "":
				self.data.set_as_used(vid.id)
				self.converted.append(ret)

	def combine_videos(self):

		if self.converted:
			now = dt.datetime.now().strftime(DT_FORMAT)
			name = str(self.data.job._id) + "_" + now
			combine_videos(self.converted, name)
			change_group(name)
			self.final = name
		else:
			logger.warning("Could not convert all the videos")

	def upload_video(self):

		logger.debug(self.data.job.autoupload)

		if self.data.job.autoupload and hasattr(self, 'final'):

			accounts = self.data.get_accounts()
			logger.debug(accounts)

			# What should i put in the description?
			# Maybe a settings for the privacy

			file = config.video_path + '%s.mp4' % self.final
			description = None
			category = 22
			keywords = yt.gen_keywords(self.downloaded)
			privacyStatus = yt.PRIVACY_STATUS[0]

			for x in accounts:
				user = x[0]
				title = yt.make_title(x[1], self.data.job)
				args = yt.UploadVideo(user, file, title, 
					description, category, keywords, privacyStatus)

				# Upload the video
				yt.upload_from_args(args, self.data.db)

	def clean_videos(self):

		# Delete videos used
		for vid in self.downloaded:
			temp = config.video_path + vid.title
			command = ['rm', '-rf', temp + ".mp4", temp + ".mpg"]
			call(command)

def combine_videos(vids, name):

	videos = "|".join([config.video_path + "%s.mpg" % x.title for x in vids])
	
 	command = [
 		config.ffmpeg_bin, '-y', '-i', 
 		'concat:%s' % videos, 
 		'-c', 'copy',
 		config.video_path + '%s.mp4' % name
 	]
	call(command)

def convert_video(vid, conf):

	result = None

	cfilter  = "[0:v]scale=%s[scaled];" % conf.scale_1
	cfilter += "[1:v]scale=%s[scaled2];" % conf.scale_2
	cfilter += " [scaled][scaled2]overlay=(main_w-overlay_w)/2:0:shortest=1[res];"
	cfilter += " [res]drawtext=fontfile=%s" % config.font_path + conf.font
	cfilter += ":text='%s':x=%s: y=%s:" % (vid.description, conf.text_x, conf.text_y)
	cfilter += " fontsize=%s:fontcolor=%s" % (conf.font_size, conf.font_color)
	cfilter += ":box=1:boxcolor=%s[out]" % conf.font_background_color

	# Horrible magic ffmpeg command
	command = [
		config.ffmpeg_bin, 
		'-loop', '1', 
		'-i', config.image_path + '%s' % conf.image, 
		'-i', config.video_path + "%s.mp4" % (vid.title), 
		'-filter_complex', 
		cfilter,
		'-map', '[out]', 
		'-map', '1:a',
		'-y', '-qscale:v', '1',
		config.video_path + '%s.mpg' % vid.title
	]

	if call(command) == 0:
		result = vid

	return result

def change_group(name):
	command = ['chgrp', config.WEB_GROUP, config.video_path + '%s.mp4' % name]
	call(command)

# Not completed

if __name__ == '__main__':
	main()