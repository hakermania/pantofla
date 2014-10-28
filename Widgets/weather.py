#!/usr/bin/env python
# -*- coding: utf-8 -*-
receiver="Weather"

from gi.repository import Gtk, Gdk, GdkPixbuf
from time import strftime, time
import urllib2, urllib, json, datetime

import Defaults.widget

from Tools.output import *
from Tools.simplemath import *
from Tools.simpleimage import *

from multiprocessing.pool import ThreadPool

from os.path import expanduser, isfile
home = expanduser("~")

class Widget():
	def __init__(self, name, parentName, parent):
		self.parent=parent
		self.hMid=False
		self.vMid=False
		self.name=parentName+name
		self.width=228
		self.height=150

		self.cityLabel=Gtk.Label()
		self.cityLabelName=self.name+"cityLabel"
		self.cityLabel.set_name(self.cityLabelName)
		self.cityLabel.set_alignment(xalign=0.2, yalign=1)
		self.cityLabel.set_hexpand(True)

		self.temperatureLabel=Gtk.Label()
		self.temperatureLabelName=self.name+"temperatureLabel"
		self.temperatureLabel.set_name(self.temperatureLabelName)
		self.temperatureLabel.set_alignment(xalign=0.2, yalign=0.2)

		self.day1Range=Gtk.Label()
		self.day1RangeName=self.name+"day1Range"
		self.day1Range.set_name(self.day1RangeName)
		self.day1Range.index=0; self.day1Range.x=27

		self.day2Range=Gtk.Label()
		self.day2RangeName=self.name+"day2Range"
		self.day2Range.set_name(self.day2RangeName)
		self.day2Range.index=1; self.day2Range.x=102

		self.day3Range=Gtk.Label()
		self.day3RangeName=self.name+"day3Range"
		self.day3Range.set_name(self.day3RangeName)
		self.day3Range.index=2; self.day3Range.x=182

		self.day1Range.y=self.day2Range.y=self.day3Range.y=158

		self.pressureLabel=Gtk.Label()
		self.pressureLabelName=self.name+"pressureLabel"
		self.pressureLabel.set_name(self.pressureLabelName)
		self.pressureLabel.index=0

		self.humidityLabel=Gtk.Label()
		self.humidityLabelName=self.name+"humidityLabel"
		self.humidityLabel.set_name(self.humidityLabelName)
		self.humidityLabel.index=1

		self.speedLabel=Gtk.Label()
		self.speedLabelName=self.name+"speedLabel"
		self.speedLabel.set_name(self.speedLabelName)
		self.speedLabel.index=2

		self.pressureIcon=loadImageSvgScaled(home+"/.pantofla/Weather/Stats/pressure.svg", 5, 5)
		self.humidityIcon=loadImageSvgScaled(home+"/.pantofla/Weather/Stats/humidity.svg", 5, 5)
		self.speedIcon=loadImageSvgScaled(home+"/.pantofla/Weather/Stats/wind.svg", 5, 5)

		self.day1ConditionIcon=Gtk.Image()
		self.day1ConditionIcon.index=0; self.day1ConditionIcon.x=27

		self.day2ConditionIcon=Gtk.Image()
		self.day2ConditionIcon.index=1; self.day2ConditionIcon.x=102

		self.day3ConditionIcon=Gtk.Image()
		self.day3ConditionIcon.index=2; self.day3ConditionIcon.x=182

		self.day1ConditionIcon.y=self.day2ConditionIcon.y=self.day3ConditionIcon.y=116

		self.f1Label=Gtk.Label()
		self.f1LabelName=self.name+"f1Label"
		self.f1Label.set_name(self.f1LabelName)
		self.f1Label.set_alignment(xalign=0.5, yalign=0.5)
		self.f1Label.index=0; self.f1Label.x=27

		self.f2Label=Gtk.Label()
		self.f2LabelName=self.name+"f2Label"
		self.f2Label.set_name(self.f2LabelName)
		self.f2Label.set_alignment(xalign=0.5, yalign=0.5)
		self.f2Label.index=1; self.f2Label.x=102

		self.f3Label=Gtk.Label()
		self.f3LabelName=self.name+"f3Label"
		self.f3Label.set_name(self.f3LabelName)
		self.f3Label.set_alignment(xalign=0.5, yalign=0.5)
		self.f3Label.index=2; self.f3Label.x=182

		self.separator1=Gtk.VSeparator()
		self.separator1.set_size_request(1, 100)
		self.separator1Name=self.name+"sep1"
		self.separator1.set_name(self.separator1Name)

		self.separator2=Gtk.VSeparator()
		self.separator2.set_size_request(1, 100)
		self.separator2Name=self.name+"sep2"
		self.separator2.set_name(self.separator2Name)

		self.f1Label.y=self.f2Label.y=self.f3Label.y=94

		self.styleProvider=Gtk.CssProvider()
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.currentCss={}

		self.forecastGrid=Gtk.Grid()
		self.forecastGridName = self.name+"forecastGrid"
		self.forecastGrid.set_row_spacing(0)
		self.forecastGrid.set_column_spacing(0)
		self.forecastGrid.set_name(self.forecastGridName)

		self.upperFrame = Gtk.Frame()
		self.upperFrameName = self.name+"upperFrame"
		self.upperFrame.set_name(self.upperFrameName)
		self.upperFrame.set_hexpand(True)

		#display a small shadow behind the weather for clarity
		self.shadow = Gtk.Frame()
		self.shadowName = self.name+"shadow"
		self.shadow.set_name(self.shadowName)
		self.shadow.set_shadow_type(Gtk.ShadowType(Gtk.ShadowType.NONE))
		self.updateCss("background-color", "rgba(0, 0, 0, 0.05)", self.shadowName)

		self.fixed=Gtk.Fixed()
		self.fixedName=self.name+"Fixed"
		self.fixed.set_name(self.fixedName)

		self.fixed.put(self.upperFrame, 0, 0)
		self.fixed.put(self.shadow, 0, 0)

		self.fixed.put(self.temperatureLabel, 15, 0)

		self.fixed.put(self.pressureLabel, 193, 5)
		self.fixed.put(self.humidityLabel, 193, 26)
		self.fixed.put(self.speedLabel, 193, 47)
		self.pressureLabel.x=self.humidityLabel.x=self.speedLabel.x=193
		self.pressureLabel.y=5; self.humidityLabel.y=26; self.speedLabel.y=47;
		self.fixed.put(self.pressureIcon, 203, 5)
		self.fixed.put(self.humidityIcon, 203, 26)
		self.fixed.put(self.speedIcon, 203, 47)

		self.fixed.put(self.cityLabel, 15, 60)

		self.fixed.put(self.f1Label, self.f1Label.x, self.f1Label.y)
		self.fixed.put(self.separator1, self.f1Label.x+10, self.f1Label.y)
		self.fixed.put(self.f2Label, self.f2Label.x, self.f2Label.y)
		self.fixed.put(self.separator2, self.f2Label.x+10, self.f2Label.y)
		self.fixed.put(self.f3Label, self.f3Label.x, self.f3Label.y)
		self.fixed.put(self.day1ConditionIcon, self.day1ConditionIcon.x, self.day1ConditionIcon.y)
		self.fixed.put(self.day2ConditionIcon, self.day2ConditionIcon.x, self.day2ConditionIcon.y)
		self.fixed.put(self.day3ConditionIcon, self.day3ConditionIcon.x, self.day3ConditionIcon.y)
		self.fixed.put(self.day1Range, self.day1Range.x, self.day1Range.y)
		self.fixed.put(self.day2Range, self.day2Range.x, self.day2Range.y)
		self.fixed.put(self.day3Range, self.day3Range.x, self.day3Range.y)

		self.frame = Gtk.Frame()
		self.frameName = self.name+"Frame"
		self.frame.set_name(self.frameName)
		self.frame.add(self.fixed)

		self.updateCss("background-color", "rgba(0,0,0,0)", self.frameName)

		self.cssClear = [ self.name, self.cityLabelName, self.temperatureLabelName,
						self.pressureLabelName, self.humidityLabelName, self.speedLabelName, self.f1LabelName,
						self.f2LabelName, self.f3LabelName, self.frameName ]

		self.frame.connect('destroy', self.destroyed)
		self.frame.connect('size-allocate', self.getSize)
		self.manuallyAllocatedDays=False

		self.lastUpdateTime=0
		self.currentlyLoading=False
		self.unit='f'

		self.pool = ThreadPool(processes=1)
		self.initEnd=False
		self.readyShow=False

	def getSize(self, widget, allocation):
		self.width=allocation.width
		self.height=allocation.height
		if(self.hMid):
			self.x=(self.parent.width - self.width)/2.0
		if(self.vMid):
			self.y=(self.parent.height - self.height)/2.0
		if(self.hMid or self.vMid):
			self.parent.fixed.move(self.frame, self.x, self.y)
		self.frame.disconnect_by_func(self.getSize)

	def allocateDays(self, widget, allocation):
		if not self.manuallyAllocatedDays:
			if(widget.index==0):
				self.fixed.move(widget, self.width/6.0-allocation.width/2.0, widget.y)
			elif(widget.index==1):
				self.fixed.move(widget, int(round((self.width-allocation.width)/2.0)), widget.y)
			elif(widget.index==2):
				self.fixed.move(widget, 5*self.width/6.0-allocation.width/2.0, widget.y)

	def allocateStats(self, widget, allocation):
		if(not self.initEnd):
			return
		self.fixed.move(widget, widget.x-allocation.width, widget.y)
		widget.disconnect_by_func(self.allocateStats)
		widgetIcon=None
		if(widget.index==0):
			widgetIcon=self.pressureIcon
		elif(widget.index==1):
			widgetIcon=self.humidityIcon
		elif(widget.index==2):
			widgetIcon=self.speedIcon
		self.fixed.move(widgetIcon, widget.x+10, widget.y)

	def destroyed(self, widget):
		for name in self.cssClear:
			self.styleProvider.load_from_data("#"+name+" { } ")

	def getWeather(self):
		self.readyShow=True #todo remove
		return []  #todo remove
		try:
			baseurl = "https://query.yahooapis.com/v1/public/yql?"
			yql_query = "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='"+self.cityName+"') and u='"+self.unit+"'"
			yql_url = baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"

			result = urllib2.urlopen(yql_url).read()
			return json.loads(result)['query']['results']['channel']
		except:
			return []

	def applyWeatherData(self, data):
		if(len(data)==0):
			print "Something went wrong!", strftime("%H:%M")
			self.lastUpdateTime=time()-180
			return False
		try:
			self.cityLabel.set_text(data['location']['city']+" - "+data['item']['condition']['text'])
			self.temperatureLabel.set_text(data['item']['condition']['temp']+u'°')
			self.pressureLabel.set_text(data['atmosphere']['pressure']+' '+data['units']['pressure'])
			self.humidityLabel.set_text(data['atmosphere']['humidity']+" %")
			self.speedLabel.set_text(data['wind']['speed']+' '+data['units']['speed'])

			conditionsImage=home+"/.pantofla/Weather/Conditions/"+data['item']['condition']['code']+".png"
			if(isfile(conditionsImage)):
				self.updateCss("background-image", "url('"+conditionsImage+"')", self.upperFrameName)
				self.applyCss()
			else:
				print conditionsImage, "does not exist!"

			for day in data['item']['forecast']:
				thisDate=datetime.datetime.strptime(day['date'], '%d %b %Y')
				if(thisDate.day==datetime.date.today().day):
					#it is today
					self.f1Label.set_text(day['day'].upper())
					self.day1ConditionIcon.set_from_pixbuf(loadPixbuf(home+"/.pantofla/Weather/Conditions-Icons/"+day['code']+".png"))
					self.day1Range.set_text(day['low']+u'°/'+day['high']+u'°')
				elif(thisDate.day==(datetime.date.today() + datetime.timedelta(days=1)).day):
					self.f2Label.set_text(day['day'].upper())
					self.day2ConditionIcon.set_from_pixbuf(loadPixbuf(home+"/.pantofla/Weather/Conditions-Icons/"+day['code']+".png"))
					self.day2Range.set_text(day['low']+u'°/'+day['high']+u'°')
				elif(thisDate.day==(datetime.date.today() + datetime.timedelta(days=2)).day):
					self.f3Label.set_text(day['day'].upper())
					self.day3ConditionIcon.set_from_pixbuf(loadPixbuf(home+"/.pantofla/Weather/Conditions-Icons/"+day['code']+".png"))
					self.day3Range.set_text(day['low']+u'°/'+day['high']+u'°')
					break

			#resize the labels again to have constant right-x so as to stay aligned
			self.pressureLabel.connect('size-allocate', self.allocateStats)
			self.humidityLabel.connect('size-allocate', self.allocateStats)
			self.speedLabel.connect('size-allocate', self.allocateStats)
			print "ALL OK!", strftime("%H:%M")
		except Exception as e:
			#something went wrong, try again in 2 minutes
			print e
			self.lastUpdateTime=time()-180
			return False
		
		self.readyShow=True

		self.separator1.show()
		self.separator2.show()
		self.pressureIcon.show()
		self.humidityIcon.show()
		self.speedIcon.show()
		return True

	def update(self):
		#update every 5 minutes
		if(not self.currentlyLoading and (time()-self.lastUpdateTime>300)):
			self.currentlyLoading=True
			self.weatherData=self.pool.apply_async(self.getWeather)
		elif(self.currentlyLoading):
			#waiting for the data
			if(self.weatherData.ready()):
				#data is ready!
				if(self.applyWeatherData(self.weatherData.get())):
					#Loading finished and the last update time is now
					self.lastUpdateTime=time()
				self.currentlyLoading=False
				self.weatherData=0

	def runCommand(self, key, value, lineCount, configurationFile):
		if(key=="temp-pos"):
			coords=value.split(",")
			if(len(coords)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'temp-pos': Format: temp-pos = x,y.\nSkipping...")
				return
			self.fixed.move(self.temperatureLabel, int(coords[0]), int(coords[1]))
		elif(key=="pressure-pos"):
			coords=value.split(",")
			if(len(coords)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'pressure-pos': Format: pressure-pos = x,y.\nSkipping...")
				return
			self.pressureLabel.x=int(coords[0]); self.pressureLabel.y=int(coords[1])
			self.fixed.move(self.pressureLabel, self.pressureLabel.x, self.pressureLabel.y)
		elif(key=="days-font"):
			self.updateCss("font", value, self.f1LabelName)
			self.updateCss("font", value, self.f2LabelName)
			self.updateCss("font", value, self.f3LabelName)
		elif(key=="days-color"):
			values=value.split(",")
			if(len(values)!=4):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'city-color': Format: city-color = R,G,B,A.\nSkipping...")
				return
			if(not representsInt(values[0]) or not representsInt(values[1]) or not representsInt(values[2]) or not representsFloat(values[3])):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'city-color': Format: city-color = R,G,B,A.\nSkipping...")
				return
			self.updateCss("color", "rgba("+values[0]+","+values[1]+","+values[2]+","+values[3]+")", self.f1LabelName)
			self.updateCss("color", "rgba("+values[0]+","+values[1]+","+values[2]+","+values[3]+")", self.f2LabelName)
			self.updateCss("color", "rgba("+values[0]+","+values[1]+","+values[2]+","+values[3]+")", self.f3LabelName)
		elif(key=="humidity-pos"):
			coords=value.split(",")
			if(len(coords)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'humidity-pos': Format: humidity-pos = x,y.\nSkipping...")
				return
			self.humidityLabel.x=int(coords[0]); self.humidityLabel.y=int(coords[1])
			self.fixed.move(self.humidityLabel, self.humidityLabel.x, self.humidityLabel.y)
		elif(key=="speed-pos"):
			coords=value.split(",")
			if(len(coords)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'speed-pos': Format: speed-pos = x,y.\nSkipping...")
				return
			self.speedLabel.x=int(coords[0]); self.speedLabel.y=int(coords[1])
			self.fixed.move(self.speedLabel, self.speedLabel.x, self.speedLabel.y)
		elif(key=="city-pos"):
			coords=value.split(",")
			if(len(coords)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'city-pos': Format: city-pos = x,y.\nSkipping...")
				return
			self.fixed.move(self.cityLabel, int(coords[0]), int(coords[1]))
		elif(key=="day1Range-pos"):
			coords=value.split(",")
			if(len(coords)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'day1Range-pos': Format: day1Range-pos = x,y.\nSkipping...")
				return
			self.fixed.move(self.day1Range, int(coords[0]), int(coords[1]))
		elif(key=="day1Range-font"):
			self.updateCss("font", value, self.day1RangeName)
		elif(key=="day1Range-color"):
			self.updateCss("color", value, self.day1RangeName)
		elif(key=="day2Range-pos"):
			coords=value.split(",")
			if(len(coords)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'day2Range-pos': Format: day2Range-pos = x,y.\nSkipping...")
				return
			self.fixed.move(self.day2Range, int(coords[0]), int(coords[1]))
		elif(key=="day2Range-font"):
			self.updateCss("font", value, self.day2RangeName)
		elif(key=="day2Range-color"):
			self.updateCss("color", value, self.day2RangeName)
		elif(key=="day3Range-pos"):
			coords=value.split(",")
			if(len(coords)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'day3Range-pos': Format: day3Range-pos = x,y.\nSkipping...")
				return
			self.fixed.move(self.day3Range, int(coords[0]), int(coords[1]))
		elif(key=="day3Range-font"):
			self.updateCss("font", value, self.day3RangeName)
		elif(key=="day3Range-color"):
			self.updateCss("color", value, self.day3RangeName)
		elif(key=="f1-pos"):
			parts=command.split("=")
			coords=value.split(",")
			if(len(coords)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'f1-pos': Format: f1-pos = x,y.\nSkipping...")
				return
			self.f1Label.x=int(coords[0]); self.f1Label.y=int(coords[1])
			self.fixed.move(self.f1Label, self.f1Label.x, self.f1Label.y)
			self.manuallyAllocatedDays=True
		elif(key=="f2-pos"):
			coords=value.split(",")
			if(len(coords)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'f2-pos': Format: f2-pos = x,y.\nSkipping...")
				return
			self.f2Label.x=int(coords[0]); self.f2Label.y=int(coords[1])
			self.fixed.move(self.f2Label, self.f2Label.x, self.f2Label.y)
			self.manuallyAllocatedDays=True
		elif(key=="f3-pos"):
			coords=value.split(",")
			if(len(coords)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'f3-pos': Format: f3-pos = x,y.\nSkipping...")
				return
			self.f3Label.x=int(coords[0]); self.f3Label.y=int(coords[1])
			self.fixed.move(self.f3Label, self.f3Label.x, self.f3Label.y)
			self.manuallyAllocatedDays=True
		elif(key=="sep1-pos"):
			coords=value.split(",")
			if(len(coords)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'sep1-pos': Format: sep1-pos = x,y.\nSkipping...")
				return
			self.fixed.move(self.separator1, int(coords[0]), int(coords[1]))
		elif(key=="sep1-length"):
			self.separator1.set_size_request(1, int(value))
		elif(key=="sep1-color"):
			self.updateCss("color", value, self.separator1Name)
		elif(key=="sep2-pos"):
			coords=value.split(",")
			if(len(coords)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'sep2-pos': Format: sep2-pos = x,y.\nSkipping...")
				return
			self.fixed.move(self.separator2, int(coords[0]), int(coords[1]))
		elif(key=="sep2-length"):
			self.separator2.set_size_request(1, int(value))
		elif(key=="sep2-color"):
			self.updateCss("color", value, self.separator2Name)
		elif(key=="size"):
			size=value.split(",")
			self.width=int(size[0])
			self.height=int(size[1])
			self.frame.set_size_request(int(size[0]), int(size[1]))
		elif(key=="upsize"):
			size=value.split(",")
			self.upperFrame.set_size_request(int(size[0]), int(size[1]))
			self.shadow.set_size_request(int(size[0]), int(size[1]))
		elif(key=="city"):
			self.cityName=value
		elif(key=="unit"):
			self.unit=value
		elif(key=="background-image"):
			if(not (value.startswith("'") and value.endswith("'"))):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'background-image': Format: background-image = 'path'.\nSkipping...")
				return
			self.updateCss("background-image", "url("+value+")", self.upperFrameName)
		elif(key=="font"):
			self.updateCss("font", value)
		elif(key=="temp-font"):
			self.updateCss("font", value, self.temperatureLabelName)
		elif(key=="temp-color"):
			values=value.split(",")
			if(len(values)!=4):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'temp-color': Format: temp-color = R,G,B,A.\nSkipping...")
				return
			if(not representsInt(values[0]) or not representsInt(values[1]) or not representsInt(values[2]) or not representsFloat(values[3])):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'temp-color': Format: temp-color = R,G,B,A.\nSkipping...")
				return
			self.updateCss("color", "rgba("+values[0]+","+values[1]+","+values[2]+","+values[3]+")", self.temperatureLabelName)

		elif(key=="city-font"):
			self.updateCss("font", value, self.cityLabelName)
		elif(key=="city-color"):
			values=value.split(",")
			if(len(values)!=4):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'city-color': Format: city-color = R,G,B,A.\nSkipping...")
				return
			if(not representsInt(values[0]) or not representsInt(values[1]) or not representsInt(values[2]) or not representsFloat(values[3])):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'city-color': Format: city-color = R,G,B,A.\nSkipping...")
				return
			self.updateCss("color", "rgba("+values[0]+","+values[1]+","+values[2]+","+values[3]+")", self.cityLabelName)
		elif(key=="stats-font"):
			self.updateCss("font", value, self.pressureLabelName)
			self.updateCss("font", value, self.humidityLabelName)
			self.updateCss("font", value, self.speedLabelName)
		elif(key=="stats-color"):
			values=value.split(",")
			if(len(values)!=4):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'stats-color': Format: stats-color = R,G,B,A.\nSkipping...")
				return
			if(not representsInt(values[0]) or not representsInt(values[1]) or not representsInt(values[2]) or not representsFloat(values[3])):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'stats-color': Format: stats-color = R,G,B,A.\nSkipping...")
				return
			self.updateCss("color", "rgba("+values[0]+","+values[1]+","+values[2]+","+values[3]+")", self.pressureLabelName)
			self.updateCss("color", "rgba("+values[0]+","+values[1]+","+values[2]+","+values[3]+")", self.humidityLabelName)
			self.updateCss("color", "rgba("+values[0]+","+values[1]+","+values[2]+","+values[3]+")", self.speedLabelName)
		elif(key=="upperFrameBorder"):
			self.updateCss("border", value, self.upperFrameName)
		elif(key=="upperFrameBorder-top"):
			self.updateCss("border-top", value, self.upperFrameName)
		elif(key=="upperFrameBorder-right"):
			self.updateCss("border-right", value, self.upperFrameName)
		elif(key=="upperFrameBorder-bottom"):
			self.updateCss("border-bottom", value, self.upperFrameName)
		elif(key=="upperFrameBorder-left"):
			self.updateCss("border-left", value, self.upperFrameName)
		elif(key=="color"):
			values=value.split(",")
			if(len(values)!=4):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'color': Format: color = R,G,B,A.\nSkipping...")
				return
			if(not representsInt(values[0]) or not representsInt(values[1]) or not representsInt(values[2]) or not representsFloat(values[3])):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'color': Format: color = R,G,B,A.\nSkipping...")
				return
			self.updateCss("color", "rgba("+values[0]+","+values[1]+","+values[2]+","+values[3]+")")
		elif(key=="border"):
			self.updateCss("border", value)
		elif(key=="border-top"):
			self.updateCss("border-top", value)
		elif(key=="border-right"):
			self.updateCss("border-right", value)
		elif(key=="border-bottom"):
			self.updateCss("border-bottom", value)
		elif(key=="border-left"):
			self.updateCss("border-left", value)
		elif(key=="padding"):
			self.updateCss("padding", value)
		elif(key=="padding-top"):
			self.updateCss("padding-top", value)
		elif(key=="padding-right"):
			self.updateCss("padding-right", value)
		elif(key=="padding-bottom"):
			self.updateCss("padding-bottom", value)
		elif(key=="padding-left"):
			self.updateCss("padding-left", value)
		elif(key=="bgColor"):
			values=value.split(",")
			if(len(values)!=4):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'bgColor': Format: bgColor = R,G,B,A.\nSkipping...")
				return

			if(not representsInt(values[0]) or not representsInt(values[1]) or not representsInt(values[2]) or not representsFloat(values[3])):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'bgColor': Format: bgColor = R,G,B,A.\nSkipping...")
				return

			self.updateCss("background-color", "rgba("+values[0]+","+values[1]+","+values[2]+","+values[3]+")", self.frameName)
		elif(key=="background-image"):
			if(not (value.startswith("'") and value.endswith("'"))):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'background-image': Format: background-image = 'path'.\nSkipping...")
				return
			self.updateCss("background-image", "url("+value+")", self.frameName)
		else:
			stderr(configurationFile+", line "+str(lineCount)+": Unknown command.")

	def updateCss(self, key, value, name=None):
		if(name is None):
			name=self.frameName
		if name not in self.currentCss:
			self.currentCss[name]={}
		key=key.rstrip(); key=key.lstrip()
		value=value.rstrip(); value=value.lstrip()

		if key not in self.currentCss[name]:
			self.currentCss[name][key]={}

		self.currentCss[name][key]["value"]=value

	def applyCss(self):
		finalString=''
		for name in self.currentCss:
			if(len(self.currentCss[name])>0):
				finalString+="#"+name+" { "
				for key in self.currentCss[name]:
					finalString+=key+" : "+self.currentCss[name][key]["value"]+"; "
				finalString+="} "

		if(finalString!=''):
			self.styleProvider.load_from_data(finalString.encode())


	def initial(self):
		self.applyCss()
		self.pressureIcon.hide()
		self.humidityIcon.hide()
		self.separator1.hide()
		self.separator2.hide()
		self.speedIcon.hide() #we will show them once the weather info is available
		self.f1Label.connect('size-allocate', self.allocateDays)
		self.f2Label.connect('size-allocate', self.allocateDays)
		self.f3Label.connect('size-allocate', self.allocateDays)
		self.day1ConditionIcon.connect('size-allocate', self.allocateDays)
		self.day2ConditionIcon.connect('size-allocate', self.allocateDays)
		self.day3ConditionIcon.connect('size-allocate', self.allocateDays)
		self.day1Range.connect('size-allocate', self.allocateDays)
		self.day2Range.connect('size-allocate', self.allocateDays)
		self.day3Range.connect('size-allocate', self.allocateDays)
		self.initEnd=True

	def widget(self):
		return self.frame