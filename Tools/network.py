#!/usr/bin/env python

from output import *
import psutil, time

oldUp=-1; oldDown=-1
lastTimeGotUp=0
lastTimeGotDown=0

dataTypes = [ "B", "K", "M", "G", "T" ]

def niceRound(number):
	if number == int(number):
		return int(number)
	else:
		return number

def dataToNiceString(data, decimalRound=None):
	data=int(data)
	maxValue=len(dataTypes)-1
	niceData=data
	counter=0
	while(niceData>=1024):
		counter+=1
		niceData/=1024.0
		if(counter==maxValue):
			break
	if(decimalRound == None):
		decimalRound=1
		if(int(niceData) < 10):
			decimalRound=2
		return str(niceRound(round(niceData, decimalRound)))+dataTypes[counter]
	elif(decimalRound == 0):
		return str(int(round(niceData, decimalRound)))+dataTypes[counter]
	else:
		return str(niceRound(round(niceData, decimalRound)))+dataTypes[counter]

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