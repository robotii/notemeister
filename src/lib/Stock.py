# Copyright (c) 2004 Dennis Craven
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

import gtk, gtk.gdk, notemeister

STOCK_APPLICATION 				= "notemeister-application"
STOCK_IMPORT 					= "notemeister-import"
STOCK_EXPORT 					= "notemeister-export"
STOCK_DATE 						= "notemeister-date"
STOCK_TIME 						= "notemeister-time"
STOCK_LINK 						= "notemeister-link"
STOCK_NOTE 						= "notemeister-note"
STOCK_FOLDER 					= "notemeister-folder"
STOCK_FOLDER_LINK 				= "notemeister-folder-link"
STOCK_WEB 		 				= "notemeister-web"

ICON_SIZE_POPUP 				= gtk.icon_size_register("notemeister-popup", 16, 16)

class IconFactory(gtk.IconFactory):

	def __init__(self, widget):
		gtk.IconFactory.__init__(self)
		self.add_default()

		icons = {
			STOCK_APPLICATION		: "notemeister.svg",
			STOCK_IMPORT 			: "import.svg",
			STOCK_EXPORT 			: "export.svg",
			STOCK_DATE 				: "calendar.svg",
			STOCK_TIME 				: "clock.svg",
			STOCK_LINK 				: "link.svg",
			STOCK_NOTE 				: "note.svg",
			STOCK_FOLDER 			: "folder.svg",
			STOCK_FOLDER_LINK		: "folder_link.svg",
			STOCK_WEB				: "web.svg"
		}

		for id, filename in icons.items():
			iconset = gtk.IconSet(gtk.gdk.pixbuf_new_from_file(notemeister.const.pixmapDir + '/' + filename))
			self.add(id, iconset)

