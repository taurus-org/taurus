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
properties.py: Methods for adding QProperties to QObjects

A call like
        set_property_methods(self,'Filters','QString',default='',
            set_callback=lambda s=self:s.loadTree(s.getFilters(),clear=True),
            reset_callback=lambda s=self:s.loadTree('',clear=True)
            )

Would replace all these lines:

    def setFilters(self,filters):
        self._filters = filters
        self.loadTree(self._filters,clear=True)

    def getFilters(self):
        return self._filters

    def resetFilters(self):
        self._filters=""
        self.loadTree(self._filters)

    filters = QtCore.pyqtProperty("QString", getFilters, setFilters, resetFilters)

Not tested yet with the classical declaration:

    #model = QtCore.pyqtProperty("QString", TaurusBaseWidget.getModel,
                            #TaurusBaseWidget.setModel,
                            #TaurusBaseWidget.resetModel)

"""

from builtins import str
from builtins import map
from taurus.external.qt import Qt
from taurus.core.util.fandango_search import isSequence, isDictionary


def join(*seqs):
    """ It returns a list containing the objects of all given sequences. """
    if len(seqs) == 1 and isSequence(seqs[0]):
        seqs = seqs[0]
    result = []
    for seq in seqs:
        if isSequence(seq):
            result.extend(seq)
        else:
            result.append(seq)
    #    result += list(seq)
    return result


def djoin(a, b):
    """ This method merges dictionaries and/or lists """
    if not any(map(isDictionary, (a, b))):
        return join(a, b)
    other, dct = sorted((a, b), key=isDictionary)
    if not isDictionary(other):
        other = dict.fromkeys(other if isSequence(other) else [other, ])
    for k, v in other.items():
        dct[k] = v if not k in dct else djoin(dct[k], v)
    return dct


def get_property_attribute(name):
    return '_' + str(name).lower()


def get_property(obj, name, callback=None):
    return (callback and callback()) or getattr(obj, get_property_attribute(name))


def set_property(obj, name, value, callback=None):
    # print 'set_property(%s,%s,%s,%s)'%(obj,name,value,callback)
    setattr(obj, get_property_attribute(name), value)
    try:
        callback and callback(value)
    except:
        callback()


def reset_property(obj, name, default=None, callback=None):
    setattr(obj, get_property_attribute(name), default)
    if callback:
        callback()

COMMON_PROPERTIES = (
    'ModelInConfig',  # If True, it will automatically register Model
    'modifiableByUser',
    #'useParentModel', #Only for widgets, not for components
    #'Model', #Controlled by ModelInConfig
)


def set_property_methods(obj, name, type_="QString", default=None, getter=None,
                         setter=None, reset=None, get_callback=None,
                         set_callback=None, reset_callback=None, qt=False,
                         config=False):
    """
    This method allows to add QProperties dynamically with calls like::

        set_property_methods(self,'Filters','QString',default='',
            set_callback=lambda s=self:s.loadTree(s.getFilters(),clear=True),
            reset_callback=lambda s=self:s.loadTree('',clear=True)
            )


    .. todo: This method should be refactored using python
             descriptors/properties and types.MethodType
    """
    klass = obj.__class__
    mname = '%s%s' % (name[0].upper(), name[1:])
    lname = '%s%s' % (name[0].lower(), name[1:])
    getter = getter or (lambda o=obj, n=name, c=get_callback: get_property(
        o, n, c))  # partial(get_property,name=name,callback=get_callback)
    setter = setter or (lambda x, y=None, o=obj, d=default, n=name, c=set_callback: set_property(
        o, n, x if x is not obj else y, c))  # partial(set_property),name=name,callback=set_callback)
    reset = reset or (lambda o=obj, n=name, d=default, c=reset_callback: reset_property(
        o, n, d, c))  # partial(reset_property,name=name,default=default,callback=reset_callback)
    setattr(obj, 'set%s' % mname, setter)
    setattr(obj, 'get%s' % mname, getter)
    setattr(obj, 'reset%s' % mname, reset)
    if qt:
        setattr(klass, lname,
                Qt.pyqtProperty("QString", getter, setter, reset)
                )
    if config:
        obj.registerConfigProperty(getter, setter, name)
    reset()
