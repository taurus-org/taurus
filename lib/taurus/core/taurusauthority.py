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

"""This module contains the base class for a taurus database"""

from __future__ import absolute_import

from .taurusbasetypes import TaurusElementType
from .taurusmodel import TaurusModel

__all__ = ["TaurusAuthority"]

__docformat__ = "restructuredtext"


class TaurusAuthority(TaurusModel):

    _description = "A Taurus Authority"

    def __init__(self, complete_name='', parent=None):
        self.call__init__(TaurusModel, complete_name, parent)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusModel implementation
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    def cleanUp(self):
        self.trace("[TaurusAuthority] cleanUp")
        TaurusModel.cleanUp(self)

    @classmethod
    def getTaurusElementType(cls):
        return TaurusElementType.Authority

    @classmethod
    def buildModelName(cls, parent_model, relative_name):
        """build an 'absolute' model name from the parent name and the
        'relative' name. parent_model is ignored since there is nothing above
        the Authority object

        Note: This is a basic implementation. You may need to reimplement this
              for a specific scheme if it supports "useParentModel".
        """
        return relative_name

    @classmethod
    def getNameValidator(cls):
        return cls.factory().getAuthorityNameValidator()

    def getDisplayDescription(self, cache=True):
        return self.getFullName()

    def getDisplayDescrObj(self, cache=True):
        obj = []
        obj.append((u'name', self.getDisplayName(cache=cache)))
        obj.append((u'description', self.description))
        return obj

    def getChildObj(self, child_name):
        if not child_name:
            return None
        return self.getDevice(child_name)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Device access method
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getDevice(self, devname):
        """Returns the device object given its name"""
        from . import taurusdevice
        return self.factory().getObject(taurusdevice.TaurusDevice, devname)

    @property
    def description(self):
        return self._description

# For backwards compatibility, we make an alias for TaurusAuthority.
# Note that no warning is issued!
TaurusDatabase = TaurusAuthority
