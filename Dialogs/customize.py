#!/usr/bin/env python

from gi.repository import Gtk, Gdk
from Tools.output import *

class Customize(Gtk.Window):
	def __init__(self, gadgetName, configurationFile, parent):
		Gtk.Window.__init__(self, type_hint=Gdk.WindowTypeHint.DIALOG)

		self.set_title('Customize '+gadgetName+' widget')
		self.parent=parent
		self.set_border_width(10)
		self.set_resizable(True)
		self.set_hexpand(True)
		self.set_vexpand(True)

		self.set_size_request(752, 545)

		self.resetButton = Gtk.Button.new_with_label('Reset')
		self.resetButton.connect('clicked', self.resetButtonClicked)
		self.resetButton.set_size_request(92, 29)

		self.saveButton = Gtk.Button.new_with_label('Save')
		self.saveButton.connect('clicked', self.saveButtonClicked)
		self.saveButton.set_size_request(92, 29)
		self.saveButton.do_grab_focus(self)

		self.closeButton = Gtk.Button.new_with_label('Close')
		self.closeButton.connect('clicked', self.closeButtonClicked)
		self.closeButton.set_size_request(92, 29)

		#Outer container
		self.grid = Gtk.Grid()
		self.grid.set_row_spacing(10)

		#Options container (upper)
		self.listBox = Gtk.ListBox()
		self.listBox.set_hexpand(True)
		self.listBox.set_vexpand(True)
		self.listBox.set_selection_mode(Gtk.SelectionMode.NONE)

		self.scrolledWindow = Gtk.ScrolledWindow()
		self.scrolledWindow.add_with_viewport(self.listBox)

		#Close/Save buttons container (lower)
		self.lowerBox = Gtk.Box()

		self.lowerBox.pack_start(self.closeButton, False, True, 5)
		self.lowerBox.pack_start(self.saveButton, False, True, 5)
		
		self.lowerBox.props.halign=Gtk.Align.END
		self.resetButton.props.halign=Gtk.Align.START

		self.grid.attach(self.scrolledWindow, 0, 0, 2, 1)
		self.grid.attach(self.lowerBox, 1, 1, 1, 1)
		self.grid.attach(self.resetButton, 0, 1, 1, 1)

		self.constructWidgetSettings()

		self.add(self.grid)

		self.show_all()

		self.connect('destroy', self.destroyed)

		self.controllingWidgets = []

	def destroyed(self, widget):
		if(self.parent!=None):
			self.parent.customizeDialogShown=False

	def addControllingWidget(self, widget):
		self.controllingWidgets.append(widget)
		self.appendSettings(widget.settings())

	def showWidgets(self):
		#show all the widgets
		self.show_all()
		#do any actions necessary for each one, after showing them (maybe hide some etc)
		for widget in self.controllingWidgets:
			widget.settingsObj.afterSettingsPlacement()

	def closeButtonClicked(self, widget):
		for widget in self.controllingWidgets:
			widget.settingsObj.resetSettings()
		self.destroy()

	def resetButtonClicked(self, widget):
		for child in self.listBox.get_children():
			self.listBox.remove(child)
		for widget in self.controllingWidgets:
			widget.settingsObj.resetSettings()
			self.appendSettings(widget.settings())
		self.showWidgets()

	def saveButtonClicked(self, widget):
		print 'save button clicked' #todo remove
		for widget in self.controllingWidgets:
			print 'saving settings...'
			widget.settingsObj.saveSettings()
		print 'writing to file....'
		if not self.parent.writeSettingsFile():
			#todo show error messagebox
			stderr('PARENT reported couldn\'t write to configuration file')
			return
		self.parent.applyConfigurationFile()
		print 'All ok!'


	def appendSettings(self, listBoxRows):
		for row in listBoxRows:
			self.listBox.add(row)

	def constructWidgetSettings(self):
		row = Gtk.ListBoxRow()
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
		row.add(hbox)
		label = Gtk.Label("This is here by default", xalign=0)

		switch = Gtk.Switch()
		switch.props.valign = Gtk.Align.CENTER

		hbox.pack_start(label, True, True, 0)
		
		hbox.pack_start(switch, False, True, 0)

		self.listBox.add(row)