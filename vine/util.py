#!/usr/bin/env python2

from string import Formatter

class Custom(Formatter):

	def __init__(self):
		Formatter.__init__(self)

	def get_value(self, key, args, kwds):
		if isinstance(key, str):
			try:
				return kwds[key]
			except KeyError:
				return '?'
		else:
			Formatter.get_value(key, args, kwds)

format = Custom().format
