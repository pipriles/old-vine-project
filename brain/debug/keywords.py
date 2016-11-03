#!/usr/bin/env python2

import os
import sys
import argparse

# Path to the vine module
path = os.path.realpath(__file__)
for x in range(3): 
	path = os.path.dirname(path)
sys.path.insert(0, path)

from vine import database as db
from vine import video as vd
from vine import youtube as yt

def main():

	parser = argparse.ArgumentParser(description="Gen keywords test code")
	parser.add_argument('-l', '--limit', default=5, type=int, help="Number of videos", metavar='')
	args = parser.parse_args()

	d = db.Database()
	d.connect()
	
	print "\033c"
	vids = vd.get_videos(d, args.limit)
	for x in vids:
		print x.description

	print ""
	for x in yt.gen_keywords(vids):
		print x

if __name__ == '__main__':

	main()