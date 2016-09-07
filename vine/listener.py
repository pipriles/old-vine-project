#!/usr/bin/python2

# This module will listen for commands and execute them
# This has a really bad design
# I will modify this
# REALLY

import os
import socket
import multiprocessing as mp
import subprocess as sp

CONFIGURE_SCRIPT =  '/home/oswald/Documents/Work'
CONFIGURE_SCRIPT += '/Vine Scraper/script/configure.sh'

SOCKET_FOLDER = '/tmp/SCRAPE'
SOCKET_PATH = SOCKET_FOLDER + '/SCRAPE_SOCKET'

MAX_CLIENTS = 1

class Socket_Process(mp.Process):

	def __init__(self, id="Listen_Process", sock=None):
		super(Socket_Process, self).__init__(name=id)
		self._sock = new_socket() if not sock else sock
		self.SCRIPT_STATUS = mp.Value('i', 1)

	def run(self):
		
		while True:

			try:
				print '\n Waiting for a connection \n'
				c, addr = self._sock.accept()
			except:
				exit("\n- Finished socket process")

			try:
				print '\n Connection from', addr, '\n'
				while True:
					msg = c.recv(1024)
					if not msg: break
					print '\n Message:', msg, '\n'
					msg = msg.lower()
					if msg == 'change status':
						self.SCRIPT_STATUS.value = not self.SCRIPT_STATUS.value
					elif msg == 'get status':
						c.sendall(str(self.SCRIPT_STATUS.value))
			finally:
				c.close()
	
	def stop(self):
		_sock.close()
		self.terminate()
		# Should i call join?

def new_socket():
	clear_socket_path()
	sock = socket.socket(
		socket.AF_UNIX, socket.SOCK_STREAM)
	sock.bind(SOCKET_PATH)
	sock.listen(MAX_CLIENTS)
	sp.call([CONFIGURE_SCRIPT])
	return sock

def clear_socket_path():
	if not os.path.exists(SOCKET_FOLDER):
		sp.call(['mkdir', '-p', SOCKET_FOLDER])
	else:
		try:
			os.unlink(SOCKET_PATH)
		except OSError:
			if os.path.exists(SOCKET_PATH):
				raise

if __name__ == '__main__':
	
	sp = Socket_Process()
	sp.start()

	try: 
		while 1: pass # Butt loop
	except:
		exit('\n- Finished main process')