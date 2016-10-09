#!/usr/bin/env python2

import logging
import urllib
import os
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

def retrieve_vid(site, url, title, path=None):
	if path is None:
		path = config.video_path

	logger.info("Downloading %s", title)
	site.retrieve(url, path + title)

# Test
if __name__ == '__main__':

	import argparse

	parser = argparse.ArgumentParser(description="This module downloads the videos")
	parser.add_argument("-u", "--url", help="Url of video to be downloaded", required=True)
	parser.add_argument("-n", "--name", help="Name of the video", default="sample.mp4", metavar='')
	parser.add_argument("-p", "--path", help="Download path", required=True)
	args = parser.parse_args()

	retrieve_vid(urllib.URLopener(), args.url, args.name, args.path)