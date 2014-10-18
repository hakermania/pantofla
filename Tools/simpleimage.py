#!/usr/bin/env python

from gi.repository import Gtk, GdkPixbuf

def loadImageScaled(path, width, height):
	image = Gtk.Image()
	pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)
	scaled_buf = pixbuf.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)
	image.set_from_pixbuf(scaled_buf)
	return image