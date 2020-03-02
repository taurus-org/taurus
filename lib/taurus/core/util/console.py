#!/usr/bin/env python

#############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""This module contains ANSI color codes"""

from builtins import object

__all__ = ["make_color_table", "NoColors", "TermColors", "HTMLColors"]

__docformat__ = "restructuredtext"


def make_color_table(in_class, use_name=False, fake=False):
    """Build a set of color attributes in a class.
    Helper function for building the TermColors classes."""
    color_templates = (
        ("Black", "0;30"),
        ("Red", "0;31"),
        ("Green", "0;32"),
        ("Brown", "0;33"),
        ("Blue", "0;34"),
        ("Purple", "0;35"),
        ("Cyan", "0;36"),
        ("LightGray", "0;37"),
        ("DarkGray", "1;30"),
        ("LightRed", "1;31"),
        ("LightGreen", "1;32"),
        ("Yellow", "1;33"),
        ("LightBlue", "1;34"),
        ("LightPurple", "1;35"),
        ("LightCyan", "1;36"),
        ("White", "1;37"),)
    if fake:
        for name, value in color_templates:
            setattr(in_class, name, "")
    else:
        if use_name:
            for name, value in color_templates:
                setattr(in_class, name, in_class._base % name)
        else:
            for name, value in color_templates:
                setattr(in_class, name, in_class._base % value)


class NoColors(object):
    NoColor = ''  # for color schemes in color-less terminals.
    Normal = ''   # Reset normal coloring
    _base = ''  # Template for all other colors


class TermColors(object):
    """Color escape sequences.

    This class defines the escape sequences for all the standard (ANSI?)
    colors in terminals. Also defines a NoColor escape which is just the null
    string, suitable for defining 'dummy' color schemes in terminals which get
    confused by color escapes.

    This class should be used as a mixin for building color schemes.

    Basicaly this class is just a copy of IPython.ColorANSI.TermColors class"""

    NoColor = ''  # for color schemes in color-less terminals.
    Normal = '\033[0m'   # Reset normal coloring
    _base = '\033[%sm'  # Template for all other colors


class HTMLColors(object):

    NoColor = ''
    Normal = '</font>'
    _base = '<font color=%s>'

# Build the actual color table as a set of class attributes:
make_color_table(NoColors, fake=True)
make_color_table(TermColors)
make_color_table(HTMLColors, True)
