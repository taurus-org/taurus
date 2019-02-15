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

"""Test for taurus.core.resource.test.test_resfactory..."""
from __future__ import print_function
import os.path as osp
import taurus
from taurus.test import insertTest
import unittest
from taurus.core.resource.resfactory import ResourcesFactory

__all__ = ["ResourceFactoryTestCase"]

attr_dict1 = {'attr_1': 'eval:1',
              'attr_2': 'eval:2',
              'attr_3': 'eval:3'
              }

attr_dict2 = {'attr_3': 'eval:4',
              'attr_4': 'eval:5',
              'attr_5': 'eval:6'
              }

attr_dict3 = {'attr_3': 'tango://foo:10000/a/b/c/d',
              'attr_4': 'tango:motor1/position',
              'attr_5': 'tango:a/b/c/d'
              }

attr_dict4 = {'attr_6': 'eval:7',
              'attr_7': 'res:attr_1',
              'attr_8': 'tango:a/b/c/d',
              'attr_9': 'res:attr_10',
              'attr_10': 'eval:8'
              }

dev_dict1 = {'dev_1': 'eval:@foo',
             'dev_2': 'tango://foo:10000/a/b/c',
             'dev_3': 'tango://a/b/c',
             'dev_4': 'eval://@mydev'
             }

auth_dict1 = {'auth_1': 'foo:10000',
              'auth_2': 'tango://foo:10000',
              'auth_3': 'eval://localhost'
              }

file_name1 = osp.join(osp.dirname(osp.abspath(__file__)),
                      'res', 'attr_resources_file.py')
print(file_name1)

# TODO: the same key can be defined in different dictionaries (with different
# priority) but getValue method can not access to the less priority values in
# case of redundancies.


# ==============================================================================
# GetValue
# TODO: Load resources from a file does not seem to work
@insertTest(helper_name='getValue',
            resources=[(file_name1, 1)], key='dev1',
            expected_value='tango:a/b/c'
            )
@insertTest(helper_name='getValue',
            resources=[(file_name1, 1)], key='attr_2',
            expected_value='a/b/c/d'
            )
@insertTest(helper_name='getValue',
            resources=[(attr_dict1, 1)], key='attr_1',
            expected_value='eval:1'
            )
# Add the same attribute twice but with different priority
@insertTest(helper_name='getValue',
            resources=[(attr_dict1, 1), (attr_dict2, 2)], key='attr_3',
            expected_value='eval:3'
            )
@insertTest(helper_name='getValue',
            resources=[(attr_dict1, 3), (attr_dict2, 2)], key='attr_3',
            expected_value='eval:4'
            )
# Add the same attribute twice but with the same priority:
# The last resources dict set the final values. (Overwriting the existing ones)
@insertTest(helper_name='getValue',
            resources=[(attr_dict1, 5), (attr_dict2, 5)], key='attr_3',
            expected_value='eval:4'
            )
@insertTest(helper_name='getValue',
            resources=[(attr_dict1, 3), (dev_dict1, 3)], key='attr_3',
            expected_value=None
            )
@insertTest(helper_name='getValue',
            resources=[(attr_dict4, 2), (attr_dict2, 3)], key='attr_3',
            expected_value='eval:4'
            )
@insertTest(helper_name='getValue',
            resources=[(attr_dict4, 8), (attr_dict2, 9)], key='attr_8',
            expected_value='tango:a/b/c/d'
            )
@insertTest(helper_name='getValue',
            resources=[(dev_dict1, 2), (attr_dict2, 9)], key='dev_2',
            expected_value='tango://foo:10000/a/b/c'
            )
# ==============================================================================
# GetAttribute
@insertTest(helper_name='getAttribute',
            resources=[(attr_dict1, 3), (attr_dict2, 4)],
            uri='res:attr_3', expected_attr_uri='eval:3'
            )
@insertTest(helper_name='getAttribute',
            resources=[(attr_dict4, 3), (attr_dict1, 1)],
            uri='res:attr_7', expected_attr_uri='eval:1'
            )
@insertTest(helper_name='getAttribute',
            resources=[(attr_dict4, 3), (dev_dict1, 4)],
            uri='res:attr_6', expected_attr_uri='eval:7'
            )
@insertTest(helper_name='getAttribute',
            resources=[(attr_dict1, 1), (attr_dict2, 1)],
            uri='res:attr_3', expected_attr_uri='eval:4'
            )
@insertTest(helper_name='getAttribute',
            resources=[(attr_dict4, 1)],
            uri='res:attr_9', expected_attr_uri='eval:8'
            )
# ==============================================================================
# GetDevice
@insertTest(helper_name='getDevice',
            resources=[(dev_dict1, 1)],
            uri='res:dev_1', expected_attr_uri='eval:@foo'
            )
# ==============================================================================
# GetAuthority
@insertTest(helper_name='getAuthority',
            resources=[(auth_dict1, 1)],
            uri='res:auth_3', expected_attr_uri='eval://localhost'
            )
class ResourceFactoryTestCase(unittest.TestCase):

    def setUp(self):
        self.resfactory = ResourcesFactory()
        self.resfactory.clear()

    def _load(self, resources):
        """ Helper for load the resources
        :param resources: list of tuples (map, priority)
        """
        for obj, priority in resources:
            self.resfactory.loadResource(obj, priority)

    def getValue(self, resources, key, expected_value):
        """ Helper for test the resourcefactory getValue method
        :param resources: list of tuple (map, priority)
        :param key: name of the key
        :param expected_value: Is the expected URI
        """
        self._load(resources)
        value = self.resfactory.getValue(key)
        msg = 'The expected value is %s, got %s' % (expected_value, value)
        self.assertEqual(value, expected_value, msg)

    def getAttribute(self, resources, uri, expected_attr_uri):
        """ Helper for test the getAttribute method
        :param resources: list of tuple (map, priority)
        :param uri: res scheme uri.
        :param expected_attr_uri: a scheme uri
        """
        self._load(resources)
        expected_attr = taurus.Attribute(expected_attr_uri)
        res_attr = self.resfactory.getAttribute(uri)
        msg = 'Attributes are different, expected %s, got %s' % (expected_attr,
                                                                 res_attr)
        self.assertIs(expected_attr, res_attr, msg)

    def getDevice(self, resources, uri, expected_attr_uri):
        """ Helper for test the getDevice method
        :param resources: list of tuple (map, priority)
        :param uri: res scheme uri.
        :param expected_attr_uri: a scheme uri
        """
        self._load(resources)
        expected_dev = taurus.Device(expected_attr_uri)
        res_dev = self.resfactory.getDevice(uri)
        msg = 'Devices are different, expected %s, got %s' % (expected_dev,
                                                              res_dev)
        self.assertIs(expected_dev, res_dev, msg)

    def getAuthority(self, resources, uri, expected_attr_uri):
        """ Helper for test the getAuthority method
        :param resources: list of tuple (map, priority)
        :param uri: res scheme uri.
        :param expected_attr_uri: a scheme uri
        """
        self._load(resources)
        expected_auth = taurus.Authority(expected_attr_uri)
        res_auth = self.resfactory.getAuthority(uri)
        msg = 'Authorities are different, expected %s, got %s' % (expected_auth,
                                                                  res_auth)
        self.assertIs(expected_auth, res_auth, msg)

    def tearDown(self):
        self.resfactory.clear()
