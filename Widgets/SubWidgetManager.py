#!/usr/bin/env python

import Widgets.label, Widgets.clock
import Defaults.widget

from gi.repository import GObject

class SubWidgetManager():
	def __init__(self):
		self.receivers={} #Holds all the widgets added
		self.widgets=[] #Holds all the classes
		self.widgets.append(Widgets.label)
		self.widgets.append(Widgets.clock)
		self.updateInterval = Defaults.widget.defaultUpdateInterval

	def setUpdateInterval(self, updateInterval):
		self.updateInterval=updateInterval

	def startUpdating(self):
		GObject.timeout_add(self.updateInterval, self.updateWidgets)
		self.updateWidgets()

	def updateWidgets(self):
		for widgetName in self.receivers:
			self.receivers[widgetName].update()
		return True