#!/usr/bin/env python2

# This is the main script, the omnipotent,
# the mind behind all this

# Notes:
# - Should i made a class for this?
# - Process can combine videos at the same time for different jobs

import argparse
import logging
from time import sleep, time

import vine

logger = logging.getLogger(__name__)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter())
logger.addHandler(stream_handler)

db = vine.Database()
sp = vine.SocketProcess()
jobs = vine.VineJobs()

running = []	# Running processes

def initialize():
	# Listen to socket
	sp.start()

	# Connect to database
	if db.open():
		jobs.init_jobs(db)
	else:
		db.connect()
		jobs.init_jobs(db)
		db.close()

def end_with_this():
	sp.stop()
	sp.join()
	for p in running: 
		p.join()
	db.close()

def run_scrape(job):

	if job.can_scrape():
		if job.scrape_pending() \
		or job.scrape_time():
			p = vine.ScrapeProcess(job)
			running.append(p)
			p.start()
	else:
		if job.scrape_time():
			job.hold_scrape()

def run_combine(job):

	if job.can_combine():
		if job.combine_pending() \
		or job.combine_time():
			p = vine.CombineProcess(job)
			running.append(p)
			p.start()
	else:
		if job.combine_time():
			job.hold_combine()

def process_jobs():
	for job in jobs:
		run_scrape(job)
		run_combine(job)

def clean_zombies():
	for x in xrange(len(running)):
		p = running.pop(0)
		if not p.is_alive():
			vine.config.DIRTY_JOBS = 1
			p.join()
		else:
			running.append(p)

def wait(old_time):
	st = vine.config.sleep_time
	interval = time() - old_time
	if interval <= st:
		interval = st - interval
		logger.info("Waiting %s seconds", interval)
		sleep(interval)

def update_jobs():
	if db.open():
		jobs.refresh_jobs(db)
	else:
		if vine.config.DIRTY_JOBS:
			db.connect()
			jobs.refresh_jobs(db)
			db.close()
			vine.config.DIRTY_JOBS = 0

def debug():
	logger.info('')
	logger.info("Jobs:")
	logger.info(jobs)
	logger.info('')
	logger.info("Running:")
	logger.info(running)
	logger.info('')

def main():
	try:
		initialize()
		while True:
			old_time = time()
			debug()
			# Main logic of the script
			logger.debug("Status: %s", vine.config.SCRIPT_STATUS)
			if vine.config.SCRIPT_STATUS: 
				process_jobs()

			clean_zombies()
			update_jobs()
			wait(old_time)
	except KeyboardInterrupt:
		logger.critical("\nGood bye")
	finally:
		end_with_this()

def set_from_args(args):
	vine.config.sleep_time = args.sleep_time
	vine.config.ffmpeg_bin = args.ffmpeg_bin
	vine.config.video_path = args.video_path
	vine.config.image_path = args.image_path
	vine.config.font_path = args.font_path

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description="Here is where the magic happens")
	parser.add_argument("--sleep-time", default=1, type=int, help="Sleep time interval", metavar='')
	parser.add_argument("--log-level", default="WARNING", help="Filter log messages", metavar='')
	parser.add_argument("--real-time", default=False, type=bool, help="Update jobs every second, (Just for debug)", metavar='')
	parser.add_argument("--video-path", default="./res/videos/", help="Path of the video folder", metavar='')
	parser.add_argument("--image-path", default="./res/images/", help="Path of the image folder", metavar='')
	parser.add_argument("--font-path", default="./res/fonts/", help="Path of the fonts folder", metavar='')
	parser.add_argument("--ffmpeg-bin", default="ffmpeg", help="ffmpeg command to be called", metavar='')

	args = parser.parse_args()
	attr = getattr(logging, args.log_level, 30)
	logging.getLogger().setLevel(attr)

	set_from_args(args)
	logger.debug("Video path: %s", vine.config.video_path)
	logger.debug("Image path: %s", vine.config.image_path)
	logger.debug("Font path:  %s", vine.config.font_path)
	logger.debug("Sleep time: %s", vine.config.sleep_time)

	if args.real_time:
		# In real time the database is always connected
		logger.debug("-> REAL TIME MODE ON")
		db.connect()

	main()