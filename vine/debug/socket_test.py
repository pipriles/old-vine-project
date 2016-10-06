#!/usr/bin/env python2

import socket
import logging

SOCKET_FOLDER = '/tmp/SCRAPE'
SOCKET_PATH = SOCKET_FOLDER + '/SCRAPE_SOCKET'

def read_cmd():
	msg = raw_input('$ ')
	return " " if msg == "" else msg

def main():
	while 1:
		try:
			s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
			s.connect((SOCKET_PATH))
			msg = read_cmd()
			s.sendall(msg)
			data = s.recv(1024)
			print 'Received', data
		except BaseException, e:
			print "\n", type(e).__name__
			break
		finally:
			s.close()


if __name__ == '__main__':
	main()