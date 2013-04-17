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
Tango extension for taurus core mode. 
The Tango extension implements :mod:`taurus.core` objects that connect to Tango
objects. The official scheme name is, obviously, 'tango'. As Tango is the default
taurus scheme, when specifing a tango model name, the scheme prefix ('tango://') can
be omited.

You should never create objects of tango classes directly. Instead you
should use the :class:`taurus.core.taurusmanager.TaurusManager` and :class:`taurus.core.taurusfactory.TaurusFactory` APIs
to access all elements.

For example, to get a reference to the Tango attribute my/tango/device/state you
should do something like::

    >>> import taurus
    >>> my_state = taurus.Attribute('tango://my/tango/device/state')
    
In fact, because the taurus default extension is Tango, you could omit the 'tango://'
prefix from the previous code::

    >>> import taurus
    >>> my_state = taurus.Attribute('my/tango/device/state')

The same is applied to a device::

    >>> import taurus
    >>> my_device = taurus.Device('my/tango/device')

...to a database::

    >>> import taurus
    >>> db = taurus.Database('homer:10000')

...and an attribute configuration::

    >>> import taurus
    >>> me_state_config = taurus.Attribute('my/tango/device/state?configuration')

The way to get access to the Tango factory is::

    >>> import taurus
    >>> factory = taurus.Factory()
"""

__docformat__ = "restructuredtext"

from enums import *
from tangodatabase import *
from tangodevice import *
from tangofactory import *
from tangoattribute import *
from tangoconfiguration import *
