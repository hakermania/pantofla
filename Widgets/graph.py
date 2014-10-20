#!/usr/bin/env python
receiver="Graph"

from gi.repository import Gtk, Gdk, GdkX11
from Tools.output import *
import math, random

class Widget():
	def __init__(self, name, parentName, parent):
		self.parent=parent
		self.hMid=False
		self.vMid=False
		self.name=parentName+name

		self.width=100
		self.height=50

		self.drawingArea=Gtk.DrawingArea()
		self.drawingAreaName=self.name+"DrawingArea"
		self.drawingArea.set_name(self.drawingAreaName)

		self.drawingArea.set_size_request(200, 200)

		self.styleProvider=Gtk.CssProvider()
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.currentCss={}

		self.cssClear = [ self.drawingAreaName ]

		self.updateCss("background-color", "rgba(255, 255, 0, 1)")

		self.color = { "r" : 1.0, "g" : 1.0, "b" : 1.0, "a" : 1.0 }

		self.pointWidth=1

		self.showAxisX=True

		self.values = [ ]
		self.maxValue=0

		self.function=self.emptyFunction #the function to show

		self.drawingArea.connect('destroy', self.destroyed)
		self.drawingArea.connect('size-allocate', self.getSize)
		self.drawingArea.connect('draw', self.draw)
		self.readyShow=True

	def destroyed(self, widget):
		for name in self.cssClear:
			self.styleProvider.load_from_data("#"+name+" { } ")

	def draw(self, widget, cr):
		cr.set_source_rgba(self.color["r"], self.color["g"], self.color["b"], self.color["a"])

		valuesN=len(self.values)
		for i in range(valuesN):
			#self.height-1 here because 0 is 1 pixel high
			if(self.maxValue==0):
				height=0
			else:
				height=(self.values[i]*(self.height-1)*1.0/self.maxValue)
			cr.rectangle(self.width-self.pointWidth*(valuesN-i), self.height-height, self.pointWidth, self.height)
		if(self.showAxisX):
			cr.rectangle(0, self.height-1, self.width, 1)
		cr.fill()		

	def update(self):
		value=self.function()
		print "GETTING", value, "bytes aka", value/1024.0, "Kbytes"
		self.values.append(value)
		if(len(self.values) > int(math.ceil(self.width*1.0/self.pointWidth))):
			self.values.pop(0)
		self.maxValue=max(self.values)

	def emptyFunction(self):
		return 0

	def getSize(self, widget, allocation):
		self.width=allocation.width
		self.height=allocation.height
		if(self.hMid):
			self.x=(self.parent.width - self.width)/2.0
		if(self.vMid):
			self.y=(self.parent.height - self.height)/2.0
		if(self.hMid or self.vMid):
			self.parent.fixed.move(self.drawingArea, self.x, self.y)

	def runCommand(self, key, value, lineCount, configurationFile):
		if(key=="size"):
			size=value.split(",")
			self.width=int(size[0])
			self.height=int(size[1])
			self.drawingArea.set_size_request(int(size[0]), int(size[1]))
		elif(key=="background-color"):
			self.updateCss(key, value)
		elif(key=="color"):
			value=value[5:-1]
			value=value.split(",")
			self.color["r"]=float(value[0])/255.0; self.color["g"]=float(value[1])/255.0;
			self.color["b"]=float(value[2])/255.0; self.color["a"]=float(value[3]);
		elif(key=="point-width"):
			self.pointWidth=int(value)
		elif(key=="function"):
			if(value=="networkUp"):
				from Tools.network import networkUp
				self.function=networkUp
			elif(value=="networkDown"):
				from Tools.network import networkDown
				self.function=networkDown
			elif(value=="cpuPercent"):
				from Tools.hardware import cpuPercent
				self.function=cpuPercent
			elif(value=="ramPercent"):
				from Tools.hardware import ramPercent
				self.function=ramPercent
			elif(value=="hddPercent"):
				from Tools.hardware import hddPercent
				self.function=hddPercent
		elif(key=="show-x"):
			if(int(value)==1):
				self.showAxisX=True
			else:
				self.showAxisX=False
		else:
			stderr(configurationFile+", line "+str(lineCount)+": Unknown command.")

	def updateCss(self, key, value, name=None):
		if(name is None):
			name=self.drawingAreaName
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

	def widget(self):
		return self.drawingArea
