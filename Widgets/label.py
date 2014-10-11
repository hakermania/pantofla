#!/usr/bin/env python

from gi.repository import Gtk, Gdk, Pango

import Defaults.widget

from Tools.output import *
from Tools.simplemath import *

receiver="Label"

class Widget():
	def __init__(self, name, parentName):
		self.gtkwidget=Gtk.Label();
		self.name=name+parentName #making a cross-widget unique name
		self.gtkwidget.set_name(self.name)
		self.styleProvider=Gtk.CssProvider()
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.currentCss=[]

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

			self.gtkwidget.modify_font(Pango.FontDescription(parts[1]))

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
		else:
			stderr(configurationFile+", line "+str(lineCount)+": Unknown command '"+command+"'")

	def updateCss(self, newCss):
		self.currentCss.append(newCss)
		self.styleProvider.load_from_data("""
			#"""+self.name+""" {
				"""+' '.join(self.currentCss)+"""
			}
		""")


	def widget(self):
		return self.gtkwidget