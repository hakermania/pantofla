#!/usr/bin/env python

import os, ConfigParser, sys, shutil, signal
import Defaults.app, Widgets.widget, Widgets.WidgetManager

from Tools.output import *

def getConfigurationFiles():
	if not os.path.isdir(Defaults.app.configurationPath):
		#The configuration folder does not exist
		return []
	else:
		#Get the configuration files, aka the files in the configuration folder ending with 'rc'
		fileList=os.listdir(Defaults.app.configurationPath)
		configurationFiles=[]
		for filename in fileList:
			if filename.endswith("rc"):
				configurationFiles.append(Defaults.app.configurationPath+filename)
		return configurationFiles

def createDefaultConfigurationFile():
	#Create the configuration folder if it doesn't exist
	if not os.path.isdir(Defaults.app.configurationPath):
		try:
			os.makedirs(Defaults.app.configurationPath)
		except OSError:
			return False

	#Copy it from the program's folders
	if(os.path.exists(Defaults.app.appDirectory+Defaults.app.configFilename)):
		shutil.copyfile(Defaults.app.appDirectory+Defaults.app.configFilename, Defaults.app.configurationPath+Defaults.app.configFilename)
		return True
	else:
		return False

def main():

	#Make sure Ctl-C works
	signal.signal(signal.SIGINT, signal.SIG_DFL)

	configurationFiles = getConfigurationFiles()
	if(len(configurationFiles)==0):
		if not createDefaultConfigurationFile():
			stderr("Could not create default configuration files. The application will now exit")
			sys.exit(1)
		else:
			configurationFiles = getConfigurationFiles()
			if(len(configurationFiles)==0):
				stderr("Could not create default configuration files. The application will now exit")
				sys.exit(1)

	widgetManager = Widgets.WidgetManager.WidgetManager()

	widgetCount=0

	for filename in configurationFiles:
		widgetCount+=1
		widgetManager.add(Widgets.widget.Widget(Defaults.widget.name+str(widgetCount), filename, True), filename)

	widgetManager.run()
		
main()