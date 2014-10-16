#!/usr/bin/env python

from gi.repository import GObject, Gtk, Gdk

import Defaults.widget, Tools.SubWidgetManager

from Tools.output import *
from Tools.simplemath import *

class Widget(Gtk.Window):

	def __init__(self, name, configurationFile, fadeIn):
		Gtk.Window.__init__(self,
			accept_focus=False, skip_pager_hint=True,
			skip_taskbar_hint=True, decorated=False,
			deletable=False, focus_on_map=False,
			focus_visible=False, has_resize_grip=False,
			type_hint=Gdk.WindowTypeHint.DOCK)
		
		#Set the window properties to look like a gadget. These cannot be changed through the configuration file
		self.set_name(name)
		self.name = name
		self.set_wmclass(Defaults.widget.wmClass, Defaults.widget.wmClass)
		self.set_keep_below(True)
		self.set_sensitive(False)
		self.stick()

		self.rgbaVisual = self.get_screen().get_rgba_visual()

		self.pantoflaWidgetManager = Tools.SubWidgetManager.SubWidgetManager()

		self.styleProvider = Gtk.CssProvider()
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

		self.currentCss=[]

		self.fixed = Gtk.Fixed()
		self.fixed.set_name(self.name+"Fixed")
		self.currentPosition=[]

		self.add(self.fixed)

		self.applyConfigurationFile(configurationFile, fadeIn)

		self.updateCss("padding: 100px;")

		self.set_resizable(False)

		self.applyCss()

		if fadeIn:
			self.fadeInToDefaultBgColor()

		self.show_all()

	def fadeInToDefaultBgColor(self):
		self.currentBgColor = [self.finalBgColor[0], self.finalBgColor[1], self.finalBgColor[2], 0.0]
		self.fadeInStepValue = self.finalBgColor[3]/100.0
		self.fadeInWidget()
		GObject.timeout_add(Defaults.widget.defaultFadeInTime/100.0, self.fadeInWidget)
		

	def fadeInWidget(self):
		self.set_visual(self.rgbaVisual)
		if(self.currentBgColor[3]+self.fadeInStepValue < self.finalBgColor[3]):
			self.currentBgColor[3]+=self.fadeInStepValue
			self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(self.currentBgColor[0], self.currentBgColor[1], self.currentBgColor[2], self.currentBgColor[3]))
			return True
		else:
			toReturn=False
			self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(self.finalBgColor[0], self.finalBgColor[1], self.finalBgColor[2], self.finalBgColor[3]))
			return False;

	def putReceiverToWidget(self, receiver):
		x, y = 0, 0
		if(not representsInt(self.currentPosition[0])):
			self.pantoflaWidgetManager.receivers[receiver].hMid=True
			x=0
		else:
			x=self.currentPosition[0]
		if(not representsInt(self.currentPosition[1])):
			self.pantoflaWidgetManager.receivers[receiver].vMid=True
			y=0
		else:
			y=self.currentPosition[1]
		self.pantoflaWidgetManager.receivers[receiver].x=x
		self.pantoflaWidgetManager.receivers[receiver].y=y
		self.fixed.put(self.pantoflaWidgetManager.receivers[receiver].widget(), x, y)

	def commandForReceiver(self, receiver, command, lineCount, configurationFile):
		"""Sends the command (property) to the appropriate widget (receiver)"""
		if receiver not in self.pantoflaWidgetManager.receivers:
			for widget in self.pantoflaWidgetManager.widgets:
				if receiver.startswith(widget.receiver):
					self.pantoflaWidgetManager.receivers[receiver]=widget.Widget(receiver, self.name, self)
					self.pantoflaWidgetManager.receivers[receiver].runCommand(command, lineCount, configurationFile)
					break
		else:
			self.pantoflaWidgetManager.receivers[receiver].runCommand(command, lineCount, configurationFile)

	def applyConfigurationFile(self, configurationFile, fadeIn):
		try:
			f = open(configurationFile, 'r')
		except:
			stderr("Could not open configuration file '"+configurationFile+"'. Default settings will be loaded")

		receiver = None #The receiver of the properties
		lastReceiver = None

		lineCount=0

		#Some values that have to be set
		sizeSet=False
		positionSet=False
		backgroundColorSet=False
		updateIntervalSet=False

		for line in f:
			lineCount+=1

			if(line.startswith("#")):
				continue #Line starts with '#', so it is a comment

			line=line.rstrip()
			line=line.lstrip()

			if(line==""):
				continue

			if(line.startswith("[")):
				#New receiver
				if not line.endswith("]"):
					stderr(configurationFile+", line "+str(lineCount)+": Syntax error: Expected ']' at the end of the line.\nSkipping...")
					continue

				#Add the last receiver to the window, because now there is a new one. The old one has finished its properties
				if(lastReceiver!="Widget" and lastReceiver!=None):
					self.putReceiverToWidget(lastReceiver)

				receiver = line[1:-1]

				#Add the new receiver to the list
				if(receiver!="Widget"):
					parts = receiver.split(',')
					if(len(parts)!=3):
						stderr(configurationFile+", line "+str(lineCount)+": Syntax error: Expected widget name, position x, position y for the widget initialization.\nSkipping...")
						continue
					receiver=parts[0]
					if(not representsInt(parts[1])):
						if(parts[1]!="middle"):
							stderr(configurationFile+", line "+str(lineCount)+": Syntax error: Expected widget name, position x, position y for the widget initialization.\nSkipping...")
							continue
					else:
						parts[1]=int(parts[1])
					if(not representsInt(parts[2])):
						if(parts[2]!="middle"):
							stderr(configurationFile+", line "+str(lineCount)+": Syntax error: Expected widget name, position x, position y for the widget initialization.\nSkipping...")
							continue
					else:
						parts[2]=int(parts[2])

					self.currentPosition=[parts[1], parts[2]]
					if receiver not in self.pantoflaWidgetManager.receivers:
						for widget in self.pantoflaWidgetManager.widgets:
							if receiver.startswith(widget.receiver):
								self.pantoflaWidgetManager.receivers[receiver]=widget.Widget(receiver, self.name, self)
								lastReceiver=receiver
								break

				continue

			#Remove the spaces between the property and the value
			if('=' in line):
				parts=line.split("=")
				if(len(parts)>=2):
					parts[0]=parts[0].rstrip()
					parts[0]=parts[0].lstrip()
					parts[1]=parts[1].lstrip()
					line=parts[0]+'='+parts[1]
					if(len(parts)>2):
						for i in range(2, len(parts)):
							line+='='+parts[i]

			if(receiver==None):
				stderr(configurationFile+", line "+str(lineCount)+": Unexpected command: I do not know the receiver of '"+line+"'.\nSkipping...")
				continue

			if(receiver=="Widget"):
				#The special receiver Widget
				if(line.startswith("position=")):
					parts=line.split("=")
					if(len(parts)!=2):
						stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'position': Format: position = x,y.\nSkipping...")
						continue
					coords=parts[1].split(",")
					if(len(coords)!=2):
						stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'position': Format: position = x,y.\nSkipping...")
						continue

					if((not representsInt(coords[0]) and coords[0]!="middle") or (not representsInt(coords[1]) and coords[1]!="middle")):
						stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'position': Format: position = x,y.\nSkipping...")
						continue
					if(coords[0]=="middle"):
						coords[0]=Defaults.widget.defaultScreen.get_width()/2-self.get_size()[0]/2
					if(coords[1]=="middle"):
						coords[1]=Defaults.widget.defaultScreen.get_height()/2-self.get_size()[1]/2

					self.move(int(coords[0]), int(coords[1]))
					positionSet=True

				elif(line.startswith("size=")):
					parts=line.split("=")
					if(len(parts)!=2):
						stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'size': Format: size = w,h.\nSkipping...")
						continue
					size=parts[1].split(",")
					if(len(size)!=2):
						stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'size': Format: size = w,h.\nSkipping...")
						continue

					if((not representsInt(size[0]) and size[0]!="half") or (not representsInt(size[1]) and size[1]!="half")):
						stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'size': Format: size = w,h.\nSkipping...")
						continue

					if(size[0]=="half"):
						size[0]=Defaults.widget.defaultScreen.get_width()/2
					if(size[1]=="half"):
						size[1]=Defaults.widget.defaultScreen.get_height()/2

					self.width = int(size[0])
					self.height = int(size[1])

					self.set_default_size(self.width, self.height)
					self.set_size_request(self.width, self.height)
					
					sizeSet=True

				elif(line.startswith("bgColor=")):
					parts=line.split("=")
					if(len(parts)!=2):
						stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'bgColor': Format: bgColor = R,G,B,A.\nSkipping...")
						continue
					values=parts[1].split(",")
					if(len(values)!=4):
						stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'bgColor': Format: bgColor = R,G,B,A.\nSkipping...")
						continue

					if(not representsInts(values[:-1]) or not representsFloat(values[-1])):
						stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'bgColor': Format: bgColor = R,G,B,A.\nSkipping...")
						continue

					if fadeIn:
						self.finalBgColor = [int(values[0]), int(values[1]), int(values[2]), float(values[3])]
					else:
						self.set_visual(self.rgbaVisual)
						self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(int(values[0]), int(values[1]), int(values[2]), float(values[3])))

					backgroundColorSet=True
				elif(line.startswith("border=")):
					parts=line.split("=")
					if(len(parts)!=2):
						stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'border': Format: border = px state color.\nSkipping...")
						return

					self.updateCss("border: "+parts[1]+";")
				elif(line.startswith("border-top=")):
					parts=line.split("=")
					if(len(parts)!=2):
						stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'border-top': Format: border-top = px.\nSkipping...")
						return

					self.updateCss("border-top: "+parts[1]+";")
				elif(line.startswith("border-right=")):
					parts=line.split("=")
					if(len(parts)!=2):
						stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'border-right': Format: border-right = px.\nSkipping...")
						return

					self.updateCss("border-right: "+parts[1]+";")
				elif(line.startswith("border-bottom=")):
					parts=line.split("=")
					if(len(parts)!=2):
						stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'border-bottom': Format: border-bottom = px.\nSkipping...")
						return

					self.updateCss("border-bottom: "+parts[1]+";")
				elif(line.startswith("border-left=")):
					parts=line.split("=")
					if(len(parts)!=2):
						stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'border-left': Format: border-left = px.\nSkipping...")
						return

					self.updateCss("border-left: "+parts[1]+";")
				elif(line.startswith("borderRadius=")):
					parts=line.split("=")
					if(len(parts)!=2):
						stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'borderRadius': Format: borderRadius = pixels/percentage.\nSkipping...")
						continue

					isPercentage=False

					if(parts[1].endswith("%")):
						if(representsInt(parts[1][:-1])):
							isPercentage=True
						else:
							stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'borderRadius': Format: borderRadius = pixels/percentage.\nSkipping...")
							continue
					elif not representsInt(parts[1]):
						stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'borderRadius': Format: borderRadius = pixels/percentage.\nSkipping...")
						continue

					if not isPercentage:
						self.updateCss("border-radius: "+parts[1]+"px;")
					else:
						self.updateCss("border-radius: "+parts[1]+";")
					
				elif(line.startswith("updateInterval=")):
					parts=line.split("=")
					if(len(parts)!=2):
						stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'updateInterval': Format: updateInterval = ms.\nSkipping...")
						continue
					if(not representsInt(parts[1])):
						stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'updateInterval': Format: updateInterval = ms.\nSkipping...")
						continue
					if(int(parts[1])<800):
						stderr(configurationFile+", line "+str(lineCount)+": Too small interval set for command 'updateInterval': Interval cannot be set less than 800. Setting to 800.")
						parts[1]=800
					self.pantoflaWidgetManager.setUpdateInterval(int(parts[1]))

					updateIntervalSet=True
				else:
					stderr(configurationFile+", line "+str(lineCount)+": Unknown command '"+line+"'")
			else:
				#The receiver is not 'Widget'
				self.commandForReceiver(receiver, line, lineCount, configurationFile)

		f.close()

		#Add the last receiver to the window. This is the last receiver as the file has ended
		if(lastReceiver!="Widget" and lastReceiver!=None):
			self.putReceiverToWidget(lastReceiver)

		#Set the default values to the ones that have to be set

		if not sizeSet:
			self.width = Defaults.widget.defaultWidth
			self.height = Defaults.widget.defaultHeight
			self.set_default_size(Defaults.widget.defaultWidth, Defaults.widget.defaultHeight)
			self.set_size_request(Defaults.widget.defaultWidth, Defaults.widget.defaultHeight)

		if not positionSet:
			self.move(Defaults.widget.defaultScreen.get_width()/2-self.get_size()[0]/2, Defaults.widget.defaultScreen.get_height()/2-self.get_size()[1]/2)

		if not backgroundColorSet:
			if fadeIn:
				self.finalBgColor = Defaults.widget.defaultBgColor
			else:
				self.set_visual(self.rgbaVisual)
				self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(Defaults.widget.defaultBgColor[0], Defaults.widget.defaultBgColor[1], Defaults.widget.defaultBgColor[2], Defaults.widget.defaultBgColor[3]))
		if not updateIntervalSet:
			self.pantoflaWidgetManager.setUpdateInterval(1000)

		#TO REMOVE START
		# self.YHeight=0
		# for child in self.fixed:
		# 	self.fixed.remove(child)
		# 	self.pantoflaWidgetManager.receivers={}
		# 	print "PERNAW1"
		# 	self.fixed.attach(Gtk.Label("Hello"+str(self.YHeight)), 0, self.YHeight, 1, 1)
		# 	self.YHeight+=1
		#TO REMOVE END

		self.pantoflaWidgetManager.applyCssToWidgets()

		self.pantoflaWidgetManager.startUpdating()

	def updateCss(self, newCss):
		self.currentCss.append(newCss)

	def applyCss(self):
		finalString=''
		for css in self.currentCss:
			finalString+=css
		self.styleProvider.load_from_data("""
			#"""+self.name+""" {
				"""+finalString+"""
			}
		""")