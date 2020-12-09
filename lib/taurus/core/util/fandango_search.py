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

"""
fandango_search.py: methods for getting matching device/attribute/alias names 
from Tango database

These methods have been borrowed from fandango modules.
"""
# TODO: tango-centric

from builtins import str
import re
import taurus

###############################################################################
# Utils


def searchCl(regexp, target):
    return re.search(extend_regexp(regexp).lower(), target.lower())


def matchCl(regexp, target):
    return re.match(extend_regexp(regexp).lower(), target.lower())


def is_regexp(s):
    return any(c in s for c in '.*[]()+?')


def extend_regexp(s):
    s = str(s).strip()
    if '.*' not in s:
        s = s.replace('*', '.*')
    if '.*' not in s:
        if ' ' in s:
            s = s.replace(' ', '.*')
        if '/' not in s:
            s = '.*' + s + '.*'
    else:
        if not s.startswith('^'):
            s = '^' + s
        if not s.endswith('$'):
            s = s + '$'
    return s


def isString(s):
    # TODO: UGLY AND FRAGILE!!! (Refactor) May not even work with py3
    typ = s.__class__.__name__.lower()
    return not hasattr(s, '__iter__') and 'str' in typ and 'list' not in typ


def isCallable(obj):
    # TODO: UGLY AND FRAGILE!!! (Refactor) May not even work with py3
    return hasattr(obj, '__call__')


def isMap(obj):
    # TODO: UGLY AND FRAGILE!!! (Refactor) May not even work with py3
    return hasattr(obj, 'has_key') or hasattr(obj, 'items')


def isDictionary(obj):
    # TODO: UGLY AND FRAGILE!!! (Refactor)
    return isMap(obj)


def isSequence(obj):
    # TODO: UGLY AND FRAGILE!!! (Refactor) May not even work with py3
    typ = obj.__class__.__name__.lower()
    return (hasattr(obj, '__iter__') or 'list' in typ) and not isString(obj) and not isMap(obj)


def split_model_list(modelNames):
    '''convert str to list if needed (commas and whitespace are considered as separators)'''
    if isString(modelNames):
        modelNames = str(modelNames).replace(',', ' ')
        modelNames = modelNames.split()
    if isSequence(modelNames):  # isinstance(modelNames,(list.Qt.QStringList)):
        modelNames = [str(s) for s in modelNames]
    return modelNames


def get_matching_devices(expressions, limit=0, exported=False):
    """
    Searches for devices matching expressions, if exported is True only running devices are returned
    """
    db = taurus.Authority()
    all_devs = [s.lower() for s in db.get_device_name('*', '*')]
    # This code is used to get data from multiples hosts
    #if any(not fun.matchCl(rehost,expr) for expr in expressions): all_devs.extend(get_all_devices(exported))
    # for expr in expressions:
    #m = fun.matchCl(rehost,expr)
    # if m:
    #host = m.groups()[0]
    # print 'get_matching_devices(%s): getting %s devices ...'%(expr,host)
    #odb = PyTango.Database(*host.split(':'))
    #all_devs.extend('%s/%s'%(host,d) for d in odb.get_device_name('*','*'))
    result = [e for e in expressions if e.lower() in all_devs]
    expressions = [extend_regexp(e) for e in expressions if e not in result]
    result.extend([d for d in all_devs if any(matchCl(extend_regexp(e), d)
                                       for e in expressions)])
    return result


def get_device_for_alias(alias):
    # TODO: Use validators instead
    db = taurus.Authority()
    try:
        return db.get_device_alias(alias)
    except Exception as e:
        if 'no device found' in str(e).lower():
            return None
        return None  # raise e


def get_alias_for_device(dev):
    # TODO: Use validators instead
    db = taurus.Authority()
    try:
        # .get_database_device().DbGetDeviceAlias(dev)
        result = db.get_alias(dev)
        return result
    except Exception as e:
        if 'no alias found' in str(e).lower():
            return None
        return None  # raise e


def get_alias_dict(exp='*'):
    tango = taurus.Authority()
    return dict((k, tango.get_device_alias(k)) for k in tango.get_device_alias_list(exp))
