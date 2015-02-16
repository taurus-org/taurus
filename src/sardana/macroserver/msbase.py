#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.sardana-controls.org/
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""This module is part of the Python MacroServer libray. It defines the base
classes for MacroServer object"""

__all__ = [",MSBaseObject", "MSObject", ]

__docformat__ = 'restructuredtext'

from sardana.sardanabase import SardanaBaseObject, SardanaObjectID


class MSBaseObject(SardanaBaseObject):
    """The MacroServer most abstract object."""

    def __init__(self, **kwargs):
        kwargs['manager'] = kwargs.pop('macro_server')
        SardanaBaseObject.__init__(self, **kwargs)

    def get_macro_server(self):
        """Return the :class:`sardana.macroserver.macroserver.MacroServer`
        which *owns* this macro server object.

        :return: the macro server which *owns* this macro server object.
        :rtype: :class:`sardana.macroserver.macroserver.MacroServer`"""
        return self.get_manager()

    def serialize(self, *args, **kwargs):
        kwargs = SardanaBaseObject.serialize(self, *args, **kwargs)
        kwargs['macro_server'] = self.macro_server.name
        return kwargs

    macro_server = property(get_macro_server,
        doc="reference to the :class:`sardana.macroserver.macroserver.MacroServer`")


class MSObject(SardanaObjectID, MSBaseObject):
    """A macro server object that besides the name and reference to the
       macro server base object has:

           - _id : the internal identifier"""

    def __init__(self, **kwargs):
        SardanaObjectID.__init__(self, id=kwargs.pop('id'))
        MSBaseObject.__init__(self, **kwargs)

    def serialize(self, *args, **kwargs):
        kwargs = MSBaseObject.serialize(self, *args, **kwargs)
        kwargs = SardanaObjectID.serialize(self, *args, **kwargs)
        return kwargs
