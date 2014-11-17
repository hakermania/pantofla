#!/usr/bin/env python

from gi.repository import Gtk, Gdk

def stringifySettings(key, value):
	"""Converts the settings of the widget to the string value that has to be stored inside the configuration file"""

	if key == 'function':
		print key, value

	if value is None:
		print 'EEE', key, value
		return ''

	if type(value) is str:
		return value

	if type(value) is list:
		return ','.join(str(x) for x in value)

	if isinstance(value, Gtk.Align):
		if value == Gtk.Align.END:
			return 'right'
		else:
			return 'left'

	return str(value)

def rgbaToValues(color):
	return color.replace('rgba', '').replace('(', '').replace(')', '').replace(' ', '').split(',')

def colorValueToRgba(color):
	values = rgbaToValues(color)
	if(len(values)!=4):
		stderr('Color value seems to be broken')
		return Gdk.RGBA(0, 0, 0, 0)
	print values
	return Gdk.RGBA(int(float(values[0]))/255.0, int(float(values[1]))/255.0, int(float(values[2]))/255.0, float(values[3]))