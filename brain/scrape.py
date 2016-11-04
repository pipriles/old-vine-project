#!/usr/bin/env python2

import requests as rq
import json
import re
import sys
import logging

from data import vine

logger = logging.getLogger(__name__)

class Scraper:
	scraped = []

	def __init__(self, url, limit="20"):
		self.url = re.split('//|/|\?', url)
		self.limit = limit
		self.vineCount = 0

	def scrape_data(self, size=20):
		self.vineCount = 0
		self.size = size

		try: i = self.url.index("vine.co")
		except ValueError:
			return "Invalid url"

		site = self.url[i+1]
		if site == "popular-now": self.get_popular()
		elif site == "channels": self.get_channel(self.url[i+2])
		elif site == "playlists": self.get_playlist(self.url[i+2])
		elif site == "tags": self.get_tag(self.url[i+2])
		elif site == "search": self.get_search(self.url[i+2])
		elif site == "editors-picks": self.get_editor_picks()
		elif site == "trends": 
			if self.url[-1] != "trends": 
				self.get_trend(self.url[i+2])
			else: 
				self.get_trends()
		else: 
			if site == "u": 
				self.get_user(self.url[i+2])
			else:
				self.get_user("vanity/" + self.url[i+1])

		return self.url

	# Get vines from the popular page
	def get_popular(self):
		for vines in self.handy_scroll("https://vine.co/api/timelines/popular"):
			self.filter_response(vines)

	# Get vines from a channel like comedy.
	def get_channel(self, category):
		url = "https://vine.co/api/timelines/channels/vanity/" + category
		channelId = rq.get(url).json()["data"]["channel"]["channelId"]
		for vines in self.handy_scroll("https://vine.co/api/timelines/channels/" + str(channelId) + "/popular"):
			self.filter_response(vines)

	# Get vines from a user playlist
	def get_playlist(self, user):
		url = "https://vine.co/api/timelines/lists/vanity/" + user +"/posts?size=" + str(self.limit)
		vines = rq.get(url).json()
		self.filter_response(vines)

	# Get vines from a user timeline
	def get_user(self, user):
		url = "https://vine.co/api/users/profiles/" + user
		userId = rq.get(url).json()["data"]["userId"]
		for vines in self.handy_scroll("https://vine.co/api/timelines/users/" + str(userId)):
			self.filter_response(vines)

	# Get vines from a tag
	def get_tag(self, tag):
		for vines in self.handy_scroll("https://vine.co/api/timelines/tags/" + tag):
			self.filter_response(vines)

	# Get vines from a vine search
	def get_search(self, search):
		for vines in self.handy_scroll("https://vine.co/api/posts/search/" + search):
			self.filter_response(vines)

	# Get vines from the editor picks section
	def get_editor_picks(self):
		for vines in self.handy_scroll("https://vine.co/api/timelines/promoted"):
			self.filter_response(vines)

	# Get vines from a trend
	def get_trend(self, trend):
		for vines in self.handy_scroll("https://vine.co/api/timelines/lists/vanity/" + trend + "/posts"):
			self.filter_response(vines)

	# More complex don't touch
	# Get trends
	def get_trends(self):
		for vines in self.handy_scroll("https://vine.co/api/timelines/lists/categories/trends", "?sort=top&"):
			for value in vines['data']['records']:
				self.vineCount += 1
				self.scraped.append({
					'videoUrl': 	value["headerPost"]["videoUrl"],
					'description': 	value["headerPost"]["description"],
					'permalinkUrl': value["headerPost"]["permalinkUrl"][18:],
					'userId': 		value["headerPost"]["userId"],
					'username': 	value["headerPost"]["username"],
					'created': 		value["headerPost"]["created"],
				})
	#

	def writeJson(self, file):
		# Pretty print :)
		file.write(json.dumps(self.scraped, sort_keys=True, indent=4, separators=(',', ': ')))
	
	# Handles the ajax request for infinite scroll
	def handy_scroll(self, url, other="?"):
		limit = int(self.limit)
		pages = limit / self.size
		page  = 1

		while page <= pages:
			_url = "{}{}page={}&anchor=&size={}".format(url, other, page, self.size)
			logger.debug(_url)
			yield rq.get(_url).json()
			page += 1

		rest = limit % self.size
		if rest != 0:
			_url = "{}?page={}&anchor=&size={}".format(url, page, rest)
			logger.debug(_url)
			yield rq.get(_url).json()

	# Do stuff with this
	def filter_response(self, vines):
		for value in vines['data']['records']:
			self.vineCount += 1
			self.scraped.append({
				'videoUrl': 	value["videoUrl"],
				'description': 	value["description"],
				'permalinkUrl': value["permalinkUrl"][18:],
				'userId': 		value["userId"],
				'username': 	value["username"],
				'loops': 		value["loops"]["count"],
				'likes': 		value["likes"]["count"],
				'comments': 	value["comments"]["count"],
				'reposts': 		value["reposts"]["count"],
				'created': 		value["created"],
				'entities': 	value['entities']
			})

	# This miss occurs sometimes
	def get_missed(self):
		return int(self.limit) - self.vineCount

# Maybe a Scraper parameter?

def process_job(job, db):
	
	data = vine.VineData(job, db)
	vids = Scraper(job.url, job.scrape_limit)
	vids.scrape_data()

	for vid in vids.scraped:
		data.insert_vine(vid)

# Test
if __name__ == '__main__':
	
	import argparse

	parser = argparse.ArgumentParser(description="This is a script to scrape a vine url")
	parser.add_argument("-u", "--url", required=True, help="Url to be scraped", metavar="https://vine.co/...")
	parser.add_argument("-s", "--size", default=10, help="Size of the request")
	args = parser.parse_args()

	scrapy = Scraper(args.url, args.size)	
	_url = scrapy.scrape_data()

	# Write the output
	scrapy.writeJson(sys.stdout)

	print "\nYou got ", int(args.size) - scrapy.get_missed()
	print _url
	