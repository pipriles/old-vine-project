#!/usr/bin/env python2
#
# This module control the 
# tasks running orden and multithreading

import logging
from multiprocessing import Process

import config
import scrape
import combine

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
		
		db = Database()
		db.connect()
		job.start_scrape(db)

		self.job = job
		self.db = db

	def run(self):
		scrape.process_job(self.job, self.db)
		self.job.finish_scrape(self.db)
		logger.info("Finished scrape process")

class CombineProcess(Process):

	def __init__(self, vid=None, job=None):
		name = "Combine Process %s" % job._id
		super(CombineProcess, self).__init__(name=name)

		db = Database()
		db.connect()

		if vid and job is None:
			proc = combine.reconvert_vid(db, vid)
		else:
			proc = combine.create_from_job(db, job)
			job.start_combine(db)

		self.proc = proc
		self.vid = vid
		self.job = job
		self.db = db

	def run(self):
		# Combine all the videos
		self.proc.create_video()
		logger.info("Finished combine process")

		# If autoupload flag is set and job is set
		if self.job:
			self.job.finish_combine(self.db)
			self.job.start_upload(self.db)
			self.proc.upload_video()
			self.job.finish_upload(self.db)
			logger.info("Finished upload process")

def request_combine(vid):
	# I have to handle the case when
	# it request concurrently
	p = CombineProcess(vid=vid)
	put_combine(p)

def put_scrape(task):
	Waiting_Scrapes.append(task)

def put_combine(task):
	Waiting_Combines.append(task)

def run_scrape():
	while Waiting_Scrapes:
		task = Waiting_Scrapes.pop(0)
		Running_Scrapes.append(task)
		task.start()

def run_combine():
	while Waiting_Combines:
		if Running_Combines \
		and not config.PARALLEL_MODE:
			break

		task = Waiting_Combines.pop(0)
		Running_Combines.append(task)
		task.start()

def exec_tasks():
	clean_zombies(Running_Scrapes)
	clean_zombies(Running_Combines)

	# I always execute the scrape
	# tasks in parallel, should i?
	run_scrape()
	run_combine()

def clean_zombies(running):
	for x in xrange(len(running)):
		p = running.pop(0)
		if not p.is_alive():
			config.DIRTY_JOBS = 1
			p.join()
		else:
			running.append(p)
			
def waiting():
	return Waiting_Scrapes + Waiting_Combines

def running():
	return Running_Scrapes + Running_Combines

def join():
	for p in Running_Scrapes : p.join()
	for p in Running_Combines: p.join()

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
		if job.combine_pending() \
		or job.combine_time():
			p = CombineProcess(job=job)
			put_combine(p)
	else:
		if job.combine_time():
			job.hold_combine()

def process_jobs(jobs):
	for job in jobs:
		try_scrape(job)
		try_combine(job)

	exec_tasks() 	# Run tasks 
