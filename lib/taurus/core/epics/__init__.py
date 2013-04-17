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

"""
.. currentmodule:: taurus.core.epics

Epics extension for taurus core model.

The epics extension provides access to Epics control system objects 

.. note:: The Epics scheme is only a proof of concept. The final syntax of the models is
          not yet set in stone and only basic functionality is implemented.  


The Epics extension implements :mod:`taurus.core` objects that connect to Epics
objects. The scheme prefix for epics objects is 'epics://'.

You should never create objects of epics classes directly. Instead you
should use the :class:`taurus.core.taurusmanager.TaurusManager` and 
:class:`taurus.core.taurusmanager.TaurusFactory` APIs to access all elements.

For example, to get a reference to the epics process variable (PV) "my:example.RBV" you
should do something like::

    >>> import taurus
    >>> myattr = taurus.Attribute('epics://my:example.RBV')

Epics attributes (should) work just as other Taurus attributes and can be
referred by their model name wherever a Taurus Attribute model is expected. For
example, you can launch a `TaurusForm` with an epics attribute::

    $> taurusform epics://my:example.RBV

Similarly, you can combine epics attributes with attributes from other schemes::

    $> taurusform 'epics://my:example.RBV' 'tango://sys/tg_test/1/float_scalar'\ 
       'eval://{epics://my:example.RBV}*{tango://sys/tg_test/1/float_scalar}'

Currently, the taurus epics scheme just supports epics PVs, implementing them as
taurus attributes (with configuration objects as well). Other taurus classes
such as the Database, and Device classes are just convenience dummy objects in
the epics scheme at this point. Epics records may eventually be mapped as
Devices.

"""

from epicsfactory import *
