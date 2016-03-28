#!/usr/bin/env python

import vine
from multiprocessing import Process, Pool
from time import sleep, time

def update_timer(job):
	# 1 minute less to timer
	dbc.execute("UPDATE job SET next_scrape = %s, next_combine = %s WHERE job.id = %s" % \
		(
			job[3] if job[4] <= 1 else job[4] - 1,	# Check scrape time left
			job[6] if job[7] <= 1 else job[7] - 1,	# Check combine time left
			job[0]
		)
	)

def scrape_time(job, cp, cs):
	
	if job[4] - 1 <= 0:
		#print "\n Scraped started\n"
		dbc.execute("UPDATE job SET job.status = CASE WHEN job.status = 0 THEN 1 ELSE 3 END WHERE job.id = %s" % job[0])
		p = Process(name="%s-scr" % job[0], target=vine.vineData_SQL, args=(job,))

		# Add a process to current scrapes
		cs[job[0]] = (cs[job[0]] + 1) if cs.get(job[0]) else 1
		cp.append(p)
		
		# Parallel scrape (No duplicate in same job)
		p.start()

def compilation_time(job, cp, cs, wait_p):

	if job[7] - 1 <= 0 or wait_p.get(job[0]) != None:
		
		# If there is scrapes running for the same job
		# And there is compilations proccessing
		if cs.get(job[0]) or len(wait_p) > 1:

			# Add one to the pend process
			if job[7] - 1 <= 0: 
				wait_p[job[0]] = (wait_p[job[0]] + 1) if wait_p.get(job[0]) else 1

		else:
			# Combine top n videos
			#print "\n Compilation started\n"
			dbc.execute("UPDATE job SET job.status = CASE WHEN job.status = 0 THEN 2 ELSE 3 END WHERE job.id = %s" % job[0])
			p = Process(name="%s-com" % job[0], target=vine.combine_top_videos, args=(job,))
			cp.append(p)

			# Horrible conditional block
			if wait_p.get(job[0]):
				wait_p[job[0]] = wait_p[job[0]] - 1
				if wait_p[job[0]] < 1:
					del wait_p[job[0]]

			p.start() # Start compilation process

def del_zombies(cp, cs):
	# Join the darkside (good practice)
	for x in xrange(len(cp)):

		temp = cp.pop(0)
		# Check for zombie process
		if not temp.is_alive():	
			temp.join()
			i = int(temp.name.split("-")[0])

			# if is a scrape process
			if "scr" in temp.name:
				#print "\n Scraped finished\n"
				dbc.execute("UPDATE job SET job.status = CASE WHEN job.status = 3 THEN 2 ELSE 0 END WHERE job.id = %s" % i)
				cs[i] -= 1
				if cs[i] == 0: 
					del cs[i]
			else:
				dbc.execute("UPDATE job SET job.status = CASE WHEN job.status = 3 THEN 1 ELSE 0 END WHERE job.id = %s" % i)
				#print "\n Compilation finished"
		else:
			cp.append(temp)

if __name__ == '__main__':

	cp = []			# List of processes
	cs = {}			# Current scrapes
	wait_q = {}		# Wait queue

	db = vine.Database().connect_db()
	dbc = db.cursor()

	try:
		while True:
			now = time()
			dbc.execute("SELECT script_status FROM settings")
			status = dbc.fetchone()[0]
			#print status

			if status == 1:
				sql = "SELECT * FROM job"
				dbc.execute(sql)

				# Check all the jobs
				jobs = dbc.fetchall()
				for job in jobs:

					#print job
					update_timer(job)

					scrape_time(job, cp, cs)
					compilation_time(job, cp, cs, wait_q)

			# Check for alive zombies :)
			del_zombies(cp, cs)
			db.commit()	# Update timer (for real)

			# Wait 1 minute	
			#print "\n Wait moment\n ", cp, "\n"
			sleep(60 - int(time() - now))

	except KeyboardInterrupt:
		for p in cp: p.join()
		
	db.commit()
	db.close()
