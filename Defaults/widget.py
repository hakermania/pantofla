#Defaults considering the default widget

from gi.repository import Gdk, Gtk

name="PantoflaWidget"
defaultUpdateInterval=1000
defaultWidth=600
defaultHeight=400
wmClass="Pantofla"
defaultBgColor=[0,0,0,0.5]
defaultScreen=Gdk.Screen.get_default()
defaultFadeInTime=400.0 #ms

defaultClockFormat="%H:%M"
defaultGmtClockValue=False