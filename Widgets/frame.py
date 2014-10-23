#!/usr/bin/env python
receiver="Frame"

from gi.repository import Gtk, Gdk

import Defaults.widget

from Tools.output import *
from Tools.simplemath import *

class Widget():
	def __init__(self, name, parentName, parent):
		self.parent=parent
		self.hMid=False
		self.vMid=False
		self.frame=Gtk.Frame()
		self.name=parentName+name
		self.frame.set_name(self.name)

		self.styleProvider=Gtk.CssProvider()
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.currentCss={}

		self.updateCss("border", "1px solid white")
		self.width=100; self.height=100
		self.frame.set_size_request(self.width, self.height)

		self.cssClear = [ self.name ]

		self.frame.connect('destroy', self.destroyed)
		self.frame.connect('size-allocate', self.getSize)

		self.readyShow=True

	def getSize(self, widget, allocation):
		self.width=allocation.width
		self.height=allocation.height
		if(self.hMid):
			self.x=(self.parent.width - self.width)/2.0
		if(self.vMid):
			self.y=(self.parent.height - self.height)/2.0
		if(self.hMid or self.vMid):
			self.parent.fixed.move(self.frame, self.x, self.y)
		widget.disconnect_by_func(self.getSize)

	def destroyed(self, widget):
		for name in self.cssClear:
			self.styleProvider.load_from_data("#"+name+" { } ")

	def update(self):
		pass

	def runCommand(self, key, value, lineCount, configurationFile):
		if(key=="border-radius"):
			self.updateCss("border-radius", value)
		elif(key=="border"):
			self.updateCss("border", value)
		elif(key=="border-top"):
			self.updateCss("border-top", value)
		elif(key=="border-right"):
			self.updateCss("border-right", value)
		elif(key=="border-bottom"):
			self.updateCss("border-bottom", value)
		elif(key=="border-left"):
			self.updateCss("border-left", value)
		elif(key=="size"):
			size=value.split(",")
			self.width=int(size[0]); self.height=int(size[1])
			self.frame.set_size_request(self.width, self.height)
		else:
			stderr(configurationFile+", line "+str(lineCount)+": Unknown command.")

	def updateCss(self, key, value, name=None):
		if(name is None):
			name=self.name
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