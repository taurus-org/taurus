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

"""This package provides the sardana library"""

__all__ = ['make_color_table', 'TermColors', 'HTMLColors', 'TermTangoColors',
           'TermTauSWDevStateColors', 'HTMLTangoColors']

__docformat__ = 'restructuredtext'

def make_color_table(in_class,use_name=False):
    """Build a set of color attributes in a class.

    Helper function for building the *TermColors classes."""
    
    color_templates = (
        ("Black"       , "0;30"),
        ("Red"         , "0;31"),
        ("Green"       , "0;32"),
        ("Brown"       , "0;33"),
        ("Blue"        , "0;34"),
        ("Purple"      , "0;35"),
        ("Cyan"        , "0;36"),
        ("LightGray"   , "0;37"),
        ("DarkGray"    , "1;30"),
        ("LightRed"    , "1;31"),
        ("LightGreen"  , "1;32"),
        ("Yellow"      , "1;33"),
        ("LightBlue"   , "1;34"),
        ("LightPurple" , "1;35"),
        ("LightCyan"   , "1;36"),
        ("White"       , "1;37"),  )

    for name,value in color_templates:
        if use_name:
            setattr(in_class,name,in_class._base % name)
        else:
            setattr(in_class,name,in_class._base % value)

class TermColors:
    """Color escape sequences.

    This class defines the escape sequences for all the standard (ANSI?) 
    colors in terminals. Also defines a NoColor escape which is just the null
    string, suitable for defining 'dummy' color schemes in terminals which get
    confused by color escapes.

    This class should be used as a mixin for building color schemes.
    
    Basicaly this class is just a copy of IPython.ColorANSI.TermColors class"""
    
    NoColor = ''  # for color schemes in color-less terminals.
    Normal = '\033[0m'   # Reset normal coloring
    _base  = '\033[%sm'  # Template for all other colors

class HTMLColors:
    
    NoColor = ''
    Normal = '</font>'
    _base = '<font color=%s>'

# Build the actual color table as a set of class attributes:
make_color_table(TermColors)
make_color_table(HTMLColors,True)

import PyTango

TermTangoColors = { PyTango.DevState.ON      : TermColors.Green,
                    PyTango.DevState.ALARM   : TermColors.Brown,
                    PyTango.DevState.FAULT   : TermColors.Red,
                    PyTango.DevState.UNKNOWN : TermColors.LightGray,
                    None                     : TermColors.DarkGray }

from taurus.core import TaurusSWDevState

TermTauSWDevStateColors = {
    TaurusSWDevState.Uninitialized       : TermColors.LightGray,
    TaurusSWDevState.Running             : TermColors.Green, 
    TaurusSWDevState.Shutdown            : TermColors.DarkGray, 
    TaurusSWDevState.Crash               : TermColors.Red,
    TaurusSWDevState.EventSystemShutdown : TermColors.Brown }
    
HTMLTangoColors = { PyTango.DevState.ON      : HTMLColors.Green,
                    PyTango.DevState.ALARM   : HTMLColors.Brown,
                    PyTango.DevState.FAULT   : HTMLColors.Red,
                    PyTango.DevState.UNKNOWN : HTMLColors.LightGray,
                    None                     : HTMLColors.DarkGray }