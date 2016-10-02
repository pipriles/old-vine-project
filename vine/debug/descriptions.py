#!/usr/bin/env python2

import os
import sys
import argparse

# Path to the vine module
path = os.path.realpath(__file__)
for x in range(3): 
	path = os.path.dirname(path)
sys.path.insert(0, path)

import vine

def main():
	db = vine.database.Database()
	db.connect()

	sql = "SELECT title FROM vine WHERE 1"
	for x in db.query(sql):
		print x[0].__repr__()

if __name__ == '__main__':
	main()