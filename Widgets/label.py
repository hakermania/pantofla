#!/usr/bin/env python
receiver='Label'

from gi.repository import Gtk, Gdk, Pango

import Defaults.widget

from Tools.output import *
from Tools.simplemath import *
from Tools.operations import *
from multiprocessing.pool import ThreadPool

class Widget():
	def __init__(self, name, parentName, parent):
		self.parent=parent
		self.label=Gtk.Label()
		self.GUIName=name
		self.name=parentName+name
		self.label.set_name(self.name)

		self.sm = Settings(self)

		self.styleProvider=Gtk.CssProvider()
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

		self.currentCss={}

		self.frame=Gtk.Frame()
		self.frame.set_shadow_type(Gtk.ShadowType(Gtk.ShadowType.NONE))
		self.frameName=self.name+'Frame'
		self.frame.set_name(self.frameName)
		self.frame.add(self.label)

		self.cssClear = [ self.name, self.frameName ]

		self.updateCss('background-color', 'rgba(0, 0, 0, 0)', self.frameName)

		self.frame.connect('destroy', self.destroyed)
		self.label.connect('size-allocate', self.getSize)

		self.readyShow = True
		self.function = None
		self.functionIndex = -1
		self.niceFunction = None
		self.functionData = None
		self.pool = None
		self.cssApplied = False
		self.isMonitoringSize = False

		self.width, self.height = self.frame.get_size_request()

	def getSize(self, widget, allocation):
		if not self.cssApplied:
			return
		self.width = allocation.width
		self.height = allocation.height

		if(self.sm.values['position'][0][0] == 'middle' or self.sm.values['position'][0][1] == 'middle'):
			self.moveMe(self.sm.values['position'][0]) #todo is this needed? <--
			self.monitorSize(True)

	def gadgetResize(self, widget, cairoRectangle=None):
		"""Called when the Gadget where this widget is placed is resized in order to center it"""

		try:
			x, y = self.frame.translate_coordinates(self.parent, 0, 0)
		except:
			return
		
		midx = int((self.parent.width-self.width)/2.0)
		midy = int((self.parent.height-self.height)/2.0)

		if (self.sm.values['position'][0][0] == 'middle' and midx != x) or (self.sm.values['position'][0][1] == 'middle' and midy != y):
			self.moveMe(self.sm.values['position'][0])

	def monitorSize(self, monitor):
		if(monitor):
			if self.isMonitoringSize:
				return
			self.isMonitoringSize = True
			self.parent.connect('check-resize', self.gadgetResize)
			self.frame.connect('size-allocate', self.gadgetResize)
		else:
			if not self.isMonitoringSize:
				return
			self.isMonitoringSize = False
			self.parent.disconnect_by_func(self.gadgetResize)
			self.frame.disconnect_by_func(self.gadgetResize)

	def destroyed(self, widget):
		for name in self.cssClear:
			self.styleProvider.load_from_data('#'+name+' { } ')

	def update(self):
		if(self.function==None):
			return
		if(self.functionData==None):
			#first time claiming data
			self.functionData=self.pool.apply_async(self.function)
		elif(self.functionData.ready()):
			self.readyShow = True
			#data is ready for presenation
			if(self.niceFunction==0):
				self.label.set_text(str(self.functionData.get()))
			else:
				self.label.set_text(str(self.niceFunction(self.functionData.get())))
			self.functionData=self.pool.apply_async(self.function)

	def runCommand(self, key, value, lineCount, configurationFile):
		if(key == 'text'):
			self.sm.values['text'][0] = value
		elif(key == 'size'):
			size=value.split(',')
			self.sm.values['size'][0] = [int(size[0]), int(size[1])]
		elif(key == 'align'):
			if(value == 'right'):
				self.sm.values['align'][0] = Gtk.Align.END
			elif(value == 'left'):
				self.sm.values['align'][0] = Gtk.Align.START
			else:
				stderr(configurationFile+', line '+str(lineCount)+': Badly formatted command "align": Format: align = left/right.\nSkipping...')
				return
		elif(key == 'font'):
			self.sm.values['font'][0] = value
		elif(key == 'color'):
			self.updateCss('color', value)
			self.sm.values['color'][0] = value
		elif(key == 'border'):
			self.updateCss('border', value)
			self.sm.values['border'][0] = value
		elif(key == 'border-top'):
			self.updateCss('border-top', value)
			self.sm.values['border-top'][0] = value
		elif(key == 'border-right'):
			self.updateCss('border-right', value)
			self.sm.values['border-right'][0] = value
		elif(key == 'border-bottom'):
			self.updateCss('border-bottom', value)
			self.sm.values['border-bottom'][0] = value
		elif(key == 'border-left'):
			self.updateCss('border-left', value)
			self.sm.values['border-left'][0] = value
		elif(key == 'function'):
			self.sm.values['function'][0] = value
		elif(key == 'position'):
			return
		else:
			stderr(configurationFile+', line '+str(lineCount)+': Unknown command.')

	def enableFunction(self, value, modified=None):
		if(modified == None):
			modified = False
		else:
			#function has been modified from the settings
			self.sm.values['function'][1] = value
		if(value=='networkUp'):
			from Tools.network import networkUp, dataToNiceString
			self.function=networkUp
			self.niceFunction=dataToNiceString
			self.functionIndex=0
		elif(value=='networkDown'):
			from Tools.network import networkDown, dataToNiceString
			self.function=networkDown
			self.niceFunction=dataToNiceString
			self.functionIndex=1
		elif(value=='networkTotalUp'):
			from Tools.network import networkTotalUp, dataToNiceString
			self.function=networkTotalUp
			self.niceFunction=dataToNiceString
			self.functionIndex=2
		elif(value=='networkTotalDown'):
			from Tools.network import networkTotalDown, dataToNiceString
			self.function=networkTotalDown
			self.niceFunction=dataToNiceString
			self.functionIndex=3
		elif(value=='cpuPercent'):
			from Tools.hardware import cpuPercent, percentToNiceString
			self.function=cpuPercent
			self.niceFunction=percentToNiceString
			self.functionIndex=4
		elif(value=='ramPercent'):
			from Tools.hardware import ramPercent, percentToNiceString
			self.function=ramPercent
			self.niceFunction=percentToNiceString
			self.functionIndex=5
		elif(value=='hddPercent'):
			from Tools.hardware import hddPercent, percentToNiceString
			self.function=hddPercent
			self.niceFunction=percentToNiceString
			self.functionIndex=6
		elif(value=='upTime'):
			from Tools.hardware import upTime, timeToNiceString
			self.function=upTime
			self.niceFunction=timeToNiceString
			self.functionIndex=7
		else:
			self.function = None
			self.niceFunction = None
			self.functionIndex = -1
			return False

		self.readyShow = False #functions do some time to gather data
		self.functionData = None
		self.pool = ThreadPool(processes=1)
		return True

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

	def moveMe(self, point):
		x, y = 0, 0
		if point[0] == 'middle':
			x = (self.parent.width - self.width) / 2
		else:
			x = point[0]
		if point[1] == 'middle':
			y = (self.parent.height - self.height) / 2
		else:
			y = point[1]

		self.parent.moveChild(self.frame, x, y)

	def applySettings(self):
		if not self.enableFunction(self.sm.values['function'][0]):
			#no function enabled, so add the text instead :D
			self.label.set_text(self.sm.values['text'][0])
		self.frame.set_size_request(self.sm.values['size'][0][0],self.sm.values['size'][0][1])

		self.moveMe(self.sm.values['position'][0])

		self.label.set_halign(self.sm.values['align'][0])
		self.updateCss('font', self.sm.values['font'][0])
		self.updateCss('color', self.sm.values['color'][0])
		self.updateCss('border', self.sm.values['border'][0])
		self.updateCss('border-top', self.sm.values['border-top'][0])
		self.updateCss('border-right', self.sm.values['border-right'][0])
		self.updateCss('border-bottom', self.sm.values['border-bottom'][0])
		self.updateCss('border-left', self.sm.values['border-left'][0])
		

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

	def initial(self):
		self.applySettings()
		self.applyCss()
		self.cssApplied=True

	def widget(self):
		return self.frame

	def settings(self):
		return self.sm.getSettingsWidgets()

class Settings():
	def __init__(self, parent):
		self.parent = parent
		self.functionNamesStore = Gtk.ListStore(str)
		for name in [
			'Network Up', 'Network Down', 'Network Total Up', 'Network Total Down', 'Cpu Percent',
			'Ram Percent', 'HDD Percent', 'Uptime'
			]:
			self.functionNamesStore.append([name])

		#default settings values
		self.values = {}
		self.values['text'] = ['Hello, World!', None]
		self.values['position'] =[['middle','middle'], None]
		self.values['size'] = [[1, 1], None]
		self.values['align'] = [Gtk.Align.START, None]
		self.values['font'] = ['Ubuntu 20', None]
		self.values['color'] = ['rgba(255, 255, 255, 1)', None]
		self.values['border'] = ['none', None]
		self.values['border-top'] = ['none', None]
		self.values['border-right'] = ['none', None]
		self.values['border-bottom'] = ['none', None]
		self.values['border-left'] = ['none', None]
		self.values['function'] = [None, None]
		

	def getSettingsWidgets(self):

		#One row is the Label button to show/hide the options of it and the other row is another listbox with the options
		rowArray = []
		
		#this listbox holds all the settings of the widget
		self.listBox = Gtk.ListBox()
		self.listBox.set_hexpand(True)
		self.listBox.set_vexpand(True)
		self.listBox.set_selection_mode(Gtk.SelectionMode.NONE)

		row = Gtk.ListBoxRow()

		button = Gtk.Button.new_with_label('')
		button.get_child().set_markup('<b>-- '+self.parent.GUIName+' --</b>')
		button.set_hexpand(True)
		button.connect('clicked', self.showOptions)

		row.add(button)
		rowArray.append(row)

		row = Gtk.ListBoxRow()
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
		
		label = Gtk.Label('Position', xalign=0)
		hbox.pack_start(label, True, True, 0)

		hbox.pack_start(Gtk.Label('X'), False, True, 0)

		self.checkBoxXMiddle = Gtk.CheckButton('Middle')
		self.checkBoxXMiddle.set_active(self.values['position'][0][0] == 'middle')
		self.checkBoxXMiddle.connect('toggled', self.labelXMiddle)

		hbox.pack_start(self.checkBoxXMiddle, False, True, 0)

		self.spinboxPosX = Gtk.SpinButton.new_with_range(0, 5000, 1)
		self.spinboxPosX.set_value(self.positionToValue(self.values['position'][0][0]))
		self.spinboxPosX.connect('value-changed', self.settingsPositionXChanged)
		self.spinboxPosX.props.valign = Gtk.Align.CENTER

		hbox.pack_start(self.spinboxPosX, False, True, 0)

		hbox.pack_start(Gtk.Label('Y'), False, True, 0)

		self.checkBoxYMiddle = Gtk.CheckButton('Middle')
		self.checkBoxYMiddle.set_active(self.values['position'][0][1] == 'middle')
		self.checkBoxYMiddle.connect('toggled', self.labelYMiddle)

		hbox.pack_start(self.checkBoxYMiddle, False, True, 0)

		self.spinboxPosY = Gtk.SpinButton.new_with_range(0, 5000, 1)
		self.spinboxPosY.set_value(self.positionToValue(self.values['position'][0][1]))
		self.spinboxPosY.connect('value-changed', self.settingsPositionYChanged)
		self.spinboxPosY.props.valign = Gtk.Align.CENTER

		hbox.pack_start(self.spinboxPosY, False, True, 0)

		row.add(hbox)
		self.listBox.add(row)

		row = Gtk.ListBoxRow()
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
		
		hbox.pack_start(Gtk.Label('Text'), False, True, 0)

		hbox.pack_start(Gtk.Label('Function'), True, True, 0)

		self.switch = Gtk.Switch()
		self.switch.props.valign = Gtk.Align.CENTER

		#todo function will be '' or NONE?????? get your shiet together
		if(self.values['function'][0] != None and self.values['function'][0] != ''):
			#the label listens to some function
			self.switch.set_state(True)
			self.switch.set_active(True)
		else:
			self.switch.set_state(False)
			self.switch.set_active(False)

		self.switch.connect('notify::active', self.functionStateChanged)

		hbox.pack_start(self.switch, True, True, 0)

		self.combo = Gtk.ComboBox.new_with_model(self.functionNamesStore)
		renderer_text = Gtk.CellRendererText()
		self.combo.pack_start(renderer_text, True)
		self.combo.add_attribute(renderer_text, 'text', 0)

		if(self.parent.functionIndex==-1):
			self.combo.set_active(0)
		else:
			self.combo.set_active(self.parent.functionIndex)
		self.combo.connect('changed', self.functionChanged)

		hbox.pack_start(self.combo, True, True, 0)

		self.textEntry = Gtk.Entry()
		self.textEntry.set_text(self.values['text'][0])
		self.textEntry.connect('changed', self.settingsTextChanged)
		self.textEntry.props.valign = Gtk.Align.CENTER

		hbox.pack_start(self.textEntry, True, True, 0)

		row.add(hbox)
		self.listBox.add(row)

		row = Gtk.ListBoxRow()
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
		
		hbox.pack_start(Gtk.Label('Font'), False, True, 0)

		button = Gtk.FontButton.new_with_font(self.values['font'][0])
		button.set_use_font(True)
		button.set_use_size(True)
		button.connect('font-set', self.getSelectedFont)
		button.props.valign = Gtk.Align.CENTER
		
		hbox.pack_start(button, True, True, 0)

		row.add(hbox)
		self.listBox.add(row)

		row = Gtk.ListBoxRow()
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
		
		hbox.pack_start(Gtk.Label('Color'), False, True, 0)
		button = Gtk.ColorButton.new_with_rgba(colorValueToRgba(self.values['color'][0]))
		button.set_use_alpha(True)
		button.connect('color-set', self.getSelectedColor)
		button.props.valign = Gtk.Align.CENTER
		
		hbox.pack_start(button, True, True, 0)

		row.add(hbox)
		self.listBox.add(row)

		row=Gtk.ListBoxRow()
		self.listBox.hide()
		row.add(self.listBox)
		rowArray.append(row)

		return rowArray

	def positionToValue(self, pos):
		if not representsInt(pos):
			return 0
		else:
			return pos

	def showOptions(self, widget):
		if(self.listBox.is_visible()):
			self.listBox.hide()
		else:
			self.listBox.show()

	def positionChanged(self):
		"""Initializes the modified position array from None to the initial values"""
		if self.values['position'][1] == None:
			self.values['position'][1] = self.values['position'][0]

	def labelXMiddle(self, widget):
		self.positionChanged()
		if widget.get_active():
			self.values['position'][1][0] = 'middle'
			self.parent.monitorSize(True)
		else:
			self.values['position'][1][0] = self.spinboxPosX.get_value()
			if not self.checkBoxYMiddle.get_state():
				#do not middle anything
				self.parent.monitorSize(False)

		self.spinboxPosX.set_sensitive(not widget.get_active())
		self.parent.moveMe(self.values['position'][1])

	def labelYMiddle(self, widget):
		self.positionChanged()
		
		if widget.get_active():
			self.values['position'][1][1] = 'middle'
			self.parent.monitorSize(True)
		else:
			self.values['position'][1][1] = self.spinboxPosY.get_value()
			if not self.checkBoxXMiddle.get_state():
				#do not middle anything
				self.parent.monitorSize(False)

		self.spinboxPosY.set_sensitive(not widget.get_active())
		self.parent.moveMe(self.values['position'][1])

	def functionChanged(self, widget):
		if(self.switch.get_state()!=True):
			return

		self.parent.functionIndex=widget.get_active()
		self.setParentFunction()
		
	def setParentFunction(self):
		if(self.parent.functionIndex == 0):
			self.parent.enableFunction('networkUp', True)
		elif(self.parent.functionIndex == 1):
			self.parent.enableFunction('networkDown', True)
		elif(self.parent.functionIndex == 2):
			self.parent.enableFunction('networkTotalUp', True)
		elif(self.parent.functionIndex == 3):
			self.parent.enableFunction('networkTotalDown', True)
		elif(self.parent.functionIndex == 4):
			self.parent.enableFunction('cpuPercent', True)
		elif(self.parent.functionIndex == 5):
			self.parent.enableFunction('ramPercent', True)
		elif(self.parent.functionIndex == 6):
			self.parent.enableFunction('hddPercent', True)
		elif(self.parent.functionIndex == 7):
			self.parent.enableFunction('upTime', True)
		else:
			self.parent.function = None
			self.parent.functionIndex = -1
			self.values['function'][0] = self.values['function'][1] = None
			self.parent.label.set_text(self.textEntry.get_text())
		self.parent.update()

	def functionStateChanged(self, widget, state):
		if(widget.get_state()!=True):
			#use function
			self.textEntry.hide()
			self.combo.show()
			if(self.parent.functionIndex==-1):
				self.parent.functionIndex=self.combo.get_active()
				if(self.parent.functionIndex==-1):
					self.parent.functionIndex=0
					self.combo.set_active(0)
		else:
			#don't use function
			self.values['function'][1] = None; #todo wtf is this? .pop('function', None)
			self.textEntry.show()
			self.combo.hide()
			self.parent.functionIndex=-1

		self.setParentFunction()

	def settingsTextChanged(self, widget):
		self.values['text'][1] = widget.get_text()
		self.parent.label.set_text(widget.get_text())

	def settingsPositionXChanged(self, widget):
		self.positionChanged()
		self.values['position'][1][0] = int(widget.get_value())
		self.parent.moveMe(self.values['position'][1])

	def settingsPositionYChanged(self, widget):
		self.positionChanged()
		self.values['position'][1][1] = int(widget.get_value())
		self.parent.moveMe(self.values['position'][1])

	def getSelectedFont(self, widget):
		self.parent.updateCss('font', widget.get_font_name())
		self.values['font'][1] = widget.get_font_name()
		self.parent.applyCss()

	def getSelectedColor(self, widget):
		rgb=widget.get_color()
		a=str(widget.get_alpha()/65535.0)
		value = 'rgba('+str(rgb.red/257.0)+', '+str(rgb.green/257.0)+', '+str(rgb.blue/257.0)+', '+a+')'
		self.parent.updateCss('color', value)
		self.values['color'][1] = value
		self.parent.applyCss()

	def afterSettingsPlacement(self):
		self.listBox.hide()
		#see if there is a function set or not
		if(self.switch.get_state() == True):
			self.textEntry.hide()
			self.combo.show()
		else:
			self.textEntry.show()
			self.combo.hide()

		self.spinboxPosX.set_sensitive(not self.checkBoxXMiddle.get_active())
		self.spinboxPosY.set_sensitive(not self.checkBoxYMiddle.get_active())

	def resetSettings(self):
		for key in self.values:
			self.values[key][1] = None
		self.parent.applySettings();
		self.parent.applyCss();

	def saveSettings(self):
		self.settingsToWrite = { }

		for key in self.values:
			#todo write all values, not only the modified ones, wtf are you doing man
			if self.values[key][1] != None:
				#key has been edited, copy it over
				self.values[key][0] = self.values[key][1]
			#reset edited value
			if type(self.values[key][0]) is list:
				self.values[key][1] = [0]*len(self.values[key][0])
			else:
				self.values[key][1] = None
			self.settingsToWrite[key] = stringifySettings(key, self.values[key][0])

		self.parent.applySettings()