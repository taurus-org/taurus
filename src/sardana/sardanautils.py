#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
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

"""This module is part of the Python Sardana libray. It defines some
utility methods"""

__all__ = ["is_pure_str", "is_non_str_seq", "is_integer", "is_number",
           "is_bool", "check_type", "assert_type"]

__docformat__ = 'restructuredtext'

import collections
import numbers
import numpy

from sardanadefs import DataType, DTYPE_MAP, R_DTYPE_MAP

__str_klasses = [str]
__int_klasses = [int, numpy.integer]
__number_klasses = [numbers.Number, numpy.number]

__DTYPE_MAP = dict(DTYPE_MAP)

__use_unicode = False
try:
    unicode
    __use_unicode = True
    __str_klasses.append(unicode)
    __DTYPE_MAP[unicode] = DataType.String
except:
    pass

__use_long = False
try:
    long
    __use_long = True
    __int_klasses.append(long)
    __DTYPE_MAP[long] = DataType.Integer
except:
    pass

__bool_klasses = [bool] + __int_klasses

__str_klasses = tuple(__str_klasses)
__int_klasses = tuple(__int_klasses)
__number_klasses = tuple(__number_klasses)
__bool_klasses = tuple(__bool_klasses)

def is_pure_str(obj):
    return isinstance(obj , __str_klasses)

def is_non_str_seq(obj):
    return isinstance(obj, collections.Sequence) and not is_pure_str(obj)

def is_integer(obj):
    return isinstance(obj, __int_klasses)

def is_number(obj):
    return isinstance(obj, __number_klasses)

def is_bool(obj):
    return isinstance(obj, __bool_klasses)

__METH_MAP = {
    DataType.Integer : is_integer,
    DataType.Double  : is_number,
    DataType.String  : is_pure_str,
    DataType.Boolean : is_bool
}

def check_type(type_info, value):
    tinfo = __DTYPE_MAP.get(type_info, type_info)
    tmeth = __METH_MAP.get(tinfo, type_info)
    return tmeth(value)
    
def assert_type(type_info, value):
    ret = check_type(type_info, value)
    if not ret:
        expected = R_DTYPE_MAP[type_info]
        recv = type(value)
        try:
            expected = expected.__name__
        except:
            expected = str(expected)
        try:
            recv = recv.__name__
        except:
            recv = str(recv)
        raise TypeError("Expected %s, but received %s", expected, recv)
    return ret
    
