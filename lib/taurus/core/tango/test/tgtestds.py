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

"""Module containing base classes for using the TangoSchemeTest DS in tests"""

__all__ = ['TangoSchemeTestLauncher']

__docformat__ = 'restructuredtext'

import PyTango

from taurus.core.tango.starter import ProcessStarter
from taurus.test import getResourcePath


class TangoSchemeTestLauncher(object):
    """A base class for TestCase classes wishing to start a TangoSchemeTest.
    Use it as a mixin class"""

    DEV_NAME = 'TangoSchemeTest/unittest/temp-1'  # the dev name

    @classmethod
    def setUpClass(cls):
        """ Create and run a TangoSchemeTest device server
        """
        # get path to DS and executable
        device = getResourcePath('taurus.core.tango.test.res',
                                 'TangoSchemeTest')
        # create starter for the device server
        cls._starter = ProcessStarter(device, 'TangoSchemeTest/unittest')
        # register
        cls._starter.addNewDevice(cls.DEV_NAME, klass='TangoSchemeTest')
        # start device server
        cls._starter.startDs()

    @classmethod
    def tearDownClass(cls):
        """ Stop the device server and undo changes to the database
        """
        d = PyTango.DeviceProxy(cls.DEV_NAME)
        d.Reset()
        cls._starter.stopDs(hard_kill=True)
        # remove server
        cls._starter.cleanDb(force=True)

    def tearDown(self):
        d = PyTango.DeviceProxy(self.DEV_NAME)
        d.Reset()

if __name__ == '__main__':
    pass
