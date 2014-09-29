#!/usr/bin/env python

import Widgets.label, Widgets.clock
import Defaults.widget

import threading

class SubWidgetManager():
	def __init__(self):
		self.receivers={} #Holds all the widgets added
		self.widgets=[] #Holds all the classes
		self.widgets.append(Widgets.label)
		self.widgets.append(Widgets.clock)
		self.updateInterval = Defaults.widget.defaultUpdateInterval
		self.t = threading.Timer(self.updateInterval/1000.0, self.updateWidgets)
		self.t.deamon=True

	def setUpdateInterval(self, updateInterval):
		self.updateInterval=updateInterval
		self.t = threading.Timer(self.updateInterval/1000.0, self.updateWidgets)
		self.t.deamon=True

	def startUpdating(self):
		print "Start Updating", self.receivers
		self.updateWidgets()

	def updateWidgets(self):
		print "Updating widgets!!", self.receivers
		for widgetName in self.receivers:
			self.receivers[widgetName].update()
		self.t = threading.Timer(self.updateInterval/1000.0, self.updateWidgets)
		self.t.deamon=True
		self.t.start()