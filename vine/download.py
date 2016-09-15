#!/usr/bin/env python2

from database import Database
import urllib
import os
from multiprocessing import Pool
from functools import partial

video_path = "/var/www/html/res/videos/"

# Downloads a videos for each CPU

def download_videos(job, videos):

	if not os.path.exists(video_path):
		os.makedirs(video_path)

	pool = Pool()
	download = partial(partial(retrieve_vid, urllib.URLopener()), job) 
	vids = [x for x in pool.map(download, videos) if x is not None]

	pool.close()
	pool.join()

	return vids

def retrieve_vid(site, job, vid):
	print "Downloading %s.mp4" % vid[1]
	try:
		site.retrieve(vid[0], video_path + "%s_%s.mp4" % (vid[1], job[0]))
		
		# Max 80 characters description
		return (vid[1], vid[2])
	except:
		return None

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
