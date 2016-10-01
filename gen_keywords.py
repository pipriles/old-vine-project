#!/usr/bin/env python2

import argparse

from vine import database as db
from vine import video as vd
from vine import youtube as yt

def main():

	parser = argparse.ArgumentParser(description="Gen keywords test code")
	parser.add_argument('-l', '--limit', default=5, type=int, help="Number of videos", metavar='')
	args = parser.parse_args()

	d = db.Database()
	d.connect()
	
	for x in vd.get_videos(d, args.limit):
		print x

if __name__ == '__main__':
	main()