#!/usr/bin/env python
receiver="Label"

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

		self.styleProvider=Gtk.CssProvider()
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.currentCss={}

		self.frame=Gtk.Frame()
		self.frame.set_shadow_type(Gtk.ShadowType(Gtk.ShadowType.NONE))
		self.frameName=self.name+"Frame"
		self.frame.set_name(self.frameName)
		self.frame.add(self.label)

		self.cssClear = [ self.name, self.frameName ]

		self.updateCss("background-color", "rgba(0,0,0,0)", self.frameName)

		self.frame.connect('destroy', self.destroyed)
		self.label.connect('size-allocate', self.getSize)

		self.readyShow=True
		self.function = None
		self.niceFunction = None
		self.functionData = None
		self.pool = None
		self.cssApplied=False

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

	def destroyed(self, widget):
		for name in self.cssClear:
			self.styleProvider.load_from_data("#"+name+" { } ")

	def update(self):
		if(self.function==None):
			return
		if(self.functionData==None):
			#first time claiming data
			self.functionData=self.pool.apply_async(self.function)
		elif(self.functionData.ready()):
			#data is ready for presenation
			if(self.niceFunction==0):
				self.label.set_text(str(self.functionData.get()))
			else:
				self.label.set_text(str(self.niceFunction(self.functionData.get())))
			self.functionData=self.pool.apply_async(self.function)

	def runCommand(self, key, value, lineCount, configurationFile):
		if(key=="text"):
			if(not (value.startswith("'") and value.endswith("'"))):
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'text': Format: text = 'text'.\nSkipping...")
				return
			
			self.text=value[1:-1] #Remove the ""

			self.label.set_text(self.text)
		elif(key=="size"):
			size=value.split(",")
			self.frame.set_size_request(int(size[0]),int(size[1]))
		elif(key=="align"):
			if(value=="right"):
				self.label.set_halign(Gtk.Align.END)
			elif(value=="left"):
				self.label.set_halign(Gtk.Align.START)
			else:
				stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'align': Format: align = left/right.\nSkipping...")
				return
		elif(key=="font"):
			self.updateCss("font", value)
		elif(key=="color"):
			self.updateCss("color", value)
		elif(key=="border"):
			self.updateCss("border", value)
		elif(key=="border-top"):
			self.updateCss("border-top", value)
		elif(key=="border-right"):
			self.updateCss("border-right", value)
		elif(key=="border-bottom"):
			self.updateCss("border-bottom", value)
		elif(key=="border-left"):
			self.updateCss("border-left", value)
		elif(key=="padding"):
			self.updateCss("padding", value)
		elif(key=="padding-top"):
			self.updateCss("padding-top", value)
		elif(key=="padding-right"):
			self.updateCss("padding-right", value)
		elif(key=="padding-bottom"):
			self.updateCss("padding-bottom", value)
		elif(key=="padding-left"):
			self.updateCss("padding-left", value)
		elif(key=="function"):
			if(value=="networkUp"):
				from Tools.network import networkUp
				self.function=networkUp
			elif(value=="networkDown"):
				from Tools.network import networkDown
				self.function=networkDown
			elif(value=="networkTotalUp"):
				from Tools.network import networkTotalUp
				self.function=networkTotalUp
			elif(value=="networkTotalDown"):
				from Tools.network import networkTotalDown
				self.function=networkTotalDown
			elif(value=="cpuPercent"):
				from Tools.hardware import cpuPercent
				self.function=cpuPercent
			elif(value=="ramPercent"):
				from Tools.hardware import ramPercent
				self.function=ramPercent
			elif(value=="hddPercent"):
				from Tools.hardware import hddPercent
				self.function=hddPercent
			elif(value=="upTime"):
				from Tools.hardware import upTime
				self.function=upTime
			self.pool = ThreadPool(processes=1)
		elif(key=="type"):
			if(value=="data"):
				from Tools.hardware import dataToNiceString
				self.niceFunction=dataToNiceString
			elif(value=="percent"):
				from Tools.hardware import percentToNiceString
				self.niceFunction=percentToNiceString
			elif(value=="time"):
				from Tools.hardware import timeToNiceString
				self.niceFunction=timeToNiceString
		else:
			stderr(configurationFile+", line "+str(lineCount)+": Unknown command.")

	def updateCss(self, key, value, name=None):
		if(name is None):
			name=self.name
		if name not in self.currentCss:
			self.currentCss[name]={}
		key=key.rstrip(); key=key.lstrip()
		value=value.rstrip(); value=value.lstrip()

		if key not in self.currentCss[name]:
			self.currentCss[name][key]={}

		self.currentCss[name][key]["value"]=value

	def applyCss(self):
		finalString=''
		for name in self.currentCss:
			if(len(self.currentCss[name])>0):
				finalString+="#"+name+" { "
				for key in self.currentCss[name]:
					finalString+=key+" : "+self.currentCss[name][key]["value"]+"; "
				finalString+="} "

		if(finalString!=''):
			self.styleProvider.load_from_data(finalString.encode())

	def initial(self):
		self.applyCss()
		self.cssApplied=True

	def widget(self):
		return self.frame

	def settings(self):
		self.settings = Settings(self)
		return self.settings.getSettingsWidgets()


class Settings():
	def __init__(self, parent):
		self.parent=parent

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
		
		label = Gtk.Label("Position", xalign=0)
		hbox.pack_start(label, True, True, 0)

		hbox.pack_start(Gtk.Label("X"), False, True, 0)

		spinbox = Gtk.SpinButton.new_with_range(0, 5000, 1)
		spinbox.set_value(self.parent.x)
		spinbox.connect('value-changed', self.settingsPositionXChanged)
		spinbox.props.valign = Gtk.Align.CENTER

		hbox.pack_start(spinbox, False, True, 0)

		hbox.pack_start(Gtk.Label("Y"), False, True, 0)

		spinbox = Gtk.SpinButton.new_with_range(0, 5000, 1)
		spinbox.set_value(self.parent.y)
		spinbox.connect('value-changed', self.settingsPositionYChanged)
		spinbox.props.valign = Gtk.Align.CENTER

		print self.parent.x, self.parent.y

		hbox.pack_start(spinbox, False, True, 0)

		row.add(hbox)
		self.listBox.add(row)

		row = Gtk.ListBoxRow()
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
		
		hbox.pack_start(Gtk.Label("Text"), False, True, 0)

		entry = Gtk.Entry()
		entry.connect('changed', self.settingsTextChanged)
		entry.props.valign = Gtk.Align.CENTER
		entry.set_text(self.parent.label.get_text())
		
		hbox.pack_start(entry, True, True, 0)

		row.add(hbox)
		self.listBox.add(row)

		row = Gtk.ListBoxRow()
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
		
		hbox.pack_start(Gtk.Label("Font"), False, True, 0)

		button = Gtk.FontButton.new_with_font(self.parent.label.get_pango_context().get_font_description().to_string())
		button.set_use_font(True)
		button.set_use_size(True)
		button.connect('font-set', self.getSelectedFont)
		button.props.valign = Gtk.Align.CENTER
		
		hbox.pack_start(button, True, True, 0)

		row.add(hbox)
		self.listBox.add(row)

		row = Gtk.ListBoxRow()
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
		
		hbox.pack_start(Gtk.Label("Color"), False, True, 0)
		button = Gtk.ColorButton.new_with_rgba(self.parent.label.get_style().props.context.get_color(Gtk.StateType.NORMAL))
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

	def showOptions(self, widget):
		if(self.listBox.is_visible()):
			self.listBox.hide()
		else:
			self.listBox.show()

	def settingsTextChanged(self, widget):
		self.parent.label.set_text(widget.get_text())

	def settingsPositionXChanged(self, widget):
		self.parent.x=int(widget.get_value())
		self.parent.parent.fixed.move(self.parent.frame, self.parent.x, self.parent.y)

	def settingsPositionYChanged(self, widget):
		self.parent.y=int(widget.get_value())
		self.parent.parent.fixed.move(self.parent.frame, self.parent.x, self.parent.y)

	def getSelectedFont(self, widget):
		self.parent.updateCss('font', widget.get_font_name())
		self.parent.applyCss()

	def getSelectedColor(self, widget):
		rgb=widget.get_color()
		a=str(widget.get_alpha()/65535.0)
		self.parent.updateCss('color', 'rgba('+str(rgb.red/257.0)+','+str(rgb.green/257.0)+','+str(rgb.blue/257.0)+','+a+')')
		print 'rgba('+str(rgb.red)+','+str(rgb.green)+','+str(rgb.blue)+','+a+')'
		self.parent.applyCss()
		# self.parent.updateCss('color', widget.get_color_name())
		# self.parent.applyCss()

	def afterSettingsPlacement(self):
		self.listBox.hide()