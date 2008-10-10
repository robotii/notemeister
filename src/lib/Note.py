#!/usr/bin/env python

import gtk

#import NoteBuffer
import notemeister

class Note:

	def __init__(self, path=None, title='', body='', link='', wrap="1"):
		self.path = path
		self.title = title
		self.body = body
		self.link = link
		self.wrap = wrap
		self.buffer = notemeister.NoteBuffer.NoteBuffer()
		self.buffer.set_text(self.body)

	def __str__(self):
		return '(%d) Note "%s" has body: %s' % (self.index, self.title, self.body)

