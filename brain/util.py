#!/usr/bin/env python2

import logging
import re
import unicodedata
import datetime as dt
from string import Formatter

import config

logger = logging.getLogger(__name__)

class Custom(Formatter):

	def __init__(self):
		Formatter.__init__(self)

	def get_value(self, key, args, kwds):
		if isinstance(key, basestring):
			try:
				return kwds[key]
			except KeyError:
				return '?'
		else:
			Formatter.get_value(key, args, kwds)

format = Custom().format

def identity(x): 
	return x

# This maybe should be moved to a class
def parse_title(job, text, func=None):

	""" Generate a YouTube video title
			
	This function uses a list of names to generate
	a title for a YouTube video

	Returns:
		The video title as a string
	
	Notes:
		This function also uses the datetime 
		formatting to give the current date
	"""

	if func is None:
		func = identity

	def _parse_count():
		if job.combine_limit:
			return job.combine_limit
		else:
			return ''

	def _parse_dr(format):
		if job.combine_limit:
			return {
				'h': int(job.combine_limit * 0.0016666),
				'm': int(job.combine_limit * 0.1),
				's': int(job.combine_limit * 6)
			}.get(format, '')
		else:
			return ''

	def _parse_ci(format):
		if job.combine_interval:
			return {
				'd': int(job.combine_interval / 1440),
				'h': int(job.combine_interval / 60),
				'm': int(job.combine_interval),
				's': int(job.combine_interval * 60)
			}.get(format, '')
		else:
			return ''

	def _parse_dl(format):
		if job.date_limit:
			return {
				'd': int(job.date_limit),
				'h': int(job.date_limit * 24),
				'm': int(job.date_limit * 1440),
				's': int(job.date_limit * 86400)
			}.get(format, '')
		else:
			return ''

	def _parser(key):

		if job is None:
			return key

		# NOTE THAT IF DATE_LIMIT CAN BE NONE IT WILL CRASH
		# This function are very ugly here i will change this
		logger.debug(key)
		return str({
			'[COUNT]':		_parse_count(),
			'[D_HOUR]':		_parse_dr('h'),
			'[D_MINUTES]':	_parse_dr('m'),
			'[D_SECONDS]':	_parse_dr('s'),
			'[I_DAYS]':		_parse_ci('d'),
			'[I_HOURS]':	_parse_ci('h'),
			'[I_MINUTES]':	_parse_ci('m'),
			'[I_SECONDS]': 	_parse_ci('s'),
			'[L_DAYS]':		_parse_dl('d'),
			'[L_HOURS]':	_parse_dl('h'),
			'[L_MINUTES]':	_parse_dl('m'),
			'[L_SECONDS]':	_parse_dl('s')
		}.get(key, func(key)))

	logger.debug(text)

	keys = re.split(r'(\[[^\[\]]+\])', text)
	new = ''.join(map(_parser, keys))

	return dt.datetime.now().strftime(new)

def parse_description(job, text, vines):

	""" Generate a YouTube video description

	{user}: Author
	{description}: Description
	{position}: Position
	{time}: Time postion
	{id}: Identifier

	[VINES="FORMAT"]
	
	"""

	format = Custom().format

	def _vine_dict(vid):
		formatter = {
			'user': vid.user,
			'description': vid.description,
			'position': _vine_dict.pos,
			'time': _vine_dict.pos * 6,
			'id': vid.id,
		}
		_vine_dict.pos += 1
		return formatter

	_vine_dict.pos = 0

	def print_vines(key):
		pattern = r'\[\s*VINES(?:=|\s)(?:\'|\")(.*)(?:\'|\")\s*\]'
		match = re.search(pattern, key)
		if match:
			style = match.group(1)
			infos = [format(style, **_vine_dict(vid)) for vid in vines]
			infos = [x.encode('ascii', 'ignore') for x in infos]
			infos.insert(0, '')
			infos.append('')
			return '\n'.join(infos)
		else:
			return key

	return parse_title(job, text, print_vines)

def gen_keywords(vids, extra=None):
		
	# Should i move this to the util module?
	if extra is None:
		extra = []
	elif isinstance(extra, basestring):
		extra = re.split('\s*,\s*', extra)

	def _add_tag(word):
		if word in tags: 
			tags[word] += 1
		else:
			tags[word]  = 1

	tags = {}
	regex_1 = re.compile(r'\w{3,}')
	regex_2 = re.compile(r'[^\w\s]')
	regex_3 = re.compile(r'\s{2,}')
	stop_words = get_stop_words("english")

	for vid in vids:
		user = unicodedata.normalize('NFD', vid.user)
		user = user.encode('ascii', 'ignore')
		description = unicodedata.normalize('NFD', vid.description)
		description = description.encode('ascii', 'ignore')
		data = regex_1.findall(description)
		data = [x[:30].lower() for x in data]
		for word in data:
			if word not in stop_words:
				_add_tag(word)

		user = regex_2.sub(' ', user)
		user = regex_3.sub(' ', user)
		_add_tag(user[:30].lower())

	ret = sorted(tags, key=lambda x: (tags[x], len(x)), reverse=True)
	logger.debug(ret)

	return extra + ret

def get_stop_words(lang):

	path = "{}{}.txt".format(config.WORDS_DIR, lang)
	with open(path) as f: 
		stop_words = f.read().split()

	return stop_words