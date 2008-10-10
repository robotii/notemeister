#!/usr/bin/env python

import os, sys

from gettext import gettext as _

if os.environ.has_key('NOTEMEISTER_TEST'):
	gladeDir = '../ui'
	pixmapDir = '../pixmaps'
else:
	PREFIX = sys.prefix
	gladeDir = PREFIX + '/share/notemeister'
	pixmapDir = PREFIX + '/share/notemeister/pixmaps'

uiFile 		= '%s/notemeisterui.xml' % gladeDir
gladeFile 	= '%s/MeisterMainWindow.glade' % gladeDir
#gladeFile 	= '%s/MeisterMainWindowTest.glade' % gladeDir
gladePrefs 	= '%s/preferences.glade' % gladeDir

dataPath 	= '%s/.notemeister/' % os.environ['HOME']
dataFile 	= '%snotemeister' % dataPath
dataFileXML = '%snotemeister.xml' % dataPath

#--------------------------------------------------------------------
#
# About box info
#
#--------------------------------------------------------------------
progName 	= 'Notemeister'
version 	= '0.1.7'
copyright 	= _('Copyright 2004 Dennis Craven')
comments 	= _('''A simple note and thought organizer for the
GNOME2 desktop environment.
''')
authors 	= ['Dennis Craven <arker66@users.sourceforge.net>']
documenters 	= ['']
translators 	= ''
#aboutPic 	= '%s/about_notemeister.png' % pixmapDir
aboutPic 	= '%s/notemeister.svg' % pixmapDir

#trayPic 	= '%s/notemeister.png' % pixmapDir
trayPic 	= '%s/tray_pencil.png' % pixmapDir
#trayPic 	= '%s/notemeister.svg' % pixmapDir

# Various custom icons
calendarPic = '%s/calendar.png' % pixmapDir
clockPic = '%s/clock.png' % pixmapDir
importPic = '%s/import.png' % pixmapDir
exportPic = '%s/export.png' % pixmapDir

