#!/usr/bin/env python

from gi.repository import GObject, Gtk, Gdk

import Defaults.widget, Tools.SubWidgetManager, Dialogs.customize

from Tools.output import *
from Tools.simplemath import *
from Tools.operations import *

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

		self.confFile = configurationFile

		self.sm = Settings(self)

		self.connect('check-resize', self.setDimensions)

		self.applyConfigurationFile()

		self.set_resizable(False)
		self.set_keep_below(True)

	def setDimensions(self, widget):
		self.width, self.height = widget.get_size_request()

	def applySettings(self):
		self.width = self.sm.values['size'][0][0]
		self.height = self.sm.values['size'][0][0]
		self.set_default_size(self.width, self.height)
		self.set_size_request(self.width, self.height)

		if self.sm.values['position'][0][0] == 'middle':
			self.x = Defaults.widget.defaultScreen.get_width()/2-self.get_size()[0]/2
		else:
			self.x = self.sm.values['position'][0][0]
		if self.sm.values['position'][0][1] == 'middle':
			self.y =  Defaults.widget.defaultScreen.get_height()/2-self.get_size()[1]/2
		else:
			self.y = self.sm.values['position'][0][1]

		self.move(self.x, self.y)

		self.GUIName = self.sm.values['name'][0]

		self.setBackgroundColorFrom(self.sm.values['background-color'][0])

		self.updateCss('border', self.sm.values['border'][0])
		self.updateCss('border-top', self.sm.values['border-top'][0])
		self.updateCss('border-right', self.sm.values['border-right'][0])
		self.updateCss('border-bottom', self.sm.values['border-bottom'][0])
		self.updateCss('border-left', self.sm.values['border-left'][0])
		self.updateCss('border-radius', self.sm.values['border-radius'][0])

		self.pantoflaWidgetManager.setUpdateInterval(self.sm.values['update-interval'][0])

	def setBackgroundColorFrom(self, cssColor):
		values = rgbaToValues(cssColor)
		self.set_visual(self.rgbaVisual)
		self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(float(values[0])/255.0, float(values[1])/255.0, float(values[2])/255.0, float(values[3])))

	def putReceiverToWidget(self, receiver):
		x, y = 0, 0
		if(not representsInt(self.currentPosition[0])):
			self.pantoflaWidgetManager.receivers[receiver].sm.values['position'][0][0] = 'middle'
		else:
			x = self.currentPosition[0]
			self.pantoflaWidgetManager.receivers[receiver].sm.values['position'][0][0] = x
		if(not representsInt(self.currentPosition[1])):
			self.pantoflaWidgetManager.receivers[receiver].sm.values['position'][0][1] = 'middle'
		else:
			y = self.currentPosition[1]
			self.pantoflaWidgetManager.receivers[receiver].sm.values['position'][0][1] = y
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

			print 'Via reading the settings file, I concluded that position is', int(coords[0]), int(coords[1])
			self.sm.values['position'][0] = [ int(coords[0]), int(coords[1]) ]

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

			self.sm.values['size'][0] = [ int(size[0]), int(size[1]) ]
		elif(key == 'name'):
			self.sm.values['name'][0] = value.rstrip().lstrip()
		elif(key == 'background-color'):
			self.sm.values['background-color'][0] = value
		elif(key == 'border'):
			self.sm.values['border'][0] = value
		elif(key == 'border-top'):
			self.sm.values['border-top'][0] = value
		elif(key == 'border-right'):
			self.sm.values['border-right'][0] = value
		elif(key == 'border-bottom'):
			self.sm.values['border-bottom'][0] = value
		elif(key == 'border-left'):
			self.sm.values['border-left'][0] = value
		elif(key == 'border-radius'):
			self.sm.values['border-radius'][0] = value
		elif(key == 'update-interval'):
			if(not representsInt(value)):
				stderr(configurationFile+', line '+str(lineCount)+': Badly formatted command \'update-interval\': Format: update-interval = ms.\nSkipping...')
				return
			if(int(value)<800):
				stderr(configurationFile+', line '+str(lineCount)+': Too small interval set for command \'update-interval\': Interval cannot be set less than 800. Setting to 800.')
				value=800
			self.sm.values['update-interval'][0] = int(value)
		else:
			stderr(configurationFile+', line '+str(lineCount)+': Unknown command.')

	def commandForReceiver(self, receiver, command, lineCount):
		'''Sends the command (property) to the appropriate widget (receiver)'''
		parts=command.split('=')
		key=parts[0]
		value=command[len(key)+1:]

		if(value == ''):
			value = None

		if receiver == 'Widget':
			#the widget itself is the receiver of the command
			self.runCommand(key, value, lineCount, self.confFile)
			return

		#some other subwidget is the receiver of the command

		if receiver not in self.pantoflaWidgetManager.receivers:
			for widget in self.pantoflaWidgetManager.widgets:
				if receiver.rstrip('1234567890')==widget.receiver:
					if not receiver in self.pantoflaWidgetManager.receivers:
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

				receiver = command[1:-1].rstrip().lstrip()

				#Add the new receiver to the list
				if(receiver!='Widget'):
					parts = receiver.split(',')
					if(len(parts)!=3):
						stderr(self.confFile+', line '+str(lineCount)+': Syntax error: Expected widget name, position x, position y for the widget initialization.\nSkipping...')
						continue
					receiver=parts[0].rstrip().lstrip()
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
							if receiver.rstrip('1234567890') == widget.receiver:
								if not receiver in self.pantoflaWidgetManager.receivers:
									self.pantoflaWidgetManager.receivers[receiver]=widget.Widget(receiver, self.name, self)
								lastReceiver = receiver
								break

				continue

			#Remove the spaces between the property and the value
			if('=' in command):
				parts=command.split('=')
				if(len(parts)>=2):
					parts[0]=parts[0].rstrip().lstrip()
					parts[1]=parts[1].rstrip().lstrip()
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

		confF.write('[Widget]')
		confF.write('\n')

		for key in self.sm.settingsToWrite:
			confF.write(key+' = '+self.sm.settingsToWrite[key])
			confF.write('\n')
		self.sm = None

		for receiver in self.pantoflaWidgetManager.receivers:
			confF.write('\n')

			x = None; y = None
			if representsInt(self.pantoflaWidgetManager.receivers[receiver].sm.values['position'][0][0]):
				x = str(int(self.pantoflaWidgetManager.receivers[receiver].sm.values['position'][0][0]))
			else:
				x = self.pantoflaWidgetManager.receivers[receiver].sm.values['position'][0][0]
			if representsInt(self.pantoflaWidgetManager.receivers[receiver].sm.values['position'][0][1]):
				y = str(int(self.pantoflaWidgetManager.receivers[receiver].sm.values['position'][0][1]))
			else:
				y = self.pantoflaWidgetManager.receivers[receiver].sm.values['position'][0][1]

			confF.write('['+receiver+', '+x+', '+y+']')
			confF.write('\n')
			#copy over only the first array item, aka only the normal preserved value, not the (possibly) edited one
			for key in self.pantoflaWidgetManager.receivers[receiver].sm.settingsToWrite:
				confF.write(key+' = '+self.pantoflaWidgetManager.receivers[receiver].sm.settingsToWrite[key])
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
			self.set_keep_below(True)
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
		self.customizeDialogShown = True
		customizeDialog = Dialogs.customize.Customize(self.GUIName, self.confFile, self)
		#add each widget's customization options into the customize dialog
		for widgetName in self.pantoflaWidgetManager.receivers:
			customizeDialog.addControllingWidget(self.pantoflaWidgetManager.receivers[widgetName])
		customizeDialog.showWidgets()

	def settings(self):
		return self.sm.getSettingsWidgets()

class Settings():
	def __init__(self, parent):
		self.parent = parent
		self.values = {}
		self.values['size'] = [[Defaults.widget.defaultWidth, Defaults.widget.defaultHeight], None]
		self.values['position'] = [['middle', 'middle'], None]
		self.values['name'] = ['PantoflaWidget', None]
		self.values['background-color'] = ['rgba(0, 0, 0, 0.5)', None]
		self.values['border'] = ['none', None]
		self.values['border-top'] = ['none', None]
		self.values['border-right'] = ['none', None]
		self.values['border-bottom'] = ['none', None]
		self.values['border-left'] = ['none', None]
		self.values['border-radius'] = ['3px', None]
		self.values['update-interval'] = [1000, None]

	def getSettingsWidgets(self):

		#One row is the Label button to show/hide the options of it and the other row is another listbox with the options
		rowArray = []

		#listbox to hold the settings
		self.listBox = Gtk.ListBox()
		self.listBox.set_hexpand(True)
		self.listBox.set_vexpand(True)
		self.listBox.set_selection_mode(Gtk.SelectionMode.NONE)

		row = Gtk.ListBoxRow()

		button = Gtk.Button.new_with_label('')
		button.get_child().set_markup('<b>-- '+self.parent.GUIName+' Widget --</b>')
		button.set_hexpand(True)
		button.connect('clicked', self.showOptions)

		row.add(button)
		rowArray.append(row)

		row = Gtk.ListBoxRow()
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
		
		label = Gtk.Label('Position', xalign=0)
		hbox.pack_start(label, True, True, 0)

		hbox.pack_start(Gtk.Label('X'), False, True, 0)

		spinbox = Gtk.SpinButton.new_with_range(0, 5000, 1)
		spinbox.set_value(self.parent.x)
		spinbox.connect('value-changed', self.settingsPositionXChanged)
		spinbox.props.valign = Gtk.Align.CENTER

		hbox.pack_start(spinbox, False, True, 0)

		hbox.pack_start(Gtk.Label('Y'), False, True, 0)

		spinbox = Gtk.SpinButton.new_with_range(0, 5000, 1)
		spinbox.set_value(self.parent.y)
		spinbox.connect('value-changed', self.settingsPositionYChanged)
		spinbox.props.valign = Gtk.Align.CENTER

		hbox.pack_start(spinbox, False, True, 0)

		row.add(hbox)
		self.listBox.add(row)

		row = Gtk.ListBoxRow()
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
		
		hbox.pack_start(Gtk.Label('Background color'), False, True, 0)
		button = Gtk.ColorButton.new_with_rgba(colorValueToRgba(self.values['background-color'][0]))
		button.set_use_alpha(True)
		button.connect('color-set', self.getSelectedColor)
		button.props.valign = Gtk.Align.CENTER
		
		hbox.pack_start(button, True, True, 0)

		row.add(hbox)
		self.listBox.add(row)

		row = Gtk.ListBoxRow()
		self.listBox.hide()
		row.add(self.listBox)
		rowArray.append(row)

		return rowArray

	def showOptions(self, widget):
		if(self.listBox.is_visible()):
			self.listBox.hide()
		else:
			self.listBox.show()

	def getSelectedColor(self, widget):
		rgb=widget.get_color()
		a=str(widget.get_alpha()/65535.0)
		value = 'rgba('+str(rgb.red/257.0)+', '+str(rgb.green/257.0)+', '+str(rgb.blue/257.0)+', '+a+')'
		self.values['background-color'][1] = value
		self.parent.setBackgroundColorFrom(value)
		# self.parent.updateCss('background-color', value)
		# self.values['background-color'][1] = value
		# self.parent.applyCss()

	def settingsPositionXChanged(self, widget):
		self.parent.x = int(widget.get_value())
		self.values['position'][1] = [self.parent.x, self.parent.y]
		print "Moving from settings", self.parent.x, self.parent.y
		self.parent.move(self.parent.x, self.parent.y)

	def settingsPositionYChanged(self, widget):
		self.parent.y = int(widget.get_value())
		self.values['position'][1] = [self.parent.x, self.parent.y]
		self.parent.move(self.parent.x, self.parent.y)
		print "Moving from settings", self.parent.x, self.parent.y

	def afterSettingsPlacement(self):
		self.listBox.hide()

	def resetSettings(self):
		for key in self.values:
			self.values[key][1] = None
		self.parent.applySettings();
		self.parent.applyCss();

	def saveSettings(self):
		self.settingsToWrite = { }

		for key in self.values:
			if self.values[key][1] != None:
				#key has been edited, copy it over
				self.values[key][0] = self.values[key][1]

			#reset edited value
			self.values[key][1] = None
			self.settingsToWrite[key] = stringifySettings(key, self.values[key][0])

		self.parent.applySettings()