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
###########################################################################

"""
This package provides TaurusGui, a generic framework for creating GUIs without
actual coding (just configuration files).

See the examples provided in the conf directory.

.. note:: 
    Please be aware that TaurusGui has only recently being developed and it
    is still under intense development. The syntax of the configuration files
    may change at some point and more features and bug fixes are likely to
    be added in the near future. 
"""

__docformat__ = 'restructuredtext'

import utils 
from paneldescriptionwizard import *
from taurusgui import *
from appsettingswizard import *
from macrolistener import *