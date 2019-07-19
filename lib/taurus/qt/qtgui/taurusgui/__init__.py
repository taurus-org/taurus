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
###########################################################################

"""
This package provides TaurusGui, a generic framework for creating GUIs without
actual coding (just configuration files).

See the examples provided in the conf subdirectory directory as well as the
documentation of the :class:`TaurusGui` class.


The "new GUI wizard" and XML configuration files
------------------------------------------------

Note that the configuration files can either be written by hand or by
launching the "new GUI" wizard with `taurus newgui`, which will create
a new directory containing configuration, resource and launcher files.

The new GUI wizard stores all the options in xml format in a file called
`config.xml` and creates a simple `config.py` file containing the following
line::

    XML_CONFIG = 'config.xml'

This line indicates that `config.xml` should also be used as a source of
configuration options (in case of conflict, the options set in `config.py`
prevail).

"""
from __future__ import absolute_import

from .paneldescriptionwizard import *
from .taurusgui import *
from .appsettingswizard import *
try:
    # this import is left here for bck-compat, but will be removed
    # TODO: remove this
    from sardana.taurus.qt.qtgui.macrolistener import (MacroBroker,
                                                       DynamicPlotManager)
except ImportError:
    pass


__docformat__ = 'restructuredtext'
