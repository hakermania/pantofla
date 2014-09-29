#!/usr/bin/env python

import sys

def stdout(message, prefix=""):
	sys.stdout.write(prefix+message+"\n")

def stderr(message, prefix="Error: "):
	sys.stderr.write(prefix+message+"\n")