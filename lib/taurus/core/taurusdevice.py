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

"""This module contains the base class for a taurus device"""

__all__ = ["TaurusDevice"]

__docformat__ = "restructuredtext"

from .taurusbasetypes import TaurusDevState, TaurusElementType
from .taurusmodel import TaurusModel


class TaurusDevice(TaurusModel):

    """A Device object. Different schemes may assign different roles, but
       in general it is a parent of Taurus Attribute objects and a child
       of a Taurus Authority"""

    _description = "A Taurus Device"

    def __init__(self, name='', **kw):
        """Object initialization."""
        parent = kw.pop('parent', None)
        storeCallback = kw.pop('storeCallback', None)
        self.__dict__.update(kw)
        self.call__init__(TaurusModel, name, parent)

        if storeCallback:
            storeCallback(self)

    def __contains__(self, key):
        """Reimplement in schemes if you want to support membership testing for
        attributes of the device
        """
        raise TypeError("'%s' does not support membership testing" %
                        self.__class__.__name__)

    @property
    def state(self):
        """Returns a scheme-agnostic representation of the state of a Taurus
        device. This default implementation always returns
        `TaurusDevState.Ready`

        Subclasses of TaurusDevice may reimplement it to return other
        :class:`taurus.core.TaurusDevState` enumeration values.

        :return: (TaurusDevState) `TaurusDevState.Ready`
        """
        return TaurusDevState.Ready

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusModel implementation
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @classmethod
    def getTaurusElementType(cls):
        return TaurusElementType.Device

    @classmethod
    def buildModelName(cls, parent_model, relative_name):
        """build an 'absolute' model name from the parent model and the 'relative'
        name.
        - If parent_model is a TaurusAuthority, the return is a composition of
        the authority model name and the device name
        - If parent_model is a TaurusDevice, the relative name is ignored and
        the parent name is returned

        Note: This is a basic implementation. You may need to reimplement this
              for a specific scheme if it supports "useParentModel".
        """
        if parent_model is None:
            return relative_name
        parent_name = parent_model.getFullName()
        if not parent_name:
            return relative_name
        if isinstance(parent_model, cls):
            return parent_name
        return '%s/%s' % (parent_name, relative_name)

    @classmethod
    def getNameValidator(cls):
        return cls.factory().getDeviceNameValidator()

    def getDisplayDescrObj(self, cache=True):
        obj = []
        obj.append((u'name', self.getDisplayName(cache=cache)))
        obj.append((u'description', self.description))
        obj.append((u'device state', self.state.name))
        return obj

    def getChildObj(self, child_name):
        if child_name is None or len(child_name) == 0:
            return None
        obj_name = "%s%s" % (self.getFullName(), child_name)
        return self.factory().findObject(obj_name)

    def poll(self, attrs, asynch=False, req_id=None):
        '''Polling certain attributes of the device. This default
        implementation simply polls each attribute one by one'''

        # asynchronous requests are not supported. If asked to do it,
        # just return an ID of 1 and in the reply (req_id != None) we do a
        # synchronous polling.
        if asynch is True:
            return 1
        for attr in attrs.values():
            attr.poll()

    @property
    def description(self):
        return self._description
