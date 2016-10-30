#!/usr/bin/env python2

# This module is a wrapper for the database
# related functions

import MySQLdb as mysql
import codecs
import logging

import config

logger = logging.getLogger(__name__)

# Remember this is old and maybe is not useful now:
# Without this doesn't work :(
codecs.register(lambda name: codecs.lookup('utf8') if name == 'utf8mb4' else None)

DEFAULT_CONFIG = (config.HOST, config.USER, config.PASS, config.DB)

class Database:
	""" Database wrapper object
	
	Here we can change the credentials for the
	connetion to the database.

	Note that if you want to connect to the 
	database you have to call the method connect
	
	"""
	
	def __init__(self, host=None, user=None, passwd=None, db=None):
		args = [host, user, passwd, db]
		self.creds = [args[i] or DEFAULT_CONFIG[i] for i in range(4)]

	def connect(self):
		if not self.open():
			logger.info("Connecting to database...")
			self.db = mysql.connect(*self.creds, charset='utf8mb4')
			self.db.set_character_set('utf8mb4')
			self.db.autocommit(True)
			logger.info("Connected to database!")
	
	def __enter__(self):
		self.connect()
		return self

	def __exit__(self, exc, val, trace):
		self.close()
		return True

	def autocommit(value):
		self.db.autocommit(value)

	def commit(self):
		self.db.commit()

	def rollback(self):
		self.db.rollback()

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

		# For now it will automatically commit
		# Note that is should not commit because
		# this will make we lose the rollback posibility

		return dbc
