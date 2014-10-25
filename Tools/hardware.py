#!/usr/bin/env python

from output import *
import psutil, time, os

dataTypes = [ "B", "K", "M", "G", "T" ]
timeTypes = [ "s", "m", "h", "d", "w", "y" ]

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
	if(decimalRound==None):
		decimalRound=1
		if(int(niceData) < 10):
			decimalRound=2
		return str(round(niceData, decimalRound))+dataTypes[counter]
	elif(decimalRound==0):
		return str(int(round(niceData, decimalRound)))+dataTypes[counter]
	else:
		return str(round(niceData, decimalRound))+dataTypes[counter]

def percentToNiceString(percent, percentDecimals=None, keepTrailing=None):
	if(percentDecimals==None or percentDecimals==0):
		return str(int(round(float(percent))))+"%"
	else:
		if(keepTrailing==None or keepTrailing==False):
			return str((round(float(percent), percentDecimals)))+"%"
		else:
			return ('{0:.'+str(percentDecimals)+'f}').format(round(float(percent), percentDecimals))+"%"

def timeToNiceString(timeValue):
	#timeValue is in seconds
	timeValue=int(round(int(timeValue)))
	years=timeValue/31536000
	timeValue-=years*31536000
	weeks=timeValue/604800
	timeValue-=weeks*604800
	days=timeValue/86400
	timeValue-=days*86400
	hours=timeValue/3600
	timeValue-=hours*3600
	minutes=timeValue/60
	timeValue-=minutes*60
	seconds=timeValue
	if(years!=0):
		if(days>3):
			#add 1 week (rounding)
			weeks+=1
		return str(years)+'y '+str(weeks)+'w'
	elif(weeks!=0):
		if(hours>12):
			#add 1 day (rounding)
			days+=1
		return str(weeks)+'w '+str(days)+'d'
	elif(days!=0):
		if(minutes>30):
			#add 1 hour (rounding)
			hours+=1
		return str(days)+'d '+str(hours)+'h'
	elif(hours!=0):
		if(seconds>30):
			#add 1 minute (rounding)
			minutes+=1
		return str(hours)+'h '+str(minutes)+'m'
	elif(minutes!=0):
		return str(minutes)+'m '+str(seconds)+'s'
	else:
		return str(seconds)+'s'

def cpuPercent():
	return psutil.cpu_percent(interval=0.9)

def ramPercent():
	return psutil.virtual_memory()[2]

def upTime():
	return time.time()-psutil.get_boot_time()

def systemLoad():
	return os.getloadavg()[0]