#!/usr/bin/env python

from gi.repository import Gtk

import output

receiver="Label"

class Widget():
	def __init__(self, name, parentName):
		print "ADDING LABEL"
		self.gtkwidget=Gtk.Label();
		self.name=name+parentName #making a cross-widget unique name
		print self.name

	def update(self):
		pass

	def runCommand(self, command, lineCount, configurationFile):
		print "I am about to run", command, "from inside the Label widget!"

		if(command.startswith("text=")):
			parts=command.split("=")
			if(len(parts)!=2):
				output.stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'text': Format: text = \"text\".\nSkipping...")
				return
			if(not (parts[1].startswith("\"") and parts[1].endswith("\""))):
				output.stderr(configurationFile+", line "+str(lineCount)+": Badly formatted command 'text': Format: text = \"text\".\nSkipping...")
				return
			
			self.text=parts[1][1:-1] #Remove the ""

			self.gtkwidget.set_text(self.text)

	def widget(self):
		print "LABEL RETURN"
		return [self.gtkwidget]