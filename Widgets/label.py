#!/usr/bin/env python
receiver='Label'

from gi.repository import Gtk, Gdk, Pango

import Defaults.widget

from Tools.output import *
from Tools.simplemath import *
from multiprocessing.pool import ThreadPool

class Widget():
	def __init__(self, name, parentName, parent):
		self.parent=parent
		self.hMid=False
		self.vMid=False
		self.label=Gtk.Label()
		self.GUIName=name
		self.name=parentName+name
		self.label.set_name(self.name)
		
		self.initializeSettings()

		self.styleProvider=Gtk.CssProvider()
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

		self.currentCss={}

		self.frame=Gtk.Frame()
		self.frame.set_shadow_type(Gtk.ShadowType(Gtk.ShadowType.NONE))
		self.frameName=self.name+'Frame'
		self.frame.set_name(self.frameName)
		self.frame.add(self.label)

		self.cssClear = [ self.name, self.frameName ]

		self.updateCss('background-color', 'rgba(0,0,0,0)', self.frameName)

		self.frame.connect('destroy', self.destroyed)
		self.label.connect('size-allocate', self.getSize)

		self.readyShow = True
		self.function = None
		self.functionIndex = -1
		self.niceFunction = None
		self.functionData = None
		self.pool = None
		self.cssApplied = False

	def getSize(self, widget, allocation):
		if not self.cssApplied:
			return
		self.width=allocation.width
		self.height=allocation.height
		if(self.hMid):
			self.x=(self.parent.width - self.width)/2.0
		if(self.vMid):
			self.y=(self.parent.height - self.height)/2.0
		if(self.hMid or self.vMid):
			self.parent.fixed.move(self.frame, self.x, self.y)
		widget.disconnect_by_func(self.getSize)

	def setPos(self, x, y):
		self.x=x; self.y=y #todo remove pos

	def destroyed(self, widget):
		for name in self.cssClear:
			self.styleProvider.load_from_data('#'+name+' { } ')

	def initializeSettings(self):
		#first item is the normal value, second is the edited one (to allow reset values, we need to keep both the original and the edited)
		self.finalSettings = {}
		self.finalSettings['text'] = ['Hello, World!', None]
		self.finalSettings['size'] = [[0, 0], None]
		self.finalSettings['align'] = [Gtk.Align.START, None]
		self.finalSettings['font'] = ['Ubuntu 20', None]
		self.finalSettings['color'] = ['rgba(255, 255, 255, 1)', None]
		self.finalSettings['border'] = ['none', None]
		self.finalSettings['border-top'] = ['none', None]
		self.finalSettings['border-right'] = ['none', None]
		self.finalSettings['border-bottom'] = ['none', None]
		self.finalSettings['border-left'] = ['none', None]
		self.finalSettings['function'] = [None, None]

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
		if(key=='text'):
			self.finalSettings['text'][0] = value
		elif(key=='size'):
			size=value.split(',')
			self.finalSettings['size'][0] = [int(size[0]), int(size[1])]
		elif(key=='align'):
			if(value=='right'):
				self.finalSettings['align'][0] = Gtk.Align.END
			elif(value=='left'):
				self.finalSettings['align'][0] = Gtk.Align.START
			else:
				stderr(configurationFile+', line '+str(lineCount)+': Badly formatted command "align": Format: align = left/right.\nSkipping...')
				return
		elif(key=='font'):
			self.finalSettings['font'][0] = value
		elif(key=='color'):
			self.updateCss('color', value)
			self.finalSettings['color'][0] = value
		elif(key=='border'):
			self.updateCss('border', value)
			self.finalSettings['border'][0] = value
		elif(key=='border-top'):
			self.updateCss('border-top', value)
			self.finalSettings['border-top'][0] = value
		elif(key=='border-right'):
			self.updateCss('border-right', value)
			self.finalSettings['border-right'][0] = value
		elif(key=='border-bottom'):
			self.updateCss('border-bottom', value)
			self.finalSettings['border-bottom'][0] = value
		elif(key=='border-left'):
			self.updateCss('border-left', value)
			self.finalSettings['border-left'][0] = value
		elif(key=='function'):
			self.finalSettings['function'][0] = value
		else:
			stderr(configurationFile+', line '+str(lineCount)+': Unknown command.')

	def enableFunction(self, value, modified=None):
		if(modified == None):
			modified = False
		else:
			#function has been modified from the settings
			self.finalSettings['function'][1] = value
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


	def applySettings(self):
		if not self.enableFunction(self.finalSettings['function'][0]):
			#no function enabled, so add the text instead :D
			self.label.set_text(self.finalSettings['text'][0])
		self.frame.set_size_request(self.finalSettings['size'][0][0],self.finalSettings['size'][0][1])
		self.parent.fixed.move(self.frame, self.x, self.y)
		self.label.set_halign(self.finalSettings['align'][0])
		self.updateCss('font', self.finalSettings['font'][0])
		self.updateCss('color', self.finalSettings['color'][0])
		self.updateCss('border', self.finalSettings['border'][0])
		self.updateCss('border-top', self.finalSettings['border-top'][0])
		self.updateCss('border-right', self.finalSettings['border-right'][0])
		self.updateCss('border-bottom', self.finalSettings['border-bottom'][0])
		self.updateCss('border-left', self.finalSettings['border-left'][0])
		

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
		self.settingsObj = Settings(self)
		return self.settingsObj.getSettingsWidgets()


class Settings():
	def __init__(self, parent):
		self.parent=parent
		self.functionNamesStore = Gtk.ListStore(str)
		for name in [
			'Network Up', 'Network Down', 'Network Total Up', 'Network Total Down', 'Cpu Percent',
			'Ram Percent', 'HDD Percent', 'Uptime'
			]:
			self.functionNamesStore.append([name])
		

	def getSettingsWidgets(self):

		rowArray = []
		
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
		
		hbox.pack_start(Gtk.Label('Text'), False, True, 0)

		hbox.pack_start(Gtk.Label('Function'), True, True, 0)

		self.switch = Gtk.Switch()
		self.switch.props.valign = Gtk.Align.CENTER
		self.switch.connect('notify::active', self.functionStateChanged)

		if(self.parent.finalSettings['function'][0] != None):
			#the label listens to some function
			self.switch.set_state(True)
		else:
			self.switch.set_state(False)

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
		self.textEntry.connect('changed', self.settingsTextChanged)
		self.textEntry.props.valign = Gtk.Align.CENTER
		self.textEntry.set_text(self.parent.finalSettings['text'][0])

		hbox.pack_start(self.textEntry, True, True, 0)

		row.add(hbox)
		self.listBox.add(row)

		row = Gtk.ListBoxRow()
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
		
		hbox.pack_start(Gtk.Label('Font'), False, True, 0)

		button = Gtk.FontButton.new_with_font(self.parent.finalSettings['font'][0])
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
		button = Gtk.ColorButton.new_with_rgba(self.colorValueToRgba(self.parent.finalSettings['color'][0]))
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

	def colorValueToRgba(self, color):
		values = rgbaToValues(color)
		if(len(values)!=4):
			stderr('Color value seems to be broken')
			return Gdk.RGBA(0, 0, 0, 0)
		print values
		return Gdk.RGBA(int(float(values[0]))/255.0, int(float(values[1]))/255.0, int(float(values[2]))/255.0, float(values[3]))

	def showOptions(self, widget):
		if(self.listBox.is_visible()):
			self.listBox.hide()
		else:
			self.listBox.show()

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
			self.parent.finalSettings['function'][0] = self.parent.finalSettings['function'][1] = None
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
			self.parent.finalSettings.pop('fuction', None)
			self.textEntry.show()
			self.combo.hide()
			self.parent.functionIndex=-1

		self.setParentFunction()

	def settingsTextChanged(self, widget):
		self.parent.finalSettings['text'][1] = widget.get_text()
		self.parent.label.set_text(widget.get_text())

	def settingsPositionXChanged(self, widget):
		self.parent.x=int(widget.get_value())
		self.parent.parent.fixed.move(self.parent.frame, self.parent.x, self.parent.y)

	def settingsPositionYChanged(self, widget):
		self.parent.y=int(widget.get_value())
		self.parent.parent.fixed.move(self.parent.frame, self.parent.x, self.parent.y)

	def getSelectedFont(self, widget):
		self.parent.updateCss('font', widget.get_font_name())
		self.parent.finalSettings['font'][1] = widget.get_font_name()
		self.parent.applyCss()

	def getSelectedColor(self, widget):
		rgb=widget.get_color()
		a=str(widget.get_alpha()/65535.0)
		value = 'rgba('+str(rgb.red/257.0)+','+str(rgb.green/257.0)+','+str(rgb.blue/257.0)+','+a+')'
		self.parent.updateCss('color', value)
		self.parent.finalSettings['color'][1] = value
		self.parent.applyCss()

	def afterSettingsPlacement(self):
		self.listBox.hide()
		#see if there is a function set or not
		if(self.switch.get_state()==True):
			self.textEntry.hide()
			self.combo.show()
		else:
			self.textEntry.show()
			self.combo.hide()

	def resetSettings(self):
		for key in self.parent.finalSettings:
			self.parent.finalSettings[key][1] = None
		self.parent.applySettings();
		self.parent.applyCss();

	def stringifySettings(self, key, value):
		"""Converts the settings of the widget to the string value that has to be stored inside the configuration file"""
		if type(value) is str:
			return value

		if type(value) is list:
			return ','.join(str(x) for x in value)

		return value

	def saveSettings(self):

		self.settingsToWrite = { }

		for key in self.parent.finalSettings:
			#todo write all values, not only the modified ones, wtf are you doing man
			if self.parent.finalSettings[key][1] != None:
				#key has been edited, copy it over and reset the edited value to None
				self.parent.finalSettings[key][0] = self.parent.finalSettings[key][1]
				self.parent.finalSettings[key][1] = None

				self.settingsToWrite[key] = self.stringifySettings(key, self.parent.finalSettings[key][0])

		self.parent.applySettings()