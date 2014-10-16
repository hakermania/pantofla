#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gdk
from time import strftime, time
import urllib2, urllib, json

import Defaults.widget

from Tools.output import *
from Tools.simplemath import *

from multiprocessing.pool import ThreadPool

receiver="Weather"

class Widget():
	def __init__(self, name, parentName, parent):
		self.parent=parent
		self.hMid=False
		self.vMid=False
		self.name=parentName+name

		self.cityLabel=Gtk.Label()
		self.cityLabelName=self.name+"cityLabel"
		self.cityLabel.set_name(self.cityLabelName)
		self.cityLabel.set_alignment(xalign=0.2, yalign=1)
		self.cityLabel.set_hexpand(True)

		self.temperatureLabel=Gtk.Label(u"25°")
		self.temperatureLabelName=self.name+"temperatureLabel"
		self.temperatureLabel.set_name(self.temperatureLabelName)
		self.temperatureLabel.set_alignment(xalign=0.2, yalign=0.2)

		self.pressureLabel=Gtk.Label("Pressure")
		self.pressureLabelName=self.name+"pressureLabel"
		self.pressureLabel.set_name(self.pressureLabelName)
		self.pressureLabel.set_alignment(xalign=1, yalign=0.5)

		self.humidityLabel=Gtk.Label("Humidity")
		self.humidityLabelName=self.name+"humidityLabel"
		self.humidityLabel.set_name(self.humidityLabelName)
		self.humidityLabel.set_alignment(xalign=1, yalign=0.5)

		self.speedLabel=Gtk.Label("Speed")
		self.speedLabelName=self.name+"speedLabel"
		self.speedLabel.set_name(self.speedLabelName)
		self.speedLabel.set_alignment(xalign=1, yalign=0.5)

		self.f1Label=Gtk.Label("F1")
		self.f1LabelName=self.name+"f1Label"
		self.f1Label.set_name(self.f1LabelName)
		self.f1Label.set_hexpand(True)

		self.f2Label=Gtk.Label("F2")
		self.f2LabelName=self.name+"f2Label"
		self.f2Label.set_name(self.f2LabelName)
		self.f2Label.set_hexpand(True)

		self.f3Label=Gtk.Label("F3")
		self.f3LabelName=self.name+"f3Label"
		self.f3Label.set_name(self.f3LabelName)
		self.f3Label.set_hexpand(True)

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
		self.updateCss("background-color: rgba(0, 0, 0, 0.2);", self.shadowName)

		self.fixed=Gtk.Fixed()
		self.fixedName=self.name+"Fixed"
		self.fixed.set_name(self.fixedName)

		self.fixed.put(self.upperFrame, 0, 0)
		self.fixed.put(self.shadow, 0, 0)

		self.fixed.put(self.temperatureLabel, 15, 0)

		self.fixed.put(self.pressureLabel, 180, 5)
		self.fixed.put(self.humidityLabel, 178, 26)
		self.fixed.put(self.speedLabel, 192, 47)

		self.fixed.put(self.cityLabel, 15, 60)

		self.fixed.put(self.f1Label, 0, 90)
		self.fixed.put(self.f2Label, 100, 90)
		self.fixed.put(self.f3Label, 200, 90)

		self.f1Label.connect('size-allocate', self.getSizeForecast)

		self.frame = Gtk.Frame()
		self.frameName = self.name+"Frame"
		self.frame.set_name(self.frameName)
		self.frame.add(self.fixed)

		self.cssClear = [ self.name, self.cityLabelName, self.temperatureLabelName,
						self.pressureLabelName, self.humidityLabelName, self.speedLabelName, self.f1LabelName,
						self.f2LabelName, self.f3LabelName, self.frameName ]

		self.frame.connect('destroy', self.destroyed)
		self.frame.connect('size-allocate', self.getSize)

		self.forecastPositionSet=False

		self.lastUpdateTime=0
		self.currentlyLoading=False

		self.pool = ThreadPool(processes=1)

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

	def getSizeForecast(self, widget, allocation):
		if(self.forecastPositionSet):
			return;
		self.fixed.move(self.f1Label, (self.width/4.0 - allocation.width), 90)
		self.fixed.move(self.f2Label, (self.width - allocation.width)/2.0, 90)
		self.fixed.move(self.f3Label, (3*self.width/4.0), 90)
		self.f1Label.disconnect_by_func(self.getSizeForecast)

	def destroyed(self, widget):
		for name in self.cssClear:
			self.styleProvider.load_from_data("#"+name+" { } ")

	def getWeather(self):
		try:
			baseurl = "https://query.yahooapis.com/v1/public/yql?"
			yql_query = "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text=\""+self.cityName+"\")"
			yql_url = baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
			result = urllib2.urlopen(yql_url).read()
			return json.loads(result)['query']['results']['channel']
		except:
			return []

	def applyWeatherData(self, data):
		self.cityLabel.set_text(data['location']['city']+" - "+data['item']['condition']['text'])
		self.temperatureLabel.set_text(data['item']['condition']['temp']+u'°'+data['units']['temperature'])
		self.pressureLabel.set_text(data['atmosphere']['pressure']+data['units']['pressure'])
		self.humidityLabel.set_text(data['atmosphere']['humidity']+"%")
		self.speedLabel.set_text(data['wind']['speed']+data['units']['speed'])

		print "Forecast:"

		counter = 0
		for day in data['item']['forecast']:
			if(day['day']==strftime('%a')):
				continue #it is today
			print day['day'].upper(), "->", day['low']+data['units']['temperature']+"/"+day['high']+data['units']['temperature'], "-", day['text']
			counter+=1
			if(counter==3):
				break

	def update(self):
		#update every 5 minutes
		if(not self.currentlyLoading and (time()-self.lastUpdateTime>300)):
			self.currentlyLoading=True
			self.weatherData=self.pool.apply_async(self.getWeather)
		elif(self.currentlyLoading):
			#waiting for the data
			if(self.weatherData.ready()):
				#data is ready!
				self.applyWeatherData(self.weatherData.get())
				self.weatherData=0
				#Loading finished and the last update time is now
				self.currentlyLoading=False
				self.lastUpdateTime=time()

	def runCommand(self, command, lineCount, configurationFile):
		if(command.startswith("temp-pos=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'temp-pos': Format: temp-pos = x,y.\nSkipping...")
				return
			coords=parts[1].split(",")
			if(len(coords)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'temp-pos': Format: temp-pos = x,y.\nSkipping...")
				return
			self.fixed.move(self.temperatureLabel, int(coords[0]), int(coords[1]))
		elif(command.startswith("pressure-pos=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'pressure-pos': Format: pressure-pos = x,y.\nSkipping...")
				return
			coords=parts[1].split(",")
			if(len(coords)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'pressure-pos': Format: pressure-pos = x,y.\nSkipping...")
				return
			self.fixed.move(self.pressureLabel, int(coords[0]), int(coords[1]))
		elif(command.startswith("humidity-pos=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'humidity-pos': Format: humidity-pos = x,y.\nSkipping...")
				return
			coords=parts[1].split(",")
			if(len(coords)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'humidity-pos': Format: humidity-pos = x,y.\nSkipping...")
				return
			self.fixed.move(self.humidityLabel, int(coords[0]), int(coords[1]))
		elif(command.startswith("speed-pos=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'speed-pos': Format: speed-pos = x,y.\nSkipping...")
				return
			coords=parts[1].split(",")
			if(len(coords)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'speed-pos': Format: speed-pos = x,y.\nSkipping...")
				return
			self.fixed.move(self.speedLabel, int(coords[0]), int(coords[1]))
		elif(command.startswith("city-pos=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'city-pos': Format: city-pos = x,y.\nSkipping...")
				return
			coords=parts[1].split(",")
			if(len(coords)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'city-pos': Format: city-pos = x,y.\nSkipping...")
				return
			self.fixed.move(self.cityLabel, int(coords[0]), int(coords[1]))
		elif(command.startswith("f1-pos=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'f1-pos': Format: f1-pos = x,y.\nSkipping...")
				return
			coords=parts[1].split(",")
			if(len(coords)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'f1-pos': Format: f1-pos = x,y.\nSkipping...")
				return
			self.forecastPositionSet=True
			self.fixed.move(self.f1Label, int(coords[0]), int(coords[1]))
		elif(command.startswith("f2-pos=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'f2-pos': Format: f2-pos = x,y.\nSkipping...")
				return
			coords=parts[1].split(",")
			if(len(coords)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'f2-pos': Format: f2-pos = x,y.\nSkipping...")
				return
			self.forecastPositionSet=True
			self.fixed.move(self.f2Label, int(coords[0]), int(coords[1]))
		elif(command.startswith("f3-pos=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'f3-pos': Format: f3-pos = x,y.\nSkipping...")
				return
			coords=parts[1].split(",")
			if(len(coords)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'f3-pos': Format: f3-pos = x,y.\nSkipping...")
				return
			self.forecastPositionSet=True
			self.fixed.move(self.f3Label, int(coords[0]), int(coords[1]))
		elif(command.startswith("size=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'size': Format: size = w, h.\nSkipping...")
				return

			size=parts[1].split(",")
			self.width=int(size[0])
			self.height=int(size[1])
			self.frame.set_size_request(int(size[0]), int(size[1]))
		elif(command.startswith("upsize=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'upsize': Format: upsize = w, h.\nSkipping...")
				return

			size=parts[1].split(",")
			self.upperFrame.set_size_request(int(size[0]), int(size[1]))
			self.shadow.set_size_request(int(size[0]), int(size[1]))
		elif(command.startswith("city=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'city': Format: city = name size.\nSkipping...")
				return

			self.cityLabel.set_text(parts[1]+" - Mostly Cloudy")
			self.cityName=parts[1]
		elif(command.startswith("background-image=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'background-image': Format: background-image = 'path'.\nSkipping...")
				return

			if(not (parts[1].startswith("'") and parts[1].endswith("'"))):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'background-image': Format: background-image = 'path'.\nSkipping...")
				return
			
			self.updateCss("background-image: url("+parts[1]+");", self.upperFrameName)
		elif(command.startswith("font=")):
			parts=command.split("=")
			if(len(parts)>2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'font': Format: font = font size.\nSkipping...")
				return

			self.updateCss("font: "+parts[1]+";")
		elif(command.startswith("tempFont=")):
			parts=command.split("=")
			if(len(parts)>2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'tempFont': Format: tempFont = font size.\nSkipping...")
				return
			
			self.updateCss("font: "+parts[1]+";", self.temperatureLabelName)
		elif(command.startswith("tempColor=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'tempColor': Format: tempColor = R,G,B,A.\nSkipping...")
				return
			values=parts[1].split(",")
			if(len(values)!=4):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'tempColor': Format: tempColor = R,G,B,A.\nSkipping...")
				return
			if(not representsInt(values[0]) or not representsInt(values[1]) or not representsInt(values[2]) or not representsFloat(values[3])):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'tempColor': Format: tempColor = R,G,B,A.\nSkipping...")
				return
			self.updateCss("color: rgba("+values[0]+","+values[1]+","+values[2]+","+values[3]+");", self.temperatureLabelName)
		elif(command.startswith("cityFont=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'cityFont': Format: cityFont = font size.\nSkipping...")
				return

			self.updateCss("font: "+parts[1]+";", self.cityLabelName)
		elif(command.startswith("cityColor=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'cityColor': Format: cityColor = R,G,B,A.\nSkipping...")
				return
			values=parts[1].split(",")
			if(len(values)!=4):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'cityColor': Format: cityColor = R,G,B,A.\nSkipping...")
				return
			if(not representsInt(values[0]) or not representsInt(values[1]) or not representsInt(values[2]) or not representsFloat(values[3])):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'cityColor': Format: cityColor = R,G,B,A.\nSkipping...")
				return
			self.updateCss("color: rgba("+values[0]+","+values[1]+","+values[2]+","+values[3]+");", self.cityLabelName)
		elif(command.startswith("statsFont=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'statsFont': Format: statsFont = font size.\nSkipping...")
				return

			self.updateCss("font: "+parts[1]+";", self.pressureLabelName)
			self.updateCss("font: "+parts[1]+";", self.humidityLabelName)
			self.updateCss("font: "+parts[1]+";", self.speedLabelName)
		elif(command.startswith("statsColor=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'statsColor': Format: statsColor = R,G,B,A.\nSkipping...")
				return
			values=parts[1].split(",")
			if(len(values)!=4):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'statsColor': Format: statsColor = R,G,B,A.\nSkipping...")
				return
			if(not representsInt(values[0]) or not representsInt(values[1]) or not representsInt(values[2]) or not representsFloat(values[3])):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'statsColor': Format: statsColor = R,G,B,A.\nSkipping...")
				return
			self.updateCss("color: rgba("+values[0]+","+values[1]+","+values[2]+","+values[3]+");", self.pressureLabelName)
			self.updateCss("color: rgba("+values[0]+","+values[1]+","+values[2]+","+values[3]+");", self.humidityLabelName)
			self.updateCss("color: rgba("+values[0]+","+values[1]+","+values[2]+","+values[3]+");", self.speedLabelName)
		elif(command.startswith("upperFrameBorder=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'upperFrameBorder': Format: upperFrameBorder = px state color.\nSkipping...")
				return

			self.updateCss("border: "+parts[1]+";", self.upperFrameName)
		elif(command.startswith("upperFrameBorder-top=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'upperFrameBorder-top': Format: upperFrameBorder-top = px state color.\nSkipping...")
				return

			self.updateCss("border-top: "+parts[1]+";", self.upperFrameName)
		elif(command.startswith("upperFrameBorder-right=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'upperFrameBorder-right': Format: upperFrameBorder-right = px state color.\nSkipping...")
				return

			self.updateCss("border-right: "+parts[1]+";", self.upperFrameName)
		elif(command.startswith("upperFrameBorder-bottom=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'upperFrameBorder-bottom': Format: upperFrameBorder-bottom = px state color.\nSkipping...")
				return

			self.updateCss("border-bottom: "+parts[1]+";", self.upperFrameName)
		elif(command.startswith("upperFrameBorder-left=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'upperFrameBorder-left': Format: upperFrameBorder-left = px state color.\nSkipping...")
				return

			self.updateCss("border-left: "+parts[1]+";", self.upperFrameName)

		elif(command.startswith("color=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'color': Format: color = R,G,B,A.\nSkipping...")
				return
			values=parts[1].split(",")
			if(len(values)!=4):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'color': Format: color = R,G,B,A.\nSkipping...")
				return
			if(not representsInt(values[0]) or not representsInt(values[1]) or not representsInt(values[2]) or not representsFloat(values[3])):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'color': Format: color = R,G,B,A.\nSkipping...")
				return
			self.updateCss("color: rgba("+values[0]+","+values[1]+","+values[2]+","+values[3]+");")
		elif(command.startswith("border=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'border': Format: border = px state color.\nSkipping...")
				return

			self.updateCss("border: "+parts[1]+";")
		elif(command.startswith("border-top=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'border-top': Format: border-top = px.\nSkipping...")
				return

			self.updateCss("border-top: "+parts[1]+";")
		elif(command.startswith("border-right=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'border-right': Format: border-right = px.\nSkipping...")
				return

			self.updateCss("border-right: "+parts[1]+";")
		elif(command.startswith("border-bottom=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'border-bottom': Format: border-bottom = px.\nSkipping...")
				return

			self.updateCss("border-bottom: "+parts[1]+";")
		elif(command.startswith("border-left=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'border-left': Format: border-left = px.\nSkipping...")
				return

			self.updateCss("border-left: "+parts[1]+";")
		elif(command.startswith("padding=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'padding': Format: padding = px state color.\nSkipping...")
				return

			self.updateCss("padding: "+parts[1]+";")
		elif(command.startswith("padding-top=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'padding-top': Format: padding-top = px.\nSkipping...")
				return

			self.updateCss("padding-top: "+parts[1]+";")
		elif(command.startswith("padding-right=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'padding-right': Format: padding-right = px.\nSkipping...")
				return

			self.updateCss("padding-right: "+parts[1]+";")
		elif(command.startswith("padding-bottom=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'padding-bottom': Format: padding-bottom = px.\nSkipping...")
				return

			self.updateCss("padding-bottom: "+parts[1]+";")
		elif(command.startswith("padding-left=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'padding-left': Format: padding-left = px.\nSkipping...")
				return

			self.updateCss("padding-left: "+parts[1]+";")
		elif(command.startswith("bgColor=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'bgColor': Format: bgColor = R,G,B,A.\nSkipping...")
				return
			values=parts[1].split(",")
			if(len(values)!=4):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'bgColor': Format: bgColor = R,G,B,A.\nSkipping...")
				return

			if(not representsInt(values[0]) or not representsInt(values[1]) or not representsInt(values[2]) or not representsFloat(values[3])):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'bgColor': Format: bgColor = R,G,B,A.\nSkipping...")
				return

			self.updateCss("background-color: rgba("+values[0]+","+values[1]+","+values[2]+","+values[3]+");", self.frameName)
		elif(command.startswith("background-image=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'background-image': Format: background-image = 'path'.\nSkipping...")
				return

			if(not (parts[1].startswith("'") and parts[1].endswith("'"))):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'background-image': Format: background-image = 'path'.\nSkipping...")
				return
			
			self.updateCss("background-image: url("+parts[1]+");", self.frameName)
		else:
			stderr(configurationFile+", line "+str(lineCount)+": Unknown command '"+command+"'")

	def updateCss(self, newCss, name=None):
		if(name is None):
			name=self.frameName
		if name not in self.currentCss:
			self.currentCss[name]=[]
		self.currentCss[name].append(newCss)

	def applyCss(self):
		finalString=''
		for name in self.currentCss:
			if(len(self.currentCss[name])>0):
				finalString+="#"+name+" { "+' '.join(self.currentCss[name])+" } "
		if(finalString!=''):
			self.styleProvider.load_from_data(finalString)

	def initial(self):
		self.applyCss()

	def widget(self):
		return self.frame