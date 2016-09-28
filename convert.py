#!/usr/bin/env python2

from subprocess import call
from collections import namedtuple
from vine import config 
import re

def convert_video(vid, conf):

	result = None

	description = fix_description(vid.description)

	cfilter  = "\"[0:v]scale=%s[scaled];" % conf.scale_1
	cfilter += "[1:v]scale=%s[scaled2];" % conf.scale_2
	cfilter += " [scaled][scaled2]overlay=(main_w-overlay_w)/2:0:shortest=1[res];"
	cfilter += " [res]drawtext=fontfile=%s" % config.font_path + conf.font
	cfilter += ":text='%s' :x=%s: y=%s:" % (description, conf.text_x, conf.text_y)
	cfilter += " fontsize=%s:fontcolor=%s" % (conf.font_size, conf.font_color)
	cfilter += ":box=1:boxcolor=%s[out]\"" % conf.font_background_color

	# Horrible magic ffmpeg command
	command = [
		config.ffmpeg_bin, 
		'-loop', '1', 
		'-i', config.image_path + '%s' % conf.image, 
		'-i', config.video_path + "%s.mp4" % (vid.title), 
		'-filter_complex', 
		cfilter,
		'-map', '"[out]"', 
		'-map', '1:a',
		'-y', '-qscale:v', '1',
		config.video_path + '%s.mpg' % vid.title
	]

	print ''
	print 'DESCRIPTION: ' + description
	print ' '.join(command)
	print ''

	if call(' '.join(command), shell=True) == 0:
		result = vid

	return result

def fix_description(description):

	pattern  = r'[^\w\d]?vc[^\w\d]?|'
	pattern += r'[^\w\d]?ac[^\w\d]?|'
	pattern += r'[^\w\d]?ib[^\w\d]?|'
	pattern += r'[^\w\d]?dt[^\w\d]?|'
	pattern += r'[^\w\d]?[\\/]w\s?|'
	pattern += r'\[[^\[\]]*\]'

	description = re.sub(pattern, '', description, flags=re.IGNORECASE)
	description = ' '.join(description.split())

	description = description.replace("'", "\'\\\\\\\\\\\'\'")
	description = description.replace('"', '\\\"')
	description = description.replace(':', '\\:')

	if len(description) > 90:
		description = u'{}...'.format(description[:90])

	return description

fields = "title "
fields += "description"
Video = namedtuple('Video', fields)

def main():

	import argparse

	parse = argparse.ArgumentParser(description="Convert script")

	parse.add_argument("-d", "--description", help="Description", required=True)
	parse.add_argument("-t", "--title", help="Title", required=True)
	args = parse.parse_args()
	args.description = unicode(args.description, 'utf-8', 'ignore')

	print args.title
	print args.description.__repr__()

	conf = config.Settings(*config.DEFAULT_SETTINGS)
	vid = Video(args.title, args.description)

	convert_video(vid, conf)


if __name__ == '__main__':
	main()