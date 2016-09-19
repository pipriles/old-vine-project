#!/usr/bin/env python2

import logging
from subprocess import call
from functools import partial
from datetime import datetime
from multiprocessing import Process, Pool

import config
import download as dl
from database import Database
from video import VideoData, VineVideo

logger = logging.getLogger(__name__)

class CombineProcess(Process):

	def __init__(self, job):
		name = "Combine Process %s" % job._id
		super(CombineProcess, self).__init__(name=name)
		self._job = job
		self._db = Database()
		self._db.connect()
		self._data = VideoData(self._job, self._db)
		
		self._job.start_combine(self._db)

	def run(self):
		cast = VideosSpell(self._data)
		cast.prepare_videos()
		try:
			# Combine all the videos
			self.combine_all(cast)

			# Here we are gonna upload
			#
		finally:
			self._job.finish_combine(self._db)
			logger.info("Finished combine process")


	def combine_all(self, cast):

		survivors = cast.convert_video_list(vids)
		
		if survivors:
			final = cast.combine_videos(survivors)
			change_group(final)
		else:
			logger.warning("Could not convert all the videos")

		cast.clean_videos(vids)

class VideosSpell:

	def __init__(self, vd):
		self.data = vd
		self.vids = []

	def prepare_videos():

		result = self.data.get_top_videos()

		p = Pool()
		self.vids = p.map(self._make_it_pretty, result)
		p.close()
		p.join()

		# I should check if the videos
		# already exists

		self.vids = dl.download_videos(self.vids)
		logger.debug(videos)

	def _make_it_pretty(vid):
		
		# I should make a column description length
		# in the settings table

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
			ret = convert_video(vid.title, conf)
			if ret != "":
				self.data.set_as_used(vid.id)
				converted.append(ret)

		return converted

	def combine_videos(self, vids):

		videos = "|".join(vids)
		final_name = '_'.join(map(str, (self.data.job._id, datetime.now().split())))

	 	command = [
	 		config.ffmpeg_bin, '-y', '-i', 
	 		'concat:%s' % videos, 
	 		'-c', 'copy',
	 		config.video_path + '%s.mp4' % final_name
	 	]
		call(command)

		return final_name

	def clean_videos(self, vids):

		# Delete videos used
		for vid in self.vids:
			temp = config.video_path + vid.title
			command = ['rm', '-rf', temp + ".mp4", temp + ".mpg"]
			call(command)

def convert_video(title, conf):

	result = ""

	# Horrible magic ffmpeg command
	command = [
		config.ffmpeg_bin, 
		'-loop', '1', 
		'-i', config.image_path + '%s' % conf.image, 
		'-i', config.video_path + "%s.mp4" % title, 
		
		'-filter_complex', 	
		"[0:v]scale=%s[scaled];" % conf.scale_1,
		"[1:v]scale=%s[scaled2];" % conf.scale_2,
		"[scaled][scaled2]overlay=(main_w-overlay_w)/2:0:shortest=1[res];",
		"[res]drawtext=fontfile=%s" % config.font_path + conf.font,
		":text='%s':x=%s: y=%s: " % (title, conf.text_x, conf.text_y),
		"fontsize=%s:fontcolor=%s" % (conf.font_size, conf.font_color),
		":box=1:boxcolor=%s[out]" % conf.font_background_color,

		'-map', '[out]', 
		'-map', '1:a',
		'-y', '-qscale:v', '1',
		config.video_path + '%s.mpg' % title
	]

	if call(command) == 0:
		result = config.video_path + "%s.mpg" % title

	return result

def change_group(name):
	command = ['chgrp', 'www-data', config.video_path + '%s.mp4' % name]
	call(command)

# Not completed
if __name__ == '__main__':
	main()