#!/usr/bin/python2

# This module provides an interface
# to interact with job related data

import datetime as dt

DT_FORMAT = "%Y-%m-%d %H:%M:%S"

def to_datetime(t, format=DT_FORMAT):
	return dt.datetime.strptime(t, format)

def to_string(t, format=DT_FORMAT):
	return t.strftime(format)

MAX_SCRAPE = 1
MAX_COMBINE = 1

class JobData:
	
	def __init__(self, db):
		self.jobs = []
		self.clear_status(db)
		jobs = self.db.query('SELECT * FROM job')
		self.jobs = [VineJob(*job) for job in jobs]

	def __iter__(self, db):
		return self.jobs

	def clear_status(self, db):
		db.query("UPDATE job SET job.status = '000'")

	def refresh_jobs(self, db):
		for job in self.jobs:
			job.refresh_job(db)

class VineJob:

	def __init__(self, _id, settings_id, name, url, 
		scrape_limit, scrape_interval, next_scrape, 
		combine_limit, combine_interval, next_combine, 
		date_limit, status, autoupload, formula):
		
		self._id = _id
		self.settings_id = settings_id
		self.name = name
		self.url = url
		self.scrape_limit = scrape_limit
		self.scrape_interval = scrape_interval
		
		if isinstance(next_scrape, dt.datetime):
			self.next_scrape = next_scrape
		else:
			self.next_scrape = to_datetime(next_scrape)

		self.combine_limit = combine_limit
		self.combine_interval = combine_interval
		
		if isinstance(next_combine, dt.datetime):
			self.next_combine = next_combine
		else:
			self.next_combine = to_datetime(next_combine)

		self.date_limit = date_limit
		self.status = status
		self.autoupload = autoupload
		self.formula = formula

		# Private
		self.__scraping = 0
		self.__combining = 0

	def refresh_job(self, db):
		
		sql = "SELECT * FROM job WHERE job.id = %s"
		dbc = self.db.query(sql % self._id)
		new = dbc.fetchone()
		self.__init__(*new)

	def scrape_time(self):
		
		present = dt.datetime.now()
		return True if self.next_scrape <= present else False

	def combine_time(self):
		
		present = dt.datetime.now()
		return True if self.next_combine <= present else False
	
	def change_status(self, new_status, db):
		
		self.status = new_status
		sql  = "UPDATE job SET job.status = '%s' WHERE job.id = '%s'"
		db.query(sql % (new_status, self.id))

	def update_scrape_time(self, db):
		
		interval = dt.timedelta(minutes=self.scrape_interval)
		self.next_scrape = dt.datetime.now() + interval

		sql = "UPDATE job SET job.next_scrape = '%s' WHERE job.id = '%s'"
		db.query(sql % (to_string(self.next_scrape), self.id)) 

	def update_combine_time(self, db):

		interval = dt.timedelta(minutes=self.combine_interval)
		self.next_combine = dt.datetime.now() + interval

		sql = "UPDATE job SET job.next_combine = '%s' WHERE job.id = '%s'"
		db.query(sql % (to_string(self.next_combine), self.id)) 

	def start_scrape(self, db):
		
		new_status = '1' + self.status[1] + self.status[2]
		self.change_status(new_status, db)
		self.update_scrape_time(db)
		self.free_scrape()

	def start_combine(self, db):
		
		new_status = self.status[0] + '1' + self.status[2]
		self.change_status(new_status, db)
		self.update_combine_time(db)
		self.free_combine()
	
	def start_upload(self, db):
		new_status = self.status[0] + self.status[1] + '1'
		self.change_status(new_status, db)

	def finish_scrape(self, db):
		new_status = '0' + self.status[1] + self.status[2]
		self.change_status(new_status, db)

	def finish_combine(self, db):
		new_status = self.status[0] + '0' + self.status[2]
		self.change_status(new_status, db)

	def finish_upload(self, db):
		new_status = self.status[0] + self.status[1] + '0'
		self.change_status(new_status, db)

	def can_scrape(self):
		return self.status[0] == '0'

	def can_combine(self):
		return True if self.status[:2] == '00' else False

	def scrape_pending(self):
		return True if self.__scraping > 0 else False

	def combine_pending(self):
		return True if self.__combining > 0 else False

	def hold_scrape(self):
		if self.__scraping < MAX_SCRAPE:
			self.__scraping += 1

	def hold_combine(self):
		if self.__combining < MAX_COMBINE:
			self.__combining += 1

	def free_scrape(self):
		if self.__scraping > 0:
			self.__scraping -= 1

	def free_combine(self):
		if self.__combining > 0:
			self.__combining -= 1
