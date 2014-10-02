#!/usr/bin/env python

def representsInt(s):
	try: 
		int(s)
		return True
	except ValueError:
		return False

def representsFloat(s):
	try:
		float(s)
		return True
	except ValueError:
		return False