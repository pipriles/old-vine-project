#!/usr/bin/env python2

# I have to add reconvert support to 
# randomize the video combination

import os
import glob
import logging
import datetime as dt
import re

from subprocess import call
from functools import partial
from datetime import datetime
from multiprocessing import Process, Pool

import config
import download as dl
import youtube as yt

from data import video

logger = logging.getLogger(__name__)

# Maybe this class should have inside
# a VideoData initialization and not 
# in the process

DT_FORMAT = "%Y%m%d%H%M%S"
NOW = dt.datetime.now

def temp_name(i):
	return "{}{}".format(NOW().strftime(DT_FORMAT), i)

def proc_job(db, job):
	data = video.VideoData(db, job=job)
	return CombineProtocol(data)

def proc_vid(db, vid):
	data = video.VideoData(db, vid=vid)
	return CombineProtocol(data)

class CombineProtocol:

	def __init__(self, data):
		self.vid = data
		self.downloaded = []
		self.converted = []
		self.combined = None

	# Should i?
	def create_video(self):
		self.vid.set_status(2)
		try:
			# Combine all the videos
			self.download_videos()
			self.convert_videos()
			self.combine_videos()
			self.apply_changes()
		except BaseException as e:
			self.vid.set_status(0)
			raise e
		finally:
			self.clean_videos()

	def download_videos(self):

		vids = self.vid.get_videos()
		self.downloaded = dl.download_videos(vids)

		for vid in self.downloaded:
			logger.debug(vid)

	def convert_videos(self):
		
		conf = self.vid.conf 	# Should be a simple function?
		
		for vine in self.downloaded:
			ret = convert_video(vine, conf)
			if ret:
				self.converted.append(ret)

	def combine_videos(self):

		if self.converted:
			if not self.vid.id is None:
				name = str(self.vid.id)
			elif not self.vid.job is None:
				name = temp_name(self.vid.job._id)
			else:
				raise RuntimeError('Cannot guess a proper name')

			ret = combine_videos(self.converted, name)
			if ret:
				self.combined = name
				change_group(self.combined)
		else:
			logger.warning("Could not convert all the videos")

	def apply_changes(self):
		logger.debug('Applying changes')
		if self.vid.id is None and self.combined:
			self.vid.create_video()
			old = "{}{}.mp4".format(config.video_path, self.combined)
			new = "{}{}.mp4".format(config.video_path, self.vid.id)
			os.rename(old, new)

			position = 0
			logger.debug('Linking videos')
			for vine in self.converted:
				self.vid.set_as_used(vine.id)
				self.vid.link_vine(vine.id, position)
				position += 1

		logger.debug('Setting status to combined')
		self.vid.set_status(1)

	def upload_video(self):

		if self.vid.job is None or self.vid.job.autoupload:

			accounts = self.vid.get_accounts()
			logger.debug(accounts)

			# I have to add the autogen description
			# Maybe a settings for the privacy

			file = config.video_path + '%s.mp4' % self.vid.id
			keywords = yt.gen_keywords(self.downloaded)
			description  = "TAGS: "
			description += ', '.join(keywords)
			category = 22
			privacyStatus = yt.PRIVACY_STATUS[0]

			for x in accounts:
				# The title and the description
				# are from the video module now

				user = x[0]
				title = yt.make_title(x[1], self.vid.job)
				args = yt.UploadVideo(user, file, title, 
					description, category, keywords, privacyStatus)

				# Upload the video
				url = yt.upload_from_args(args, self.vid.db)

				if url is not None:
					# Here we should link to an account
					self.vid.link_account(user, title, url)


	def clean_videos(self):
		# Delete videos used
		for vid in self.downloaded:
			temp = "{}{}.*".format(config.video_path, vid.title)
			for file in glob.glob(temp):
				os.remove(file)
				logger.debug("Deleting %s", file)

def combine_videos(vids, name):

	files = ['{}{}.mpg'.format(config.video_path, x.title) for x in vids]
	videos = "|".join(files)
	
	# Changed the codec of the video
	# to H264 and AAC audio
 	command = [
 		config.ffmpeg_bin, '-y', '-i', 
 		'concat:%s' % (videos,), 
 		'-c:v', 'libx264',
 		'-c:a', 'aac',
 		'-preset', 'fast',
 		'-crf', '18',
 		'%s%s.mp4' % (config.video_path, name)
 	]

 	return True	if call(command) == 0 else False

def convert_video(vid, conf):

	result = None

	description = fix_description(vid.description)

	cfilter  = "\"[0:v]scale=%s[scaled];" % conf.scale_1
	cfilter += "[1:v]scale=%s[scaled2];" % conf.scale_2
	cfilter += " [scaled][scaled2]overlay=(main_w-overlay_w)/2:0:shortest=1[res];"
	cfilter += " [res]drawtext=fontfile=%s" % config.font_path + conf.font
	cfilter += ":text='%s' :x=%s: y=%s:" % (description, conf.text_x, conf.text_y)
	cfilter += " fontsize=%s:fontcolor=%s" % (conf.font_size, conf.font_color)
	cfilter += ":box=1:boxcolor=%s[out]\"" % conf.font_background_color

	# Horrible magic ffmpeg command
	command = [
		config.ffmpeg_bin, 
		'-loop', '1', 
		'-i', '%s%s' % (config.image_path, conf.image), 
		'-i', '%s%s.mp4' % (config.video_path, vid.title), 
		'-filter_complex', 
		cfilter,
		'-map', '"[out]"', 
		'-map', '1:a',
		'-y', '-qscale:v', '1',
		'%s%s.mpg' % (config.video_path, vid.title)
	]

	# Ugly join call should not be used
	if call(' '.join(command), shell=True) == 0:
		result = vid

	return result

def fix_description(description):

	pattern  = r'((?:((?<!\w)[\\/]?w[\\/]?|'
	pattern += r'[avtc]c|ib|[yd]t)'
	pattern += r'[\:\|\/\\\-\_\s\!]*)?'
	pattern += r'(?:[\:\|\/\\\&\-\_\,\+\s]*))*'
	pattern += r'(\[[^\[\]]*\]|\@\w+)(\'\w+)?'
	
	# Remove the ugly vine slang
	description = re.sub(pattern, '', description, flags=re.IGNORECASE)

	pattern  = r'[\{\(\[][\s\W]*[\}\)\]]|'
	pattern += r'([\|\'\"])[\s\W]*\1'
	
	# Remove the empty enclose symbols
	description = re.sub(pattern, '', description)

	# Remove the extra white spaces
	description = re.sub(r'\s{2,}', ' ', description)
	
	description = description.replace("'", "\'\\\\\\\\\\\'\'")
	description = description.replace('"', '\\\"')
	description = description.replace(':', '\\:')

	if len(description) > 90:
		description = u'{}...'.format(description[:90])

	return description

# I should change this
def change_group(name):
	command = ['chgrp', config.WEB_GROUP, config.video_path + '%s.mp4' % name]
	call(command)

# Not completed

if __name__ == '__main__':
	main()