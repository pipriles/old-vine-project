#!/usr/bin/env python2

# This is the main script, the omnipotent,
# the mind behind all this

# Notes:
# - Maybe some unnecessary modules
# - Should i make a class for all this?
# - Process can combine videos at the same time for different jobs
# - I have to make a function that checks that there are no already running (REMEMBER)
# - I think i will add the scrapes and combines queues to the job class

import vine
from time import sleep, time
from multiprocessing import Process
import socket
import os

# main script

running = []		# Running processes
held_scrapes = []	# Scrapes waiting
held_combines = []	# Combines waiting

def initialize():
	global jobs
	global sp
	try:
		# Listen to socket
		sp = vine.Socket_Process()
		sp.start()
		print 'Listening to socket:', SOCKET_PATH

		db = vine.Database()
		jobs = vine.JobData(db)
		db.close()

	except Exception, e:
		raise e:

def end_with_this():
	sp.stop()
	for p in running: 
		p.join()

def run_scrape(jobs):

	for x in jobs:
		x.can_scrape()

	for x in jobs:
		if x.can_scrape():
			p = vine.ScrapeProcess(x)
			running.append(p)
			p.start()
		else:
			if not x in held_scrapes:
				held_scrapes.append(x)

def run_combine(jobs):

	for x in jobs:
		if x.can_combine():
			p = vine.CombineProcess(x)
			running.append(p)
			p.start()
		else:
			if not x in held_combines:
				held_combines.append(x)

def process_jobs(jobs):
	run_scrape(jobs.need_scrape())
	run_combine(jobs.need_combine())

def clean_zombies():

	count = len(running)
	for x in xrange(count):
		p = running.pop(0)
		if not p.is_alive():
			p.join()
		else:
			running.append(p)

def run_idle_jobs():

	count = len(held_scrapes)
	for x in xrange(count):
		x = held_scrapes.pop(0)
		if x.can_scrape():
			p = vine.ScrapeProcess(x)
			running.append(p)
			p.start()
		else:
			held_scrapes.append(x)

	count = len(held_combines)
	for x in xrange(count):
		x = held_combines.pop(0)
		if x.can_combine():
			p = vine.CombineProcess(x)
			running.append(p)
			p.start()
		else:
			held_combines.append(x)

Status = True

def main():
	try:
		initialize()
		while True:

			if Status: process_jobs()
			clean_zombies()
			run_idle_jobs()

			sleep(1)

	finally:
		end_with_this()


if __name__ == '__main__':
	main()