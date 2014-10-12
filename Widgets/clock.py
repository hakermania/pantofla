#!/usr/bin/env python

from gi.repository import Gtk, Gdk
from time import gmtime, strftime

import Defaults.widget

from Tools.output import *
from Tools.simplemath import *

receiver="Clock"

class Widget():
	def __init__(self, name, parentName):
		self.gtkwidget=Gtk.Label()
		self.name=parentName+name
		self.gtkwidget.set_name(self.name)

		self.format=Defaults.widget.defaultClockFormat
		self.gmt=Defaults.widget.defaultGmtClockValue
		self.styleProvider=Gtk.CssProvider()
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.currentCss={}

		self.gtkwidget.set_hexpand(True)
		self.alignment=Gtk.Alignment()
		self.alignment.set(0.5, 0.1, 0, 0)
		self.alignmentName = self.name+"Alignment"
		self.alignment.set_name(self.alignmentName)
		self.alignment.add(self.gtkwidget)

		self.frame = Gtk.Frame()
		self.frameName = self.name+"Frame"
		self.frame.set_name(self.frameName)
		self.frame.set_shadow_type(Gtk.ShadowType(Gtk.ShadowType.NONE))
		self.frame.add(self.alignment)

		self.frame.connect('destroy', self.destroyed)

		self.cssClear = [ self.name, self.alignmentName, self.frameName ]
		self.firstUpdate=True

		#self.updateCss("margin-top: 50px;", self.alignmentName)

	def destroyed(self, widget):
		for name in self.cssClear:
			self.styleProvider.load_from_data("#"+name+" { } ")

	def update(self):
		if(self.firstUpdate):
			self.firstUpdate=False
			self.applyCss()
		if(self.gmt):
			self.gtkwidget.set_text(strftime(self.format, gmtime()))
		else:
			self.gtkwidget.set_text(strftime(self.format))

	def runCommand(self, command, lineCount, configurationFile):
		if(command.startswith("format=")):
			self.format=command[7:]
		elif(command.startswith("gmt=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'gmt': Format: gmt = true/false.\nSkipping...")
				return
			if(parts[1]=="True"):
				self.gmt=True
			else:
				self.gmt=False
		elif(command.startswith("font=")):
			parts=command.split("=")
			if(len(parts)>2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'font': Format: font = fontName size, N integer.\nSkipping...")
				return

			self.updateCss("font: "+parts[1]+";")
		elif(command.startswith("color=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'color': Format: color = R,G,B,A.\nSkipping...")
				return
			values=parts[1].split(",")
			if(len(values)!=4):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'color': Format: color = R,G,B,A.\nSkipping...")
				return
			if(not representsInt(values[0]) or not representsInt(values[1]) or not representsInt(values[2]) or not representsFloat(values[3])):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'color': Format: color = R,G,B,A.\nSkipping...")
				return
			self.updateCss("color: rgba("+values[0]+","+values[1]+","+values[2]+","+values[3]+");")
		elif(command.startswith("bgColor=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'bgColor': Format: bgColor = R,G,B,A.\nSkipping...")
				return
			values=parts[1].split(",")
			if(len(values)!=4):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'bgColor': Format: bgColor = R,G,B,A.\nSkipping...")
				return

			if(not representsInt(values[0]) or not representsInt(values[1]) or not representsInt(values[2]) or not representsFloat(values[3])):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'bgColor': Format: bgColor = R,G,B,A.\nSkipping...")
				return

			self.updateCss("background-color: rgba("+values[0]+","+values[1]+","+values[2]+","+values[3]+");", self.frameName)
		elif(command.startswith("background-image=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'background-image': Format: background-image = 'path'.\nSkipping...")
				return

			if(not (parts[1].startswith("'") and parts[1].endswith("'"))):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'background-image': Format: background-image = 'path'.\nSkipping...")
				return
			
			self.updateCss("background-image: url("+parts[1]+");", self.frameName)
		else:
			stderr(configurationFile+", line "+str(lineCount)+": Unknown command '"+command+"'")

	def updateCss(self, newCss, name=None):
		if(name is None):
			name=self.name
		if name not in self.currentCss:
			self.currentCss[name]=[]
		print "'"+newCss+"'"
		self.currentCss[name].append(newCss)

	def applyCss(self):
		finalString=''
		for name in self.currentCss:
			finalString+="#"+name+" { "+' '.join(self.currentCss[name])+" } "
		print finalString
		self.styleProvider.load_from_data(finalString)

	def widget(self):
		return self.frame