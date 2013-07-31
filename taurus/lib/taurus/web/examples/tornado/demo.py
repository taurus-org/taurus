#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""
"""

__docformat__ = "restructuredtext"

import os.path

from taurus.web.taurustornado import RequestHandler
from taurus.web.taurustornado import start, get_default_handlers

class MainPageHandler(RequestHandler):
    def get(self):
        self.render("demo.html")

class DemoPageHandler(RequestHandler):
    
    def get(self, page):
        self.render(page)


def main():
    local_path = os.path.dirname(__file__)
    static_path = os.path.join(local_path, 'static')
    handlers = [ (r"/", MainPageHandler),  (r"/(demo.*)", DemoPageHandler)] + get_default_handlers() 
    
    start(handlers=handlers, port=8888, static_path=static_path, debug=True)

if __name__ == "__main__":
    main()
