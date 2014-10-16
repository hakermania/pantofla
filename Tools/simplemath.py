#!/usr/bin/env python

def representsInt(s):
	try: 
		int(s)
		return True
	except ValueError:
		return False

def representsInts(array):
	for value in array:
		if not representsInt(value):
			return False
	return True

def representsFloat(s):
	try:
		float(s)
		return True
	except ValueError:
		return False