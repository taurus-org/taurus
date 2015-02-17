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

"""Base classes for the controller tests"""

__all__ = ['BasePoolTestCase', 'ControllerLoadsTestCase',
           'ControllerCreationTestCase', 'ElementCreationTestCase']

import os
import PyTango
from taurus import Device
from taurus.external import unittest
from taurus.core.tango.starter import ProcessStarter
from sardana import sardanacustomsettings
from sardana.taurus.core.tango.sardana import (registerExtensions,
                                              unregisterExtensions)
from sardana.tango.core.util import (get_free_server, get_free_device,
                                     get_free_alias)
from taurus.core.util import whichexecutable


class BasePoolTestCase(object):
    """Abstract class for pool DS testing.
    """
    pool_ds_name = getattr(sardanacustomsettings, 'UNITTEST_POOL_DS_NAME')
    pool_name = getattr(sardanacustomsettings, 'UNITTEST_POOL_NAME')

    def setUp(self):
        """Start Pool DS and register extensions.
        """
        # Discover the Pool launcher script
        poolExec = whichexecutable.whichfile("Pool")
        # register Pool server
        pool_ds_name = "Pool/" + self.pool_ds_name
        pool_free_ds_name = get_free_server(PyTango.Database(),
                                            pool_ds_name)
        self._starter = ProcessStarter(poolExec, pool_free_ds_name)
        # register Pool device
        dev_name_parts = self.pool_name.split('/')
        prefix = '/'.join(dev_name_parts[0:2])
        start_from = int(dev_name_parts[2])
        self.pool_name = get_free_device(PyTango.Database(), prefix, start_from)
        self._starter.addNewDevice(self.pool_name, klass='Pool')
        # start Pool server
        self._starter.startDs()
        # register extensions so the test methods can use them
        registerExtensions()
        self.pool = Device(self.pool_name)

    def tearDown(self):
        """Remove the Pool instance.
        """
        unregisterExtensions()
        self._starter.cleanDb(force=True)


# TODO: Currently test inputs are implemented as class members, it would be
# more aesthetic to implement them as decorators.
class ControllerLoadsTestCase(BasePoolTestCase):
    """Class for loading an arbitrary Sardana controller library and class.
    """
    controller_classes = []
    def test_controller_loads(self):
        """Test that the controller library and class can be loaded.
        """
        libraries = self.pool.getElementsOfType('ControllerLibrary').values()
        libraries_names = [lib.getName() for lib in libraries]
        classes = self.pool.getElementsOfType('ControllerClass').values()
        classes_names = [cls.getName() for cls in classes]

        for test_lib, test_classes in self.controller_classes.items():
            msg = 'ControllerLibrary %s was not correctly loaded.' % test_lib
            self.assertIn(test_lib, libraries_names, msg)
            msg = 'ControllerClass %s was not correctly loaded.'
            for test_class in test_classes:
                self.assertIn(test_class, classes_names, msg % test_class)


# TODO: Currently test inputs are implemented as class members, it would be
# more aesthetic to implement them as decorators.
class ControllerCreationTestCase(BasePoolTestCase):
    """Class for creating a controller and testing the correct creation.
    """
    controller_infos = []

    def test_controller_creation(self):
        """Test that the controller has been created with the correct name.
        """
        for cls, name, props  in self.controller_infos:
            ctrl = self.pool.createController(cls, name, *props)
            msg = 'Controller %s was not correctly created.' % name
            self.assertEqual(ctrl.getName(), name, msg)
            ctrl = self.pool.deleteElement(ctrl.getName())


# TODO: Currently test inputs are implemented as class members, it would be
# more aesthetic to implement them as decorators.
class ElementCreationTestCase(BasePoolTestCase):
    """Class used for creating a Sardana controller and Sardana elements.
    """
    controller_infos = []
    NAME = 0
    AXIS = 1

    def test_element_creation(self):
        """Test that controller and elements have been correctly created.
        """
        for cls, name, props, elements  in self.controller_infos:
            ctrl = self.pool.createController(cls, name, *props)
            msg = 'Controller %s was not correctly created.' % name
            self.assertEqual(ctrl.getName(), name, msg)
            for element_info in elements:
                test_name = element_info[self.NAME]
                test_axis = element_info[self.AXIS]
                elem = self.pool.createElement(test_name, ctrl, test_axis)
                msg = 'Element %s was not correctly created.' % test_name
                self.assertIsNotNone(elem, msg)
                name = elem.getName()
                msg = 'Element name: %s does not correspond to: %s.' % \
                      (name, test_name)
                self.assertEqual(name, test_name, msg)
                elem = self.pool.deleteElement(test_name)
                msg = 'Element %s was not correctly deleted.' % test_name
                self.assertIsNotNone(elem, msg)
            ctrl = self.pool.deleteElement(ctrl.getName())


if __name__ == '__main__':

    class BuiltinControllerLoadsTest(ControllerLoadsTestCase,
                                     unittest.TestCase):

        controller_classes = {
        'DummyMotorController':('DummyMotorController',)
        }

    class BuiltinControllerCreationTest(ControllerCreationTestCase,
                                     unittest.TestCase):

        controller_infos = [('DummyMotorController', 'unittest', ())
        ]

    class BuiltinElementCreationTest(ElementCreationTestCase,
                                     unittest.TestCase):
        alias = get_free_alias(PyTango.Database(), "mot_test")
        controller_infos = [('DummyMotorController',
                            'unittest',
                            (),
                            [(alias, 1)])
                           ]

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
    BuiltinElementCreationTest)
    unittest.TextTestRunner(descriptions=True, verbosity=2).run(suite)
