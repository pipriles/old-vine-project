#!/usr/bin/env python2

import logging
import urllib
import os
from multiprocessing import Pool
from functools import partial

import config
from database import Database

# Downloads a videos for each CPU

logger = logging.getLogger(__name__)

def download_videos(videos):

	if not os.path.exists(config.video_path):
		os.makedirs(config.video_path)

	vids = []
	site = urllib.URLopener()
	for x in videos:
		retrieve_vid(site, x.url, "%s.mp4" % x.title)
		vids.append(x)

	return vids

def retrieve_vid(site, url, title):
	logger.info("Downloading %s", title)
	site.retrieve(url, config.video_path + title)

# Test
if __name__ == '__main__':

	import argparse

	parser = argparse.ArgumentParser(description="This module downloads the videos")
	parser.add_argument("--id", default=0, help="Job identifier", metavar='')
	parser.add_argument("--name", default="Test", help="Job name", metavar='')
	parser.add_argument("-u", "--url", default="https://vine.co/popular-now", help="Job url", metavar='')
	parser.add_argument("-s", "--combine-limit", default=3, help="Job combine limit (videos to be downloaded)", metavar='')
	parser.add_argument("--date-limit", default=0, help="Job date limit for the videos", metavar='')

	args = parser.parse_args()

	print args.id
	print args.name
	print args.url
	print args.combine_limit
	print args.date_limit
