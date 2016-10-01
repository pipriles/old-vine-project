#!/usr/bin/env python2

# This module provides an interface for
# Yotube data and functions

import logging
import httplib 		# For exceptions
import httplib2
import datetime as dt
import re

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2Credentials
from oauth2client.client import EXPIRY_FORMAT
from collections import namedtuple

import config
from database import Database

logger = logging.getLogger(__name__)

CLIENT_ID = "892925157774-u9l5kehvb7fgnqnb86rdoj0a3ek6ktd0.apps.googleusercontent.com"
CLIENT_SECRET = "k52sVi1FQCr4rj-NOICvSDDZ"
TOKEN_URI = "https://accounts.google.com/o/oauth2/token"

YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

PRIVACY_STATUS = ("public", "private", "unlisted")

fields  = "user "
fields += "file "
fields += "title "
fields += "description "
fields += "category "
fields += "keywords "
fields += "privacyStatus"

UploadVideo = namedtuple("UploadVideo", fields)

def make_title(title, job):
	
	""" Generate a YouTube video title
		
	This function uses a list of names to generate
	a title for a YouTube video

	Returns:
		The video title as a string
	
	Notes:
		This function also uses the datetime 
		formatting to give the current date
	"""

	def _interpret(var):

		return str({
			'[COUNT]':		job.combine_limit,
			'[D_HOUR]':		int(job.combine_limit * 0.0016666),
			'[D_MINUTES]':	int(job.combine_limit * 0.1),
			'[D_SECONDS]':	6 * job.combine_limit,
			'[L_DAYS]':		job.date_limit,
			'[L_HOURS]':	int(job.date_limit * 24),
			'[L_MINUTES]':	int(job.date_limit * 1440),
			'[L_SECONDS]':	int(job.date_limit * 86400),
			'[I_DAYS]':		int(job.combine_interval / 1440),
			'[I_HOURS]':	int(job.combine_interval / 60),
			'[I_MINUTES]':	job.combine_interval,
			'[I_SECONDS]': 	int(job.combine_interval * 60)
		}.get(var, var))

	words = re.split(r'(\[[\w\d]+\])', title)
	new = ''.join(map(_interpret, words))

	return dt.datetime.now().strftime(new)

def gen_keywords(vids):
	
	tags = {}
	regex = re.compile(r'[\w]{2,}')
	stop_words = _get_stop_words()

	for vid in vids:
		data = regex.findall(vid.description)
		data = [x.lower() for x in data]
		for word in data:
			if word not in stop_words:
				_add_tag(tags, word)

		_add_tag(tags, vid.user.lower())

	return sorted(tags, key=lambda x: (tags[x], len(x)), reverse=True)

def _add_tag(tags, word):
	
	if word in tags:
		tags[word] += 1
	else:
		tags[word] = 1

def _get_stop_words():

	with open(config.WORDS_DIR + "english.txt") as f: 
		stop_words = f.read().split()
	
	return stop_words

class YouTubeData:

	def __init__(self, user, db):
		self._db = db
		self._user = user

	def get_fucking_data(self):

		""" Gets the fucking data from a user
		
		This data has the same order as the parameters for
		OAuth2Credentials constructor from the google api

		Returns:
			A tuple with the user information

		Notes:
			Remember to close your database connection
		"""
		
		sql = "SELECT * FROM account WHERE account.user = %s;"
		result = self._db.query(sql, (self._user,))
		token = result.fetchone()

		access_token = token[1]
		refresh_token = token[4]
		token_expiry = dt.datetime.strptime(token[3], EXPIRY_FORMAT)

		return (access_token, CLIENT_ID, CLIENT_SECRET,
			refresh_token, token_expiry, TOKEN_URI, None,)

	def update_credentials(self, creds):

		""" Update the credentials for the user
		
		Args:
			creds: Credentials object from the google api

		Notes:
			This function just updates the access token
			and the token expiry 

		"""

		sql =  "UPDATE account SET"
		sql += " access_token = %s,"
		sql += " token_expiry = %s "
		sql += "WHERE"
		sql += " user = %s"


		token_info = (creds.access_token, 
			creds.token_expiry.strftime(EXPIRY_FORMAT), 
			self._user)

		result = self._db.query(sql, token_info)
		self._db.commit()


def get_authenticated_service(data):

	""" Gets an authenticated service from 
	the data of a user
	
	Args:
		data: A tuple with the user information

	Returns:
		A YouTube service

	Notes:
		The data tuple has the same order as
		the parameters of the OAuth2Credentials
	"""

	token_info = data.get_fucking_data()
	credentials = OAuth2Credentials(*token_info)

	http = credentials.authorize(httplib2.Http())
	
	# Refresh access token if expired
	if credentials.access_token_expired:
		credentials.refresh(http)
		data.update_credentials(credentials)

	return build(YOUTUBE_API_NAME, YOUTUBE_API_VERSION,
		credentials=credentials)


def init_upload(youtube, opt):

	""" Initialize a upload request
	
	Args:
		youtube: An authenticated youtube service
		opt: The options for the video

	"""

	if isinstance(opt.keywords, basestring):
		tags = opt.keywords.split(",")
	else:
		tags = opt.keywords

	body = {
		'snippet': {
			'title': opt.title,
			'description': opt.description,
			'tags': tags,
			'categoryId': opt.category
		},
		'status': {
			'privacyStatus': opt.privacyStatus
		}
	}

	try:
		upload_request = youtube.videos().insert(
			part=",".join(body.keys()),
			body=body,
			media_body=MediaFileUpload(opt.file, chunksize=-1, resumable=True)
		)
	except IOError:
		exit("You lied to me!")

	upload_video(upload_request)

def upload_video(request):
	
	result = None
	while result is None:	

		# I should handle exceptions
		logger.info("Uploading video...")
		status, result = request.next_chunk()
		
		if 'id' in result:
			logger.info("Watch video in: http://www.youtube.com/watch?v=%s" % result['id'])
		else:
			logger.debug(result)
			logger.warning("Bad response trying to upload the video :(")

def upload_from_args(args, db):
	data = YouTubeData(args.user, db)
	youtube = get_authenticated_service(data)
	try:
		init_upload(youtube, args)
	except HttpError, e:
		logger.error("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
#
# This is a test to upload 
# a video to youtube 

if __name__ == '__main__':

	import argparse
	
	parser = argparse.ArgumentParser(description="This script uploads a video to YouTube")
	parser.add_argument("-u", "--user", required=True, help="YouTube username")
	parser.add_argument("-f", "--file", required=True, help="Video file to upload")
	parser.add_argument("--title", help="Video title", default="Test video", metavar='')
	parser.add_argument("--description", help="Video description", metavar='')
	parser.add_argument("--category", default="22", help="Each category has an id", metavar='')
	parser.add_argument("--keywords", help="Video keywords", metavar='')
	parser.add_argument("--privacyStatus", choices=PRIVACY_STATUS, default=PRIVACY_STATUS[1], 
		help="Privacy status", metavar='')

	args = parser.parse_args()
	if args.keywords:
		tags = opt.keywords.split(",")

	db = Database()
	db.connect()

	# Here i find the data for a user
	data = YouTubeData(args.user, db)
	youtube = get_authenticated_service(data)

	db.close()

	try:
		init_upload(youtube, args)
	except HttpError, e:
		print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)