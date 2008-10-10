#!/usr/bin/env python

import gtk, gnome, gnome.ui, gconf

#import const
#import notemeister_main
import notemeister

class Configurator:

	def __init__(self):
		self.client = gconf.client_get_default()
		if not self.client.dir_exists("/apps/notemeister"):
			self.client.add_dir("/apps/notemeister", gconf.CLIENT_PRELOAD_NONE)
			self.set_bool("/apps/notemeister/enable_autosave", 0)
			self.set_int("/apps/notemeister/autosave_time", 3)
			self.set_bool("/apps/notemeister/enable_trayicon", 0)
			self.set_bool("/apps/notemeister/long_date", 0)
			self.set_bool("/apps/notemeister/twelve_hour_time", 0)
			self.set_int("/apps/notemeister/window_size_x", 600)
			self.set_int("/apps/notemeister/window_size_y", 300)
			self.set_int("/apps/notemeister/window_pos_x", 200)
			self.set_int("/apps/notemeister/window_pos_y", 300)
			self.set_int("/apps/notemeister/tree_width", 160)
			self.set_string("/apps/notemeister/tree_state", "0")
		self.client.add_dir("/apps/notemeister", gconf.CLIENT_PRELOAD_NONE)
		self.load_config()

	def load_config(self):
		self.enable_autosave = self.get_bool("/apps/notemeister/enable_autosave", 0)
		self.autosave_time = self.get_int("/apps/notemeister/autosave_time", 3)
		self.enable_trayicon = self.get_bool("/apps/notemeister/enable_trayicon", 0)
		self.long_date = self.get_bool("/apps/notemeister/long_date", 1)
		self.twelve_hour_time = self.get_bool("/apps/notemeister/twelve_hour_time", 1)
		self.window_size_x = self.get_int("/apps/notemeister/window_size_x", 600)
		self.window_size_y = self.get_int("/apps/notemeister/window_size_y", 300)
		self.window_pos_x = self.get_int("/apps/notemeister/window_pos_x", 200)
		self.window_pos_y = self.get_int("/apps/notemeister/window_pos_y", 300)
		self.tree_width = self.get_int("/apps/notemeister/tree_width", 160)
		self.tree_state = self.get_string("/apps/notemeister/tree_state", "0")

	def get_string(self, value, defval=''):
		v = self.client.get_string(value)
		if self.client.get(value):
			return v
		else:
			return defval

	def get_bool(self, key, defval=0):
		v = self.client.get_bool(key)
		if self.client.get(key):
			return v
		else:
			return defval

	def get_int(self, key, defval=0):
		v = self.client.get_int(key)
		if self.client.get(key):
			return v
		else:
			return defval

	def set_int(self, key, value):
		self.client.set_int(key, value)

	def set_bool(self, key, value):
		self.client.set_bool(key, value)

	def set_string(self, key, value):
		self.client.set_string(key, value)



