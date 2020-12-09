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
Tango extension for taurus core mode.
The Tango extension implements :mod:`taurus.core` objects that connect to Tango
objects. The official scheme name is, obviously, 'tango'.

This extension maps the (Py)Tango objects into Taurus objects as follows:

- A Tango database is represented as a subclass of
  :class:`taurus.core.TaurusAuthority`
- A Tango device is represented as a subclass of
  :class:`taurus.core.TaurusDevice`
- A Tango device attribute is represented as a subclass
  :class:`taurus.core.TaurusAttribute`

You should never create objects from the above classes directly. Instead, you
should use :meth:`taurus.Authority`, :meth:`taurus.Device`,
and :meth:`taurus.Attribute` helper functions,
as in the examples below, or if you require more control, use the
:class:`taurus.core.taurusmanager.TaurusManager` or
:class:`taurus.core.taurusfactory.TaurusFactory` APIs.

Here are some examples:

The Taurus Authority associated with the Tango database
running on host "machine01" and port 10000 is named "//machine:10000"
(note that Taurus authority names are always prefixed by "//", to comply with
RFC3986). And you can get the corresponding Taurus Authority object as:

    >>> import taurus
    >>> my_db = taurus.Authority('tango://machine:10000')

If "tango" is configured as the default scheme for Taurus, the 'tango:' prefix
could be avoided and same database could be accessed as::

    >>> my_db = taurus.Authority('//machine:10000')

Now, assume that a TangoTest device is registered  in the above database as
``sys/tg_test/1``. In this case, the corresponding Taurus device full name
would be ``tango://machine:10000/sys/tg_test/1`` and it could be accessed as::

    >>> import taurus
    >>> my_device = taurus.Device('tango://machine:10000/sys/tg_test/1')

If "tango" is configured as the default scheme for Taurus, the previous name
could be shortened to ``//machine:10000/sys/tg_test/1`` or even to
``sys/tg_test/1`` if the TANGO_HOST environment variable
(or tango.rc file) point to `machine:10000` as the default tango database.
Furthermore, if, on top of that,  this device is aliased as ``tgtest1`` in the
database, it could be accessed as::

    >>> import taurus
    >>> my_device = taurus.Device('tgtest1')

Similarly, accessing the ``ampli`` attribute from the above Tango device can be
done using its full name::

    >>> import taurus
    >>> my_attr = taurus.Attribute('tango://machine:10000/sys/tg_test/1/ampli')

And of course shorter names can also be used for attributes. Following the
examples for the device above, the following names could also have been passed
to :meth:`taurus.Attribute`:

- ``//machine:10000/sys/tg_test/1/ampli``
- ``sys/tg_test/1/ampli``
- ``tgtest1/ampli``

Finally, the TangoFactory object can be accessed as::

    >>> import taurus
    >>> tg_factory = taurus.Factory('tango')


.. note:: Previous to TEP3, a RFC3986 non-compliant syntax was used for the
          Tango scheme (e.g., allowing names such as ``tango://a/b/c/d`` -note
          the double slash which should not be there).
          This syntax is now deprecated and should not be used. Taurus will
          issue warnings if detected.
"""

from __future__ import absolute_import

from .enums import *
from .tangodatabase import *
from .tangodevice import *
from .tangofactory import *
from .tangoattribute import *
from .tangoconfiguration import *


__docformat__ = "restructuredtext"
