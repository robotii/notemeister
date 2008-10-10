#!/usr/bin/env python

import gtk

class timedStatusbar(gtk.Statusbar):
    _o = None
    def __init__(self):
        gtk.Statusbar.__init__(self)
        self._initialize()
        
    def _initialize(self):
        self.last_tag = None

    def output(self, msg, timeout):
        self.del_timer()
        self.pop(1)
        self.push(1,msg)
        self.set_timer(timeout)

    def del_timer(self):
        if self.last_tag:
            gtk.timeout_remove(self.last_tag)
    
    def set_timer(self, timeout):
        if timeout > 0:
            self.last_tag = gtk.timeout_add(timeout,self.clear)

    def clear(self):
        self.pop(1)
        self.push(1,"")
        return gtk.FALSE

