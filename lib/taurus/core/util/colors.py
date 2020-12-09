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

"""This module contains color codes for state and quality"""
from __future__ import print_function
from builtins import object

__all__ = ["DEVICE_STATE_DATA", "ATTRIBUTE_QUALITY_DATA", "ColorPalette",
           "DEVICE_STATE_PALETTE", "ATTRIBUTE_QUALITY_PALETTE"]


DEVICE_STATE_DATA = {
    # map for TaurusDevState states (used for agnostic TaurusDevice.state)
    "TaurusDevState.Ready": ("Green", 0, 255, 0, 0),
    "TaurusDevState.NotReady": ("Red", 255, 0, 0, 0),
    "TaurusDevState.Undefined": ("Gray", 128, 128, 128, 0),

    # The following is a bck-compat map for taurus.core.tango.DevState
    # (i.e. PyTango.DevState). Used for "state" TangoAttribute rvalues
    "ON": ("Dead Frog Green", 0, 255, 0, 0),
    "OFF": ('White', 255, 255, 255, 0),
    "CLOSE": ("White", 255, 255, 255, 3),
    "OPEN": ("Green", 0, 255, 0, 0),
    "INSERT": ("White", 255, 255, 255, 0),
    "EXTRACT": ("Green", 0, 255, 0, 0),
    "MOVING": ("Light Blue", 128, 160, 255, 0),
    "STANDBY": ("Yellow", 255, 255, 0, 0),
    "FAULT": ("Red", 255, 0, 0, 0),
    "INIT": ("Grenoble", 204, 204, 122, 0),
    "RUNNING": ("Light Blue", 128, 160, 255, 0),
    "ALARM": ("Tangorange", 255, 140,   0, 1),
    "DISABLE": ("Magenta", 255,   0, 255, 0),
    "UNKNOWN": ("Gray", 128, 128, 128, 0),
    str(None): ("Gray", 128, 128, 128, 0),
    # Support also explicit keys from str representations of
    # taurus.core.tango.util.enums.DevState
    "DevState.ON": ("Dead Frog Green", 0, 255, 0, 0),
    "DevState.OFF": ('White', 255, 255, 255, 0),
    "DevState.CLOSE": ("White", 255, 255, 255, 3),
    "DevState.OPEN": ("Green", 0, 255, 0, 0),
    "DevState.INSERT": ("White", 255, 255, 255, 0),
    "DevState.EXTRACT": ("Green", 0, 255, 0, 0),
    "DevState.MOVING": ("Light Blue", 128, 160, 255, 0),
    "DevState.STANDBY": ("Yellow", 255, 255, 0, 0),
    "DevState.FAULT": ("Red", 255, 0, 0, 0),
    "DevState.INIT": ("Grenoble", 204, 204, 122, 0),
    "DevState.RUNNING": ("Light Blue", 128, 160, 255, 0),
    "DevState.ALARM": ("Tangorange", 255, 140,   0, 1),
    "DevState.DISABLE": ("Magenta", 255,   0, 255, 0),
    "DevState.UNKNOWN": ("Gray", 128, 128, 128, 0),
}

ATTRIBUTE_QUALITY_DATA = {
    "ATTR_INVALID": ("Gray", 128, 128, 128, 1),
    "ATTR_VALID": ("Frog Green", 0, 255, 0, 0),
    "ATTR_ALARM": ("Orange", 255, 140, 0, 1),
    "ATTR_WARNING": ("Orange", 255, 140, 0, 1),
    "ATTR_CHANGING": ("Lightblue", 128, 160, 255, 0),
    "UNKNOWN": ("Gray", 128, 128, 128, 0),
    str(None): ("Gray", 128, 128, 128, 0),
}

_BW_RGB = [(0, 0, 0, "Black"), (255, 255, 255, "White"),
           (255, 255, 0, "Yellow"), (0, 128, 0, "Green")]


class ColorPalette(object):
    """Provides the list of taurus colors equivalent to Tango colors."""

    def __init__(self, dat, int_decoder_dict=None):

        self._rgb_data = dat
        self._int_decoder_dict = int_decoder_dict

    def _decoder(self, elem):
        if type(elem) == int:
            elem = self._int_decoder_dict.get(elem)
        return str(elem)

    def rgb(self, stoq, fg=False):
        """Returns a triplet of rgb colors in the range of 0 .. 255."""
        name = self._decoder(stoq)
        dat = self._rgb_data[name]
        if fg:
            return _BW_RGB[dat[4]][0:3]
        else:
            return dat[1:4]

    def rgb_pair(self, stoq):
        """Returns pair of foreground and background colors."""
        return (self.rgb(stoq), self.rgb(stoq, fg=True))

    def hex(self, stoq, fmt="%06x", fg=False):
        """Returns the rgb colors as string of lowercase hexadecimal characters"""
        return fmt % self.number(stoq, fg)

    def number(self, stoq, fg=False):
        """Returns the colors as a number,
        suitable for conversion to hexadecimal as argument to QtGui.QColor."""
        r = self.rgb(stoq, fg)
        return r[0] * 256 * 256 + r[1] * 256 + r[2]

    def __iter__(self):
        return list(self._rgb_data.keys()).__iter__()

    def name(self, stoq, fg=False):
        """Returns the name of the color."""
        name = self._decoder(stoq)
        if fg:
            return _BW_RGB[self._rgb_data[name][4]][3]
        else:
            return self._rgb_data[name][0]

    def has(self, name):
        return name in self._rgb_data

    def size(self):
        return len(self._rgb_data)

    def format_SimStates(self, var="T1"):
        count = DEVICE_STATE_PALETTE.size() - 1
        txt = ""
        for state in DEVICE_STATE_PALETTE:
            txt += "%s=Attr('%s')>%d\n" % (state, var, count)
            count = count - 1
        return txt

    def htmlStyle(self, htmlTag, stoq):
        name = self._decoder(stoq)
        bg = str(self.rgb(stoq))
        fg = str(self.rgb(stoq, fg=True))
        txt = """<style type='text/css'>
%s.%s { background-color : rgb%s;  color : rgb%s; }
</style>""" % (htmlTag, name, bg, fg)
        return txt

    def qtStyleSheet(self, stoq):
        name = self._decoder(stoq)
        bg = str(self.rgb(stoq))
        fg = str(self.rgb(stoq, fg=True))
        txt = "background-color : rgb%s;  color : rgb%s; " % (bg, fg)
        return txt


class _DeprecationDecoder(list):
    def __init__(self, palette, elements):
        self.palette = palette
        list.__init__(self, elements)

    def get(self, i):
        from taurus.core.util.log import deprecated
        deprecated(dep='Using ints for accessing elements of %s' % self.palette,
                   alt='"%s"' % self[i], rel='4.0')
        return self[i]


_PYTANGO_DEVSTATE_INT_DECODER = _DeprecationDecoder(
        'DEVICE_STATE_PALETTE',
        ["ON",
         "OFF",
         "CLOSE",
         "OPEN",
         "INSERT",
         "EXTRACT",
         "MOVING",
         "STANDBY",
         "FAULT",
         "INIT",
         "RUNNING",
         "ALARM",
         "DISABLE",
         "UNKNOWN",])

_PYTANGO_ATTRQUALITY_INT_DECODER = _DeprecationDecoder(
        'ATTRIBUTE_QUALITY_PALETTE',
        ["ATTR_VALID",
         "ATTR_INVALID",
         "ATTR_ALARM",
         "ATTR_CHANGING",
         "ATTR_WARNING",])


DEVICE_STATE_PALETTE = ColorPalette(DEVICE_STATE_DATA,
                                    _PYTANGO_DEVSTATE_INT_DECODER)

ATTRIBUTE_QUALITY_PALETTE = ColorPalette(ATTRIBUTE_QUALITY_DATA,
                                         _PYTANGO_ATTRQUALITY_INT_DECODER)


def print_color_palette(pal):
    """Prints a list of colors to stdout."""
    for stoq in pal:
        fg_color = pal.name(stoq, fg=True)
        bg_color = pal.name(stoq)
        rgb = "(%3.3d, %3.3d, %3.3d)" % pal.rgb(stoq)
        hx = pal.hex(stoq)
        print("%7s %5s on %13s %15s #%s" % (stoq, fg_color, bg_color, rgb, hx))


if __name__ == "__main__":
    print_color_palette(DEVICE_STATE_PALETTE)
    print_color_palette(ATTRIBUTE_QUALITY_PALETTE)
    from taurus.core import TaurusDevState
    import PyTango
    print()
    print(DEVICE_STATE_PALETTE.rgb(TaurusDevState.Ready))
    print(DEVICE_STATE_PALETTE.rgb('TaurusDevState.Ready'))
    print(DEVICE_STATE_PALETTE.rgb(PyTango.DevState.ON))
    print(DEVICE_STATE_PALETTE.rgb(0))
