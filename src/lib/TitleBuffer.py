#!/usr/bin/env python

import gtk
import gnome
import gnome.ui
import gtk.gdk
import pango

import notemeister

class TitleBuffer(gtk.TextBuffer):

	def __init__(self):
		gtk.TextBuffer.__init__(self)

		self.create_tag('welcome', weight=pango.WEIGHT_BOLD,
								scale=pango.SCALE_LARGE,
								justification=gtk.JUSTIFY_CENTER)
		self.create_tag('title', weight=pango.WEIGHT_BOLD,
								size=25000,
								justification=gtk.JUSTIFY_CENTER,
								foreground='darkblue',
								style=pango.STYLE_ITALIC)
		self.create_tag('message', justification=gtk.JUSTIFY_CENTER)

		self.button = gtk.Button("Create New Note")
		self.image = gtk.Image()
		self.image.set_from_file(notemeister.const.aboutPic)

		self.create_text()

	def create_text(self):
		welcome = "\n"
		title = "Notemeister " + notemeister.const.version + ""
		msg = "\nCopyright (c) 2004, Dennis Craven\n\n"
		iter = self.get_iter_at_line_offset(6, 0)
		self.insert_with_tags_by_name(iter, welcome, 'welcome')
		self.insert_with_tags_by_name(iter, title, 'title')
		self.image_anchor = self.create_child_anchor(iter)

		self.insert_with_tags_by_name(iter, msg, 'message')
		self.insert_with_tags_by_name(iter, ' ', 'welcome')
		self.button_anchor = self.create_child_anchor(iter)

