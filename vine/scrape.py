#!/usr/bin/env python2

import requests as rq
import json
import re
import sys

from datetime import datetime as dt
from multiprocessing import Process

from database import Database

class Scraper:
	vinedata = []

	def __init__(self, url, limit="20"):
		self.url = re.split('//|/|\?', url)
		self.limit = limit
		self.vineCount = 0

	def get_VineData(self, size=20):
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
			self.get_Vines(vines)

	# Get vines from a channel like comedy.
	def get_channel(self, category):
		url = "https://vine.co/api/timelines/channels/vanity/" + category
		channelId = rq.get(url).json()["data"]["channel"]["channelId"]
		for vines in self.handy_scroll("https://vine.co/api/timelines/channels/" + str(channelId) + "/popular"):
			self.get_Vines(vines)

	# Get vines from a user playlist
	def get_playlist(self, user):
		print user
		url = "https://vine.co/api/timelines/lists/vanity/" + user +"/posts?size=" + str(self.limit)
		vines = rq.get(url).json()
		self.get_Vines(vines)

	# Get vines from a user timeline
	def get_user(self, user):
		url = "https://vine.co/api/users/profiles/" + user
		userId = rq.get(url).json()["data"]["userId"]
		for vines in self.handy_scroll("https://vine.co/api/timelines/users/" + str(userId)):
			self.get_Vines(vines)

	# Get vines from a tag
	def get_tag(self, tag):
		for vines in self.handy_scroll("https://vine.co/api/timelines/tags/" + tag):
			self.get_Vines(vines)

	# Get vines from a vine search
	def get_search(self, search):
		for vines in self.handy_scroll("https://vine.co/api/posts/search/" + search):
			self.get_Vines(vines)

	# Get vines from the editor picks section
	def get_editor_picks(self):
		for vines in self.handy_scroll("https://vine.co/api/timelines/promoted"):
			self.get_Vines(vines)

	# Get vines from a trend
	def get_trend(self, trend):
		for vines in self.handy_scroll("https://vine.co/api/timelines/lists/vanity/" + trend + "/posts"):
			self.get_Vines(vines)

	# More complex don't touch
	# Get trends
	def get_trends(self):
		for vines in self.handy_scroll("https://vine.co/api/timelines/lists/categories/trends", "?sort=top&"):
			for value in vines['data']['records']:
				self.vineCount += 1
				self.vinedata.append({
					'videoUrl': value["headerPost"]["videoUrl"],
					'description': value["headerPost"]["description"],
					'permalinkUrl': value["headerPost"]["permalinkUrl"][18:],
					'userId': value["headerPost"]["userId"],
					'username': value["headerPost"]["username"],
					'created': value["headerPost"]["created"]
				})

	#

	def writeJson(self, file):
		# Pretty print :)
		file.write(json.dumps(self.vinedata, sort_keys=True, indent=4, separators=(',', ': ')))
	
	# Handles the ajax request for infinite scroll
	def handy_scroll(self, url, other="?"):
		limit = int(self.limit)
		pages = limit / self.size
		page  = 1

		while page <= pages:
			_url = url + other + "page=" + str(page) + "&anchor=&size=" + str(self.size)
			#print _url
			yield rq.get(_url).json()
			page += 1

		rest = limit % self.size
		if rest != 0:
			_url = url + "?page=" + str(page) + "&anchor=&size=" + str(rest)
			#print _url
			yield rq.get(_url).json()

	# Do stuff with this
	def get_Vines(self, vines):
		for value in vines['data']['records']:
			self.vineCount += 1
			self.vinedata.append({
				'videoUrl': value["videoUrl"],
				'description': value["description"],
				'permalinkUrl': value["permalinkUrl"][18:],
				'userId': value["userId"],
				'username': value["username"],
				'loops': value["loops"]["count"],
				'likes': value["likes"]["count"],
				'comments': value["comments"]["count"],
				'reposts': value["reposts"]["count"],
				'created': value["created"]
			})

	# This miss occurs sometimes
	def get_MissedCount(self):
		return int(self.limit) - self.vineCount

class VineData:

	def __init__(self, job, db):
		self.db = db
		self.job = job

	def insert_user(self, user):

		sql  = 'INSERT IGNORE INTO user (id, name, banned)'
		sql += 'VALUES ("%s", "%s", 0)'

		self.db.query(sql % args)

	def insert_vine(self, vine):

		sql  = "INSERT INTO vine (id, url, title, userID, views, likes, comments, reposts, date)"
		sql += "VALUES ("%s", "%s", "%s", "%s", %s, %s, %s, %s, "%s")"
		sql += "ON DUPLICATE KEY UPDATE"
		sql += "views = %s, likes = %s, comments = %s, reposts = %s, dbdate = NOW()"

		self.db.query(sql % vine)

	def link_to_job(self, vine):
		sql  = "INSERT IGNORE INTO vine_job (jobID, vineID, used)"
		sql += "VALUES (%s, %s, 0)"

		args = (self.job._id, vine)
		self.db.query(sql % args)


class ScrapeProcess(Process):

	def __init__(self, job):
		name = "Scrape Process %s" % job._id
		super(ScrapeProcess, self).__init__(name=name)
		self._job = job
		self._db = Database()
		self._db.connect()
		self._job.start_scrape(self._db)

	def run(sef):
		self.scrape_data()
		data = VineData(self._job, self._db)
		for vine in self._scrape.vinedata:
			data.insert_user(args_for_insert_user(vine))
			data.insert_vine(args_for_insert_vine(vine))
			data.link_to_job(vine['permalinkUrl'])
			
		self._db.commit()
		self._db.close()

	def scrape_data(self):
		url = self._job.url
		limit = self._job.scrape_limit
		self._scrape = Scraper(url, limit)

		size = 20	# Default request size
		return self._scrape.get_VineData(size)

# Helpers
def args_for_insert_user(vine):
	# Por que reemplazar las comillas dobles
	# por las comillas simples?
	return (vine['userId'], vine['username'].replace("\"", "\'"))

def args_for_insert_vine(vine):

	# Filter emoji and hashtags
	title = fix(video['description'])

	# Convert the time in a compatible time for the database
	created = dt.strptime(video['created'], "%Y-%m-%dT%H:%M:%S.%f")
	
	return (video['permalinkUrl'], video['videoUrl'], title, 
		video['userId'], video['loops'], video['likes'], video['comments'], 
		video['reposts'], created.strftime('%Y-%m-%d %H:%M:%S'), 
		video['loops'], video['likes'], video['comments'], video['reposts'],)

def vineData_SQL(job, size=20):

	## Setting up encode
	db = Database().connect_db()
	dbc = db.cursor()
	dbc.execute('SET NAMES utf8mb4;')
	dbc.execute('SET CHARACTER SET utf8mb4;')
	dbc.execute('SET character_set_connection=utf8mb4;')
	db.commit()

	vine = VineData(job[2], job[3])
	_url = vine.get_VineData(size)
	# precious data

	for video in vine.vinedata:

		sql = 'INSERT IGNORE INTO user (id, name, banned) VALUES ("%s", "%s", 0)'
		dbc.execute(sql % )
		db.commit()

		sql = """
			INSERT INTO vine (id, url, title, userID, views, likes, comments, reposts, date) 
			VALUES ("%s", "%s", "%s", "%s", %s, %s, %s, %s, "%s") 
			ON DUPLICATE KEY UPDATE
			views = %s, likes = %s, comments = %s, reposts = %s, dbdate = NOW()
		"""

		# Filter emoji and hashtags
		title = fix(video['description'])

		# Convert the time in a compatible time for the database
		created = dt.strptime(video['created'], "%Y-%m-%dT%H:%M:%S.%f")

		dbc.execute(sql % (\
			video['permalinkUrl'], \
			video['videoUrl'], \
			title, \
			video['userId'], \
			video['loops'], \
			video['likes'], \
			video['comments'], \
			video['reposts'], \
			created.strftime('%Y-%m-%d %H:%M:%S'), \
			video['loops'], \
			video['likes'], \
			video['comments'], \
			video['reposts'])
		)
		db.commit()

		# Insert video relation with job
		dbc.executemany("INSERT IGNORE INTO vine_job (jobID, vineID, used) VALUES (%s, %s, 0)", [(job[0], video['permalinkUrl'])])
		db.commit()

	db.close()

def fix(title):
	if "w/" in title: title = title[:title.find("w/")-1]
	elif "W/" in title: title = title[:title.find("W/")-1]
	title = re.sub("[^a-zA-Z 0-9#@]", '', title).split()
	title = ' '.join(filter(lambda x: '#' not in x and '@' not in x, title))
	
	return title

# Test
if __name__ == '__main__':
	
	try:
		url = raw_input("\nEnter a vine url: ")
		limit = raw_input("Enter max num of videos: ")
		size = 20

		vine = Scraper(url, limit)	
		_url = vine.get_VineData(size)
		print "You got ", int(limit) - vine.get_MissedCount()
		print "\n", _url

		# Write the output
		vine.writeJson(sys.stdout)

	except KeyboardInterrupt:
		exit("What's the problem?")
