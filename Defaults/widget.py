#Defaults considering the default widget

from gi.repository import Gdk

name="PantoflaWidget"
defaultUpdateInterval=1000
defaultWidth=600
defaultHeight=400
wmClass="Pantofla"
defaultBgColor=Gdk.RGBA(0,0,0,0.5)
defaultScreen=Gdk.Screen.get_default()

defaultClockFormat="%H:%M"
defaultGmtClockValue=False