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


class TestFactoryGarbageCollection(TestCase):

    def test_authority(self):
        def create():
            taurus.Authority()
        create()
        msg = "factory is polluted with authority "
        # TODO: uncomment this line whenever TangoFactory starts recycling
        # authorities
        # self.assertEqual(len(taurus.Factory().tango_auths), 0, msg)

    def test_device(self):
        def create():
            taurus.Device("sys/tg_test/1")
        create()
        msg = "factory is polluted with device"
        self.assertEqual(len(taurus.Factory().tango_devs), 0, msg)

    def test_attribute(self):
        def create():
            taurus.Attribute("sys/tg_test/1/state")
        create()
        msg = "factory is polluted with attribute"
        self.assertEqual(len(taurus.Factory().tango_attrs), 0, msg)
