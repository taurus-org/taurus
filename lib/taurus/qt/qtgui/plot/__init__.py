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

"""
Taurus Plot module (old)
========================

This module is now deprecated.

If available, it exposes the plot API now implemented in
`taurus.qt.qtgui.qwt5`. Otherwise it tries to provide a minimal API
(essentially the TaurusPlot and TaurusTrend classes from taurus_pyqtgraph)
to help with the transition to another plotting module such as
taurus.qt.qtgui.tpg.

Note that if you really want to continue using the old Qwt5-based widgets and
avoid deprecation warnings, you can import the old API from
taurus.qt.qtgui.qwt5

Note that `PyQwt5 module <http://pyqwt.sourceforge.net/>`_
only works with Python2 and PyQt4 and is no longer supported,
so taurus is moving to other modules for plotting (pyqtgraph, silx, ...)

"""

from __future__ import absolute_import
from taurus.core.util import log as __log

__log.deprecated(dep='taurus.qt.qtgui.plot', rel='4.5',
                 alt='taurus.qt.qtgui.tpg or taurus.qt.qtgui.qwt5')

try:
    # Import all from qwt5
    from taurus.qt.qtgui.qwt5 import *
    # ...and patch sys.modules to expose all qwt5 submodules here
    # (even those not in the public API). This fixes
    # https://github.com/taurus-org/taurus/issues/909)
    import sys
    d = {}
    for k, v in sys.modules.items():
        if 'taurus.qt.qtgui.qwt5.' in k:
            d[k.replace('taurus.qt.qtgui.qwt5.', 'taurus.qt.qtgui.plot.')] = v
    sys.modules.update(d)
except:
    try:
        from taurus.qt.qtgui.tpg import TaurusPlot, TaurusTrend
        __log.info('plot: Using taurus.qt.qtgui.tpg to provide a minimal API '
                   + 'to facilitate the transition')
    except:
        __log.info('plot: Cannot import taurus.qt.qtgui.tpg to provide a '
                   + 'minimal API for transition')



