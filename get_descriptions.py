#!/usr/bin/env python2

import vine

def main():
	db = vine.database.Database()
	db.connect()

	sql = "SELECT title FROM vine WHERE 1"
	for x in db.query(sql):
		print x[0].__repr__()

if __name__ == '__main__':
	main()