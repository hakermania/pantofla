#!/usr/bin/env python
receiver="Progressbar"

from gi.repository import Gtk, Gdk, GdkX11
from Tools.output import *
from multiprocessing.pool import ThreadPool

class Widget():
	def __init__(self, name, parentName, parent):
		self.parent=parent
		self.hMid=False
		self.vMid=False
		self.name=parentName+name

		self.drawingArea=Gtk.DrawingArea()
		self.drawingAreaName=self.name+"DrawingArea"
		self.drawingArea.set_name(self.drawingAreaName)

		self.width=100
		self.height=50

		self.drawingArea.set_size_request(self.width+2, self.height+2)

		self.styleProvider=Gtk.CssProvider()
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.currentCss={}

		self.updateCss("background-color", "rgba(255, 255, 0, 1)")

		self.color = { "r" : 1.0, "g" : 1.0, "b" : 1.0, "a" : 1.0 }
		self.outlineColor = { "r" : 1.0, "g" : 1.0, "b" : 1.0, "a" : 1.0 }

		self.valueLabel=0

		self.values = [ ]
		self.maxValue=0

		self.function=self.emptyFunction #the function to show
		self.niceFunction=self.emptyFunction

		self.fixed=Gtk.Fixed()
		self.fixedName=self.name+"Fixed"
		self.fixed.set_name(self.fixedName)
		self.fixed.put(self.drawingArea, 0, 0)

		self.frame=Gtk.Frame()
		self.frameName=self.name+"Frame"
		self.frame.set_name(self.frameName)
		self.frame.set_shadow_type(Gtk.ShadowType(Gtk.ShadowType.NONE))

		self.frame.add(self.fixed)

		self.frame.connect('destroy', self.destroyed)
		self.drawingArea.connect('size-allocate', self.getSize)
		self.drawingArea.connect('draw', self.draw)

		self.updateCss("background-color", "rgba(0,0,0,0)", self.frameName)

		self.cssClear = [ self.name, self.fixedName, self.frameName, self.drawingAreaName ]

		self.lastPercentage=0
		self.labelFrame=0
		self.outline=True
		self.readyShow=True
		self.functionData = None
		self.function = None
		self.pool = ThreadPool(processes=1)

	def destroyed(self, widget):
		for name in self.cssClear:
			self.styleProvider.load_from_data("#"+name+" { } ")

	def draw(self, widget, cr):

		progressValue=0
		if(self.height>self.width):
			progressValue=int(round(self.lastPercentage*self.height/100.0))
		else:
			progressValue=int(round(self.lastPercentage*self.width/100.0))
		
		if self.outline:
			cr.set_source_rgba(self.outlineColor["r"], self.outlineColor["g"], self.outlineColor["b"], self.outlineColor["a"])
			cr.move_to(0,0)
			cr.line_to(self.width, 0)
			cr.line_to(self.width, self.height)
			cr.line_to(0, self.height)
			cr.line_to(0, 0)
			cr.stroke()
			cr.set_source_rgba(self.color["r"], self.color["g"], self.color["b"], self.color["a"])
			if(self.width>self.height):
				cr.rectangle(1, 1, progressValue, self.height)
			else:
				cr.rectangle(0, self.height-progressValue, self.width, progressValue)
		else:
			cr.set_source_rgba(self.color["r"], self.color["g"], self.color["b"], self.color["a"])
			if(self.width>self.height):
				cr.rectangle(0, 0, progressValue, self.height)
			else:
				cr.rectangle(0, self.height-progressValue, self.width, progressValue)
		cr.fill()

	def update(self):
		if(self.function==None):
			return
		if(self.functionData==None):
			#first time claiming data
			self.functionData=self.pool.apply_async(self.function)
		elif(self.functionData.ready()):
			#data is ready for presenation
			self.lastPercentage=self.functionData.get()

			if(self.valueLabel!=0):
				updatedString=str(self.niceFunction(self.lastPercentage))
				if(updatedString!=self.valueLabel.get_text()):
					self.valueLabel.set_text(updatedString)

			self.functionData=self.pool.apply_async(self.function)

	def emptyFunction(self):
		return 0

	def initValueLabel(self):
		self.valueLabel=Gtk.Label()
		self.valueLabelName=self.name+"ValueLabel"
		self.valueLabel.set_name(self.valueLabelName)
		self.labelFrame=Gtk.Frame()
		self.labelFrame.set_shadow_type(Gtk.ShadowType(Gtk.ShadowType.NONE))
		self.labelFrame.add(self.valueLabel)
		self.fixed.put(self.labelFrame, 10, 10)

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
			#plus two goes for the outline
			self.drawingArea.set_size_request(int(size[0])+2, int(size[1])+2)
		elif(key=="progressbar-pos"):
			coords=value.split(",")
			self.fixed.move(self.drawingArea, int(coords[0]), int(coords[1]))
		elif(key=="background-color"):
			self.updateCss(key, value)
		elif(key=="color"):
			value=value[5:-1]
			value=value.split(",")
			self.color["r"]=float(value[0])/255.0; self.color["g"]=float(value[1])/255.0;
			self.color["b"]=float(value[2])/255.0; self.color["a"]=float(value[3]);
		elif(key=="function"):
			if(value=="networkUp"):
				from Tools.network import networkUp
				self.function=networkUp
			elif(value=="networkDown"):
				from Tools.network import networkDown
				self.function=networkDown
			elif(value=="networkTotalUp"):
				from Tools.network import networkTotalUp
				self.function=networkTotalUp
			elif(value=="networkTotalDown"):
				from Tools.network import networkTotalDown
				self.function=networkTotalDown
			elif(value=="cpuPercent"):
				from Tools.hardware import cpuPercent
				self.function=cpuPercent
			elif(value=="ramPercent"):
				from Tools.hardware import ramPercent
				self.function=ramPercent
			elif(value=="hddPercent"):
				from Tools.hardware import hddPercent
				self.function=hddPercent
			elif(value=="upTime"):
				from Tools.hardware import upTime
				self.function=upTime
		elif(key=="label"):
			if(int(value)==1):
				self.initValueLabel()
		elif(key=="label-pos"):
			coords=value.split(",")
			if(self.labelFrame==0):
				self.initValueLabel()
				self.fixed.move(self.labelFrame, int(coords[0]), int(coords[1]))
			else:
				self.fixed.move(self.labelFrame, int(coords[0]), int(coords[1]))
		elif(key=="label-type"):
			if(value=="data"):
				from Tools.hardware import dataToNiceString
				self.niceFunction=dataToNiceString
			elif(value=="percent"):
				from Tools.hardware import percentToNiceString
				self.niceFunction=percentToNiceString
			elif(value=="time"):
				from Tools.hardware import timeToNiceString
				self.niceFunction=timeToNiceString
		elif(key=="label-font"):
			self.updateCss("font", value, self.valueLabelName)
		elif(key=="label-color"):
			self.updateCss("color", value, self.valueLabelName)
		elif(key=="label-align"):
			if(value=="right"):
				self.valueLabel.set_halign(Gtk.Align.END)
			elif(value=="left"):
				self.valueLabel.set_halign(Gtk.Align.START)
		elif(key=="label-size"):
			size=value.split(",")
			self.labelFrame.set_size_request(int(size[0]), int(size[1]))
		elif(key=="outline"):
			if(int(value)==1):
				self.outline=True
			else:
				self.outline=False
		elif(key=="outline-color"):
			value=value[5:-1]
			value=value.split(",")
			self.outlineColor["r"]=float(value[0])/255.0; self.outlineColor["g"]=float(value[1])/255.0;
			self.outlineColor["b"]=float(value[2])/255.0; self.outlineColor["a"]=float(value[3]);
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
		return self.frame
