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

"""This module is part of the Python Sardana library. It defines some
utility methods"""

from __future__ import absolute_import

__all__ = ["is_pure_str", "is_non_str_seq", "is_integer", "is_number",
           "is_bool", "check_type", "assert_type", "str_to_value",
           "is_callable", "translate_version_str2int",
           "translate_version_str2list"]

__docformat__ = 'restructuredtext'

import numpy
import numbers
import collections

from sardana.sardanadefs import DataType, DataFormat, DTYPE_MAP, R_DTYPE_MAP

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

def is_callable(obj):
    return hasattr(obj, "__call__")

__METH_MAP = {
    DataType.Integer : is_integer,
    DataType.Double  : is_number,
    DataType.String  : is_pure_str,
    DataType.Boolean : is_bool,
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

_DTYPE_FUNC = {
    DataType.Integer : int,
    DataType.Double  : float,
    DataType.String  : str,
    DataType.Boolean : bool,
}

def str_to_value(value, dtype=DataType.Double, dformat=DataFormat.Scalar):
    f = _DTYPE_FUNC[dtype]
    if dformat == DataFormat.Scalar:
        ret = f(value)
    elif dformat == DataFormat.OneD:
        ret = [ f(v) for v in value ]
    elif dformat == DataFormat.TwoD:
        ret = []
        for v1 in value:
            ret.append([ f(v2) for v2 in v1 ])
    return ret

def translate_version_str2int(version_str):
    """Translates a version string in format x[.y[.z[...]]] into a 000000 number.
    Each part of version number can have up to 99 possibilities."""
    import math
    parts = version_str.split('.')
    i, v, l = 0, 0, len(parts)
    if not l: return v
    while i < 3:
        try:
            v += int(parts[i]) * int(math.pow(10, (2 - i) * 2))
            l -= 1
            i += 1
        except ValueError:
            return v
        if not l: return v
    return v

    try:
        v += 10000 * int(parts[0])
        l -= 1
    except ValueError:
        return v
    if not l: return v

    try:
        v += 100 * int(parts[1])
        l -= 1
    except ValueError:
        return v
    if not l: return v

    try:
        v += int(parts[0])
        l -= 1
    except ValueError:
        return v
    if not l: return v

def translate_version_str2list(version_str, depth=2):
    """Translates a version string in format 'x[.y[.z[...]]]' into a list of
    numbers"""
    if version_str is None:
        ver = depth * [0, ]
    else:
        ver = []
        for i in version_str.split(".")[:depth]:
            try:
                i = int(i)
            except:
                i = 0
            ver.append(i)
    return ver

