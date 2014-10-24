#!/usr/bin/env python

#Defaults considering the application itself

import os

appName="Pantofla"
configurationFolderName="pantofla"

appDirectory="/usr/share/pantofla/"
configurationPath = os.path.expanduser(os.getenv('XDG_CONFIG_HOME', '~/.config/'))+'/'+configurationFolderName+"/"
configFilename="widget1rc"