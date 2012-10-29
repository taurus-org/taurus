#!/usr/bin/env python

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

"""This module contains a definition for ViewOptions"""

from __future__ import with_statement
from __future__ import print_function

__all__ = ['ViewOption']


def ViewOptionMeta(name, bases, attrs):
    for k in attrs['_DEFAULT_VIEW_OPTIONS']:
        attrs[k] = k
    return type(name, bases, attrs)

class ViewOption(object):
    __metaclass__ = ViewOptionMeta

    _DEFAULT_VIEW_OPTIONS = {
        'ShowDial' : True,
    }    
    
    @classmethod
    def init_options(cls, d):
        d.update(cls._DEFAULT_VIEW_OPTIONS)
        return d

    @classmethod
    def reset_option(cls, d, name):
        if name in cls._DEFAULT_VIEW_OPTIONS:
            d[name] = cls._DEFAULT_VIEW_OPTIONS[name]
        else:
            del d[name]
    
    
