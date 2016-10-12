#!/usr/bin/env python2

# This module is a wrapper for the database
# related functions

import MySQLdb as mysql
import codecs
import logging

# Remember this is old and maybe is not useful now:
# Without this doesn't work :(
codecs.register(lambda name: codecs.lookup('utf8') if name == 'utf8mb4' else None)

logger = logging.getLogger(__name__)

class Database:
	""" Database wrapper object
	
	Here we can change the credentials for the
	connetion to the database.

	Note that if you want to connect to the 
	database you have to call the method connect
	
	"""
	
	def __init__(self, host='localhost', user='vine_app', 
			password='supervine', db='vine'):

		self.host = host
		self.user = user
		self.password = password
		self.db_name = db
	
	def connect(self):
		if not self.open():
			logger.info("Connecting to database...")
			self.db = mysql.connect(self.host, self.user, 
				self.password, self.db_name, charset='utf8mb4')
			self.db.set_character_set('utf8mb4')
			logger.info("Connected to database!")
	
	def temporal_use(self, func):
		self.connect()
		func(self)
		self.close()

	def commit(self):
		self.db.commit()

	def open(self):
		if hasattr(self, 'db') and self.db.open:
			return True
		else:
			return False

	def close(self):
		if self.open():
			self.db.commit()
			self.db.close()
			logger.info("Disconnected from database!")

	def __del__(self):
		self.close()

	# Each module makes a query

	def query(self, sql, args=()):
		logger.debug(sql)
		dbc = self.db.cursor()
		dbc.execute(sql, args)
		self.commit()
		return dbc
