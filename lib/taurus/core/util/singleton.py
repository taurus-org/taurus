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

"""This module contains a class which can be used as a super class for all
classes that need to implement the Singleton design pattern."""

from builtins import object

__all__ = ["Singleton"]

__docformat__ = "restructuredtext"


class Singleton(object):
    """ This class allows Singleton objects
    The __new__ method is overriden to force Singleton behaviour.
    The Singleton is created for the lowest subclass.
    Usage::

        from taurus.core.util.singleton import Singleton

        class MyManager(Singleton):

            def init(self, *args, **kwargs):
                print "Singleton initialization"

    command line::

        >>> manager1 = MyManager()
        Singleton initialization

        >>> manager2 = MyManager()

        >>> print(manager1,manager2)
        <__main__.MyManager object at 0x9c2a0ec>
        <__main__.MyManager object at 0x9c2a0ec>

    Notice that the two instances of manager point to the same object even
    though you *tried* to construct two instances of MyManager.

    .. warning::

        although __new__ is overriden __init__ is still being called for
        each instance=Singleton()
    """

    # Singleton object
    _the_instance = None

    def __new__(cls, *p, **k):
        # srubio: added type checking
        if cls != type(cls._the_instance):
            cls._the_instance = object.__new__(cls)

            # srubio: added init_single check
            if 'init_single' in cls.__dict__:
                cls._the_instance.init_single(*p, **k)
            else:
                cls._the_instance.init(*p, **k)
        return cls._the_instance

    def init(self, *p, **k):
        pass
