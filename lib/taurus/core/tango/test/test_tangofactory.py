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

"""Tests for taurus.core.tango.tangofactory"""


import taurus

from taurus.external.unittest import TestCase
from taurus.core.tango.test.tgtestds import TangoSchemeTestLauncher


class TestFactoryGarbageCollection(TangoSchemeTestLauncher, TestCase):

    # in order to not interfere with the following tests this device should
    # not be used in another tests
    DEV_NAME = 'TangoSchemeTest/unittest/temp-tfgc-1'

    def setUp(self):
        self.factory = taurus.Factory()

    # TODO: Uncomment this test when tango factory recycles authority
    # def test_authority(self):
    #     old_len = len(self.factory.tango_db)
    # 
    #     def create():
    #         taurus.Authority()
    # 
    #     create()
    #     msg = "factory is polluted with authority "
    #     self.assertEqual(len(self.factory.tango_db), old_len, msg)

    def test_device(self):
        old_len = len(self.factory.tango_devs)

        def create():
            taurus.Device(self.DEV_NAME)

        create()
        msg = "factory is polluted with device"
        self.assertEqual(len(self.factory.tango_devs), old_len, msg)

    def test_attribute(self):
        old_len = len(self.factory.tango_attrs)

        def create():
            taurus.Attribute(self.DEV_NAME + "/state")

        create()
        msg = "factory is polluted with attribute"
        self.assertEqual(len(self.factory.tango_attrs), old_len, msg)

    def tearDown(self):
        self.factory = None
