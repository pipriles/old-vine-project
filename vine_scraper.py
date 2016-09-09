#!/usr/bin/env python2

# This is the main script, the omnipotent,
# the mind behind all this

# Notes:
# - Should i call the database in the constructor?
# - What about the socket process?
# - There are some variables with ugly names
# - Maybe some unnecessary modules
# - What about the job, should i make a class?
# - This thing of timer sucks, will change it
# - Ugly code, clean_zombies plz, i can't even see it
# - Should i keep the connection to the database open?
# - Should i make a class for all this?

import vine
from time import sleep, time
from multiprocessing import Process, Value
import socket
import os

class Vine_Bot:
	
	def __init__(self):
		# Connect to database
		self.db = vine.Database()
		self.db.connect()
		print 'Connected to database: vine'

		# Listen to socket
		self.sp = Socket_Process()
		self.sp.start()
		print 'Listening to socket:', SOCKET_PATH

		self.cp = []		# List of processes
		self.cs = {}		# Current scrapes
		self.wait_q = {}	# Wait queue

	def __del__(self):
		self.close()

	def process_jobs(self):
		
		for job in self.get_jobs():
			
			print job 	# Just debug things

			self.update_timer(job)
			self.run_scrape(job)
			self.run_convert(job)

		self.db.commit()	# Update timer (for real)

	def run_scrape(self, job):
		if job[5] - 1 <= 0:
			print "\n Started to scrape \n"	# Just debug things

			sql = "UPDATE job SET job.status = CASE WHEN job.status = 0 THEN 1 ELSE 3 END WHERE job.id = %s"
			self.dbc.execute(sql % job[0])
			self.db.commit()

			p = Process(name="%s-scr" % job[0], target=vine.vineData_SQL, args=(job,))
			self.cp.append(p)

			# Add a process to current scrapes
			self.cs[job[0]] = (self.cs[job[0]] + 1) if self.cs.get(job[0]) else 1
			
			p.start()	# Parallel scrape (No duplicate in same job)

	def run_convert(self, job):
		if job[8] - 1 <= 0 or self.wait_q.get(job[0]) != None:

			# If there is scrapes running for the same job
			# or there is compilations proccessing
			if self.cs.get(job[0]) or len(self.wait_q) > 1:

				# Add one to the pend process
				if job[8] - 1 <= 0: 
					self.wait_q[job[0]] = (self.wait_q[job[0]] + 1) if self.wait_q.get(job[0]) else 1
			else:
				# Combine top n videos
				print "\n Compilation started\n"	# Just debug things

				sql = "UPDATE job SET job.status = CASE WHEN job.status = 0 THEN 2 ELSE 3 END WHERE job.id = %s"
				self.dbc.execute(sql % job[0])
				self.db.commit()
				
				p = Process(name="%s-com" % job[0], target=vine.combine_top_videos, args=(job,))
				self.cp.append(p)

				# Horrible conditional block
				if self.wait_q.get(job[0]):
					self.wait_q[job[0]] = self.wait_q[job[0]] - 1
					if self.wait_q[job[0]] < 1:
						del self.wait_q[job[0]]

				p.start() # Start compilation process

	def clean_zombies(self):
		for x in xrange(len(self.cp)):

			temp = self.cp.pop(0)
			if not temp.is_alive():	
				
				temp.join()
				# Join the darkside (good practice)
				
				print temp.name 	# Just debug things
				i = int(temp.name.split("-")[0])

				# if is a scrape process
				if "scr" in temp.name:
					sql = "UPDATE job SET job.status = CASE WHEN job.status = 3 THEN 2 ELSE 0 END WHERE job.id = %s"
					print "\n Scrape finished \n"	# Just debug things
					self.cs[i] -= 1
					if self.cs[i] == 0: 
						del self.cs[i]

				else:
					sql = "UPDATE job SET job.status = CASE WHEN job.status = 3 THEN 1 ELSE 0 END WHERE job.id = %s"
					print "\n Compilation finished \n"	# Just debug things

				self.dbc.execute(sql % i)
				self.db.commit()

			else:
				self.cp.append(temp)

	def start(self):
		while True:
			now = time()
			if self.sp.status.value: 
				bot.process_jobs()

			bot.clean_zombies()	# Check for alive zombies :)

			print "\n Status:", self.sp.status.value
			print " Wait moment \n ", self.cp, "\n"	# Just debug things
			sleep(5 - int(time() - now))			# Wait some time

	def close(self):
		self.sp.close()
		for p in self.cp: p.join()
		if self.db.open:
			self.db.commit()
			self.db.close()

def main(args):

	while True:
		now = time()
		
		

		sleep(1 - int(time() - now))

if __name__ == '__main__':
	main(args)