#!/usr/bin/env python

from gi.repository import GObject, Gtk, Gdk

import Defaults.widget, Tools.SubWidgetManager, Dialogs.customize

from Tools.output import *
from Tools.simplemath import *

class Widget(Gtk.Window):

	def __init__(self, name, configurationFile):
		Gtk.Window.__init__(self,
			accept_focus=False, skip_pager_hint=True,
			skip_taskbar_hint=True, decorated=False,
			deletable=False, focus_on_map=False,
			focus_visible=False, has_resize_grip=False,
			type_hint=Gdk.WindowTypeHint.DOCK)
		
		#Set the window properties to look like a gadget. These cannot be changed through the configuration file
		self.stick()
		self.set_name(name)
		self.name = name
		self.GUIName = name
		self.set_wmclass(Defaults.widget.wmClass, Defaults.widget.wmClass)
		self.set_keep_below(True)
		#self.set_sensitive(False)

		self.rgbaVisual = self.get_screen().get_rgba_visual()

		self.pantoflaWidgetManager = Tools.SubWidgetManager.SubWidgetManager()

		self.styleProvider = Gtk.CssProvider()
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

		self.currentCss={}

		self.fixed = Gtk.Fixed()
		self.fixed.set_name(self.name+'Fixed')
		self.currentPosition=[]
		self.customizeDialogShown=False

		self.add(self.fixed)

		self.createMenu()

		self.confFile=configurationFile

		self.initializeSettings()

		self.applyConfigurationFile()

		self.set_resizable(False)

	def initializeSettings(self):
		self.finalSettings = {}
		self.finalSettings['size'] = [[Defaults.widget.defaultWidth, Defaults.widget.defaultHeight], None]
		self.finalSettings['position'] = [[Defaults.widget.defaultScreen.get_width()/2-self.get_size()[0]/2, Defaults.widget.defaultScreen.get_height()/2-self.get_size()[1]/2], None]
		self.finalSettings['name'] = ['PantoflaWidget', None]
		self.finalSettings['background-color'] = ['rgba(0,0,0,0.5)', None]
		self.finalSettings['border'] = ['none', None]
		self.finalSettings['border-top'] = ['none', None]
		self.finalSettings['border-right'] = ['none', None]
		self.finalSettings['border-bottom'] = ['none', None]
		self.finalSettings['border-left'] = ['none', None]
		self.finalSettings['border-radius'] = ['3px', None]
		self.finalSettings['update-interval'] = [1000, None]

	def applySettings(self):
		self.width = self.finalSettings['size'][0][0]
		self.height = self.finalSettings['size'][0][0]
		self.set_default_size(self.width, self.height)
		self.set_size_request(self.width, self.height)

		self.move(self.finalSettings['position'][0][0], self.finalSettings['position'][0][1])

		self.GUIName = self.finalSettings['name'][0]

		values = rgbaToValues(self.finalSettings['background-color'][0])
		self.set_visual(self.rgbaVisual)
		self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(int(values[0]), int(values[1]), int(values[2]), float(values[3])))

		self.updateCss('border', self.finalSettings['border'][0])
		self.updateCss('border-top', self.finalSettings['border-top'][0])
		self.updateCss('border-right', self.finalSettings['border-right'][0])
		self.updateCss('border-bottom', self.finalSettings['border-bottom'][0])
		self.updateCss('border-left', self.finalSettings['border-left'][0])
		self.updateCss('border-radius', self.finalSettings['border-radius'][0])

		self.pantoflaWidgetManager.setUpdateInterval(self.finalSettings['update-interval'][0])


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
		self.pantoflaWidgetManager.receivers[receiver].setPos(x, y)
		self.fixed.put(self.pantoflaWidgetManager.receivers[receiver].widget(), x, y)

	def moveChild(self, widget, x, y):
		self.fixed.move(widget, x, y)

	def runCommand(self, key, value, lineCount, configurationFile):
		#The special receiver Widget
		if(key == 'position'):
			coords = value.split(',')
			if(len(coords)!=2):
				stderr(configurationFile+', line '+str(lineCount)+': Badly formatted command \'position\': Format: position = x,y.\nSkipping...')
				return

			if((not representsInt(coords[0]) and coords[0]!='middle') or (not representsInt(coords[1]) and coords[1]!='middle')):
				stderr(self.confFile+', line '+str(lineCount)+': Badly formatted command \'position\': Format: position = x,y.\nSkipping...')
				return

			if(coords[0]=='middle'):
				coords[0]=Defaults.widget.defaultScreen.get_width()/2-self.get_size()[0]/2
			if(coords[1]=='middle'):
				coords[1]=Defaults.widget.defaultScreen.get_height()/2-self.get_size()[1]/2


			self.finalSettings['position'][0] = [ int(coords[0]), int(coords[1]) ]

		elif(key == 'size'):
			size=value.split(',')
			if(len(size)!=2):
				stderr(configurationFile+', line '+str(lineCount)+': Badly formatted command \'size\': Format: size = w,h.\nSkipping...')
				return

			if((not representsInt(size[0]) and size[0]!='half') or (not representsInt(size[1]) and size[1]!='half')):
				stderr(configurationFile+', line '+str(lineCount)+': Badly formatted command \'size\': Format: size = w,h.\nSkipping...')
				return

			if(size[0]=='half'):
				size[0]=Defaults.widget.defaultScreen.get_width()/2
			if(size[1]=='half'):
				size[1]=Defaults.widget.defaultScreen.get_height()/2

			self.finalSettings['size'][0] = [ int(size[0]), int(size[1]) ]
		elif(key == 'name'):
			self.finalSettings['name'][0] = value.rstrip().lstrip()
		elif(key == 'background-color'):
			self.finalSettings['background-color'][0] = value
		elif(key == 'border'):
			self.finalSettings['border'][0] = value
		elif(key == 'border-top'):
			self.finalSettings['border-top'][0] = value
		elif(key == 'border-right'):
			self.finalSettings['border-right'][0] = value
		elif(key == 'border-bottom'):
			self.finalSettings['border-bottom'][0] = value
		elif(key == 'border-left'):
			self.finalSettings['border-left'][0] = value
		elif(key == 'border-radius'):
			self.finalSettings['border-radius'][0] = value
		elif(key == 'update-interval'):
			if(not representsInt(parts[1])):
				stderr(configurationFile+', line '+str(lineCount)+': Badly formatted command \'update-interval\': Format: update-interval = ms.\nSkipping...')
				return
			if(int(value)<800):
				stderr(configurationFile+', line '+str(lineCount)+': Too small interval set for command \'update-interval\': Interval cannot be set less than 800. Setting to 800.')
				value=800
			self.finalSettings['update-interval'] = int(value)
		else:
			stderr(configurationFile+', line '+str(lineCount)+': Unknown command.')

	def commandForReceiver(self, receiver, command, lineCount):
		'''Sends the command (property) to the appropriate widget (receiver)'''
		parts=command.split('=')
		key=parts[0]
		value=command[len(key)+1:]

		if receiver == 'Widget':
			#the widget itself is the receiver of the command
			self.runCommand(key, value, lineCount, self.confFile)
			return

		#some other subwidget is the receiver of the command

		if receiver not in self.pantoflaWidgetManager.receivers:
			for widget in self.pantoflaWidgetManager.widgets:
				if receiver.rstrip('1234567890')==widget.receiver:
					self.pantoflaWidgetManager.receivers[receiver]=widget.Widget(receiver, self.name, self)
					self.pantoflaWidgetManager.receivers[receiver].runCommand(key, value, lineCount, self.confFile)
					break
		else:
			self.pantoflaWidgetManager.receivers[receiver].runCommand(key, value, lineCount, self.confFile)

	def applyConfigurationFile(self):
		try:
			f = open(self.confFile, 'r')
		except:
			stderr('Could not open configuration file ''+self.confFile+''. Default settings will be loaded')

		receiver = None #The receiver of the properties
		lastReceiver = None

		lineCount=0

		for command in f:
			lineCount+=1

			command=command.rstrip()
			command=command.lstrip()

			if(command.startswith('#')):
				continue #Line starts with '#', so it is a comment

			if(command == ''):
				continue

			if(command.startswith('[')):
				#New receiver
				if not command.endswith(']'):
					stderr(self.confFile+', line '+str(lineCount)+': Syntax error: Expected \']\' at the end of the line.\nSkipping...')
					continue

				#Add the last receiver to the window, because now there is a new one. The old one has finished its properties
				if(lastReceiver!='Widget' and lastReceiver!=None):
					self.putReceiverToWidget(lastReceiver)

				receiver = command[1:-1]

				#Add the new receiver to the list
				if(receiver!='Widget'):
					parts = receiver.split(',')
					if(len(parts)!=3):
						stderr(self.confFile+', line '+str(lineCount)+': Syntax error: Expected widget name, position x, position y for the widget initialization.\nSkipping...')
						continue
					receiver=parts[0]
					if(not representsInt(parts[1])):
						parts[1]=parts[1].rstrip().lstrip()
						if(parts[1]!='middle'):
							stderr(self.confFile+', line '+str(lineCount)+': Syntax error: Expected widget name, position x, position y for the widget initialization.\nSkipping...')
							continue
					else:
						parts[1]=int(parts[1])
					if(not representsInt(parts[2])):
						parts[2]=parts[2].rstrip().lstrip()
						if(parts[2]!='middle'):
							stderr(self.confFile+', line '+str(lineCount)+': Syntax error: Expected widget name, position x, position y for the widget initialization.\nSkipping...')
							continue
					else:
						parts[2]=int(parts[2])

					self.currentPosition=[parts[1], parts[2]]
					if receiver not in self.pantoflaWidgetManager.receivers:
						for widget in self.pantoflaWidgetManager.widgets:
							if receiver.rstrip('1234567890')==widget.receiver:
								self.pantoflaWidgetManager.receivers[receiver]=widget.Widget(receiver, self.name, self)
								lastReceiver=receiver
								break

				continue

			#Remove the spaces between the property and the value
			if('=' in command):
				parts=command.split('=')
				if(len(parts)>=2):
					parts[0]=parts[0].rstrip()
					parts[0]=parts[0].lstrip()
					parts[1]=parts[1].lstrip()
					command=parts[0]+'='+parts[1]
					if(len(parts)>2):
						for i in range(2, len(parts)):
							command+='='+parts[i]

			if(receiver == None):
				stderr(self.confFile+', line '+str(lineCount)+': Unexpected command: I do not know the receiver of ''+line+''.\nSkipping...')
				continue

			self.commandForReceiver(receiver, command, lineCount)

		f.close()

		#Add the last receiver to the window. This is the last receiver as the file has ended
		if(lastReceiver!='Widget' and lastReceiver!=None):
			self.putReceiverToWidget(lastReceiver)

		self.applySettings()
		self.applyCss()

		self.pantoflaWidgetManager.callWidgetsInitial()
		self.show_all()
		self.hide()
		self.pantoflaWidgetManager.startUpdating()

		GObject.timeout_add(1000, self.checkWidgetsReady)
		self.checkWidgetsReady()

	def writeSettingsFile(self):
		#get the settings from each widget and save them to the configuration file
		try:
			confF = open(self.confFile, 'w');
		except:
			stderr('Could not write to '+self.confFile+' the applied changes!')
			return False

		#write self settings first

		for receiver in self.pantoflaWidgetManager.receivers:
			confF.write('['+receiver+','+str(self.pantoflaWidgetManager.receivers[receiver].x)+','+str(self.pantoflaWidgetManager.receivers[receiver].y)+']')
			confF.write('\n')
			#copy over only the first array item, aka only the normal preserved value, not the (possibly) edited one
			for key in self.pantoflaWidgetManager.receivers[receiver].settingsObj.settingsToWrite:
				confF.write(key+' = '+self.pantoflaWidgetManager.receivers[receiver].settingsObj.settingsToWrite[key])
				confF.write('\n')
		confF.close()
		return True

	def checkWidgetsReady(self):
		atLeastOneNotReady=False
		for receiver in self.pantoflaWidgetManager.receivers:
			if(not self.pantoflaWidgetManager.receivers[receiver].readyShow):
				atLeastOneNotReady=True
		if atLeastOneNotReady:
			return True #call again until ready
		else:
			self.show()
			return False #all widgets ready

	def updateCss(self, key, value, name=None):
		if(name is None):
			name=self.name
		if name not in self.currentCss:
			self.currentCss[name]={}
		key=key.rstrip(); key=key.lstrip()
		value=value.rstrip(); value=value.lstrip()

		if key not in self.currentCss[name]:
			self.currentCss[name][key]={}

		self.currentCss[name][key]['value']=value

	def applyCss(self):
		finalString=''
		for name in self.currentCss:
			if(len(self.currentCss[name])>0):
				finalString+='#'+name+' { '
				for key in self.currentCss[name]:
					finalString+=key+' : '+self.currentCss[name][key]['value']+'; '
				finalString+='} '

		if(finalString!=''):
			self.styleProvider.load_from_data(finalString.encode())

	def createMenu(self):
		self.menu=Gtk.Menu()
		item = Gtk.MenuItem.new_with_mnemonic('Customize')
		item.connect('activate', self.showCustomizeDialog)
		self.menu.append(item)
		self.menu.show_all()

		self.connect('button_press_event', self.popupHandler, self.menu)
		
	def popupHandler(self, widget, event, menu):
		if( event.button != Gdk.BUTTON_SECONDARY ):
			return
		menu.popup(None, None, None, Gdk.BUTTON_SECONDARY, event.button, event.time)

	def showCustomizeDialog(self, widget):
		if self.customizeDialogShown:
			return
		#construct the customize dialog
		self.customizeDialogShown=True
		customizeDialog = Dialogs.customize.Customize(self.GUIName, self.confFile, self)
		#add each widget's customization options into the customize dialog
		for widgetName in self.pantoflaWidgetManager.receivers:
			customizeDialog.addControllingWidget(self.pantoflaWidgetManager.receivers[widgetName])
		customizeDialog.showWidgets()