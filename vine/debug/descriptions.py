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

	parser = argparse.ArgumentParser(description="List descriptions from vine")
	parser.add_argument('--limit', '-l', help="Limit of vines", required=True, default=20, type=int)
	args = parser.parse_args()

	sql = "SELECT title FROM vine WHERE 1 LIMIT {}".format(args.limit)
	for x in db.query(sql):
		print x[0].__repr__()

if __name__ == '__main__':
	main()