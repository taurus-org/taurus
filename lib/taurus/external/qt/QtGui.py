# -*- coding: utf-8 -*-
#
# Copyright © 2018- CELLS / ALBA Synchrotron, Bellaterra, Spain
# Copyright © 2014-2015 Colin Duquesnoy
# Copyright © 2009-2018 The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

"""
Provides QtGui classes and functions.
.. warning:: Contrary to qtpy.QtGui, this module exposes the namespace
    available in ``PyQt4.QtGui``.
    See: http://pyqt.sourceforge.net/Docs/PyQt5/pyqt4_differences.html#qtgui-module
"""
import warnings

from . import PYQT5, PYQT4, PYSIDE, PYSIDE2, PythonQtError


if PYQT5:
    from PyQt5.QtGui import *
    # import * from QtWidgets and QtPrintSupport for PyQt4 style compat
    from PyQt5.QtWidgets import *
    from PyQt5.QtPrintSupport import *
elif PYSIDE2:
    from PySide2.QtGui import *
    # import * from QtWidgets and QtPrintSupport for PyQt4 style compat
    from PySide2.QtWidgets import *
    from PySide2.QtPrintSupport import *
elif PYQT4:
    from PyQt4.QtGui import *

elif PYSIDE:
    from PySide.QtGui import *
else:
    raise PythonQtError('No Qt bindings could be found')
