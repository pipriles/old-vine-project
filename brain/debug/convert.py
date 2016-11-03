#!/usr/bin/env python2

import os
import sys
import re
import argparse

from subprocess import call
from collections import namedtuple

# Path to the vine module
path = os.path.realpath(__file__)
for x in range(3): 
	path = os.path.dirname(path)
sys.path.insert(0, path)

from vine import config 

config.video_path = "{}/{}".format(path, config.video_path)
config.image_path = "{}/{}".format(path, config.image_path)
config.font_path = "{}/{}".format(path, config.font_path)

def convert_video(vid, conf):

	result = None

	description = fix_description(vid.description)

	cfilter  = "\"[0:v]scale=%s[scaled];" % conf.scale_1
	cfilter += "[1:v]scale=%s[scaled2];" % conf.scale_2
	cfilter += " [scaled][scaled2]overlay=(main_w-overlay_w)/2:0:shortest=1[res];"
	cfilter += " [res]drawtext=fontfile='%s'" % (config.font_path + conf.font)
	cfilter += ":text='%s' :x=%s: y=%s:" % (description, conf.text_x, conf.text_y)
	cfilter += " fontsize=%s:fontcolor=%s" % (conf.font_size, conf.font_color)
	cfilter += ":box=1:boxcolor=%s[out]\"" % conf.font_background_color

	# Horrible magic ffmpeg command
	command = [
		config.ffmpeg_bin, 
		'-loop', '1', 
		'-i \'{}{}\''.format(config.image_path, conf.image), 
		'-i \'{}{}.mp4\''.format(config.video_path, vid.title), 
		'-filter_complex', 
		cfilter,
		'-map', '"[out]"', 
		'-map', '1:a',
		'-y', '-qscale:v', '1',
		"\'{}{}.mpg\'".format(config.video_path, vid.title)
	]

	print ''
	print 'DESCRIPTION: ' + description
	print ' '.join(command)
	print ''

	if call(' '.join(command), shell=True) == 0:
		result = vid

	return result

def fix_description(description):

	pattern  = r'((?:((?<!\w)[\\/]?w[\\/]?|'
	pattern += r'[avtc]c|ib|[yd]t)'
	pattern += r'[\:\|\/\\\-\_\s\!]*)?'
	pattern += r'(?:[\:\|\/\\\&\-\_\,\+\s]*))*'
	pattern += r'(\[[^\[\]]*\]|\@\w+)(\'\w+)?'
	
	# Remove the ugly vine slang
	description = re.sub(pattern, '', description, flags=re.IGNORECASE)

	pattern  = r'[\{\(\[][\s\W]*[\}\)\]]|'
	pattern += r'([\|\'\"])[\s\W]*\1'
	
	# Remove the empty enclose symbols
	description = re.sub(pattern, '', description)

	# Remove the extra white spaces
	description = re.sub(r'\s{2,}', ' ', description)
	
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