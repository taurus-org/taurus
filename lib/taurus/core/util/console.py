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

"""This module contains ANSI color codes"""

__all__ = ["make_color_table", "NoColors", "TermColors", "HTMLColors",
           "NoTangoColors", "TermTangoColors", "HTMLTangoColors", 
           "NoTaurusSWDevStateColors", "TermTaurusSWDevStateColors",
           "NoTauSWDevStateColors", "TermTauSWDevStateColors",
           "ANSIEscapeCodeHandler"]

__docformat__ = "restructuredtext"

import os

__color_templates = (
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

def make_color_table(in_class,use_name=False,fake=False):
    """Build a set of color attributes in a class.

    Helper function for building the *TermColors classes."""
    global __color_templates
    if fake:
        for name, value in __color_templates:
            setattr(in_class, name, "")
    else:
        if use_name:
            for name,value in __color_templates:
                setattr(in_class,name,in_class._base % name)
        else:
            for name,value in __color_templates:
                setattr(in_class,name,in_class._base % value)

class NoColors:
    NoColor = ''  # for color schemes in color-less terminals.
    Normal = ''   # Reset normal coloring
    _base  = ''  # Template for all other colors
    
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
make_color_table(NoColors,fake=True)
make_color_table(TermColors)
make_color_table(HTMLColors,True)

import PyTango

NoTangoColors = { PyTango.DevState.ON      : NoColors.Green,
                    PyTango.DevState.ALARM   : NoColors.Brown,
                    PyTango.DevState.FAULT   : NoColors.Red,
                    PyTango.DevState.UNKNOWN : NoColors.LightGray,
                    None                     : NoColors.DarkGray }

TermTangoColors = { PyTango.DevState.ON      : TermColors.Green,
                    PyTango.DevState.ALARM   : TermColors.Brown,
                    PyTango.DevState.FAULT   : TermColors.Red,
                    PyTango.DevState.UNKNOWN : TermColors.LightGray,
                    None                     : TermColors.DarkGray }

HTMLTangoColors = { PyTango.DevState.ON      : HTMLColors.Green,
                    PyTango.DevState.ALARM   : HTMLColors.Brown,
                    PyTango.DevState.FAULT   : HTMLColors.Red,
                    PyTango.DevState.UNKNOWN : HTMLColors.LightGray,
                    None                     : HTMLColors.DarkGray }
                    
from taurus.core.taurusbasetypes import TaurusSWDevState

NoTaurusSWDevStateColors = {
    TaurusSWDevState.Uninitialized       : NoColors.LightGray,
    TaurusSWDevState.Running             : NoColors.Green, 
    TaurusSWDevState.Shutdown            : NoColors.DarkGray, 
    TaurusSWDevState.Crash               : NoColors.Red,
    TaurusSWDevState.EventSystemShutdown : NoColors.Brown }

TermTaurusSWDevStateColors = {
    TaurusSWDevState.Uninitialized       : TermColors.LightGray,
    TaurusSWDevState.Running             : TermColors.Green, 
    TaurusSWDevState.Shutdown            : TermColors.DarkGray, 
    TaurusSWDevState.Crash               : TermColors.Red,
    TaurusSWDevState.EventSystemShutdown : TermColors.Brown }

NoTauSWDevStateColors = NoTaurusSWDevStateColors
TermTauSWDevStateColors = TermTaurusSWDevStateColors

class ANSIEscapeCodeHandler(object):
    """ANSI Escape sequences handler"""
    if os.name == 'nt':
        # Windows terminal colors:
        ANSI_COLORS = ( # Normal, Bright/Light
                       ('#000000', '#808080'), # 0: black
                       ('#800000', '#ff0000'), # 1: red
                       ('#008000', '#00ff00'), # 2: green
                       ('#808000', '#ffff00'), # 3: yellow
                       ('#000080', '#0000ff'), # 4: blue
                       ('#800080', '#ff00ff'), # 5: magenta
                       ('#008080', '#00ffff'), # 6: cyan
                       ('#c0c0c0', '#ffffff'), # 7: white
                       )
    elif os.name == 'mac':
        # Terminal.app colors:
        ANSI_COLORS = ( # Normal, Bright/Light
                       ('#000000', '#818383'), # 0: black
                       ('#C23621', '#FC391F'), # 1: red
                       ('#25BC24', '#25BC24'), # 2: green
                       ('#ADAD27', '#EAEC23'), # 3: yellow
                       ('#492EE1', '#5833FF'), # 4: blue
                       ('#D338D3', '#F935F8'), # 5: magenta
                       ('#33BBC8', '#14F0F0'), # 6: cyan
                       ('#CBCCCD', '#E9EBEB'), # 7: white
                       )
    else:
        # xterm colors:
        ANSI_COLORS = ( # Normal, Bright/Light
                       ('#000000', '#7F7F7F'), # 0: black
                       ('#CD0000', '#ff0000'), # 1: red
                       ('#00CD00', '#00ff00'), # 2: green
                       ('#CDCD00', '#ffff00'), # 3: yellow
                       ('#0000EE', '#5C5CFF'), # 4: blue
                       ('#CD00CD', '#ff00ff'), # 5: magenta
                       ('#00CDCD', '#00ffff'), # 6: cyan
                       ('#E5E5E5', '#ffffff'), # 7: white
                       )
    def __init__(self):
        self.intensity = 0
        self.italic = None
        self.bold = None
        self.underline = None
        self.foreground_color = None
        self.background_color = None
        self.default_foreground_color = 30
        self.default_background_color = 47
        
    def set_code(self, code):
        assert isinstance(code, int)
        if code == 0:
            # Reset all settings
            self.reset()
        elif code == 1:
            # Text color intensity
            self.intensity = 1
            # The following line is commented because most terminals won't 
            # change the font weight, against ANSI standard recommendation:
#            self.bold = True
        elif code == 3:
            # Italic on
            self.italic = True
        elif code == 4:
            # Underline simple
            self.underline = True
        elif code == 22:
            # Normal text color intensity
            self.intensity = 0
            self.bold = False
        elif code == 23:
            # No italic
            self.italic = False
        elif code == 24:
            # No underline
            self.underline = False
        elif code >= 30 and code <= 37:
            # Text color
            self.foreground_color = code
        elif code == 39:
            # Default text color
            self.foreground_color = self.default_foreground_color
        elif code >= 40 and code <= 47:
            # Background color
            self.background_color = code
        elif code == 49:
            # Default background color
            self.background_color = self.default_background_color
        self.set_style()
        
    def reset(self):
        self.current_format = None
        self.intensity = 0
        self.italic = False
        self.bold = False
        self.underline = False
        self.foreground_color = None
        self.background_color = None