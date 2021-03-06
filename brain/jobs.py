#!/usr/bin/env python2

# This module provides an interface
# to interact with job related data

import re
import datetime as dt
import config

from data import props

def to_datetime(t, format=config.DT_FORMAT):
	if t is None:
		t = dt.datetime.now().strftime(format)
	return dt.datetime.strptime(t, format)

def to_string(t, format=config.DT_FORMAT):
	if t is None:
		t = dt.datetime.now()
	return t.strftime(format)

class VineJobs:
	# I should pass the database too
	def __init__(self):
		self.jobs = []

	def __iter__(self):
		return iter(self.jobs)

	def __repr__(self):
		rep = []
		for x in self.jobs:
			rep.append("%s" % x)
		return "\n".join(rep)

	def clear_status(self, db):
		db.query("UPDATE job SET job.status = '000'")

	def init_jobs(self, db):
		self.clear_status(db)
		self.refresh_jobs(db)

	def refresh_jobs(self, db):
		jobs = db.query('SELECT * FROM job')
		self.jobs = [JobObj(*job) for job in jobs]

class JobObj:

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

	def __repr__(self):
		args = (self._id, self.url, 
			self.next_scrape - dt.datetime.now(),
			self.next_combine - dt.datetime.now())

		return "[%s, %s, %s, %s]" % args

	# This maybe should be moved to a class
	def interpret(self, text, func=None):

		if func is None:
			func = lambda x: x

		def _parse_count():
			if self.combine_limit:
				return self.combine_limit
			else:
				return ''

		def _parse_dr(format='s'):
			if self.combine_limit:
				return {
					'h': int(self.combine_limit * 0.0016666),
					'm': int(self.combine_limit * 0.1),
					's': int(self.combine_limit * 6)
				}.get(format, '')
			else:
				return ''

		def _parse_ci(format='m'):
			if self.combine_interval:
				return {
					'd': int(self.combine_interval / 1440),
					'h': int(self.combine_interval / 60),
					'm': int(self.combine_interval),
					's': int(self.combine_interval * 60)
				}.get(format, '')
			else:
				return ''

		def _parse_dl(format='d'):
			if self.date_limit:
				return {
					'd': int(self.date_limit),
					'h': int(self.date_limit * 24),
					'm': int(self.date_limit * 1440),
					's': int(self.date_limit * 86400)
				}.get(format, '')
			else:
				return ''

		def _parser(key):

			# NOTE THAT IF DATE_LIMIT CAN BE NONE IT WILL CRASH
			# This function are very ugly here i will change this

			return str({
				'[COUNT]':		_parse_count(),
				'[D_HOUR]':		_parse_dr('h'),
				'[D_MINUTES]':	_parse_dr('m'),
				'[D_SECONDS]':	_parse_dr('s'),
				'[I_DAYS]':		_parse_ci('d'),
				'[I_HOURS]':	_parse_ci('h'),
				'[I_MINUTES]':	_parse_ci('m'),
				'[I_SECONDS]': 	_parse_ci('s'),
				'[L_DAYS]':		_parse_dl('d'),
				'[L_HOURS]':	_parse_dl('h'),
				'[L_MINUTES]':	_parse_dl('m'),
				'[L_SECONDS]':	_parse_dl('s')
			}.get(key, func(key)))

		keys = re.split(r'(\[[^\[\]]+\])', text)
		new_title = ''.join(map(_parser, keys))
		return dt.datetime.now().strftime(new_title)

	###

	def scrape_time(self):
		present = dt.datetime.now()
		return True if self.next_scrape <= present else False

	def combine_time(self):
		present = dt.datetime.now()
		return True if self.next_combine <= present else False

	def can_scrape(self):
		return self.status[0] == '0' and (
			self.__combining == 0 or self.status[1] == '1')

	def can_combine(self):
		return self.status[:2] == '00'

	def scrape_pending(self):
		return True if self.__scraping > 0 else False

	def combine_pending(self):
		return True if self.__combining > 0 else False

	def hold_scrape(self):
		if self.__scraping < config.MAX_SCRAPE:
			self.__scraping += 1

	def hold_combine(self):
		if self.__combining < config.MAX_COMBINE:
			self.__combining += 1

	def free_scrape(self):
		if self.__scraping > 0:
			self.__scraping -= 1

	def free_combine(self):
		if self.__combining > 0:
			self.__combining -= 1

class JobData:

	def __init__(self, job, db=None):
		self.job = job
		self.db = db

	# Maybe useful in the future
	def refresh_job(self):
		sql = "SELECT * FROM job WHERE job.id = %s"
		dbc = self.db.query(sql, (self.job._id,))
		new = dbc.fetchone()
		self.job.__init__(*new)

	def get_accounts(self):
		sql  = "SELECT"
		sql += " accountID, title, description,"
		sql += " keywords, category, language "
		sql += "FROM job_account "
		sql += "WHERE jobID = %s"
		dbc = self.db.query(sql, (self.job._id,))
		return dbc.fetchall()

	def set_db(self, db):
		self._db = db

	def unset_db(self):
		self._db = None

	def fetch_conf(self):
		return props.fetch_conf(self.job.settings_id, self.db)

	def get_attr(self):
		return (self.job, self.db)

	def _change_status(self, new_status):
		self.job.status = new_status
		sql  = "UPDATE job SET job.status = %s WHERE job.id = %s"
		self.db.query(sql, (new_status, self.job._id))

	def update_scrape_time(self):
		job = self.job
		interval = dt.timedelta(minutes=job.scrape_interval)
		job.next_scrape = dt.datetime.now() + interval

		sql = "UPDATE job SET job.next_scrape = %s WHERE job.id = %s"
		self.db.query(sql, (to_string(job.next_scrape), job._id)) 

	def update_combine_time(self):
		job = self.job
		interval = dt.timedelta(minutes=job.combine_interval)
		job.next_combine = dt.datetime.now() + interval

		sql = "UPDATE job SET job.next_combine = %s WHERE job.id = %s"
		self.db.query(sql, (to_string(job.next_combine), job._id)) 

	def start_scrape(self):
		old_status = self.job.status
		new_status = '1' + old_status[1] + old_status[2]
		self._change_status(new_status)
		self.update_scrape_time()
		self.job.free_scrape()

	def start_combine(self):
		old_status = self.job.status
		new_status = old_status[0] + '1' + old_status[2]
		self._change_status(new_status)
		self.update_combine_time()
		self.job.free_combine()
	
	def start_upload(self):
		old_status = self.job.status
		new_status = old_status[0] + old_status[1] + '1'
		self._change_status(new_status)

	def finish_scrape(self):
		old_status = self.job.status
		new_status = '0' + old_status[1] + old_status[2]
		self._change_status(new_status)

	def finish_combine(self):
		old_status = self.job.status
		new_status = old_status[0] + '0' + old_status[2]
		self._change_status(new_status)

	def finish_upload(self):
		old_status = self.job.status
		new_status = old_status[0] + old_status[1] + '0'
		self._change_status(new_status)