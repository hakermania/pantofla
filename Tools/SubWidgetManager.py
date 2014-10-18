#!/usr/bin/env python

import Widgets
import Defaults.widget, pkgutil

from gi.repository import GObject

class SubWidgetManager():
	"""
	Manages the (Gtk) (sub)widgets of each Gadget (Widget).
	For exapmle, this class calls the update function for
	each widget.
	"""
	def __init__(self):
		self.receivers={} #Holds all the widgets added to the Gadget
		self.widgets=[] #Holds all the widget modules

		#dynamically add all the modules inside the Widgets package
		for importer, modname, ispkg in pkgutil.iter_modules(Widgets.__path__):
			self.widgets.append(importer.find_module(modname).load_module(modname))

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

	def callWidgetsInitial(self):
		for widgetName in self.receivers:
			self.receivers[widgetName].initial()