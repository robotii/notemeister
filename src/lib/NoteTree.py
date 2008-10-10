#!/usr/bin/env python

import sys, cPickle
import gtk
import gnome
import gnome.ui
import gtk.gdk
import gobject
import xml.dom.minidom 
from xml.dom.ext import PrettyPrint

from gettext import gettext as _

import notemeister

class NoteTree(gtk.TreeView):

	anote = None
	noteList = []

	def __init__(self, view):
		gtk.TreeView.__init__(self)
		self.view = view
		self.init_model()
		self.init_view_columns()
		self.set_rules_hint(gtk.TRUE)
		self.set_reorderable(gtk.TRUE)

		self.connect("cursor-changed", self.on_selection_changed)
		self.connect("button-press-event", self.on_button_press_event)

	def init_model(self):
		self.store = gtk.TreeStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING, 
				gobject.TYPE_PYOBJECT)
		self.set_model(self.store)

	def init_view_columns(self):
		self.col = gtk.TreeViewColumn()
		self.col.set_title(_('Title'))
		render_pixbuf = gtk.CellRendererPixbuf()
		self.col.pack_start(render_pixbuf, expand=False)
		self.col.add_attribute(render_pixbuf, 'pixbuf', 0)
		render_text = gtk.CellRendererText()
		self.col.pack_start(render_text, expand=True)
		self.col.add_attribute(render_text, 'text', 1)
		self.append_column(self.col)

	def ref_tree_popup(self, popup):
		self.popup_menu = popup

	def on_button_press_event(self, object, event):
		if event.button == 3:
			self.popup_menu.popup(None, None, None, event.button, event.time)
			return gtk.TRUE
		if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
			path = self.get_path_at_pos(int(event.x), int(event.y))

			if path != None:
				iter = self.store.get_iter(path[0])
				self.emit("doubleclick", iter)

	def get_refs(self, widget):
		self.wrap_toggle = widget
		self.wrap_toggle.connect('toggled', self.on_word_wrap_toggled)

	def on_word_wrap_toggled(self, obj):
		self.set_word_wrap(self.wrap_toggle.get_active())

	def set_word_wrap(self, is_wrap):
		if is_wrap:
			self.view.set_wrap_mode(gtk.WRAP_WORD)
			self.wrap_toggle.set_active(gtk.TRUE)
			self.anote.wrap = '1'
		else:
			self.view.set_wrap_mode(gtk.WRAP_NONE)
			self.wrap_toggle.set_active(gtk.FALSE)
			self.anote.wrap = '0'

	def loadNotes(self):
		# Test to see whether XML data is available
		# if it is, use it
		if notemeister.utils.check_path_exists(notemeister.const.dataFileXML):
			self.noteList = self.load_from_xml(notemeister.const.dataFileXML)
			for note in self.noteList:
				if len(note.path) > 1 :
					self.add_new_note_to_tree(note, self.get_parent_iter(note), gtk.TRUE)
				else : 
					self.add_new_note_to_tree(note, None, gtk.TRUE)
		else: # First time run with new version
			try:
				f = file(notemeister.const.dataFile)
				self.noteList = cPickle.load(f)
				f.close()
			except EOFError:
				self.noteList = []
			except IOError:
				self.noteList = []

			for item in self.noteList:
				if len(item) == 3: # version pre link & wrap
					note = notemeister.Note.Note(item[0], item[1], item[2])
				elif len(item) == 5: # version with link & wrap
					note = notemeister.Note.Note(item[0], item[1], item[2], item[3], item[4])
				self.view.format_body_from_tags(note)
				parent_path = note.path[:-1]
				if len(parent_path):
					parent_iter = self.store.get_iter(parent_path)
					self.add_new_note_to_tree(note, parent_iter, gtk.TRUE)
				else:
					self.add_new_note_to_tree(note, None, gtk.TRUE)
		return len(self.noteList)

	def load_from_xml(self, filename, from_string=gtk.FALSE):
		self.noteList = []
		try:
			if from_string:
				doc = xml.dom.minidom.parseString(filename)
			else :
				doc = xml.dom.minidom.parse(filename)
		except xml.parsers.expat.ExpatError:
			notemeister.Dialogs.Error(None, "Invalid File Format", 
					"The selected file does not appear to be a valid Notemeister note.").run()
			return None
		collection = self.get_collection(doc)
		note_list = doc.getElementsByTagName("note")
		for e in note_list:
			path_node = e.getElementsByTagName("path")
			path = path_node[0].childNodes[0].nodeValue
			title_node = e.getElementsByTagName("title")
			title = title_node[0].childNodes[0].nodeValue
			body_node = e.getElementsByTagName("body")
			body = body_node[0].childNodes[0].nodeValue
			link_node = e.getElementsByTagName("link")
			link = link_node[0].childNodes[0].nodeValue
			wrap_node = e.getElementsByTagName("wrap")
			wrap = wrap_node[0].childNodes[0].nodeValue

			note = notemeister.Note.Note(path, title, body, link.strip(), wrap)
			self.view.format_body_from_tags(note)
			self.noteList.append(note)
		return self.noteList

	def get_collection(self, doc):
		collection = None
		for e in doc.childNodes:
			if e.nodeType == e.ELEMENT_NODE and e.localName == "collection":
				collection = e
				break
		return collection


	def saveNotes(self):
		self.noteList = []
		self.store.foreach(self.add_note_to_list)
		self.store.foreach(self.save_linked_notes)
#        try:
#            f = file(notemeister.const.dataFile, 'w')
#        except IOError:
#            print _('NoteTree.saveNotes(): Error opening data file!')
#            gtk.main_quit()
#
#        cPickle.dump(self.noteList, f)
#        f.close()
		xml_doc = self.note_list_to_xml(self.noteList)
		self.write_xml_to_file(xml_doc, notemeister.const.dataFileXML)

	def note_list_to_xml(self, note_list):
		doc = xml.dom.minidom.Document()
		collection = doc.createElement("collection")
		doc.appendChild(collection)
		for note in note_list:
			new_note = doc.createElement("note")
			collection.appendChild(new_note)

			path = doc.createElement("path")
			new_note.appendChild(path)
			path.appendChild(doc.createTextNode(note[0]))
			title = doc.createElement("title")
			new_note.appendChild(title)
			title.appendChild(doc.createTextNode(note[1]))
			body = doc.createElement("body")
			new_note.appendChild(body)
			body.appendChild(doc.createTextNode(note[2]))
			link = doc.createElement("link")
			new_note.appendChild(link)
			link.appendChild(doc.createTextNode(note[3]))
			wrap = doc.createElement("wrap")
			new_note.appendChild(wrap)
			wrap.appendChild(doc.createTextNode(str(note[4])))
		return doc

	def write_xml_to_file(self, doc, filename):
		file = open(filename, 'w')
		PrettyPrint(doc, file)
		file.close()

	def restore_tree_state(self, tree_state):
		# TODO select first item in list
		selected_path = ''
		expand_list = tree_state.split(",")
		if len(expand_list) > 1:
			selected_path = self.store.get_path(self.store.get_iter_from_string(expand_list[0]))
		for path in expand_list[1:]:
			try:
				iter = self.store.get_iter_from_string(path)
			except ValueError:
				return
			self.expand_to_path(self.store.get_path(iter))
		return selected_path

	def get_tree_state(self):
		(model, iter) = self.get_selection().get_selected()
		if not iter:
			return ''
		self.tree_state_list = []
		self.tree_state_list.append(self.store.get_string_from_iter(iter))
		self.store.foreach(self.check_expanded)
		tree_state = ','.join(self.tree_state_list)
		return tree_state

	def check_expanded(self, store, path, iter, data=None):
		if self.row_expanded(path):
			self.tree_state_list.append(self.store.get_string_from_iter(iter))

	def get_parent_iter(self, note):
		parent_path = note.path[0 : note.path.rfind(':')]
		if len(parent_path) > 0:
			return self.store.get_iter_from_string(parent_path)
		else:
			return None

	def save_linked_notes(self, store, path, iter, data=None):
		note = store.get_value(iter, 2)
		#FIXME file exist? Warn and overwrite
		if len(note.link) > 0:
			try:
				f = file(note.link, 'w')
			except IOError:
				pass #FIXME any file permissions checking etc?

			f.write(note.buffer.get_text(note.buffer.get_start_iter(), note.buffer.get_end_iter()))
			f.close()

	def add_note_to_list(self, store, path, iter, data=None):
		note = store.get_value(iter, 2)
		self.view.format_body_with_tags(note)
#        self.noteList.append((path, note.title, note.body, note.link, note.wrap))
		self.noteList.append((self.store.get_string_from_iter(iter), note.title, note.body, note.link, note.wrap))

	def refresh_note_path(self, store, path, iter, data=None):
		note = self.store.get_value(iter, 2)
		note.path = path

	def subtree_to_list(self, list, root_iter):
		if not root_iter:
			return
		note = self.store.get_value(root_iter, 2)
		list.append([self.store.get_string_from_iter(root_iter), note.title, note.body, note.link, note.wrap])
		self.subtree_to_list(list, self.store.iter_children(root_iter))
		self.subtree_to_list(list, self.store.iter_next(root_iter))

	def move_children_up(self, this_iter, dest_iter):
		if not this_iter:
			return
		else :
			self.move_children_up(self.store.iter_children(this_iter),
					self.store.append(dest_iter, [ self.store.get_value(this_iter, 0),
						self.store.get_value(this_iter, 1),
						self.store.get_value(this_iter, 2)]))
			temp = self.store.iter_next(this_iter)
			if temp:
				self.move_children_up(self.store.iter_next(this_iter),
						self.store.append(self.store.iter_parent(dest_iter), [ self.store.get_value(this_iter, 0),
							self.store.get_value(this_iter, 1),
							self.store.get_value(this_iter, 2)]))


	def subtree_to_list_of_notes(self, list, root_iter):
		if not root_iter:
			return
		note = self.store.get_value(root_iter, 2)
		list.append(note)
		self.subtree_to_list_of_notes(list, self.store.iter_children(root_iter))
		self.subtree_to_list_of_notes(list, self.store.iter_next(root_iter))
	
	def get_string_from_path(self, path):
		return self.store.get_string_from_iter(self.store.get_iter(path))

	def add_new_note_to_tree(self, note, parent=None, load=gtk.FALSE):
		iter = self.store.append(parent, [self.get_icon_pixbuf(link=note.link), note.title, note])
		note.path = self.store.get_path(iter)
#        note.buffer.add_selection_clipboard(self.view.clipboard)

		if parent: # change parent icon in Tree
			self.store.set_value(parent, 0, self.get_icon_pixbuf(self.store.get_value(parent,2).link, gtk.TRUE))

		if not load:
			self.expand_to_path(note.path)
			self.set_cursor_on_cell(note.path, None, None, gtk.FALSE)

		self.view.set_flags(gtk.CAN_FOCUS)
		self.view.grab_focus()

	def remove_note_from_tree(self):
		(model, iter) = self.get_selection().get_selected()
		parent = self.store.iter_parent(iter)
#        if self.store.iter_has_child(iter):
#            self.move_children_up(self.store.iter_children(iter), self.store.iter_parent(iter))
		self.store.remove(iter)
		if parent:
			link = self.store.get_value(parent, 2).link
			path = self.store.get_path(parent)
			self.set_cursor(path)
			if self.store.iter_has_child(parent):
				self.store.set_value(parent, 0, self.get_icon_pixbuf(link, gtk.TRUE))
			else:
				self.store.set_value(parent, 0, self.get_icon_pixbuf(link, gtk.FALSE))
		else:
			self.set_cursor((0,), None, gtk.FALSE)




	def get_selected_link(self):
		(model, iter) = self.get_selection().get_selected()
		if not iter:
			return ""
		else:
			return self.store.get_value(iter, 2).link

	def set_new_name(self, new_name):
		(model, iter) = self.get_selection().get_selected()
		if not iter:
			return
		else:
			self.store.get_value(iter, 2).title = new_name
			self.store.set_value(iter, 1, new_name)

	def get_icon_pixbuf(self, link, is_parent=gtk.FALSE):
		"""Returns the appropriate icon for a given node"""
		if is_parent:
			if len(link) < 1 :
				return self.render_icon(stock_id=notemeister.Stock.STOCK_FOLDER, size=gtk.ICON_SIZE_MENU,
						detail=None)
			else:
				return self.render_icon(stock_id=notemeister.Stock.STOCK_FOLDER_LINK, size=gtk.ICON_SIZE_MENU,
						detail=None)
		else:
			if len(link) < 1 :
				return self.render_icon(stock_id=notemeister.Stock.STOCK_NOTE, size=gtk.ICON_SIZE_MENU,
						detail=None)
			else:
				return self.render_icon(stock_id=notemeister.Stock.STOCK_LINK, size=gtk.ICON_SIZE_MENU, detail=None)

	def get_selected_title(self):
		(model, iter) = self.get_selection().get_selected()
		if iter:
			return self.store.get_value(iter, 1)
		else: 
			return _('None')

	def get_list_of_titles(self):
		self.title_list = []
		self.store.foreach(self.add_title_to_list)
		return self.title_list

	def add_title_to_list(self, store, path, iter, data=None):
		title = store.get_value(iter, 1)
		self.title_list.append(title)

	def on_selection_changed(self, treeview):
		if self.anote:
			self.anote.body = self.anote.buffer.get_text(
					self.anote.buffer.get_start_iter(),
					self.anote.buffer.get_end_iter())
		(model, iter) = self.get_selection().get_selected()
		if iter:
			note = self.store.get_value(iter, 2)
			self.view.set_buffer(note.buffer)
			self.anote = note
			self.set_word_wrap(note.wrap)
		else:
			self.anote = None

	def is_empty(self):
		if self.store.get_iter_root():
			return gtk.FALSE
		else:
			return gtk.TRUE

	def save_active_note(self):
		if self.anote:
			self.anote.body = self.anote.buffer.get_text(
					self.anote.buffer.get_start_iter(),
					self.anote.buffer.get_end_iter())


gobject.signal_new("doubleclick", NoteTree, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, (gobject.TYPE_PYOBJECT, ))

