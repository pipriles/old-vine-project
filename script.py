#!/usr/bin/env python2

# This is the main script, the omnipotent,
# the mind behind all this

# Notes:
# - Should i made a class for this?
# - Process can combine videos at the same time for different jobs

import vine
from time import sleep, time

sp = vine.SocketProcess()
jobs = vine.JobData()

running = []	# Running processes

def initialize():
	try:
		# Listen to socket
		sp.start()
		print 'Listening to socket...'

		print "Connecting to database..."
		db = vine.Database()
		db.connect()
		jobs.init_jobs(db)
		db.close()
		print "Connected to database!"
	except:
		pass

def end_with_this():
	sp.stop()
	for p in running: 
		p.join()

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
			p.join()
		else:
			running.append(p)

def wait(old_time):
	interval = time() - old_time
	if interval <= 1:
		print "Waiting", 1-interval, "seconds"
		sleep(1 - interval)

Status = True

def main():
	initialize()
	try:
		while True:
			old_time = time()
			if Status: process_jobs()
			clean_zombies()
			wait(old_time)
	except KeyboardInterrupt:
		print ''
	except:
		print "Maybe mysql server is not running..."

	finally:
		end_with_this()


if __name__ == '__main__':
	main()