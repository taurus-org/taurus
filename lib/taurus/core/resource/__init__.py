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
.. currentmodule:: taurus.core.resource

Resource scheme extension for taurus core mode.
The resource extension is a special extension that acts like a name map
for actual model names.

This allows to indirect the hardcoded model names of your application and keep
the actual specific model names grouped in one place for better portability and
reusability of your application.

The scheme name is 'res'. The map can be implemented either as python
modules or as dicts (see below).

The main class for the extension module is :class:`ResourcesFactory` and
you can add resource maps with :meth:`ResourcesFactory.loadResource`.

By default, the :class:`ResourcesFactory` will always try to load a resource
module named 'taurus_resources' from the application directory (so
you can create a file called `taurus_resources.py` in your application directory
and skip the step of calling :meth:`ResourcesFactory.loadResource`.


Mapping implemented as python modules
-------------------------------------

If a resource is a python module, the factory will use its global variables as
the resource keys. The variable value, which must be a string will be used as
the mapped model. For example, if the `taurus_resources.py` file in
the application directory contains the following definitions::

    my_device = 'tango:a/b/c'
    my_state = my_device + '/state'

Then, in your code, you can access the Device and Attribute objects by doing::

    >>> import taurus
    >>> my_device_obj = taurus.Device('res:my_device')
    >>> my_state_obj = taurus.Attribute('res:my_state')

Note that you can use python code to automate the contents of the module.
Example::

    base = 'my/motor/'
    g = globals()

    for i in xrange(256):
        i_str = str(i)
        g['mym"+i_str] = base + i_str

Mapping implemented as dictionaries
-----------------------------------

Dictionaries can also be registered (as an alternative to modules) as resource
maps::

    >>> d = {'my_device':'tango:a/b/c', 'my_state':'tango:a/b/c/state'}
    >>> import taurus
    >>> factory = taurus.Factory('res')
    >>> factory.loadResource(d)
    >>> my_device_obj = taurus.Device('res:my_device')
    >>> my_state_obj = taurus.Attribute('res:my_state')

Note: for coherence with the file mapping, valid key names are restricted to
valid variable names (i.e. to the following regexp: `[a-zA-Z_][a-zA-Z0-9_]*`

Important: Models object type is the mapped type
-------------------------------------------------

The model objects returned by the :class:`ResourcesFactory` will be of the
mapped model type. In other words: if the model name 'eval:Q(rand())' is
mapped to the `myattr` resource name, calling `taurus.Attribute('res:myattr')`
will return a :class:`EvaluationAttribute`, not a `ResAttribute` (`ResAttribute`
is not even defined).

"""
from __future__ import absolute_import

from .resfactory import *
