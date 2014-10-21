#!/usr/bin/env python

from output import *
import psutil, time

pcInterface=''
interfaceFile='/proc/net/route'
transmittedFile='/proc/net/dev'

interfaces=['ppp0', 'ppp1', 'wlp2s0', 'wlp2s1', 'wlan0', 'wlan1', 'eth0', 'eth1', 'enp0s0', 'enp0s1']

oldUp=-1; oldDown=-1
lastTimeGotUp=0
lastTimeGotDown=0

def timeNow():
	return int(round(time.time() * 1000))

def networkTotalDown():
	return psutil.net_io_counters()[1]

def networkTotalUp():
	return psutil.net_io_counters()[0]

def networkUp():
	global oldUp, lastTimeGotUp
	if(oldUp==-1):
		#first run
		lastTimeGotUp=timeNow()
		oldUp=networkTotalUp()
		return 0
	else:
		delta=timeNow()-lastTimeGotUp
		lastTimeGotUp=timeNow()
		newUp=networkTotalUp()
		toReturn=((newUp-oldUp)*1.0)*(1000.0/delta)
		oldUp=newUp
		return toReturn

def networkDown():
	global oldDown, lastTimeGotDown
	if(oldDown==-1):
		#first run
		lastTimeGotDown=timeNow()
		oldDown=networkTotalDown()
		return 0
	else:
		delta=timeNow()-lastTimeGotDown
		lastTimeGotDown=timeNow()
		newDown=networkTotalDown()
		toReturn=((newDown-oldDown)*1.0)*(1000.0/delta)
		oldDown=newDown
		return toReturn