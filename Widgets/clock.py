#!/usr/bin/env python

from gi.repository import Gtk, Gdk
from time import gmtime, strftime

import Defaults.widget

from Tools.output import *
from Tools.simplemath import *

receiver="Clock"

class Widget():
	def __init__(self, name, parentName, parent):
		self.parent=parent
		self.hMid=False
		self.vMid=False
		self.clockLabel=Gtk.Label()
		self.name=parentName+name

		self.clockLabelName=self.name+"clockLabel"
		self.clockLabel.set_name(self.clockLabelName)

		self.format=Defaults.widget.defaultClockFormat
		self.gmt=Defaults.widget.defaultGmtClockValue
		self.styleProvider=Gtk.CssProvider()
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.currentCss={}

		self.clockLabel.set_hexpand(True)
		self.alignment=Gtk.Alignment()
		self.alignment.set(0.5, 0.1, 0, 0)
		self.alignmentName = self.name+"Alignment"
		self.alignment.set_name(self.alignmentName)
		self.alignment.add(self.clockLabel)

		self.frame = Gtk.Frame()
		self.frameName = self.name+"Frame"
		self.frame.set_name(self.frameName)
		self.frame.set_shadow_type(Gtk.ShadowType(Gtk.ShadowType.NONE))
		self.frame.add(self.alignment)

		self.cssClear = [ self.name, self.alignmentName, self.frameName ]

		self.frame.connect('destroy', self.destroyed)
		self.frame.connect('size-allocate', self.getSize)

	def getSize(self, widget, allocation):
		self.width=allocation.width
		self.height=allocation.height
		if(self.hMid):
			self.x=(self.parent.width - self.width)/2.0
		if(self.vMid):
			self.y=(self.parent.height - self.height)/2.0
		if(self.hMid or self.vMid):
			self.parent.fixed.move(self.frame, self.x, self.y)

	def destroyed(self, widget):
		for name in self.cssClear:
			self.styleProvider.load_from_data("#"+name+" { } ")

	def update(self):
		if(self.gmt):
			self.clockLabel.set_text(strftime(self.format, gmtime()))
		else:
			self.clockLabel.set_text(strftime(self.format))

	def runCommand(self, command, lineCount, configurationFile):
		parts=command.split("=")
		if(len(parts)!=2):
			stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command.\nSkipping...")
			return
		if(command.startswith("format=")):
			self.format=parts[1]
		elif(command.startswith("gmt=")):
			if(parts[1]=="True"):
				self.gmt=True
			else:
				self.gmt=False
		elif(command.startswith("font=")):
			self.updateCss("font: "+parts[1]+";")
		elif(command.startswith("color=")):
			values=parts[1].split(",")
			if(len(values)!=4):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'color': Format: color = R,G,B,A.\nSkipping...")
				return
			if(not representsInt(values[0]) or not representsInt(values[1]) or not representsInt(values[2]) or not representsFloat(values[3])):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'color': Format: color = R,G,B,A.\nSkipping...")
				return
			self.updateCss("color: rgba("+values[0]+","+values[1]+","+values[2]+","+values[3]+");")
		elif(command.startswith("border=")):
			self.updateCss("border: "+parts[1]+";")
		elif(command.startswith("border-top=")):
			self.updateCss("border-top: "+parts[1]+";")
		elif(command.startswith("border-right=")):
			self.updateCss("border-right: "+parts[1]+";")
		elif(command.startswith("border-bottom=")):
			self.updateCss("border-bottom: "+parts[1]+";")
		elif(command.startswith("border-left=")):
			self.updateCss("border-left: "+parts[1]+";")
		elif(command.startswith("padding=")):
			self.updateCss("padding: "+parts[1]+";")
		elif(command.startswith("padding-top=")):
			self.updateCss("padding-top: "+parts[1]+";")
		elif(command.startswith("padding-right=")):
			self.updateCss("padding-right: "+parts[1]+";")
		elif(command.startswith("padding-bottom=")):
			self.updateCss("padding-bottom: "+parts[1]+";")
		elif(command.startswith("padding-left=")):
			self.updateCss("padding-left: "+parts[1]+";")
		elif(command.startswith("bgColor=")):
			values=parts[1].split(",")
			if(len(values)!=4):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'bgColor': Format: bgColor = R,G,B,A.\nSkipping...")
				return

			if(not representsInt(values[0]) or not representsInt(values[1]) or not representsInt(values[2]) or not representsFloat(values[3])):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'bgColor': Format: bgColor = R,G,B,A.\nSkipping...")
				return

			self.updateCss("background-color: rgba("+values[0]+","+values[1]+","+values[2]+","+values[3]+");", self.frameName)
		elif(command.startswith("background-image=")):
			if(not (parts[1].startswith("'") and parts[1].endswith("'"))):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'background-image': Format: background-image = 'path'.\nSkipping...")
				return
			
			self.updateCss("background-image: url("+parts[1]+");", self.frameName)
		else:
			stderr(configurationFile+", line "+str(lineCount)+": Unknown command '"+command+"'")

	def updateCss(self, newCss, name=None):
		if(name is None):
			name=self.clockLabelName
		if name not in self.currentCss:
			self.currentCss[name]=[]
		self.currentCss[name].append(newCss)

	def applyCss(self):
		finalString=''
		for name in self.currentCss:
			if(len(self.currentCss[name])>0):
				finalString+="#"+name+" { "+' '.join(self.currentCss[name])+" } "
		if(finalString!=''):
			self.styleProvider.load_from_data(finalString)

	def initial(self):
		self.applyCss()

	def widget(self):
		return self.frame