# -*- coding: utf-8 -*-

##############################################################################
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
##############################################################################

from __future__ import absolute_import

try:
    from pint import *
except ImportError:
    # pint from local import
    import os
    import sys
    import warnings
    warnings.warn("pint not available. Using local pint", ImportWarning)
    sys.path.append(os.path.dirname(__file__))
    from pint import *
    del warnings
    del sys
    del os

UR = UnitRegistry()
UR.default_format = '~P'
Quantity = UR.Quantity
