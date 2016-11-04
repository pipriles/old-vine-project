#!/usr/bin/env python2

# This is the main script, the omnipotent,
# the mind behind all this

# Notes:
# - Should i made a class for this?
# - Process can combine videos at the same time for different jobs

import argparse
import logging
from time import sleep, time

import brain

# Should make a root logger

logger = logging.getLogger(__name__)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter())
logger.addHandler(stream_handler)

db = brain.Database()
sp = brain.SocketProcess()
jobs = brain.VineJobs()

def init_process():
	# Listen to socket
	sp.start()

	# Connect to database
	with db:
		jobs.init_jobs(db)
		
def finish_script():
	sp.stop()
	sp.join()
	brain.tasker.join()
	db.close()

def update_jobs():
	if brain.config.REAL_TIME \
	or brain.config.DIRTY_JOBS:
		with db:
			jobs.refresh_jobs(db)
		brain.config.DIRTY_JOBS = 0

def debug():
	logger.info("\nJobs:\n%s\n", jobs)
	logger.info("Waiting:\n%s\n", brain.tasker.waiting())
	logger.info("Running:\n%s\n", brain.tasker.running())
	logger.debug("Status: %s", brain.config.SCRIPT_STATUS)

def wait(old_time):
	st = brain.config.sleep_time
	interval = time() - old_time
	if interval <= st:
		interval = st - interval
		logger.info("Waiting %s seconds", interval)
		sleep(interval)

# Main logic of the script
def main():
	init_process()
	while True:
		old_time = time()
		debug()
		if brain.config.SCRIPT_STATUS:
			brain.tasker.process_jobs(jobs)
		update_jobs()
		wait(old_time)

def set_from_args(args):
	brain.config.REAL_TIME  = args.real_time
	brain.config.sleep_time = args.sleep_time
	brain.config.ffmpeg_bin = args.ffmpeg_bin

if __name__ == '__main__':

	parser = argparse.ArgumentParser(
		description="Here is where the magic happens")
	
	parser.add_argument("--sleep-time", 
		default=1, 
		type=int, 
		help="Sleep time interval", 
		metavar='')
	
	parser.add_argument("--log-level", 
		default="WARNING", 
		help="Filter log messages", 
		metavar='')

	parser.add_argument("--real-time", 
		default=False, 
		type=bool, 
		help="Update jobs every second, (Just for debug)", 
		metavar='')

	parser.add_argument("--ffmpeg-bin", 
		default="ffmpeg", 
		help="ffmpeg command to be called", 
		metavar='')

	args = parser.parse_args()
	attr = getattr(logging, args.log_level, 30)
	logging.getLogger().setLevel(attr)

	set_from_args(args)
	logger.debug("Video path: %s", brain.config.video_path)
	logger.debug("Image path: %s", brain.config.image_path)
	logger.debug("Font path:  %s", brain.config.font_path)
	logger.debug("Sleep time: %s", brain.config.sleep_time)

	if brain.config.REAL_TIME:
		# In real time the database is always connected
		logger.debug("-> REAL TIME MODE ON")
		db.connect()

	try:
		main()
	except KeyboardInterrupt:
		logger.critical("\nGood bye")
	finally:
		finish_script()