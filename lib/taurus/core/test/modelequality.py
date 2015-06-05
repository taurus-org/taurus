#!/usr/bin/env python
#############################################################################
##
## This file is part of Taurus
## 
## http://taurus-scada.org
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

import functools

from taurus import Device, Attribute #, Authority
from taurus.test import insertTest
        
class TaurusModelEqualityTestCase(object):
    """Base class for taurus model equality testing."""
    
    def modelsEqual(self, models, class_, equal=True):
        """A helper method to create tests that checks equality (or inequality)
        of taurus objects e.g. TaurusAttribute.

        :param models: (seq<str>): a sequence of two taurus models
        :param class_: (type) a class (or a factory function) that will be used
                       to create objects
        :param equal: (bool) a flag argument, whether to check equality or 
                      inequality
        """

        if len(models) > 2:
            raise ValueError('models length is higher than 2')        
        obj1 = class_(models[0])        
        obj2 = class_(models[1])        
        if equal:
            msg = '%s objects: %s and %s are not equal but should be' % \
                  (class_.__name__, obj1, obj2)
            self.assertEqual(obj1, obj2, msg)            
        else:
            msg = '%s objects: %s and %s are equal but should not be' % \
                  (class_.__name__, obj1, obj2)
            self.assertNotEqual(obj1, obj2, 'Case insensitivity failed')
            
# testAuthorityModelEquality = functools.partial(insertTest, 
#                               helper_name = 'modelsSensitive',
#                               class_ = Authority,
#                               test_method_name = 'testAuthorityModelEquality')
            
testDeviceModelEquality = functools.partial(insertTest, 
                                   helper_name = 'modelsEqual',
                                   class_ = Device,
                                   test_method_name = 'testDeviceModelEquality')

testAttributeModelEquality = functools.partial(insertTest, 
                                helper_name = 'modelsEqual',
                                class_ = Attribute,
                                test_method_name = 'testAttributeModelEquality')

# def set_alias(device):
#     import PyTango
#     db = PyTango.Database()
#     db.put_device_alias(device, 'unit_test')
#     return 'unit_test'
# 
# def get_alias(device):
#     import PyTango
#     d = PyTango.DeviceProxy(device)
#     try:
#         return d.alias()
#     except:
#         return None
# 
# def del_alias():
#     import PyTango
#     db = PyTango.Database()
#     db.delete_device_alias('unit_test')        
#         
# class TaurusCaseSensitivityTest(unittest.TestCase):
# 
#     def setUp(self):
#         self.tango_device_name = ["sys/tg_test/1"]
# 
#     def test_tango_device(self):
#         '''Test tango case insensitivity'''
#         for d in self.tango_device_name:
#             delalias = False
#             alias = get_alias(d)
#             if alias is None:
#                 alias = set_alias(d)
#                 delalias = True
#             self.check_tango_device(d,alias)    
#             if delalias:
#                 del_alias()
# 
#     def check_tango_device(self, device_name, device_alias):
#         tango_host = os.environ['TANGO_HOST']
#         tango_scheme = "tango://"
#             
#         m1 = device_name
#         m2 = tango_scheme + tango_host + '/' + rand_uppercase(m1) 
#         m3 = device_alias
#         m4 = tango_scheme + rand_uppercase(m3)
#         ### Tango devices
#         d1 = Device(rand_uppercase(m1))
#         d2 = Device(m2)
#         d3 = Device(rand_uppercase(m3))
#         d4 = Device(m4)
# 
# 
#         self.assertEqual(d1, d2, "Device, %s is not equal %s" %(d1,d2))
#         self.assertEqual(d3, d4, "Device, %s is not equal %s" %(d3,d4))
#         self.assertEqual(d1, d3, "Device, %s is not equal %s" %(d1,d2))
#         
# if __name__ == '__main__':    
#     unittest.main(verbosity=2)