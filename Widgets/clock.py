#!/usr/bin/env python

from gi.repository import Gtk, Gdk

import output, Defaults.widget
from time import gmtime, strftime

from simplemath import *

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
		self.currentCss=[]

		self.gtkwidget.set_hexpand(True)
		self.alignment=Gtk.Alignment()
		self.alignment.set(0.5, 0.1, 0, 0)
		self.alignment.add(self.gtkwidget)

	def update(self):
		if(self.gmt):
			self.gtkwidget.set_text(strftime(self.format, gmtime()))
		else:
			self.gtkwidget.set_text(strftime(self.format))

	def runCommand(self, command, lineCount, configurationFile):
		print command
		if(command.startswith("format=")):
			self.format=command[7:]
		elif(command.startswith("gmt=")):
			parts=command.split("=")
			if(len(parts)!=2):
				output.stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'gmt': Format: gmt = true/false.\nSkipping...")
				return
			if(parts[1]=="True"):
				self.gmt=True
			else:
				self.gmt=False
		elif(command.startswith("size=")):
			parts=command.split("=")
			if(len(parts)>2):
				output.stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'size': Format: size = Npx, N integer.\nSkipping...")
				return
			if(not representsInt(parts[1][:-2])):
				output.stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'size': Format: size = Npx, N integer.\nSkipping...")
				return

			self.updateCss("font-size: "+parts[1]+";")
		elif(command.startswith("color=")):
			parts=command.split("=")
			if(len(parts)!=2):
				output.stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'color': Format: color = R,G,B,A.\nSkipping...")
				return
			values=parts[1].split(",")
			if(len(values)!=4):
				output.stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'color': Format: color = R,G,B,A.\nSkipping...")
				return
			if(not representsInt(values[0]) or not representsInt(values[1]) or not representsInt(values[2]) or not representsFloat(values[3])):
				output.stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'color': Format: color = R,G,B,A.\nSkipping...")
				return
			self.updateCss("color: rgba("+values[0]+","+values[1]+","+values[2]+","+values[3]+");")
		else:
			output.stderr(configurationFile+", line "+str(lineCount)+": Unknown command '"+command+"'")

	def updateCss(self, newCss):
		self.currentCss.append(newCss)
		self.styleProvider.load_from_data("""
			#"""+self.name+""" {
				"""+' '.join(self.currentCss)+"""
			}
		""")

	def widget(self):
		return self.alignment
		return self.gtkwidget