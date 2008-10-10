#!/usr/bin/env python

import os, sys
from distutils.core import setup, Extension

datadir = "share/notemeister/"
version = '0.1.7'

setup(
		name 			= 	"notemeister",
		version 		= 	version,
		description 	= 	"Notemeister note organizer for GNOME",
		author 			= 	"Dennis Craven",
		author_email 	= 	"arker66@users.sourceforge.net",
		url 			= 	"http://notemeister.sourceforge.net/",
		license 		= 	"GPL",

		packages 		= 	[ 'notemeister' ],
		package_dir 	= 	{ 'notemeister': 'src/lib' },

		scripts 		= 	[ "src/notemeister" ],

		data_files 		= 	[
							( "share/pixmaps", [
								"pixmaps/notemeister.svg"
							 ] ),

							( 'share/notemeister/pixmaps', [
								'pixmaps/notemeister.svg',
								'pixmaps/tray_pencil.png',
								'pixmaps/calendar.svg',
								'pixmaps/clock.svg',
								'pixmaps/import.svg',
								'pixmaps/export.svg',
								'pixmaps/note.svg',
								'pixmaps/link.svg',
								'pixmaps/folder.svg',
								'pixmaps/folder_link.svg',
								'pixmaps/web.svg'
							] ),

							 (datadir,
								["ui/MeisterMainWindow.glade",
								 "ui/preferences.glade",
								 "ui/notemeisterui.xml"]),
							 ("doc/notemeister-" + version,
								["COPYING", "README", "NEWS", "AUTHORS"]),
							 ("share/applications", ["gnome/notemeister.desktop"])
							 ]
							 )


