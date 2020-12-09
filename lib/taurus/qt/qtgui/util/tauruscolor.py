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

"""This module provides Qt color management for taurus"""

__all__ = ["QtColorPalette",
           "QT_DEVICE_STATE_PALETTE",
           "QT_ATTRIBUTE_QUALITY_PALETTE",
           ]

__docformat__ = 'restructuredtext'

from taurus.external.qt import Qt

from taurus.core.util.colors import ColorPalette, \
    DEVICE_STATE_DATA, ATTRIBUTE_QUALITY_DATA
from taurus.core.taurusbasetypes import AttrQuality
from taurus.core.util.log import deprecation_decorator


class QtColorPalette(ColorPalette):

    def __init__(self, dat, int_decoder_dict):
        ColorPalette.__init__(self, dat, int_decoder_dict)
        self._qcolor_cache_fg = dict()
        self._qcolor_cache_bg = dict()
        self._qbrush_cache_fg = dict()
        self._qbrush_cache_bg = dict()

    def qbrush(self, stoq):
        # print stoq
        """Returns the brush for the specified state or quality"""
        name = self._decoder(stoq)

        f = self._qbrush_cache_fg
        b = self._qbrush_cache_bg
        if name not in f:
            f[name] = Qt.QBrush(self.qcolor(stoq)[1])

        if name not in b:
            b[name] = Qt.QBrush(self.qcolor(stoq)[0])
            if name == 'None':
                b[name].setStyle(Qt.Qt.BDiagPattern)

        return (b[name], f[name])

    def qcolor(self, stoq):
        """Returns the color for the specified state or quality"""
        name = self._decoder(stoq)

        f = self._qcolor_cache_fg
        b = self._qcolor_cache_bg
        if name not in f:
            f[name] = Qt.QColor(self.number(name, True))

        if name not in b:
            b[name] = Qt.QColor(self.number(name))

        return (b[name], f[name])

    @deprecation_decorator(alt='QtColorPalette.qcolor()', rel='4.5')
    def qvariant(self, stoq):
        """Returns the color for the specified state or quality"""
        return self.qcolor(stoq)



QT_ATTRIBUTE_QUALITY_PALETTE = QtColorPalette(ATTRIBUTE_QUALITY_DATA,
                                              AttrQuality)

try:
    # TODO: Tango-centric
    from taurus.core.tango import DevState
    QT_DEVICE_STATE_PALETTE = QtColorPalette(DEVICE_STATE_DATA, DevState)
except ImportError:
    QT_DEVICE_STATE_PALETTE = QtColorPalette(DEVICE_STATE_DATA, {})
