#/usr/bin/env python
receiver="HSeparator"

from gi.repository import Gtk, Gdk
from Tools.output import *

class Widget():
	def __init__(self, name, parentName, parent):
		self.name=parentName+name
		self.separator = Gtk.HSeparator()
		self.separatorName=self.name+"HSeparator"
		self.separator.set_name(self.separatorName)
		self.parent=parent
		self.hMid=False
		self.vMid=False

		self.separator.set_size_request(100, 1)

		self.styleProvider=Gtk.CssProvider()
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.currentCss={}

		self.cssClear = [ self.separatorName ]
		self.separator.connect('destroy', self.destroyed)
		self.separator.connect('size-allocate', self.getSize)
		self.readyShow=True

	def destroyed(self, widget):
		for name in self.cssClear:
			self.styleProvider.load_from_data("#"+name+" { } ")

	def getSize(self, widget, allocation):
		self.width=allocation.width
		self.height=allocation.height
		if(self.hMid):
			self.x=(self.parent.width - self.width)/2.0
		if(self.vMid):
			self.y=(self.parent.height - self.height)/2.0
		if(self.hMid or self.vMid):
			self.parent.fixed.move(self.separator, self.x, self.y)

	def update(self):
		pass

	def runCommand(self, key, value, lineCount, configurationFile):
		if(key=="length"):
			self.separator.set_size_request(int(value), 1)
		elif(key=="color"):
			self.updateCss("color", value)
		else:
			stderr(configurationFile+", line "+str(lineCount)+": Unknown command.")

	def updateCss(self, key, value, name=None):
		if(name is None):
			name=self.separatorName
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
		return self.separator