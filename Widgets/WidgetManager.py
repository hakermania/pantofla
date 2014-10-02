#!/usr/bin/env python

from gi.repository import Gtk, Gdk

class WidgetManager():
	def __init__(self):
		self.widgets=[]

	def add(self, widget):
		self.widgets.append(widget)

	def run(self):
		Gtk.main()