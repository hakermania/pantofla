#!/usr/bin/env python

from output import *

pcInterface=''
interfaceFile='/proc/net/route'
transmittedFile='/proc/net/dev'

interfaces=['ppp0', 'ppp1', 'wlp2s0', 'wlp2s1', 'wlan0', 'wlan1', 'eth0', 'eth1', 'enp0s0', 'enp0s1']

interfaceFound=False
oldUp=-1; oldDown=-1



def strInFile(text, fileName):
	try:
		return text in open(fileName).read()
	except:
		stderr("File "+fileName+" cannot be opened!")
		return False

def findInterface():
	global interfaceFound, pcInterface
	for interface in interfaces:
		if(strInFile(interface, interfaceFile)):
			pcInterface=interface
			print interface
			interfaceFound=True
			break

def getTotalUp():
	if not interfaceFound:
		findInterface()
		if not interfaceFound:
			stderr("Interface could not be found")
			return 0
	try:
		print "try1"
		trFile=open(transmittedFile, 'r')
		print "try1.5"
		infoLine=''
		for line in trFile:
			print "try2"
			line=line.rstrip()
			line=line.lstrip()
			if(not line.startswith(pcInterface)):
				continue
			else:
				#line found
				infoLine=line
				break

		trFile.close()
		print infoLine.split()
		return int(infoLine.split()[9])
	except:
		stderr("Could not open file "+transmittedFile+" for reading!")
		return 0

def networkUp():
	global oldUp
	if not interfaceFound:
		findInterface()
		if not interfaceFound:
			stderr("Interface could not be found")
			return 0
	if(oldUp==-1):
		#first run
		oldUp=getTotalUp()
		return 0
	else:
		newUp=getTotalUp()
		toReturn=newUp-oldUp
		oldUp=newUp
		return toReturn


findInterface()
print pcInterface