#!/usr/bin/env python

import gtk
import gnome
import gnome.ui
import gtk.gdk
import pango

#import const

class NoteBuffer(gtk.TextBuffer):

	tag_list = []

	def __init__(self):
		gtk.TextBuffer.__init__(self)
		self.create_tags()

	def get_cursor_iter(self):
		return self.get_iter_at_mark(self.get_insert())

	def create_tags(self):
		self.scale_tags = []
		self.create_tag('bold', weight=pango.WEIGHT_BOLD)
		self.create_tag('italic', style=pango.STYLE_ITALIC)
		self.create_tag('underline', underline=pango.UNDERLINE_SINGLE)
		self.scale_tags.append(self.create_tag('xsmall', scale=pango.SCALE_X_SMALL))
		self.scale_tags.append(self.create_tag('small', scale=pango.SCALE_SMALL))
		self.scale_tags.append(self.create_tag('large', scale=pango.SCALE_LARGE))
		self.scale_tags.append(self.create_tag('xlarge', size=15000))

	def on_text_inserted(self, buffer, iter, text, length, data=None):
		self.handler_block(self.insert_id)
		start = iter.copy()
		end = iter.copy()
		moved = start.backward_char()
		for tag in self.tag_list:
			self.apply_tag_by_name('bold', start, end)
		self.handler_unblock(self.insert_id)

	def get_text_tag(self, tag):
		table = self.get_tag_table()
		if tag == table.lookup('bold'):
			return 'b'
		elif tag == table.lookup('italic'):
			return 'i'
		elif tag == table.lookup('underline'):
			return 'u'
		elif tag == table.lookup('large'):
			return 'l'
		elif tag == table.lookup('small'):
			return 's'
		elif tag == table.lookup('xlarge'):
			return 'L'
		elif tag == table.lookup('xsmall'):
			return 'S'


		
