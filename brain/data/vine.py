#!/usr/bin/env python2

# This module manipulates the data of the vine
# videos

# Vine video struct
# I should transform this in a class
# With database methods related

from collections import namedtuple
from datetime import datetime as dt

class VineVideo:

	def __init__(self, url, vid, 
		description, title, user):

		self.url = url
		self.id = vid
		self.description = description
		self.title = title
		self.user = user

class VineData:

	def __init__(self, job, db):
		self.db = db
		self.job = job

	def insert_user(self, user):

		sql  = "INSERT INTO user (id, name, banned)"
		sql += ' VALUES (%s, %s, 0) '
		sql += "ON DUPLICATE KEY UPDATE"
		sql += " id=id"

		_user = args_for_insert_user(user)
		self.db.query(sql, _user)

	def insert_vine(self, vine):

		self.insert_user(vine)

		sql  = "INSERT INTO vine (id, url, title, userID, views, likes, comments, reposts, date)"
		sql += ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) '
		sql += "ON DUPLICATE KEY UPDATE"
		sql += " views = %s, likes = %s, comments = %s, reposts = %s, dbdate = NOW()"

		_vine = args_for_insert_vine(vine)
		self.db.query(sql, _vine)

		self.link_to_job(vine)

	def link_to_job(self, vine):
		sql  = "INSERT INTO vine_job (jobID, vineID, used)"
		sql += ' VALUES (%s, %s, 0) '
		sql += "ON DUPLICATE KEY UPDATE"
		sql += " jobID=jobID"

		args = (self.job._id, vine['permalinkUrl'])
		self.db.query(sql, args)

# Helpers
def args_for_insert_user(vine):
	# Por que reemplazar las comillas dobles
	# por las comillas simples?
	return (vine['userId'], vine['username'].replace("\"", "\'"))

def args_for_insert_vine(vine):

	# Filter unicode 
	title = fix_description(vine)

	# Convert the time in a compatible time for the database
	created = dt.strptime(vine['created'], "%Y-%m-%dT%H:%M:%S.%f")
	
	return (vine['permalinkUrl'], vine['videoUrl'], title, 
		vine['userId'], vine['loops'], vine['likes'], vine['comments'], 
		vine['reposts'], created.strftime('%Y-%m-%d %H:%M:%S'), 
		vine['loops'], vine['likes'], vine['comments'], vine['reposts'],)

def fix_description(vine):

	t = list(vine['description'])
	dif = 0

	entities = sorted(vine['entities'], key=lambda x: x['range'][0])

	for x in entities:
		r = x['range']
		t.insert(r[0]+dif  , '[')
		t.insert(r[1]+dif+1, ']')
		dif += 2

	title = ''.join(t)
	title = ' '.join(title.split())

	# .encode('ascii', 'ignore')
	# Need to filter emoji
	# #hashtags, @users,
	# nonalphanumeric 
	# Not sense descriptions
	# Remove extra whitespaces

	return title
