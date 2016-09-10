#!/usr/bin/python2

# This module provides an interface
# to interact with job related data

import datetime as dt

DT_FORMAT = "%Y-%m-%d %H:%M:%S"

def to_datetime(t, format=DT_FORMAT):
	return dt.datetime.strptime(t, format)

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

	def need_scrape(self):
		return [x for x in self.jobs if x.need_scrape()]

	def need_combine(self):
		return [x for x in self.jobs if x.need_combine()]

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

	def refresh_job(self, db):
		sql = "SELECT * FROM job WHERE job.id = %s"
		dbc = self.db.query(sql % self._id)
		new = dbc.fetchone()
		self.__init__(*new)

	def need_scrape(self)
		present = dt.datetime.now()
		return True if self.next_scrape <= present else False

	def need_combine(self):
		present = dt.datetime.now()
		return True if self.next_combine <= present else False
		
	def started(self, key, db):
		s = self.status
		code = "%s%s%s"
		new_status = {
			'S': code % ('1', s[1], s[2]),
			'C': code % (s[0], '1', s[2]),
			'U': code % (s[0], s[1], '1')
		}[key]
		self.status = new_status
		sql  = "UPDATE job SET job.status = '%s' WHERE job.id = '%s'"
		db.query(sql % (new_status, self.id))

	def finished(self, key, db):
		s = self.status
		code = "%s%s%s"
		new_status = {
			'S': code % ('0', s[1], s[2]),
			'C': code % (s[0], '0', s[2]),
			'U': code % (s[0], s[1], '0')
		}[key]
		self.status = new_status
		sql  = "UPDATE job SET job.status = '%s' WHERE job.id = '%s'"
		db.query(sql % (new_status, self.id))

	def can_scrape(self):
		return self.status[0] == '0'

	def can_combine(self):
		return True if self.status[:2] == '00' else False
