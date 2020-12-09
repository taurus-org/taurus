#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

"""[DEPRECATED since taurus v4]
This module contains the base class for a taurus attribute configuration"""

from builtins import object
from .taurusmodel import TaurusModel
from .util.log import taurus4_deprecation


__all__ = ["TaurusConfigurationProxy", "TaurusConfiguration"]

__docformat__ = "restructuredtext"


class TaurusConfigurationProxy(object):
    """
    TaurusAttribute has a reference to TaurusConfiguration and it should also have
    a reference to TaurusAttribute. To solve this cyclic dependency,
    TaurusConfiguration has a weak reference to TaurusAttribute. But then we must
    be sure that no other references to TaurusConfiguration exist so that
    no one tries to use it after its TaurusAttribute has disappeared.
    That's why to the outside world we don't give access to it directly
    but to objects of this new TaurusConfigurationProxy class.
    """
    @taurus4_deprecation(dbg_msg='Do not use this class')
    def __init__(self, parent):
        self.__parent = parent

    def __getattr__(self, name):
        return getattr(self.__parent._getRealConfig(), name)

    def getRealConfigClass(self):
        return self.__parent._getRealConfig().__class__


class TaurusConfiguration(TaurusModel):

    @taurus4_deprecation(alt='TaurusAttribute', dbg_msg='Do not use this class')
    def __init__(self, name, parent, storeCallback=None):
        pass
