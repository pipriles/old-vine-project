#!/usr/bin/python2

# This module will listen for commands, interpret
# them and make the script change its flow

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
		self._sock = ListenSocket()
		self.SCRIPT_STATUS = mp.Value('i', 1)

	def run(self):
		while True:
			self._sock.wait()
			try:
				msg = self._sock.recv()
				print '-> Message:', msg	
				self.interpret_msg(msg)()
			finally:
				self._sock.disconnect()

	def toggle_status(self):
		new_status = not self.SCRIPT_STATUS.value
		self.SCRIPT_STATUS.value = new_status

	def get_status(self):
		status = str(self.SCRIPT_STATUS.value)
		self._sock.send(status)

	def stop(self):
		self._sock.close()
		self.terminate()
		# Should i call join?

	def interpret_msg(self, msg):
		msg = msg.upper()
		return {
			'CHANGE STATUS': self.toggle_status,
			'GET STATUS': self.get_status
		}[msg]

class ListenSocket:
	
	def __init__(self, sock=None):
		clear_socket_path()
		self._sock = socket.socket(
			socket.AF_UNIX, socket.SOCK_STREAM)
		self._sock.bind(SOCKET_PATH)
		self._sock.listen(MAX_CLIENTS)
		sp.call([CONFIGURE_SCRIPT])
		self._conn = None

	def wait(self):
		print 'Waiting for a connection \n'
		self._conn = self._sock.accept()[0]

	def recv(self, buff=1024):
		if self._conn:
			msg = self._conn.recv(buff)
		return msg

	def send(self, msg):
		if self._conn:
			self._conn.sendall(msg)

	def disconnect(self):
		if self._conn:
			self._conn.close()
			self._conn = None

	def close(self):
		self.disconnect()
		if self._sock: 
			self._sock.close()
			clear_socket_path()

	def __del__(self):
		self.close()

# Helper
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

	# Listener Test
	
	test = Socket_Process()
	test.start()

	try: 
		while 1: pass # Butt loop
	except:
		exit('\n- Finished main process')