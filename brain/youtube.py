#!/usr/bin/env python2

# This module provides an interface for
# Yotube data and functions

import logging
import httplib 		# For exceptions
import httplib2
import datetime as dt

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2Credentials
from oauth2client.client import EXPIRY_FORMAT
from collections import namedtuple

import config
from database import Database

logger = logging.getLogger(__name__)

# Move this to the config module

PRIVACY_STATUS = ("public", "private", "unlisted")

fields  = "user "
fields += "file "
fields += "title "
fields += "description "
fields += "category "
fields += "keywords "
fields += "privacyStatus"

UploadVideo = namedtuple("UploadVideo", fields)

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

		return (access_token, config.CLIENT_ID, config.CLIENT_SECRET,
			refresh_token, token_expiry, config.TOKEN_URI, None,)

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

	return build(config.YOUTUBE_API_NAME, config.YOUTUBE_API_VERSION,
		credentials=credentials)


def init_upload(youtube, opt):

	""" Initialize a upload request
	
	Args:
		youtube: An authenticated youtube service
		opt: The options for the video
	Notes:
		The keywords request should be 500 bytes long
		Description max length is 4500
	"""

	if isinstance(opt.keywords, basestring):
		tags = opt.keywords[:500].split(",")
	else:
		tags = []
		acum = 0
		for x in opt.keywords:
			acum += len(x)
			if acum + len(tags) < 500:
				tags.append(x)
			else:
				break
		logger.debug(tags)

	body = {
		'snippet': {
			'title': opt.title,
			'description': opt.description[:4500],
			'tags': tags,
			'categoryId': 22 # opt.category (I have to fix it to change the category)
		},
		'status': {
			'privacyStatus': opt.privacyStatus
		}
	}

	try:
		media_file = MediaFileUpload(opt.file, chunksize=-1, resumable=True)
	except IOError:
		exit("You lied to me!")

	url = None
	loop = True
	while loop:
		try:
			# I have to elaborate the request again
			upload_request = youtube.videos().insert(
				part=",".join(body.keys()),
				body=body,
				media_body=media_file)
			url = upload_video(upload_request)
			loop = False
		except HttpError, e:
			logger.debug("HttpError!")
			if e.resp.status == 400 \
			and len(body['snippet']['tags']) != 0:
				del body['snippet']['tags'][-1]
				logger.debug('Deleted one tag')	
			else:
				# Should just log as warning not raise
				loop = False
				raise e

	return url

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

		logger.debug("End of while")

	return result['id']

def upload_from_args(args, db):
	url = None
	data = YouTubeData(args.user, db)
	youtube = get_authenticated_service(data)
	try:
		url = init_upload(youtube, args)
	except HttpError, e:
		logger.error("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
	return url
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