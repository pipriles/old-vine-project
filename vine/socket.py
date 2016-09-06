#!/usr/bin/python2

# This module will listen for commands and execute them
# This has a really bad design
# I will modify this
# REALLY

class Socket_Process:
	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	status = Value('i', 1)
	lp = None

	def __init__(self):
		# Listen to socket
		call(['mkdir', '-p', SOCKET_FOLDER])
		self.check_socket()
		self.s.bind(SOCKET_PATH)
		self.s.listen(1)
		call(['./configure.sh'])

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
		if os.path.exists(SOCKET_FOLDER):
			try:
			    os.unlink(SOCKET_PATH)
			except OSError:
			    if os.path.exists(SOCKET_PATH):
			        raise