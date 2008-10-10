#!/usr/bin/env python

import gtk
import gnome
import gnome.ui
import gtk.gdk
import pango
import datetime

import notemeister

class NoteView(gtk.TextView):

	def __init__(self, configurator):
		gtk.TextView.__init__(self)
		self.Conf = configurator
		self.set_wrap_mode(gtk.WRAP_WORD)
		self.set_left_margin(8)
		self.set_right_margin(8)
		self.set_pixels_above_lines(2)

		self.display = gtk.gdk.display_manager_get().get_default_display()
		self.clipboard = gtk.Clipboard(self.display, "CLIPBOARD")
		self.get_buffer().add_selection_clipboard(self.clipboard)
		
		self.connect("move-cursor", self.on_move_cursor)
		self.connect("button-press-event", self.on_button_press)

	def on_button_press(self, obj, event):
		"""Catch button press events in the main window"""
		buffer = self.get_buffer()
		if event.button == 3:
			self.popup_menu.popup(None, None, None, event.button, event.time)
			return gtk.TRUE

	def ref_font_label(self, label):
		self.font_label = label

	def ref_view_popup(self, popup):
		self.popup_menu = popup

	def get_line_count(self):
		buffer = self.get_buffer()
		return buffer.get_line_count()

	def get_char_count(self):
		buffer = self.get_buffer()
		return buffer.get_char_count()

	def get_word_count(self):
		buffer = self.get_buffer()
		return notemeister.utils.get_word_count(buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter()))

	def on_select_all_activate(self, obj):
		buffer = self.get_buffer()
		(start, end) = buffer.get_bounds()
		buffer.select_range(start, end)

	def on_cut_activate(self, obj):
		self.get_buffer().cut_clipboard(self.clipboard, self.get_editable())

	def on_copy_activate(self, obj):
		self.get_buffer().copy_clipboard(self.clipboard)

	def on_paste_activate(self, obj):
		self.get_buffer().paste_clipboard(self.clipboard, None, self.get_editable())
		
	def on_date_clicked(self, obj):
		buffer = self.get_buffer()
		t = datetime.date.today()
		if self.Conf.long_date:
			today = t.strftime("%B %e, %Y ")
		else:
			today = t.strftime("%m-%d-%y ")
		buffer.insert_at_cursor(today)

	def on_time_clicked(self, obj):
		buffer = self.get_buffer()
		t = datetime.datetime.now()
		if self.Conf.twelve_hour_time:
			now = t.strftime("%l:%M %p ")
		else:
			now = t.strftime("%R ")
		buffer.insert_at_cursor(now)

	def get_selected_text(self):
		buffer = self.get_buffer()
		insert = buffer.get_iter_at_mark(buffer.get_insert())
		selection_bound = buffer.get_iter_at_mark(self.get_buffer().get_selection_bound())
		if insert and selection_bound:
			return (buffer.get_text(insert, selection_bound), insert, selection_bound)
		else:
			return (None, None, None)

	def on_move_cursor(self, view, step_size, count, extend):
		buffer = self.get_buffer()
		iter = buffer.get_cursor_iter()
		table = buffer.get_tag_table()
		index = self.get_font_scale(buffer, iter)
		if index == None:
			self.font_label.set_text('Normal Size')
		elif index == 0:
			self.font_label.set_text('xSmall')
		elif index == 1:
			self.font_label.set_text('Small')
		elif index == 2:
			self.font_label.set_text('Large')
		elif index == 3:
			self.font_label.set_text('xLarge')

	def on_font_combo_activate(self, text):
		buffer = self.get_buffer()
		iters = buffer.get_selection_bounds()
		for tag in buffer.scale_tags:
			buffer.remove_tag(tag, iters[0], iters[1])
		if text == 'xSmall':
			buffer.apply_tag_by_name('xsmall', iters[0], iters[1])
		elif text == 'Small':
			buffer.apply_tag_by_name('small', iters[0], iters[1])
		elif text == 'Normal':
			pass
		elif text == 'Large':
			buffer.apply_tag_by_name('large', iters[0], iters[1])
		elif text == 'xLarge':
			buffer.apply_tag_by_name('xlarge', iters[0], iters[1])


	def on_font_scale_activate(self, obj):
		buffer = self.get_buffer()
		iters = buffer.get_selection_bounds()
		self.cycle_font_scale(buffer, iters)

	def on_bold_activate(self, obj):
		buffer = self.get_buffer()
		iters = buffer.get_selection_bounds()
		if not len(iters) == 0:
			self.toggle_bold(buffer, iters)

	def on_italic_activate(self, obj):
		buffer = self.get_buffer()
		iters = buffer.get_selection_bounds()
		if not len(iters) == 0:
			self.toggle_italic(buffer, iters)

	def on_underline_activate(self, obj):
		buffer = self.get_buffer()
		iters = buffer.get_selection_bounds()
		if not len(iters) == 0:
			self.toggle_underline(buffer, iters)

	def toggle_bold(self, buffer, iters):
		table = buffer.get_tag_table()
		bold_tag = table.lookup('bold')
		if iters[0].has_tag(bold_tag):
			buffer.remove_tag_by_name('bold', iters[0], iters[1])
		else:
			buffer.apply_tag_by_name('bold', iters[0], iters[1])

	def toggle_italic(self, buffer, iters):
		table = buffer.get_tag_table()
		italic_tag = table.lookup('italic')
		if iters[0].has_tag(italic_tag):
			buffer.remove_tag_by_name('italic', iters[0], iters[1])
		else:
			buffer.apply_tag_by_name('italic', iters[0], iters[1])

	def toggle_underline(self, buffer, iters):
		table = buffer.get_tag_table()
		underline_tag = table.lookup('underline')
		if iters[0].has_tag(underline_tag):
			buffer.remove_tag_by_name('underline', iters[0], iters[1])
		else:
			buffer.apply_tag_by_name('underline', iters[0], iters[1])

	def cycle_font_scale(self, buffer, iters):
		if len(iters) > 0:
			index = self.get_font_scale(buffer, iters[0])
			for tag in buffer.scale_tags:
				buffer.remove_tag(tag, iters[0], iters[1])
			if index == None:
				buffer.apply_tag(buffer.scale_tags[2], iters[0], iters[1])
				self.font_label.set_text('Large')
			elif index == 0:
				buffer.apply_tag(buffer.scale_tags[1], iters[0], iters[1])
				self.font_label.set_text('Small')
			elif index == 1:
				self.font_label.set_text('Normal Size')
				pass
			elif index == 2:
				buffer.apply_tag(buffer.scale_tags[3], iters[0], iters[1])
				self.font_label.set_text('xLarge')
			elif index == 3:
				buffer.apply_tag(buffer.scale_tags[0], iters[0], iters[1])
				self.font_label.set_text('xSmall')

	def get_font_scale(self, buffer, iter):
		for tag in buffer.scale_tags:
			if iter.has_tag(tag):
				return buffer.scale_tags.index(tag)

	def format_body_with_tags(self, obj):
		string = ''
		buffer = obj.buffer
		iter = buffer.get_start_iter()
		while not iter.is_end():
			on_tags = iter.get_toggled_tags(gtk.TRUE)
			if len(on_tags) > 0:
				for tag in on_tags:
					string = string + '<' + buffer.get_text_tag(tag) + '>'
			off_tags = iter.get_toggled_tags(gtk.FALSE)
			if len(off_tags) > 0:
				for tag in off_tags:
					string = string + '</' + buffer.get_text_tag(tag) + '>'
			string = string + iter.get_char()
			if iter.forward_char():
				continue
		obj.body = string

	def format_body_from_tags(self, obj):
		string = obj.body
		buffer = obj.buffer 
		buffer.set_text('')
		iter = buffer.get_start_iter()
		tag_list = []
		i = 0
		while i < len(string):
			if string[i] == '<' and string[i+2] == '>': # tag on
				if string[i+1] == 'b':
					tag_list.append('bold')
				elif string[i+1] == 'i':
					tag_list.append('italic')
				elif string[i+1] == 'u':
					tag_list.append('underline')
				elif string[i+1] == 'l':
					tag_list.append('large')
				elif string[i+1] == 's':
					tag_list.append('small')
				elif string[i+1] == 'L':
					tag_list.append('xlarge')
				elif string[i+1] == 'S':
					tag_list.append('xsmall')
				i = i + 3
				continue
			elif string[i] == '<' and string[i+1] == '/' and string[i+3] == '>':
				if string[i+2] == 'b':
					tag_list.remove('bold')
				elif string[i+2] == 'i':
					tag_list.remove('italic')
				elif string[i+2] == 'u':
					tag_list.remove('underline')
				elif string[i+2] == 'l':
					tag_list.remove('large')
				elif string[i+2] == 's':
					tag_list.remove('small')
				elif string[i+2] == 'L':
					tag_list.remove('xlarge')
				elif string[i+2] == 'S':
					tag_list.remove('xsmall')
				i = i + 4
				continue
			elif not string[i] == '<':
				buffer.insert(iter, string[i])
				end = iter.copy()
				end.backward_char()
				for tag in tag_list:
					buffer.apply_tag_by_name(tag, end, iter)

			iter.forward_char()
			i = i + 1


