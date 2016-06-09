"""Provide a Signal class for non-QObject objects"""

__all__ = ['baseSignal']

from PyQt4 import Qt
from threading import Lock
from weakref import WeakKeyDictionary


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
