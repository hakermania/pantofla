#!/usr/bin/env python

from gi.repository import Gtk, Gdk, Pango

import Defaults.widget

from Tools.output import *
from Tools.simplemath import *

receiver="Label"

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

	def destroyed(self, widget):
		for name in self.cssClear:
			self.styleProvider.load_from_data("#"+name+" { } ")

	def update(self):
		pass

	def runCommand(self, command, lineCount, configurationFile):
		if(command.startswith("text=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'text': Format: text = 'text'.\nSkipping...")
				return
			if(not (parts[1].startswith("'") and parts[1].endswith("'"))):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'text': Format: text = 'text'.\nSkipping...")
				return
			
			self.text=parts[1][1:-1] #Remove the ""

			self.gtkwidget.set_text(self.text)
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
		elif(command.startswith("border=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'border': Format: border = px state color.\nSkipping...")
				return

			self.updateCss("border: "+parts[1]+";")
		elif(command.startswith("border-top=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'border-top': Format: border-top = px.\nSkipping...")
				return

			self.updateCss("border-top: "+parts[1]+";")
		elif(command.startswith("border-right=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'border-right': Format: border-right = px.\nSkipping...")
				return

			self.updateCss("border-right: "+parts[1]+";")
		elif(command.startswith("border-bottom=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'border-bottom': Format: border-bottom = px.\nSkipping...")
				return

			self.updateCss("border-bottom: "+parts[1]+";")
		elif(command.startswith("border-left=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'border-left': Format: border-left = px.\nSkipping...")
				return

			self.updateCss("border-left: "+parts[1]+";")
		elif(command.startswith("padding=")):
			parts=command.split("=")
			if(len(parts)!=2):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'padding': Format: padding = px state color.\nSkipping...")
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
			name=self.name
		if name not in self.currentCss:
			self.currentCss[name]=[]
		self.currentCss[name].append(newCss)

	def applyCss(self):
		finalString=''
		for name in self.currentCss:
			finalString+="#"+name+" { "+' '.join(self.currentCss[name])+" } "
		print finalString
		self.styleProvider.load_from_data(finalString)

	def widget(self):
		return self.frame