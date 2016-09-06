#!/usr/bin/env python2
# This module is getting "better" :/

import MySQLdb as mysql
import codecs

# Without this doesn't work :(
codecs.register(lambda name: codecs.lookup('utf8') if name == 'utf8mb4' else None)

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
		self.db = mysql.connect(self.host, self.user, 
			self.password, self.db_name, charset='utf8mb4')

		self.db.set_character_set('utf8mb4')
	
	def commit(self):
		self.db.commit()

	def close(self):
		self.db.close()

	# Each module makes a query

	def query(self, sql):
		dbc = self.db.cursor()
		dbc.execute(sql)
		return dbc