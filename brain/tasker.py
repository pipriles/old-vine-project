#!/usr/bin/env python2
#
# This module control the 
# tasks running orden and multithreading

import logging
from multiprocessing import Process

import config
import scrape

from combine import VideosSpell
from database import Database

logger = logging.getLogger(__name__)

# I will make a switch to run this 
# either secuencial or parallel

Waiting_Scrapes = []
Waiting_Combines = []
Running_Scrapes = []
Running_Combines = []

class ScrapeProcess(Process):

	def __init__(self, job):
		name = "Scrape Process %s" % job._id
		super(ScrapeProcess, self).__init__(name=name)
		logger.info("Started scrape process")
		self.job = job
		
		self.db = Database()
		self.db.connect()

		self.job.start_scrape(self.db)

	def run(self):
		try:
			scrape.process_job(self.job, self.db)
		finally:
			self.job.finish_scrape(self.db)
			logger.info("Finished scrape process")

class CombineProcess(Process):

	def __init__(self, job):
		name = "Combine Process %s" % job._id
		super(CombineProcess, self).__init__(name=name)
		self.job = job
		
		self.db = Database()
		self.db.connect()

		self.job.start_combine(self.db)

	def run(self):
		cast = VideosSpell(self.db, self.job)
		try:
			# Combine all the videos
			cast.download_videos()
			cast.convert_videos()
			cast.combine_videos()
			cast.apply_changes()
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

def put_scrape(task):
	Waiting_Scrapes.append(task)

def put_combine(task):
	Waiting_Combines.append(task)

def run_scrape(task=None):
	if task is None:
		task = Waiting_Scrapes.pop(0)
	Running_Scrapes.append(task)
	task.start()

def run_combine(task=None):
	if task is None:
		task = Waiting_Combines.pop(0)
	Running_Combines.append(task)
	task.start()

def exec_tasks():
	
	# I always execute the scrape
	# tasks in parallel
	run_scrape()

	if not Running_Combines \
	or config.PARALLEL_MODE:
		run_combine()

def clean_zombies():
	running = Running_Scrapes + Running_Combines
	for x in xrange(len(running)):
		p = running.pop(0)
		if not p.is_alive():
			config.DIRTY_JOBS = 1
			p.join()
		else:
			running.append(p)

def join():
	running = Running_Scrapes + Running_Combines
	map(running, lambda x: x.join)

def try_scrape(job):

	if job.can_scrape():
		if job.scrape_pending() \
		or job.scrape_time():
			p = ScrapeProcess(job)
			put_scrape(p)
	else:
		if job.scrape_time():
			job.hold_scrape()

def try_combine(job):

	if job.can_combine():
		if job.combine_pending() or job.combine_time():
			p = CombineProcess(job)
			put_combine(p)
	else:
		if job.combine_time():
			job.hold_combine()

def process_jobs():
	for job in jobs:
		try_scrape(job)
		try_combine(job)
	if 

def parallel_scrape():
	return not running or config.PARALLEL_MODE
