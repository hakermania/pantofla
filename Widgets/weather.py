#!/usr/bin/env python

from gi.repository import Gtk, Gdk
from time import strftime

import Defaults.widget

from Tools.output import *
from Tools.simplemath import *

receiver="Weather"

units='C' #possible values 'C' or 'F'

class Widget():
	def __init__(self, name, parentName):
		self.name=parentName+name

		self.cityLabel=Gtk.Label()
		self.cityLabelName=self.name+"cityLabel"
		self.cityLabel.set_name(self.cityLabelName)

		self.temperatureLabel=Gtk.Label()
		self.temperatureLabelName=self.name+"temperatureLabel"
		self.temperatureLabel.set_name(self.temperatureLabelName)

		self.conditionLabel=Gtk.Label("LEL")
		self.conditionLabelName=self.name+"conditionLabel"
		self.conditionLabel.set_name(self.conditionLabelName)

		self.pressureLabel=Gtk.Label()
		self.pressureLabelName=self.name+"pressureLabel"
		self.pressureLabel.set_name(self.pressureLabelName)

		self.humidityLabel=Gtk.Label()
		self.humidityLabelName=self.name+"humidityLabel"
		self.humidityLabel.set_name(self.humidityLabelName)

		self.speedLabel=Gtk.Label()
		self.speedLabelName=self.name+"speedLabel"
		self.speedLabel.set_name(self.speedLabelName)

		self.d1Label=Gtk.Label()
		self.d1LabelName=self.name+"d1Label"
		self.d1Label.set_name(self.d1LabelName)

		self.d2Label=Gtk.Label()
		self.d2LabelName=self.name+"d2Label"
		self.d2Label.set_name(self.d2LabelName)

		self.d3Label=Gtk.Label()
		self.d3LabelName=self.name+"d3Label"
		self.d3Label.set_name(self.d3LabelName)

		self.styleProvider=Gtk.CssProvider()
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.currentCss={}

		# self.cityLabel.set_hexpand(True)
		# self.alignment=Gtk.Alignment()
		# self.alignment.set(0.5, 0.1, 0, 0)
		# self.alignmentName = self.name+"Alignment"
		# self.alignment.set_name(self.alignmentName)
		# self.alignment.add(self.cityLabel)
		self.grid=Gtk.Grid()

		self.grid.attach(self.cityLabel, 0, 0, 1, 1)
		self.grid.attach(self.temperatureLabel, 1, 0, 1, 1)
		self.grid.attach(self.conditionLabel, 2, 0, 1, 1)
		self.grid.attach(self.pressureLabel, 3, 0, 1, 1)
		self.grid.attach(self.humidityLabel, 4, 0, 1, 1)
		self.grid.attach(self.speedLabel, 5, 0, 1, 1)
		self.grid.attach(self.d1Label, 6, 0, 1, 1)
		self.grid.attach(self.d2Label, 7, 0, 1, 1)
		self.grid.attach(self.d3Label, 8, 0, 1, 1)


		self.frame = Gtk.Frame()
		self.frameName = self.name+"Frame"
		self.frame.set_name(self.frameName)
		self.frame.set_shadow_type(Gtk.ShadowType(Gtk.ShadowType.NONE))
		self.frame.add(self.grid)

		self.cssClear = [ self.name, self.frameName ]

		self.frame.connect('destroy', self.destroyed)

	def destroyed(self, widget):
		for name in self.cssClear:
			self.styleProvider.load_from_data("#"+name+" { } ")

	def update(self):
		pass

	def runCommand(self, command, lineCount, configurationFile):
		if(command.startswith("font=")):
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