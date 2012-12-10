#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
##
## This file is part of Sardana
## 
## http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""This package provides the spock's ipython configuration class"""

__all__ = ['Spock']

from IPython.config.configurable import Configurable
from IPython.utils.traitlets import Unicode, Bool

class Spock(Configurable):
    macro_server_name = Unicode(config=True)
    door_name = Unicode(config=True)
    macro_server_alias = Unicode(config=True)
    door_alias = Unicode(config=True)
    ready = Bool(default_value=False, config=True)