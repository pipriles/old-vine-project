#!/usr/bin/env python

import MySQLdb as mysql
import codecs

# Without this doesn't work :(
codecs.register(lambda name: codecs.lookup('utf8') if name == 'utf8mb4' else None)

class Database:
	""" Database class object """
	def __init__(self, host='localhost', user='vine_app', password='supervine', db='vine'):
		self.host = host
		self.user = user
		self.password = password
		self.db = db
	
	def connect_db(self):
		db = mysql.connect(self.host, self.user, self.password, self.db, charset='utf8mb4')
		db.set_character_set('utf8mb4')
		return db
