#!/usr/bin/env python2

# This module will listen for commands, interpret
# them and make the script change its flow

import os
import socket
import multiprocessing as mp
import subprocess as sp
import logging
import time

CONFIGURE_SCRIPT =  '/home/oswald/Documents/Work'
CONFIGURE_SCRIPT += '/Vine Scraper/script/configure.sh'

SOCKET_FOLDER = '/tmp/SCRAPE'
SOCKET_PATH = SOCKET_FOLDER + '/SCRAPE_SOCKET'

MAX_CLIENTS = 1

logger = logging.getLogger(__name__)

class SocketProcess(mp.Process):

	def __init__(self, id="Listen_Process", sock=None):
		super(SocketProcess, self).__init__(name=id)
		self._sock = ListenSocket()
		self.SCRIPT_STATUS = mp.Value('i', 1)
		self.DIRTY_JOBS = mp.Value('i', 0)

	def run(self):
		logger.info('Listening to socket...')
		while True:
			try:
				self._sock.wait()
				msg = self._sock.recv()
				logger.debug('-> Message: %s', msg)
				self.interpret_msg(msg)()
			except KeyboardInterrupt:
				break
			except socket.error, e:
				logger.critical('Broken pipe!')
			except Exception as e:
				# I should handle the broken pipe
				logger.critical(e)
				logger.critical("Socket process: %s", type(e).__name__)
				break
			finally:
				self._sock.disconnect()

	def toggle_status(self):
		new_status = not self.SCRIPT_STATUS.value
		self.SCRIPT_STATUS.value = new_status

	def __get_status(self):
		status = str(self.SCRIPT_STATUS.value)
		self._sock.send(status)

	def refresh_jobs_on(self):
		self.DIRTY_JOBS.value = 1

	def refresh_jobs_off(self):
		self.DIRTY_JOBS.value = 0

	def need_refresh_jobs(self):
		if self.DIRTY_JOBS.value:
			logger.debug("Script needs to refresh jobs")
			return True
		else:
			return False

	def stop(self):
		self._sock.close()
		self.terminate()
		# Should i call terminate?

	def not_valid(self):
		self._sock.send('NOT VALID')

	def interpret_msg(self, msg):
		msg = msg.upper()
		return {
			'CHANGE STATUS': self.toggle_status,
			'GET STATUS': self.__get_status,
			'REFRESH JOBS': self.refresh_jobs_on
		}.get(msg, self.not_valid)

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
			self._sock.close()
			self._sock = None
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
	logging.basicConfig(level=logging.DEBUG)

	test = SocketProcess()
	test.start()

	try: 
		while 1: pass # Butt loop
	except:
		test.stop()
		test.join()
		exit('\n- Finished main process')