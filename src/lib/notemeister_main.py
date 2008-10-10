#!/usr/bin/env python

import sys, os
import gobject
import gtk
import gnome
import gnome.ui
import gtk.glade
import gtk.gdk

import notemeister

from gettext import gettext as _

class NoteMeister:

	visible = gtk.TRUE

	def __init__(self):
		self.program = gnome.program_init('notemeister', notemeister.const.version)
		self.Conf = notemeister.Configurator.Configurator()
		self.textview = notemeister.NoteView.NoteView(self.Conf)
		self.treeview = notemeister.NoteTree.NoteTree(self.textview)
		self.init_interface()
		self.treescroller.add(self.treeview)
		self.viewscroller.add(self.textview)

		self.treeview.connect("button_press_event", self.on_button_press_event)
		self.treeview.connect("doubleclick", self.on_doubleclick)

		self.treeview.loadNotes()
			
		tree_state = self.Conf.get_string("/apps/notemeister/tree_state")
		if len(self.treeview.noteList) > 0:
			path = self.treeview.restore_tree_state(tree_state)
			if len(path):
				self.treeview.set_cursor(path, None, gtk.FALSE)
		else:
			self.show_welcome()

		if self.Conf.enable_autosave:
			self.auto_save_notes()

		notemeister.utils.make_path(notemeister.const.dataPath)

		self.topWindow.show_all()
		gtk.main()

	def show_welcome(self):
		title_buffer = notemeister.TitleBuffer.TitleBuffer()
		self.textview.set_buffer(title_buffer)
		self.textview.add_child_at_anchor(title_buffer.image, title_buffer.image_anchor)
		self.textview.add_child_at_anchor(title_buffer.button, title_buffer.button_anchor)
		title_buffer.button.connect('clicked', self.on_add_note_activate)
		self.textview.unset_flags(gtk.CAN_FOCUS)
		title_buffer.image.show()
		title_buffer.button.show()

	def init_interface(self):
		"""Initializes the GLADE interface, aquiring references to the widgets
		that it needs
		"""
		self.gtop 		= gtk.glade.XML(notemeister.const.gladeFile, "notemeister", "notemeister")
		self.topWindow 	= self.gtop.get_widget("notemeister")
		self.topWindow.resize(self.Conf.window_size_x, self.Conf.window_size_y)
		self.topWindow.move(self.Conf.window_pos_x, self.Conf.window_pos_y)
		pic = gtk.gdk.pixbuf_new_from_file(notemeister.const.aboutPic)
		self.topWindow.set_icon(pic)
		self.topWindow.set_title("Notemeister")
		self.topWindow.connect("delete_event", self.delete_event)
		self.topWindow.connect("destroy", self.destroy)
		self.topWindow.connect("frame_event", self.on_window_frame_event)

		self.icons = notemeister.Stock.IconFactory(self)

		window_actions = [
			('FileMenu', None, '_File'),
			('Add',	gtk.STOCK_ADD, 'Add Note', None, 'Add a Note', 'on_add_note_activate'),
			('Rename', None, 'Rename Note', None, 'Rename a Note', 'on_rename_note_activate'),
			('Remove', gtk.STOCK_REMOVE, 'Remove Note', None, 'Remove a Note', 'on_remove_note_activate'),
			('Import', notemeister.Stock.STOCK_IMPORT, 'Import from...'),
			('ImportText', notemeister.Stock.STOCK_NOTE, 'Text', None, 'Import a Note from a Text File', 'on_import_text_activate'),
			('ImportNM', notemeister.Stock.STOCK_APPLICATION, 'Notemeister Note', None, 'Import a Notemeister Note', 'on_import_nm_activate'),
			('Export', notemeister.Stock.STOCK_EXPORT, 'Export to...'),
			('ExportText', notemeister.Stock.STOCK_NOTE, 'Text', None, 'Export a Note to a Text File', 'on_export_text_activate'),
			('ExportNM', notemeister.Stock.STOCK_APPLICATION, 'Notemeister Note', None, 'Export a Notemeister Note', 'on_export_nm_activate'),
			('Quit', gtk.STOCK_QUIT, 'Quit', '<control>Q', 'Quit Notemeister', 'destroy'),
			('EditMenu', None, '_Edit'),
			('Cut', gtk.STOCK_CUT, 'Cut', '<control>X', 'Cut to Clipboard', 'on_cut_activate'),
			('Copy', gtk.STOCK_COPY, 'Copy', '<control>C', 'Copy to Clipboard', 'on_copy_activate'),
			('Paste', gtk.STOCK_PASTE, 'Paste', '<control>V', 'Paste from Clipboard', 'on_paste_activate'),
			('FormatMenu', None, 'F_ormat'),
			('Bold', gtk.STOCK_BOLD, 'Bold', '<control>B', 'Bold Selected Text', 'on_bold_activate'),
			('Italics', gtk.STOCK_ITALIC, 'Italics', '<control>I', 'Italicize Selected Text', 'on_italic_activate'),
			('Underline', gtk.STOCK_UNDERLINE, 'Underline', '<control>U', 'Underline Selected Text', 'on_underline_activate'),
			('ToolsMenu', None, '_Tools'),
			('Preferences', gtk.STOCK_PREFERENCES, 'Preferences', '<control><alt>P', 'Change Preferences', 'on_preferences_activate'),
			('HelpMenu', None, '_Help'),
			('About', notemeister.Stock.STOCK_APPLICATION, 'About', None, 'About Notemeister', 'on_about_activate'),
			('FontSize', gtk.STOCK_SELECT_FONT, None, None, 'Cycle Font Size', 'on_font_scale_activate'),
			('Date', notemeister.Stock.STOCK_DATE, 'Date', None, 'Insert Current Date', 'on_date_clicked'),
			('Time', notemeister.Stock.STOCK_TIME, 'Time', None, 'Insert Current Time', 'on_time_clicked'),
			('Properties', gtk.STOCK_PROPERTIES, 'Properties', None, 'View Note Properties', 'on_properties_activate'),
			('SelectAll', None, 'Select All', None, 'Select All Text in Note', 'on_select_all_activate'),
			('Website', notemeister.Stock.STOCK_WEB, 'Notemeister Homepage', None, 'Go to the Notemeister Hompage', 'on_website_activate'),
			]
		
		ag = gtk.ActionGroup('NotemeisterActions')

		ag.add_toggle_actions([
				('Wrap', None, 'Word wrap', None, 'Toggle Word Wrap for Note', 'on_word_wrap_toggled')
				])

		wrap_toggle = ag.get_action('Wrap')
		self.treeview.get_refs(wrap_toggle)

		actions = self.fix_actions(window_actions, self)
		ag.add_actions(actions)
		self.ui = gtk.UIManager()
		self.ui.insert_action_group(ag, 0)
		self.ui.add_ui_from_file(notemeister.const.uiFile)
		self.topWindow.add_accel_group(self.ui.get_accel_group())

		self.menubox 	= self.gtop.get_widget("handlebox1")
		self.toolbox 	= self.gtop.get_widget("handlebox2")
		self.toolbar = self.ui.get_widget('/Toolbar')
		self.toolbar.set_style(gtk.TOOLBAR_ICONS)
		self.menubar = self.ui.get_widget('/Menubar')
		self.menubox.add(self.menubar)
		self.toolbox.add(self.toolbar)

		view_popup = self.ui.get_widget('/ViewMenu')
		self.textview.ref_view_popup(view_popup)

		tree_popup = self.ui.get_widget('/TreeMenu')
		self.treeview.ref_tree_popup(tree_popup)

		# Add the font size indicator to the toolbar
		self.font_indicator = gtk.ToolItem()
		self.font_label = gtk.Label()
		self.font_indicator.add(self.font_label)
		self.font_label.set_size_request(80, -1)
		self.textview.ref_font_label(self.font_label)
		self.font_label.unset_flags(gtk.CAN_FOCUS)
		self.toolbar.insert(self.font_indicator, 11)

		self.treescroller 	= self.gtop.get_widget("tree_scroll")
		self.viewscroller 	= self.gtop.get_widget("view_scroll")
		self.hpaned1 = self.gtop.get_widget("hpaned1")
		self.hpaned1.set_position(self.Conf.tree_width)


#        if self.Conf.enable_trayicon:
#            self.trayicon 	= trayicon.TrayIcon("trayicon")
#            self.traybox = gtk.EventBox()
#            self.trayicon.add(self.traybox)
#            self.tray_image = gtk.Image()
#            self.tray_image.set_from_file(notemeister.const.trayPic)
#            self.treeview.save_active_note()
#            self.traybox.add(self.tray_image)
#            self.traybox.connect("button_press_event", self.on_tray_activate)
#            self.trayicon.show_all()

		self.vbox 		= self.gtop.get_widget("vbox1")
		self.statusbar 	= notemeister.TimedStatusbar.timedStatusbar()
		self.vbox.pack_end(self.statusbar, gtk.FALSE, gtk.FALSE)

	def on_doubleclick(self, obj, iter):
		self.show_properties_dialog()

	def on_website_activate(self, obj):
		gnome.url_show('http://notemeister.sourceforge.net')

	def on_select_all_activate(self, obj):
		self.textview.on_select_all_activate(self)

	def on_cut_activate(self, obj):
		self.textview.on_cut_activate(self)

	def on_copy_activate(self, obj):
		self.textview.on_copy_activate(self)

	def on_paste_activate(self, obj):
		self.textview.on_paste_activate(self)

	def on_bold_activate(self, obj):
		self.textview.on_bold_activate(self)

	def on_italic_activate(self, obj):
		self.textview.on_italic_activate(self)

	def on_underline_activate(self, obj):
		self.textview.on_underline_activate(self)

	def on_font_scale_activate(self, obj):
		self.textview.on_font_scale_activate(self)

	def on_date_clicked(self, obj):
		self.textview.on_date_clicked(self)

	def on_time_clicked(self, obj):
		self.textview.on_time_clicked(self)

	def fix_actions(self, actions, instance):
		"Helper function to map methods to an instance"
		retval = []
		
		for i in range(len(actions)):
			curr = actions[i]
			if len(curr) > 5:
				curr = list(curr)
				curr[5] = getattr(instance, curr[5])
				curr = tuple(curr)
				
			retval.append(curr)
		return retval


	def check_data_path(self):
		if not os.path.exists(notemeister.const.dataPath):
			os.mkdir(notemeister.const.dataPath)

	def delete_event(self, widget, event, data=None):
		"""Close via the windowmanager"""
		self.on_exit_activate()
		return gtk.TRUE

	def destroy(self, widget, data=None):
		"""Do cleanup and kill the toplevel widget"""
		self.on_exit_activate()

	def on_move_cursor(self, obj, event, iter):
		print 'moved'

	def on_exit_activate(self):
		"""Save data and clean up"""
		self.save_window_state()
		self.treeview.save_active_note()
		self.treeview.saveNotes()
		gtk.main_quit()

	def save_window_state(self):
		tree_state = self.treeview.get_tree_state()
		self.Conf.set_string("/apps/notemeister/tree_state", tree_state)
		(x, y) = self.topWindow.get_size()
		self.Conf.set_int("/apps/notemeister/window_size_x", x)
		self.Conf.set_int("/apps/notemeister/window_size_y", y)
		(x, y) = self.topWindow.get_position()
		self.Conf.set_int("/apps/notemeister/window_pos_x", x)
		self.Conf.set_int("/apps/notemeister/window_pos_y", y)
		x = self.hpaned1.get_position()
		self.Conf.set_int("/apps/notemeister/tree_width", x)

	def on_window_frame_event(self, obj):
		print "in frame_event"

	def on_about_activate(self, obj):
		"""Displays the about box."""
		pixbuf = gtk.gdk.pixbuf_new_from_file(notemeister.const.aboutPic)
		pixbuf = pixbuf.scale_simple(120, 120, gtk.gdk.INTERP_BILINEAR)

		gnome.ui.About(notemeister.const.progName,
						notemeister.const.version,
						notemeister.const.copyright,
						notemeister.const.comments,
						notemeister.const.authors,
						notemeister.const.documenters,
						notemeister.const.translators,
						pixbuf).show()

	def on_add_note_activate(self, obj, popup=gtk.FALSE):
		"""Displays the 'Add Note' dialog and adds a note to the NoteTree"""
		selected_title = self.treeview.get_selected_title() 
		title_list = self.treeview.get_list_of_titles()
		newNoteDlg = notemeister.NewNoteDlg.NewNoteDlg(selected_title, title_list)
		if popup == gtk.TRUE and not selected_title == _('None'):
			newNoteDlg.checkbutton.set_active(gtk.TRUE)
		response = newNoteDlg.run()

		if response == gtk.RESPONSE_CANCEL:
			newNoteDlg.destroy()
		else:
			title = newNoteDlg.get_entry()
			note = notemeister.Note.Note(title = title, link = newNoteDlg.get_link_path())
			checked = newNoteDlg.get_checked()
			if checked:
				(model, iter) = self.treeview.get_selection().get_selected()
				self.treeview.add_new_note_to_tree(note, iter)
			else:
				self.treeview.add_new_note_to_tree(note)

		newNoteDlg.destroy()	

	def on_remove_note_activate(self, obj):
		"""Removes a note from the tree"""
		dlg = gtk.Dialog(_("Remove Note"))
		pic = gtk.gdk.pixbuf_new_from_file(notemeister.const.aboutPic)
		dlg.set_icon(pic)
		hbox = gtk.HBox(gtk.FALSE, 8)
		hbox.set_border_width(8)
		image = gtk.Image()
		image.set_from_stock(gtk.STOCK_DIALOG_QUESTION, gtk.ICON_SIZE_DIALOG)
		dlg.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
		dlg.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
		title = self.treeview.get_selected_title()
		label = gtk.Label(_("Are you sure you want to \nremove note <b>") + title + "</b>?")
		label.set_use_markup(gtk.TRUE)
		dlg.vbox.pack_start(hbox, gtk.SHRINK)
		hbox.pack_start(image, gtk.SHRINK)
		hbox.pack_start(label, gtk.SHRINK)
		dlg.show_all()

		response = dlg.run()
		if not response == gtk.RESPONSE_OK:
			pass
		else:
			self.treeview.remove_note_from_tree()
			if self.treeview.is_empty():
				self.show_welcome()
		dlg.destroy()

	def on_rename_note_activate(self, obj):
		"""Renames a note in the tree, via a dialog"""
		hbox = gtk.HBox(gtk.FALSE, 8)
		entry = gtk.Entry()
		entry.set_activates_default(gtk.TRUE)
		label = gtk.Label(_("Enter new name: "))
		image = gtk.Image()
		image.set_from_stock(gtk.STOCK_DIALOG_QUESTION, gtk.ICON_SIZE_DIALOG)

		dlg = gtk.Dialog(_("Rename Note"))
		pic = gtk.gdk.pixbuf_new_from_file(notemeister.const.aboutPic)
		dlg.set_icon(pic)
		dlg.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
		dlg.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
		dlg.set_default_response(gtk.RESPONSE_OK)

		hbox.set_border_width(8)
		dlg.vbox.pack_start(hbox, gtk.SHRINK)
		hbox.pack_start(image, gtk.SHRINK)
		hbox.pack_start(label, gtk.SHRINK)
		hbox.pack_start(entry, gtk.SHRINK)
		selected_title = self.treeview.get_selected_title() 
		entry.set_text(selected_title)
		entry.select_region(-1, -1)

		dlg.show_all()
		
		response = dlg.run()
		if response != gtk.RESPONSE_OK:
			dlg.destroy()
			return
		new_name = entry.get_text()
		self.treeview.set_new_name(new_name)
		dlg.destroy()

	def on_preferences_activate(self, obj):
		self.show_prefs_dialog()

	def on_properties_activate(self, obj):
		self.show_properties_dialog()

	def on_import_nm_activate(self, obj):
#        dialog = gtk.FileChooserDialog("Import a Note...",
#                None,
#                gtk.FILE_CHOOSER_ACTION_OPEN,
#                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
#                 gtk.STOCK_OPEN, gtk.RESPONSE_OK))
#        parent_checkbox = gtk.CheckButton("Append to current note?")
#        dialog.set_extra_widget(parent_checkbox)
		dialog = notemeister.Dialogs.ImportNoteChooser()
		if dialog.run() == gtk.RESPONSE_OK:
			dialog.hide()
			position = dialog.get_append_position()
			filename = dialog.get_filename()
			note_list = self.treeview.load_from_xml(filename)

			if not note_list: # imported file was of invalid format
				dialog.destroy()
				return
			
			if position == "current":
				(model, iter) = self.treeview.get_selection().get_selected()
				# append subtree as last child of selected note
				note_list[0].path = self.treeview.store.get_string_from_iter(iter) + ':' + str(self.treeview.store.iter_n_children(iter))
				root_path = note_list[0].path
				self.treeview.add_new_note_to_tree(note_list[0], self.treeview.get_parent_iter(note_list[0]))
				for note in note_list[1:]:
					note.path = note.path.replace('root', root_path)
					self.treeview.add_new_note_to_tree(note, self.treeview.get_parent_iter(note))
			elif position == "root":
				note_list[0].path = str(self.treeview.store.iter_n_children(None))
				root_path = note_list[0].path
				self.treeview.add_new_note_to_tree(note_list[0], self.treeview.get_parent_iter(note_list[0]))
				for note in note_list[1:]:
					note.path = note.path.replace('root', root_path)
					self.treeview.add_new_note_to_tree(note, self.treeview.get_parent_iter(note))

			self.statusbar.output(_("Notes imported from " + filename + ' ...'), 5000)
		else:
			pass
		dialog.destroy()

	def on_import_text_activate(self, obj):
#        dialog = gtk.FileChooserDialog("Import a file...",
#                None,
#                gtk.FILE_CHOOSER_ACTION_OPEN,
#                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
#                 gtk.STOCK_OPEN, gtk.RESPONSE_OK))
#        addon = notemeister.Dialogs.FileChooserAddon('Import Options')
#        link_checkbox = gtk.CheckButton("Link Note to File")
#        addon.add(link_checkbox)
#        addon.show_all()
#        dialog.set_extra_widget(addon)
		dialog = notemeister.Dialogs.ImportTextChooser()
		if dialog.run() == gtk.RESPONSE_OK:
			dialog.hide()
			filename = dialog.get_filename()
			contents = self.get_text_file_contents_to_string(filename)

			if contents == None:
				dialog.destroy()
				return

			selected_title = self.treeview.get_selected_title() 
			title_list = self.treeview.get_list_of_titles()
			if dialog.get_link_active():
				newNoteDlg = notemeister.NewNoteDlg.NewNoteDlg(selected_title, title_list, os.path.basename(filename), gtk.FALSE)
			else :
				newNoteDlg = notemeister.NewNoteDlg.NewNoteDlg(selected_title, title_list, os.path.basename(filename))
			response = newNoteDlg.run()

			if response == gtk.RESPONSE_CANCEL:
				newNoteDlg.destroy()
			else:
				title = newNoteDlg.get_entry()
				link_path = newNoteDlg.get_link_path()

				note = notemeister.Note.Note(title = title, body = contents, link = link_path)
				if dialog.get_link_active():
					note.link = filename
				checked = newNoteDlg.get_checked()
				if checked:
					(model, iter) = self.treeview.get_selection().get_selected()
					self.treeview.add_new_note_to_tree(note, iter)
				else:
					self.treeview.add_new_note_to_tree(note)
				newNoteDlg.destroy()	
				self.statusbar.output(_("Note imported from " + filename + ' ...'), 5000)
		else:
			dialog.destroy()

	def get_text_file_contents_to_string(self, filename):
		if not notemeister.utils.check_read_permissions(filename):
			notemeister.Dialogs.Error(None, "Permission Denied", "You don't have permission to read the specified file.").run()
			return None
		
		try:
			f = file(filename, 'r')
		except IOError:
			pass  #FIXME : Do the right thing dummy..

		contents = f.read()
		f.close()
		return contents

	def on_export_nm_activate(self, obj):
#        dialog = gtk.FileChooserDialog("Export to Note...", 
#                None, 
#                gtk.FILE_CHOOSER_ACTION_SAVE,
#                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
#                 gtk.STOCK_SAVE, gtk.RESPONSE_OK))
		(model, iter) = self.treeview.get_selection().get_selected()
#        subtree_checkbox = gtk.CheckButton("Export entire subtree")
		if self.treeview.store.iter_has_child(iter):
			dialog = notemeister.Dialogs.ExportNoteChooser(gtk.TRUE)
		else :
			dialog = notemeister.Dialogs.ExportNoteChooser()
#            dialog.set_extra_widget(subtree_checkbox)
		title = self.treeview.get_selected_title()
		dialog.set_current_name(notemeister.utils.note_name_to_file_name(title))
		if dialog.run() == gtk.RESPONSE_OK:
			dialog.hide()
			note_list = []
			filename = dialog.get_filename()

			# Do we have write permissions?
			if not notemeister.utils.check_write_permissions(filename):
				notemeister.Dialogs.Error(None, "Permission Denied", "You don't have permission to write to the specified location.").run()
				dialog.destroy()
				return

			# Does the file already exist?
			if notemeister.utils.check_path_exists(filename):
				if not notemeister.Dialogs.FileOverwrite(None, filename).run():
					dialog.destroy()
					return

			notes = dialog.get_notes_to_export() # single note, whole, or subtree?
			if notes == "subtree":
				note_list = []
				root_path = self.treeview.store.get_string_from_iter(iter)
				note = self.treeview.store.get_value(iter, 2)
				self.textview.format_body_with_tags(note)
				note_list.append(('root', note.title, note.body, note.link, note.wrap))
				self.treeview.subtree_to_list(note_list, self.treeview.store.iter_children(iter))
				for note in note_list[1:]:
					note[0] = note[0].replace(root_path, 'root', 1)
					note[3] = '' # don't want to preserve exported links just yet
			elif notes == "single":
				note = self.treeview.store.get_value(iter, 2)
				self.textview.format_body_with_tags(note)
				note_list.append(('root', 
									note.title, 
									note.body, 
									'', # don't preserve links just yet 
									note.wrap))
			elif notes == "whole":
				print "Not yet implemented"

			xml_doc = self.treeview.note_list_to_xml(note_list)
			self.treeview.write_xml_to_file(xml_doc, filename)

			self.statusbar.output(_("Note saved as " + filename + '...'), 5000)
		else:
			pass
		dialog.destroy()

	def on_export_text_activate(self, obj):
		"""Initiates the saving of notes to disk"""
		dialog = gtk.FileChooserDialog("Export to text...", 
				None, 
				gtk.FILE_CHOOSER_ACTION_SAVE,
				(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
				 gtk.STOCK_SAVE, gtk.RESPONSE_OK))
		title = self.treeview.get_selected_title()
		dialog.set_current_name(notemeister.utils.note_name_to_file_name(title))
		if dialog.run() == gtk.RESPONSE_OK:
			dialog.hide()
			filename = dialog.get_filename()
			buffer = self.textview.get_buffer()
			text = buffer.get_text(buffer.get_start_iter(),
									buffer.get_end_iter())

			# Do we have write permissions?
			if not notemeister.utils.check_write_permissions(filename):
				notemeister.Dialogs.Error(None, "Permission Denied", "You don't have permission to write to the specified location.").run()
				dialog.destroy()
				return

			# Does the file already exist?
			if notemeister.utils.check_path_exists(filename):
				if not notemeister.Dialogs.FileOverwrite(None, filename).run():
					dialog.destroy()
					return

			try:
				f = file(filename, 'w')
			except IOError:
				pass  #FIXME : Do the right thing dummy..

			f.write(text + '\n')
			f.close()
			self.statusbar.output(_("Note saved as " + filename + '...'), 5000)
		else:
			dialog.destroy()
			
	def auto_save_notes(self):
		"""Autosave routine to store data automatically"""
		timer = gtk.timeout_add(self.Conf.autosave_time * 60000, self.save_notes_to_disk, None)

	def save_notes_to_disk(self, obj):
		self.statusbar.output(_("Autosaving data..."), 2000)
		self.treeview.saveNotes()
		if self.Conf.enable_autosave:
			return gtk.TRUE
		else:
			return gtk.FALSE

	def on_tray_activate(self, obj, event):
		if event.button == 1:
			self.toggle_visibility()

	def toggle_visibility(self):
		if NoteMeister.visible:
			self.topWindow.hide()
			NoteMeister.visible = gtk.FALSE
		else:
			self.topWindow.show()
			NoteMeister.visible = gtk.TRUE
			

	def on_button_press_event(self, obj, event):
		"""Catch button press events in the main window"""
		if event.button == 3:
			self.popup_menu.popup(None, None, None, event.button, event.time)

	def show_properties_dialog(self):
		self.ptop = gtk.glade.XML(notemeister.const.gladePrefs, "properties_dialog")
		self.prop_dlg = self.ptop.get_widget("properties_dialog")
		lines_label = self.ptop.get_widget("lines_label")
		lines_label.set_text('<span weight="bold">Number of Lines: </span>' + str(self.textview.get_line_count()))
		lines_label.set_use_markup(gtk.TRUE)
		chars_label = self.ptop.get_widget("chars_label")
		chars_label.set_text('<span weight="bold">Number of Characters: </span>' + str(self.textview.get_char_count()))
		chars_label.set_use_markup(gtk.TRUE)
		words_label = self.ptop.get_widget("words_label")
		words_label.set_text('<span weight="bold">Number of Words: </span>' + str(self.textview.get_word_count()))
		words_label.set_use_markup(gtk.TRUE)
		link_label = self.ptop.get_widget("link_label")
		link = self.treeview.get_selected_link()
		if link != "":
			link_label.set_text(link)
		link_label.set_use_markup(gtk.TRUE)
		change_link_button = self.ptop.get_widget("change_link_button")
		change_link_button.connect("clicked", self.on_change_link_button_clicked, link_label)
		clear_link_button = self.ptop.get_widget("clear_link_button")
		clear_link_button.connect("clicked", self.on_clear_link_button_clicked, link_label)

		response = self.prop_dlg.run()
		self.prop_dlg.destroy()

	def on_clear_link_button_clicked(self, obj, link_label):
		(model, iter) = self.treeview.get_selection().get_selected()
		note = self.treeview.store.get_value(iter, 2)
		link_label.set_text('<span weight="bold">Note has no link.</span>')
		link_label.set_use_markup(gtk.TRUE)
		note.link = ''
		if self.treeview.store.iter_has_child(iter):
			self.treeview.store.set_value(iter, 0, self.treeview.get_icon_pixbuf(note.link, gtk.TRUE ))
		else:
			self.treeview.store.set_value(iter, 0, self.treeview.get_icon_pixbuf(note.link, gtk.FALSE))

	def on_change_link_button_clicked(self, obj, link_label):
		dialog = gtk.FileChooserDialog("Changing link...", 
				self.prop_dlg, 
				gtk.FILE_CHOOSER_ACTION_SAVE,
				(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
				 gtk.STOCK_SAVE, gtk.RESPONSE_OK))
		
		(model, iter) = self.treeview.get_selection().get_selected()
		if dialog.run() == gtk.RESPONSE_OK:
			#FIXME check permissions etc
			link_label.set_text(dialog.get_filename())
			note = self.treeview.store.get_value(iter, 2)
			note.link = dialog.get_filename()
			if self.treeview.store.iter_has_child(iter):
				self.treeview.store.set_value(iter, 0, self.treeview.get_icon_pixbuf(note.link, gtk.TRUE))
			else:
				self.treeview.store.set_value(iter, 0, self.treeview.get_icon_pixbuf(note.link, gtk.FALSE))

		dialog.destroy()


	def show_prefs_dialog(self):
		self.ptop = gtk.glade.XML(notemeister.const.gladePrefs, "preferences_dialog")
		self.dlg = self.ptop.get_widget("preferences_dialog")
		self.dlg.set_resizable(gtk.FALSE)

		# General Settings	
#        tray_checkbox = self.ptop.get_widget("tray_checkbutton")
		autosave_checkbox = self.ptop.get_widget("autosave_checkbutton")
		autosave_entry = self.ptop.get_widget("autosave_entry")

#        if self.Conf.enable_trayicon:
#            tray_checkbox.set_active(gtk.TRUE)
		if self.Conf.enable_autosave:
			autosave_checkbox.set_active(gtk.TRUE)

		autosave_entry.set_value(self.Conf.autosave_time)

		# Format Settings
		twelve_hour_radio = self.ptop.get_widget("twelve_hour_radio")
		twentyfour_hour_radio = self.ptop.get_widget("twentyfour_hour_radio")
		long_date_radio = self.ptop.get_widget("long_date_radio")
		short_date_radio = self.ptop.get_widget("short_date_radio")

		if self.Conf.twelve_hour_time:
			twelve_hour_radio.set_active(gtk.TRUE)
		else:
			twentyfour_hour_radio.set_active(gtk.TRUE)

		if self.Conf.long_date:
			long_date_radio.set_active(gtk.TRUE)
		else:
			short_date_radio.set_active(gtk.TRUE)

		self.ptop.signal_autoconnect({
#                "on_tray_checkbutton_toggled" 	: self.on_tray_checkbutton_toggled,
				"on_autosave_checkbutton_toggled" 	: self.on_autosave_checkbutton_toggled,
				"on_autosave_entry_changed"         : self.on_autosave_entry_changed,
				"on_long_date_radio_toggled" 		: self.on_long_date_radio_toggled,
				"on_twelve_hour_radio_toggled" 		: self.on_twelve_hour_radio_toggled,
				})

		response = self.dlg.run()
		self.dlg.destroy()

	def on_tray_checkbutton_toggled(self, obj):
		if self.Conf.get_bool("/apps/notemeister/enable_trayicon"):
			self.Conf.set_bool("/apps/notemeister/enable_trayicon", 0)
			self.Conf.enable_trayicon = 0
			self.trayicon.destroy()
		else:
			self.Conf.set_bool("/apps/notemeister/enable_trayicon", 1)
			self.Conf.enable_trayicon = 1
			self.trayicon = trayicon.TrayIcon("trayicon")
			self.traybox = gtk.EventBox()
			self.trayicon.add(self.traybox)
			self.tray_image = gtk.Image()
			self.tray_image.set_from_file(notemeister.const.trayPic)
			self.traybox.add(self.tray_image)
			self.traybox.connect("button_press_event", self.on_tray_activate)
			self.trayicon.show_all()

	def on_autosave_checkbutton_toggled(self, obj):
		if self.Conf.get_bool("/apps/notemeister/enable_autosave"):
			self.Conf.set_bool("/apps/notemeister/enable_autosave", 0)
			self.Conf.enable_autosave = 0
		else:
			self.auto_save_notes()
			self.Conf.set_bool("/apps/notemeister/enable_autosave", 1)
			self.Conf.enable_autosave = 1

	def on_autosave_entry_changed(self, obj):
		autosave_entry = self.ptop.get_widget("autosave_entry")
		new_time = autosave_entry.get_value_as_int()
		self.Conf.set_int("/apps/notemeister/autosave_time", new_time)
		self.Conf.autosave_time = new_time
		self.auto_save_notes()

	def on_long_date_radio_toggled(self, obj):
		if self.Conf.get_bool("/apps/notemeister/long_date"):
			self.Conf.set_bool("/apps/notemeister/long_date", 0)
			self.Conf.long_date = 0
		else:
			self.Conf.set_bool("/apps/notemeister/long_date", 1)
			self.Conf.long_date = 1

	def on_twelve_hour_radio_toggled(self, obj):
		if self.Conf.get_bool("/apps/notemeister/twelve_hour_time"):
			self.Conf.set_bool("/apps/notemeister/twelve_hour_time", 0)
			self.Conf.twelve_hour_time = 0
		else:
			self.Conf.set_bool("/apps/notemeister/twelve_hour_time", 1)
			self.Conf.twelve_hour_time = 1


