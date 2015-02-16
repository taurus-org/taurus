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

__all__ = ['dummyCounterTimerConf01', 'dummyMeasurementGroupConf01',
           'dummyPoolCTCtrlConf01']

# Pool Elements

'''Minimum configuration to create a Pool CounterTimer'''
dummyCounterTimerConf01 = { 'axis': 1,
                            'ctrl': None,
                            'full_name': '',
                            'id': 2,
                            'name': '',
                            'pool': None }

'''Minimum configuration to create a Pool MeasurementGroup'''
dummyMeasurementGroupConf01 = { 'full_name': '',
                              'id': 3,
                              'name': '',
                              'pool': None,
                              'user_elements': [2] }

# Pool Ctrls

'''Minimum configuration to create a Pool CounterTimer controller'''
dummyPoolCTCtrlConf01 = { 'class_info': None,
                        'full_name': '',
                        'id': 1,
                        'klass': 'DummyCounterTimerController',
                        'lib_info': None,
                        'library': 'DummyCounterTimerController.py',
                        'name': '',
                        'pool': None,
                        'properties': {},
                        'role_ids': '',
                        'type': 'CTExpChannel' }
