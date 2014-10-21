#!/usr/bin/env python

from gi.repository import Gtk, Gdk, GObject
import os

import Widgets.widget

class WidgetManager():
	"""
	Manages the Widgets (or Gadgets) placed on the desktop.
	Each Gadget can have many SubWidgets.
	"""
	def __init__(self):
		self.widgets=[]

	def add(self, widget, confFile):
		editTime=os.stat(confFile).st_mtime
		#[config file path, GtkWidget, previous check last edit time, current check last edit time]
		self.widgets.append({"config" : confFile, "widget" : widget, "previousEditTime" : editTime, "currentEditTime" : editTime})

	def run(self):
		self.monitorConfigChanges();
		Gtk.main()

	def monitorConfigChanges(self):
		GObject.timeout_add(200, self.checkConfigChange)

	def checkConfigChange(self):
		toRemoveIndexes=[]
		removedConfs=[]
		addedIndex=0
		for widget in self.widgets:
			widget["currentEditTime"]=os.stat(widget["config"]).st_mtime
			if(widget["previousEditTime"]!=widget["currentEditTime"]):
				toRemoveIndexes.append(addedIndex)
				removedConfs.append({"config" : widget["config"], "name" : widget["widget"].name})
				widget["widget"].destroy()
				widget["widget"].pantoflaWidgetManager.receivers=[]
				widget["widget"].pantoflaWidgetManager=0
			addedIndex+=1
				
		if(len(toRemoveIndexes) > 0):
			print "Config changed!"
			counter=len(toRemoveIndexes)
			for i in reversed(toRemoveIndexes):
				counter-=1
				self.widgets.pop(i)
				self.add(Widgets.widget.Widget(removedConfs[counter]["name"], removedConfs[counter]["config"]), removedConfs[counter]["config"])
		return True