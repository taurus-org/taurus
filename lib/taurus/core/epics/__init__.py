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
.. currentmodule:: taurus.core.epics

Epics extension for taurus core model.

The epics extension provides access to Epics control system objects via Channel
Access

.. note:: The Epics scheme is only a proof of concept. The final syntax of
          the model names is not yet set in stone and only basic functionality
          is implemented.


The Epics extension implements :mod:`taurus.core` objects that connect to Epics
PVs. The scheme name for channel access epics models is 'ca' ('epics' also
works at this moment).

You should never instantiate models from epics model classes directly. Instead,
use the :class:`taurus.core.taurusmanager.TaurusManager` and
:class:`taurus.core.taurusmanager.TaurusFactory` APIs to access all elements.

For example, to get a reference to the epics process variable (PV)
"my:example.RBV" you should do something like::

    >>> import taurus
    >>> myattr = taurus.Attribute('ca:my:example.RBV')

Epics attributes (should) work just as other Taurus attributes and can be
referred by their model name wherever a Taurus Attribute model is expected. For
example, you can launch a `TaurusForm` with an epics attribute::

    $> taurus form ca:my:example

Similarly, you can combine epics attributes with attributes from other schemes::

    $> taurus form 'ca:my:example' 'tango:sys/tg_test/1/float_scalar'\
       'eval:{ca:my:example}*{tango:sys/tg_test/1/float_scalar}'

Currently, the taurus epics scheme just supports epics PVs, implementing them as
taurus attributes. Other model types such as the Authority, and Device classes
are just convenience dummy objects in the epics scheme at this point.
Epics records may eventually be mapped as Devices.
"""
from __future__ import absolute_import
from .epicsfactory import *
