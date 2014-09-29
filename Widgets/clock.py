#!/usr/bin/env python

from gi.repository import Gtk

import output, Defaults.widget
from time import gmtime, strftime

receiver="Clock"

class Widget():
	def __init__(self, parentName, name):
		print "ADDING CLOCK"
		self.gtkwidget=Gtk.Label();
		self.format= Defaults.widget.defaultClockFormat
		self.name=name+parentName

	def update(self):
		print "Setting clock text to", strftime(self.format, gmtime())
		self.gtkwidget.set_text(strftime(self.format, gmtime()))

	def runCommand(self, command, lineCount, configurationFile):
		#GMTTIME TRUE OR FALSE
		print "I am about to run", command, "from inside the Clock widget!"

		if(command.startswith("format=")):
			parts=command.split("=")
			if(len(parts)!=2):
				output.stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'format': Format: format = format.\nSkipping...")
				return
			
			self.format=parts[1]

	def widget(self):
		print "CLOCK RETURN"
		return [self.gtkwidget]