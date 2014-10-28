#!/usr/bin/env python

from gi.repository import Gtk, Gdk

todoremove=False

class Customize(Gtk.Window):
	def __init__(self, gadgetName, configurationFile, parent):
		Gtk.Window.__init__(self, type_hint=Gdk.WindowTypeHint.DIALOG)

		self.set_title('Customize '+gadgetName+' widget')
		self.parent=parent
		self.set_border_width(10)
		self.set_hexpand(True)
		self.set_vexpand(True)

		self.set_size_request(500, 340)

		self.resetButton = Gtk.Button.new_with_label('Reset')
		self.resetButton.connect('clicked', self.resetButtonClicked)

		self.closeButton = Gtk.Button.new_with_label('Close')
		self.closeButton.connect('clicked', self.closeButtonClicked)

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

		#Close/Reset buttons container (lower)
		self.lowerBox = Gtk.Box()

		

		self.lowerBox.pack_start(self.resetButton, False, True, 5)
		self.lowerBox.pack_start(self.closeButton, False, True, 5)
		self.lowerBox.props.halign=Gtk.Align.END

		self.grid.add(self.scrolledWindow)
		self.grid.attach_next_to(self.lowerBox, self.scrolledWindow, Gtk.PositionType.BOTTOM, 1, 1)

		self.constructListBox()

		self.add(self.grid)

		self.show_all()

		self.connect('destroy', self.destroyed)

	def destroyed(self, widget):
		if(self.parent!=None):
			self.parent.customizeDialogShown=False

	def closeButtonClicked(self, widget):
		self.destroy()
		if todoremove:
			sys.exit(0)

	def resetButtonClicked(self, widget):
		print 'reset clicked'

	def appendSettings(self, listBoxRows):
		for row in listBoxRows:
			self.listBox.add(row)

	def constructListBox(self):
		row = Gtk.ListBoxRow()
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
		row.add(hbox)
		label = Gtk.Label("This is here by default", xalign=0)

		switch = Gtk.Switch()
		switch.props.valign = Gtk.Align.CENTER

		hbox.pack_start(label, True, True, 0)
		
		hbox.pack_start(switch, False, True, 0)

		self.listBox.add(row)

if __name__ == '__main__':
	todoremove=True
	import sys
	Customize('test', 'noconf', None)
	Gtk.main()