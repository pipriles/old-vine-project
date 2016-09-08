#!/usr/bin/python2

# This module provides an interface
# to interact with job related data

class JobData:
	
	def __init__(self, db):
		self.db = db
	
	def get_jobs(self, job):
		dbc = self.db.query('SELECT * FROM job')
		return dbc.fetchall()