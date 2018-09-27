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

"""This module contains the base Object class for taurus."""

from builtins import object

__all__ = ["Object"]

__docformat__ = "restructuredtext"


class Object(object):

    def __init__(self):
        pass

    def call__init__(self, klass, *args, **kw):
        """Method to be called from subclasses to call superclass corresponding
        __init__ method. This method ensures that classes from diamond like
        class hierarquies don't call their super classes __init__ more than
        once."""

        if 'inited_class_list' not in self.__dict__:
            self.inited_class_list = []

        if klass not in self.inited_class_list:
            self.inited_class_list.append(klass)
            klass.__init__(self, *args, **kw)

    def call__init__wo_kw(self, klass, *args):
        """Same as call__init__ but without keyword arguments because PyQT does
        not support them."""

        if 'inited_class_list' not in self.__dict__:
            self.inited_class_list = []

        if klass not in self.inited_class_list:
            self.inited_class_list.append(klass)
            klass.__init__(self, *args)

    def getAttrDict(self):
        attr = dict(self.__dict__)
        if 'inited_class_list' in attr:
            del attr['inited_class_list']
        return attr

    def updateAttrDict(self, other):
        attr = other.getAttrDict()
        self.__dict__.update(attr)
