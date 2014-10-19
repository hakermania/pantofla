#!/usr/bin/env python

from gi.repository import Gtk, GdkPixbuf, Rsvg, Gdk
import cairo
import math

def loadImage(path):
	return []
	return Gtk.Image.new_file(path)

def loadImageSvgScaled(path, width, height):
	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
	context = cairo.Context(surface)

	#context.scale(2, 2)
	context.rotate (45*math.pi/180);
	context.set_matrix(cairo.Matrix(xx=width, yy=height))
	#context.paint()
	#context.stroke()

	svg = Rsvg.Handle().new_from_file(path)
	svg.render_cairo(context)

	# image=Gtk.Image()
	# pixbuf = GdkPixbuf.Pixbuf.new_from_data(surface.get_data(), GdkPixbuf.Colorspace.RGB, True, 8, width, height, 0, None, None)
	# image.set_from_pixbuf(pixbuf)

	# image=Gtk.Image()
	# image.set_from_pixbuf(Gdk.pixbuf_get_from_surface(surface, 0, 0, surface.get_width(), surface.get_height()))
	

	image = Gtk.Image()
	image.set_from_pixbuf(svg.get_pixbuf())

	return image


def loadPixbuf(path):
	return GdkPixbuf.Pixbuf.new_from_file(path)

# def loadImageScaled(path, width, height):
# 	pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)
# 	image = Gtk.Image()
# 	image.set_from_pixbuf(pixbuf.scale_simple(width, height, GdkPixbuf.InterpType.HYPER))
# 	return image