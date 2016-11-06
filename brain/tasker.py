#!/usr/bin/env python2
#
# This module control the 
# tasks running orden and multithreading

import logging
from multiprocessing import Process
from threading import Lock

import config
import scrape
import combine
import jobs

from database import Database
from jobs import JobData

logger = logging.getLogger(__name__)

# I will make a switch to run this 
# either secuencial or parallel

Waiting_Scrapes = []
Waiting_Combines = []
Running_Scrapes = []
Running_Combines = []
Recombining = set()

def scrape_msg(func):
	def wrapper(self):
		logger.info("Started scrape process")
		func(self)
		logger.info("Finished scrape process")
	return wrapper

def combine_msg(func):
	def wrapper(self):
		logger.info("Started combine process")
		func(self)
		logger.info("Finished combine process")
	return wrapper

def upload_msg(func):
	def wrapper(self):
		logger.info("Started upload process")
		func(self)
		logger.info("Finished upload process")
	return wrapper

class ScrapeTask(Process):

	def __init__(self, job):
		name = "Scrape Process %s" % job._id
		db = Database()
		db.connect()
		data = jobs.JobData(job, db)
		data.start_scrape()

		super(ScrapeTask, self).__init__(name=name)
		self.data = data

	def run(self):
		self.scrape()

	@scrape_msg
	def scrape(self):
		data = self.data
		scrape.process_job(data.job, data.db)
		data.finish_scrape()

class CombineJobTask(Process):

	def __init__(self, job):
		name = "Combine Process %s" % job._id
		db = Database()
		db.connect()
		data = jobs.JobData(job, db)
		data.start_combine()
		proc = combine.proc_job(db, job)

		super(CombineJobTask, self).__init__(name=name)
		self.data = data
		self.proc = proc

	def run(self):
		self.combine()
		self.upload()

	@combine_msg
	def combine(self):
		self.proc.create_video()
		self.data.finish_combine()

	@upload_msg
	def upload(self):
		self.data.start_upload()
		self.proc.upload_video()
		self.data.finish_upload()

class RecombineTask(Process):

	def __init__(self, vid):
		Recombining.add(vid)

		name = "Recombine Process %s" % vid
		db = Database()
		db.connect()

		super(RecombineTask, self).__init__(name=name)
		self.proc = combine.proc_vid(db, vid)
		self.vid = vid

	def run(self):
		self.recombine()

	@combine_msg
	def recombine(self):
		self.proc.create_video()

	def join(self):
		# Notice is not remove
		Recombining.discard(self.vid)
		super(RecombineTask, self).join()

def request_combine(vid):
	# Should i put a lock here?
	if not vid in Recombining:
		p = RecombineTask(vid)
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
			p = ScrapeTask(job)
			put_scrape(p)
	else:
		if job.scrape_time():
			job.hold_scrape()

def try_combine(job):

	if job.can_combine():
		if job.combine_pending() \
		or job.combine_time():
			p = CombineJobTask(job=job)
			put_combine(p)
	else:
		if job.combine_time():
			job.hold_combine()

def process_jobs(jobs):
	for job in jobs:
		try_scrape(job)
		try_combine(job)

	exec_tasks() 	# Run tasks 
