#!/usr/bin/env python2

# This module will listen for commands, interpret
# them and make the script change its flow

import os
import re
import errno
import socket
import logging
import time
import config

from threading import Thread, Lock

import tasker

logger = logging.getLogger(__name__)

# Should this class be in the tasker?
# (This is not a task)

class SocketProcess(Thread):

	def __init__(self, id="Listen_Process", sock=None):
		super(SocketProcess, self).__init__(name=id)
		self._sock = ListenSocket()

	def run(self):
		logger.info('Listening to socket...')
		while self._sock.alive():
			try:
				self._sock.wait()
				msg = self._sock.recv()
				logger.debug('-> Message: %s', msg)
				self.interpret_msg(msg)
			except socket.error, e:
				logger.debug('Broken pipe!')
			except Exception as e:
				logger.critical(e)
				logger.critical("Socket process: %s", type(e).__name__)
				self.stop()
			finally:
				self._sock.disconnect()

	def toggle_status(self):
		logger.debug('SE ESTA LLAMANDO A TOGGLE STATUS')
		new_status = not config.SCRIPT_STATUS
		config.SCRIPT_STATUS = new_status

	def get_status(self):
		status = "1" if config.SCRIPT_STATUS else "0"
		self._sock.send(status)

	def refresh_jobs(self):
		config.DIRTY_JOBS = 1

	def not_valid(self):
		self._sock.send('NOT VALID')

	def reconvert_vid(self, vid):
		logger.debug('Request combine for %s', vid)
		tasker.request_combine(vid)

	def default(self, msg):

		match = re.search('^COMBINE (\d+)$', msg)
		if match:
			vid = match.group(1)
			self.reconvert_vid(vid)
		else:
			self.not_valid()

	def interpret_msg(self, msg):
		msg = msg.upper()
		if msg == 'CHANGE STATUS':
			self.toggle_status()
		elif msg == 'GET STATUS':
			self.get_status()
		elif msg == 'REFRESH JOBS':
			self.refresh_jobs()
		else:
			self.default(msg)

	def stop(self):
		self._sock.close()
		# Should i call terminate?

class ListenSocket:
	
	def __init__(self, sock=None):
		clear_socket_path()
		self._sock = socket.socket(
			socket.AF_UNIX, socket.SOCK_STREAM)
		self._sock.bind(config.SOCKET_PATH)
		self._sock.listen(config.MAX_CLIENTS)
		os.chmod(config.SOCKET_PATH, 0o0777)
		self._conn = None
		self.lock = Lock()

	def alive(self):
		with self.lock:
			alive = False if self._sock is None else True
		return alive

	def wait(self):
		logger.info('Waiting for connection...')
		self._conn = self._sock.accept()[0]

	def recv(self, buff=1024):
		if self._conn:
			return self._conn.recv(buff)
		else:
			return ''

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
			with self.lock:
				self._sock.shutdown(socket.SHUT_RDWR)
				self._sock.close()
				self._sock = None
			clear_socket_path()

	def __del__(self):
		self.close()

# Helpers
def clear_socket_path():
	if not os.path.exists(config.SOCKET_FOLDER):
		os.makedirs(config.SOCKET_FOLDER)
		os.chmod(config.SOCKET_FOLDER, 0o0777)
	else:
		unlink(config.SOCKET_PATH)

def unlink(path):
	try:
		os.remove(path)
	except OSError as e:
		if e.errno != errno.ENOENT:
			raise

if __name__ == '__main__':

	# Listener Test
	logging.basicConfig(format="%(message)s", level=logging.DEBUG)

	test = SocketProcess()
	test.start()

	try: 
		while 1: pass # Butt loop
	except:
		test.stop()
		test.join()
		exit('- Finished main process')