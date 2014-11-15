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
		Gtk.main()