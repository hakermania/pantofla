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
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'font': Format: font = font size.\nSkipping...")
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
		elif(command.startswith("border=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'border': Format: border = px state color.\nSkipping...")
				return

			self.updateCss("border: "+parts[1]+";")
		elif(command.startswith("border-top=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'border-top': Format: border-top = px state color.\nSkipping...")
				return

			self.updateCss("border-top: "+parts[1]+";")
		elif(command.startswith("border-right=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'border-right': Format: border-right = px state color.\nSkipping...")
				return

			self.updateCss("border-right: "+parts[1]+";")
		elif(command.startswith("border-bottom=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'border-bottom': Format: border-bottom = px state color.\nSkipping...")
				return

			self.updateCss("border-bottom: "+parts[1]+";")
		elif(command.startswith("border-left=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'border-left': Format: border-left = px state color.\nSkipping...")
				return

			self.updateCss("border-left: "+parts[1]+";")
		elif(command.startswith("padding=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'padding': Format: padding = px.\nSkipping...")
				return

			self.updateCss("padding: "+parts[1]+";")
		elif(command.startswith("padding-top=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'padding-top': Format: padding-top = px.\nSkipping...")
				return

			self.updateCss("padding-top: "+parts[1]+";")
		elif(command.startswith("padding-right=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'padding-right': Format: padding-right = px.\nSkipping...")
				return

			self.updateCss("padding-right: "+parts[1]+";")
		elif(command.startswith("padding-bottom=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'padding-bottom': Format: padding-bottom = px.\nSkipping...")
				return

			self.updateCss("padding-bottom: "+parts[1]+";")
		elif(command.startswith("padding-left=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'padding-left': Format: padding-left = px.\nSkipping...")
				return

			self.updateCss("padding-left: "+parts[1]+";")
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