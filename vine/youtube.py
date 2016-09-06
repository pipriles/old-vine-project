#!/usr/bin/python2

import httplib 		# For exceptions
import httplib2
import datetime

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2Credentials
from oauth2client.client import EXPIRY_FORMAT

from database import Database

CLIENT_ID = "892925157774-u9l5kehvb7fgnqnb86rdoj0a3ek6ktd0.apps.googleusercontent.com"
CLIENT_SECRET = "k52sVi1FQCr4rj-NOICvSDDZ"
TOKEN_URI = "https://accounts.google.com/o/oauth2/token"

YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

PRIVACY_STATUS = ("public", "private", "unlisted")

class YouTubeData:

	def __init__(self, user, db):
		self.db = db
		self.user_id = user

	def get_fucking_data(self):
		""" Gets the fucking data from a user
		
		This data has the same order as the parameters for
		OAuth2Credentials constructor from the google api

		Returns:
			A tuple with the user information

		Notes:
			Remember to close your database connection
		"""
		
		sql = "SELECT * FROM account WHERE account.user = '%s';"
		result = self.db.query(sql % user)
		token = result.fetchone()

		access_token = token[1]
		refresh_token = token[4]
		token_expiry = datetime.datetime.strptime(token[3], EXPIRY_FORMAT)

		print token

		return (access_token, CLIENT_ID, CLIENT_SECRET,
			refresh_token, token_expiry, TOKEN_URI, None,)

	def update_credentials(self, creds):

		sql = """ 
			UPDATE account SET
				access_token = '',
				token_expiry = '',
				WHERE
					user = '';
		"""

		token_info = creds.access_token, 
			creds.token_expiry.strftime(EXPIRY_FORMAT),

		result = db.query(sql % token_info)
		db.commit()


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
	credentials = OAuth2Credentials(*data.get_fucking_data())

	print "1 -->", credentials.access_token
	print "  -->", credentials.token_expiry

	http = credentials.authorize(httplib2.Http())
	
	# Refresh access token if expired
	print credentials.access_token_expired

	if credentials.access_token_expired:
		credentials.refresh(http)
		data.update_credentials(credentials)

	print "2 -->", credentials.access_token
	print "  -->", credentials.token_expiry

	return build(YOUTUBE_API_NAME, YOUTUBE_API_VERSION,
		credentials=credentials)


def init_upload(youtube, opt):
	
	# opt (Options for the video)

	tags = None
	if opt.keywords:
		tags = opt.keywords.split(",")

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
		print "Uploading video..."
		status, result = request.next_chunk()
		
		if 'id' in result:
			print "Watch video in: http://www.youtube.com/watch?v=%s" % result['id']
		else:
			exit("Bad response :(")

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