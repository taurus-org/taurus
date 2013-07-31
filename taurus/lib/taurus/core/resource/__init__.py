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
.. currentmodule:: taurus.core.resource

Resource extension for taurus core mode.
The resource extension is a special extension that acts like a name dictionary
for actual model names. The official scheme names are 'res' and 'resource'. You
can used both of them indiferently.

The resources module of taurus will read one or more resources (usualy files) 
which should contain a dictionary where the keys are resource alias and the values
are the actual model names.

The main class for the extension module is :class:`ResourcesFactory`.

By default, the :class:`ResourcesFactory` will use a resource 
file called 'taurus_resources.py'. It will search for this file in the application
directory.

You can add additional resources with the method :meth:`ResourcesFactory.loadResource`.

What is a resource
------------------

A resource can be a python file or a simple python dictionary<str,str>. Below there 
is an example of how register a python dictionary as a resource.

Python resource files
~~~~~~~~~~~~~~~~~~~~~

If a resource is a python file, the factory will recognize resource keys as global
variables. The resource value will be the variable value which must be a string.
For example, the contents of a python resource file could be something like::

    my_device = 'my/tango/device'
    my_state = my_device + '/state'

Afterward, in your code, you could access the Device and Attribute objects by doing::

    >>> import taurus
    >>> my_device_obj = taurus.Device('res://my_device')
    >>> my_state_obj = taurus.Attribute('res://my_state')

The advantage of this is that you can design an application that is independent 
on the real device names.

Note that nothing prevents you from placing any python code in the python resource file.
This means you can have a script that simplifies the contents of the file. Example::

    base = 'my/motor/'
    g = globals()
    
    for i in xrange(256):
        i_str = str(i)
        g['mym"+i_str] = base + i_str

Dictionary resources
~~~~~~~~~~~~~~~~~~~~

Instead of having a complete resource file you can also register a dictionary
as a resource::

    >>> d = { 'my_device' : 'my/tango/device', 'my_state' = 'my/tango/device/state' }
    >>> import taurus
    >>> factory = taurus.Factory('res')
    >>> factory.loadResource(d)
    >>> my_device_obj = taurus.Device('res://my_device')
    >>> my_state_obj = taurus.Attribute('res://my_state')
"""

from resfactory import *