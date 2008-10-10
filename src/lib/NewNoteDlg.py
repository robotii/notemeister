#!/usr/bin/env python

import gtk

from gettext import gettext as _

#import const
#import notemeister_main
import notemeister

class NewNoteDlg(gtk.Dialog):

	def __init__(self, selected_title, title_list, text='', link=gtk.TRUE):
		gtk.Dialog.__init__(self, _('Add Note'))
		self.link_path = ''
		pic = gtk.gdk.pixbuf_new_from_file(notemeister.const.aboutPic)
		self.set_icon(pic)
		self.hbox = gtk.HBox(gtk.FALSE, 8)
		self.table = gtk.Table(3, 2, gtk.FALSE)
		self.checkbutton = gtk.CheckButton(_('Add to folder: ') + selected_title)
		self.label1 = gtk.Label(_('Enter Title'))
		self.label2 = gtk.Label(_('Add to '))
		self.entry = gtk.Entry()
		self.image = gtk.Image()
		self.image.set_from_stock(gtk.STOCK_DIALOG_QUESTION, gtk.ICON_SIZE_DIALOG)
		self.combo = gtk.Combo()
		self.combo.set_popdown_strings(title_list)
		self.combo.entry.set_text(selected_title)
		self.link_button = gtk.Button("Link to filesystem...")
		self.link_button.connect("clicked", self.on_link_button_clicked)

		self.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
		self.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
		self.set_default_response(gtk.RESPONSE_OK)
		self.entry.set_activates_default(gtk.TRUE)

		self.hbox.set_border_width(8)
		self.vbox.pack_start(self.hbox, gtk.FALSE, gtk.FALSE, 0)
		self.hbox.pack_start(self.image, gtk.SHRINK)
		if link:
			self.vbox.pack_start(self.link_button, gtk.SHRINK)
		
		self.table.set_row_spacings(4)
		self.table.set_col_spacings(4)
		self.hbox.pack_start(self.table)

		self.table.attach(self.label1, 0, 1, 0, 1)
		self.table.attach(self.entry, 1, 2, 0 ,1)
		self.label1.set_mnemonic_widget(self.entry)

		self.table.attach(self.checkbutton, 1, 2, 1, 2)

		self.entry.set_text(text)
		self.entry.select_region(-1, -1)
		self.set_resizable(gtk.FALSE)
		self.show_all()

	def on_link_button_clicked(self, obj):
		chooser = gtk.FileChooserDialog("Choose a file...", 
				self, 
				gtk.FILE_CHOOSER_ACTION_SAVE,
				(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
				 gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		response = chooser.run()
		if response == gtk.RESPONSE_OK:
			self.link_path = chooser.get_filename()
		chooser.destroy()

	def get_entry(self):
		return self.entry.get_text()

	def set_entry(self, text):
		self.entry.set_text(text)
		self.entry.select_region(-1, -1)

	def get_checked(self):
		return self.checkbutton.get_active()

	def get_parent(self):
		return self.combo.entry.get_text()

	def get_link_path(self):
		return self.link_path

