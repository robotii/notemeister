#!/usr/bin/env python

import gtk
import gnome.ui

import notemeister

from gettext import gettext as _

class Dialog(gtk.Dialog):

	def __init__(self, parent, title, buttons, default = None):
		gtk.Dialog.__init__(self, title, parent, gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_MODAL | gtk.DIALOG_NO_SEPARATOR)

		self.set_border_width(6)
		self.vbox.set_spacing(12)
		self.set_resizable(gtk.FALSE)

		for stock, response in buttons:
			self.add_button(stock, response)

		if default is not None:
			self.set_default_response(default)
		else:
			self.set_default_response(buttons[-1][1])


	def get_button(self, index):
		buttons = self.action_area.get_children()
		return index < len(buttons) and buttons[index] or None



class Hig(Dialog):

	def __init__(self, parent, pritext, sectext, stockimage, buttons, default = None):
		Dialog.__init__(self, parent, "", buttons, default)

		# hbox separating dialog image and contents
		hbox = gtk.HBox()
		hbox.set_spacing(12)
		hbox.set_border_width(6)
		self.vbox.pack_start(hbox)

		# set up image
		if stockimage is not None:
			image = gtk.Image()
			image.set_from_stock(stockimage, gtk.ICON_SIZE_DIALOG)
			image.set_alignment(0.5, 0)
			hbox.pack_start(image, gtk.FALSE, gtk.FALSE)

		# set up main content area
		self.contents = gtk.VBox()
		self.contents.set_spacing(10)
		hbox.pack_start(self.contents)

		label = gtk.Label()
		label.set_markup("<span size=\"larger\" weight=\"bold\">" + pritext + "</span>\n\n" + sectext)
		label.set_line_wrap(gtk.TRUE)
		label.set_alignment(0, 0)
		self.contents.pack_start(label)


	def run(self):
		self.show_all()
		response = gtk.Dialog.run(self)
		self.destroy()

		return response



class Error(Hig):

	def __init__(self, parent, pritext, sectext):
		Hig.__init__(
			self, parent, pritext, sectext, gtk.STOCK_DIALOG_ERROR,
			[ [ gtk.STOCK_OK, gtk.RESPONSE_OK ] ]
		)



class FileOverwrite(Hig):

	def __init__(self, parent, file):
		Hig.__init__(
			self, parent, "Overwrite existing file?",
			"The file '" + file + "' already exists. If you choose to overwrite the file, its contents will be lost.", gtk.STOCK_DIALOG_WARNING,
			[ [ gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ], [ gtk.STOCK_OK, gtk.RESPONSE_OK ] ],
			gtk.RESPONSE_CANCEL
		)


	def run(self):
		return Hig.run(self) == gtk.RESPONSE_OK


class FileChooserAddon(gtk.FileChooserDialog):
	def __init__(self):
		gtk.FileChooserDialog.__init__(self)
		self.addon_frame = gtk.Frame()
		self.set_extra_widget(self.addon_frame)
		self.addon_vbox = gtk.VBox(spacing=3)
		self.addon_frame.add(self.addon_vbox)

	def set_frame_title(self, title):
		frame_title = '<span weight="bold">' + title + '</span>'
		frame_label = gtk.Label(frame_title)
		frame_label.set_use_markup(gtk.TRUE)
		self.addon_frame.set_label_widget(frame_label)

	def add(self, widget, expand=gtk.TRUE, fill=gtk.TRUE, padding=28):
		hbox = gtk.HBox()
		hbox.pack_start(gtk.Label(), gtk.FALSE, gtk.FALSE)
		hbox.pack_start(widget, expand, fill, padding)
		self.addon_vbox.pack_start(hbox)

class ImportTextChooser(FileChooserAddon):
	def __init__(self):
		FileChooserAddon.__init__(self)
		self.set_title("Import a text file...")
		self.add_buttons(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
						gtk.STOCK_OPEN, gtk.RESPONSE_OK)
		self.set_frame_title('Import Options')
		self.link_checkbox = gtk.CheckButton("Link Note to File")
		self.add(self.link_checkbox)
		self.show_all()

	def get_link_active(self):
		return self.link_checkbox.get_active()

class ImportNoteChooser(FileChooserAddon):
	def __init__(self):
		FileChooserAddon.__init__(self)
		self.set_title("Import a Notemeister note...")
		self.add_buttons(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
						gtk.STOCK_OPEN, gtk.RESPONSE_OK)
		self.set_frame_title('Import Options')
		self.append_radiobutton = gtk.RadioButton(None, "Append to Currently Selected Note")
		self.root_radiobutton = gtk.RadioButton(self.append_radiobutton, 'Add to Toplevel of Note Tree')
		self.add(self.append_radiobutton)
		self.add(self.root_radiobutton)
		self.show_all()

	def get_append_position(self):
		if self.root_radiobutton.get_active():
			return "root"
		elif self.append_radiobutton.get_active():
			return "current"

class ExportNoteChooser(FileChooserAddon):
	def __init__(self, has_children=gtk.FALSE):
		FileChooserAddon.__init__(self)
		self.set_title("Export Notemeister Notes...")
		self.set_action(gtk.FILE_CHOOSER_ACTION_SAVE)
		self.add_buttons(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
						gtk.STOCK_SAVE, gtk.RESPONSE_OK)
		self.set_frame_title('Export Options')
		self.single_radio = gtk.RadioButton(None, "Export Single Note")
		self.sub_tree_radio = gtk.RadioButton(self.single_radio, "Export this Sub Tree")
		self.whole_tree_radio = gtk.RadioButton(self.single_radio, "Export Entire Note Tree")
		self.add(self.single_radio)
		if has_children:
			self.add(self.sub_tree_radio)
#        self.add(self.whole_tree_radio)
		self.show_all()

	def get_notes_to_export(self):
		if self.single_radio.get_active():
			return "single"
		elif self.sub_tree_radio.get_active():
			return "subtree"
		elif self.whole_tree_radio.get_active():
			return "whole"

