#!/usr/bin/env python2

import sys
import requests as rq
import datetime as dt

LIMIT = 12
DT_FORMAT = '%Y-%m-%d %H:%M:%S'
INSTA_URL = 'https://www.instagram.com/'
QUERY_URL = 'https://www.instagram.com/query/'
user = None

def scrape_it(url, p):
	r = rq.get(url, params=p)
	return r.json()

if len(sys.argv) > 1:
	user = sys.argv[1]

p = {
	'__a': 1
}

user = str(user)
REQ_URL = INSTA_URL + user

data = scrape_it(REQ_URL, p)['user']
media = data['media']
posts = media['nodes']

print "User: {}".format(data['username'])
print "Id: {}".format(data['id'])
print "Follows: {}".format(data['follows']['count'])
print "Followers: {}".format(data['followed_by']['count'])
print "Posts: {}".format(media['count'])

cont = LIMIT

while posts and cont:
	
	end = media['page_info']['end_cursor']

	for vid in posts:
		if not vid['is_video']:
			continue

		# Request here for each video
		print ""
		VID_URL = "{}p/{}/".format(INSTA_URL, vid['code'])
		r = rq.get(VID_URL, params={
				'__a': 1
			})

		vd = r.json()['media']
		print "Id: {}".format(vd['code'])
		print "User: {}".format(vd['owner']['id'])
		print "Url: {}".format(vd.get('video_url', ''))
		print "Views: {}".format(vd.get('video_views', ''))
		print "Likes: {}".format(vd['likes']['count'])
		print "Comments: {}".format(vd['comments']['count'])
		print u"Caption: {}".format(vd.get('caption', ''))
		
		date = dt.datetime.utcfromtimestamp(vd['date'])
		print "Date: {}".format(date.strftime(DT_FORMAT))

		cont -= 1
		if cont <= 0: break

	# Iterate over media requests
	p['max_id'] = end
	media = scrape_it(REQ_URL, p)['user']['media']
	posts = media['nodes']
