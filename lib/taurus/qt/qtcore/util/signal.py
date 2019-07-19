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


"""Provide a Signal class for non-QObject objects"""
from __future__ import print_function

from builtins import object

from taurus.external.qt import Qt
from threading import Lock
from weakref import WeakKeyDictionary

__all__ = ['baseSignal']


def baseSignal(name, *args):
    """Signal class for non-Qobject objects.

    :param name: signal name (unlike pyqtSignal, name has
                 to be specified explicitely)
    :param args: arguments passed to the pyqtSignal
    """
    main_lock = Lock()
    lock_dict = WeakKeyDictionary()
    classname = name.capitalize() + "Signaller"
    attrs = {name: Qt.pyqtSignal(*args, name=name)}
    signaller_type = type(classname, (Qt.QObject,), attrs)

    def get_lock(self):
        with main_lock:
            if self not in lock_dict:
                lock_dict[self] = Lock()
        return lock_dict[self]

    def get_signaller(self):
        with get_lock(self):
            if not hasattr(self, '_signallers'):
                self._signallers = {}
            if (name, args) not in self._signallers:
                self._signallers[name, args] = signaller_type()
        return self._signallers[name, args]

    def get_signal(self):
        return getattr(get_signaller(self), name)

    doc = "Base signal {}".format(name)
    return property(get_signal, doc=doc)

if __name__ == '__main__':

    class Base(object):
        test = baseSignal('test', int)

    def print_func(arg):
        print(arg)

    base1, base2 = Base(), Base()
    base1.test.connect(print_func)
    base2.test.connect(print_func)
    base1.test.emit(1)
    base2.test.emit(2)
