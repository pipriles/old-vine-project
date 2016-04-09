#!/usr/bin/env python

import vine
from time import sleep, time
from multiprocessing import Process, Value
import socket
import os

socket_folder = '/tmp/SCRAPE_SOCKET'
socket_path = socket_folder + '/SCRAPE_SOCKET'

class Vine_Bot:
	cp = []			# List of processes
	cs = {}			# Current scrapes
	wait_q = {}		# Wait queue
	
	def __init__(self):
		
		# Connect to database
		self.db = vine.Database().connect_db()
		self.dbc = self.db.cursor()
		print 'Connected to database: vine'

		# Listen to socket
		self.sp = Socket_Process()
		self.sp.start()
		print 'Listening to socket:', socket_path

	def __del__(self):
		self.close()

	def get_jobs(self):
		self.dbc.execute('SELECT * FROM job')
		self.db.commit()
		return self.dbc.fetchall()

	def process_jobs(self):
		
		for job in self.get_jobs():
			
			print job 	# Just debug things

			self.update_timer(job)
			self.run_scrape(job)
			self.run_convert(job)

		self.db.commit()	# Update timer (for real)

	def update_timer(self, job):
		self.dbc.execute("UPDATE job SET next_scrape = %s, next_combine = %s WHERE job.id = %s" % \
			(
				job[4] if job[5] <= 1 else job[5] - 1,	# Check scrape time left
				job[7] if job[8] <= 1 else job[8] - 1,	# Check combine time left
				job[0]
			)
		)
		# 1 minute less to timer
		# You should call commit here

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

class Socket_Process:
	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	status = Value('i', 1)
	lp = None

	def __init__(self):
		# Listen to socket
		self.check_socket()
		self.s.bind(socket_path)
		self.s.listen(1)

	def __del__(self):
		self.close()

	def start(self):
		if self.lp != None: self.close()
		self.lp = Process(name="listen_process", target=self.listen)
		self.lp.start()

	def stop(self):
		if self.lp != None:
			self.lp.terminate()
			self.lp.join()
		self.lp = None

	def close(self):
		self.stop()
		self.s.close()
		self.check_socket()

	def listen(self):
		try:
			while True:
				print '\n Waiting for a connection \n'
				c, addr = self.s.accept()
				try:
					print '\n Connection from', addr, '\n'
					while True:
						msg = c.recv(1024)
						if not msg: break
						print '\n Message:', msg, '\n'
						msg = msg.lower()
						if msg == 'change status':
							self.status.value = not self.status.value
						elif msg == 'get status':
							c.sendall(str(self.status.value))
				except:
					pass
				finally:
					c.close()
		except KeyboardInterrupt:
			pass

	def check_socket(self):
		if os.path.exists(socket_folder):
			try:
			    os.unlink(socket_path)
			except OSError:
			    if os.path.exists(socket_path):
			        raise

if __name__ == '__main__':
	bot = Vine_Bot()
	try: bot.start()
	except KeyboardInterrupt: 
		print "\nWhy? :("