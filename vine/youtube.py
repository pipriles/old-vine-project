#!/usr/bin/python2

import httplib 		# For exceptions
import httplib2

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2Credentials

from database import Database

YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

CLIENT_ID = "892925157774-u9l5kehvb7fgnqnb86rdoj0a3ek6ktd0.apps.googleusercontent.com"
CLIENT_SECRET = "k52sVi1FQCr4rj-NOICvSDDZ",
TOKEN_URI = "https://accounts.google.com/o/oauth2/token"

# This function is stupid, bad design
# I'll get over of this shit

def get_fucking_data(user):

	# - Access Token 	=> Database
	# - Client id 		=> 892925157774-u9l5kehvb7fgnqnb86rdoj0a3ek6ktd0.apps.googleusercontent.com
	# - Client secret 	=> k52sVi1FQCr4rj-NOICvSDDZ
	# - Refresh Token 	=> Database
	# - Token expiry 	=> Timestamp - This will be null
	# - Token uri 		=> "https://accounts.google.com/o/oauth2/token"
	# - User agent 		=> null

	db = Database().connect_db()
	dbc = db.cursor()

	dbc.execute("SELECT * FROM account WHERE user = %s;" % user)
	token = dbc.fetchone()

	access_token = token[1]
	refresh_token = token[5]

	return (access_token, CLIENT_ID, CLIENT_SECRET,
		refresh_token, None, TOKEN_URI, None,)


def get_authenticated_service(data):

	credentials = OAuth2Credentials(*data)

	# Refresh access token if expired
	if credentials.access_token_expired():
		credentials.refresh(httplib2.Http())

	return build(YOUTUBE_API_NAME, YOUTUBE_API_VERSION,
		http=credentials.authorize(httplib2.Http()))

def init_upload(youtube, opt)
	
	# opt (Options for the video)

	tags = None
	if opt.keywords:
		tags = opt.keywords.split(",")

	body = {
		snippet: {
			title: opt.title,
			description: opt.description,
			tags: tags,
			categoryId: opt.category
		}
		status: {
			privacyStatus: opt.privacyStatus
		}
	}

	upload_request = youtube.videos().insert(
		part=",".join(body.keys()),
		body=body,
		media_body=MediaFileUpload(opt.file, chunksize=-1, resumable=True)
	)

	upload_video(upload_request)

def upload_video(request):
	result = None
	while result is None:	

		# I should handle exceptions
		print "Uploading video..."
		status, result = upload_request.next_chunk()
		
		if 'id' in result:
			print "Watch video in: http://www.youtube.com/watch?v=%s" % result['id']
		else:
			exit("Bad response :(")

#
# This is a test to upload 
# a video to youtube 

if __name__ == '__main__':

	# Here i find the data for a user
	user = "Me"
	data = get_fucking_data(user)

	youtube = get_authenticated_service(data)
	try:
		init_upload(youtube, options)
	except HttpError, e:
		print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)