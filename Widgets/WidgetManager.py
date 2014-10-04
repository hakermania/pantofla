#!/usr/bin/env python

from gi.repository import Gtk, Gdk, GObject
import os

import Widgets.widget

class WidgetManager():
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
		GObject.timeout_add(1000, self.checkConfigChange)

	def checkConfigChange(self):
		print "Checking config change"
		toRemoveIndexes=[]
		removedConfs=[]
		currentIndex=0
		for widget in self.widgets:
			widget["currentEditTime"]=os.stat(widget["config"]).st_mtime
			if(widget["previousEditTime"]!=widget["currentEditTime"]):
				toRemoveIndexes.append(currentIndex)
				removedConfs.append({"config" : widget["config"], "name" : widget["widget"].name})
				widget["widget"].destroy()
			currentIndex+=1
		if(len(toRemoveIndexes) > 0):
			for i in reversed(toRemoveIndexes):
				self.widgets.pop(i)
				self.add(Widgets.widget.Widget(removedConfs[i]["name"], removedConfs[i]["config"]), removedConfs[i]["config"])
		return True


