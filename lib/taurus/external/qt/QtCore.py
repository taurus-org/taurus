# -*- coding: utf-8 -*-
#
# Copyright © 2018- CELLS / ALBA Synchrotron, Bellaterra, Spain
# Copyright © 2014-2015 Colin Duquesnoy
# Copyright © 2009-2018 The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

"""
Provides QtCore classes and functions.
"""
from builtins import str as __str
from taurus.core.util.log import deprecation_decorator as __deprecation

from . import PYQT5, PYSIDE2, PYQT4, PYSIDE, PythonQtError


# --------------------------------------------------------------------------
# QString, from_qvariant and to_qvariant are kept for now to
# facilitate transition of existing code but using them
# should be avoided (they only make sense with API 1, which is not supported)
@__deprecation(rel='4.0.1', alt='str')
class QString(__str):
    pass


@__deprecation(rel='4.0.1', alt='python objects directly')
def from_qvariant(qobj=None, convfunc=None):
    return qobj


@__deprecation(rel='4.0.1', alt='python objects directly')
def to_qvariant(pyobj=None):
    return pyobj
# --------------------------------------------------------------------------

if PYQT5:
    from PyQt5.QtCore import *
    from PyQt5.QtCore import pyqtSignal as Signal
    from PyQt5.QtCore import pyqtSlot as Slot
    from PyQt5.QtCore import pyqtProperty as Property
    from PyQt5.QtCore import QT_VERSION_STR as __version__

    # For issue #153 of qtpy
    from PyQt5.QtCore import QDateTime
    QDateTime.toPython = QDateTime.toPyDateTime

elif PYSIDE2:
    from PySide2.QtCore import *
    from PySide2.QtCore import Signal as pyqtSignal
    from PySide2.QtCore import Slot as pyqtSlot

    # ------------------------------------------------
    # Calling Property with doc="" produces segfaults in the tests.
    # As a workaround, just remove the doc kwarg. Note this is an ad-hoc
    # workaround: I could not find the API definition for
    # PySide.QtCore.Property in order to do a more complete mock
    def pyqtProperty(*args, **kwargs):
        kwargs.pop('doc', None)
        return Property(*args, **kwargs)
    # -------------------------------------------------

    try:  # may be limited to PySide-5.11a1 only
        from PySide2.QtGui import QStringListModel
    except:
        pass

elif PYQT4:
    from PyQt4.QtCore import *
    from PyQt4.QtCore import QCoreApplication
    from PyQt4.QtCore import Qt
    from PyQt4.QtCore import pyqtSignal as Signal
    from PyQt4.QtCore import pyqtSlot as Slot
    from PyQt4.QtCore import pyqtProperty as Property
    from PyQt4.QtGui import (QItemSelection, QItemSelectionModel,
                             QItemSelectionRange, QSortFilterProxyModel,
                             QStringListModel)
    from PyQt4.QtCore import QT_VERSION_STR as __version__

    # QDesktopServices has has been split into (QDesktopServices and
    # QStandardPaths) in Qt5
    # This creates a dummy class that emulates QStandardPaths
    from PyQt4.QtGui import QDesktopServices as _QDesktopServices

    class QStandardPaths():
        StandardLocation = _QDesktopServices.StandardLocation
        displayName = _QDesktopServices.displayName
        DesktopLocation = _QDesktopServices.DesktopLocation
        DocumentsLocation = _QDesktopServices.DocumentsLocation
        FontsLocation = _QDesktopServices.FontsLocation
        ApplicationsLocation = _QDesktopServices.ApplicationsLocation
        MusicLocation = _QDesktopServices.MusicLocation
        MoviesLocation = _QDesktopServices.MoviesLocation
        PicturesLocation = _QDesktopServices.PicturesLocation
        TempLocation = _QDesktopServices.TempLocation
        HomeLocation = _QDesktopServices.HomeLocation
        DataLocation = _QDesktopServices.DataLocation
        CacheLocation = _QDesktopServices.CacheLocation
        writableLocation = _QDesktopServices.storageLocation


    # Deprecated. QVariant is kept for now to facilitate transition of existing
    # code but using QVariant should be avoided (with API 2 it is superfluous)
    @__deprecation(rel='4.0.1', alt='python objects directly')
    def QVariant(pyobj=None):
        return pyobj


elif PYSIDE:
    from PySide.QtCore import *
    from PySide.QtCore import Signal as pyqtSignal
    from PySide.QtCore import Slot as pyqtSlot
    from PySide.QtCore import Property as pyqtProperty
    from PySide.QtGui import (QItemSelection, QItemSelectionModel,
                              QItemSelectionRange, QSortFilterProxyModel,
                              QStringListModel)

    # QDesktopServices has has been split into (QDesktopServices and
    # QStandardPaths) in Qt5
    # This creates a dummy class that emulates QStandardPaths
    from PySide.QtGui import QDesktopServices as _QDesktopServices

    class QStandardPaths():
        StandardLocation = _QDesktopServices.StandardLocation
        displayName = _QDesktopServices.displayName
        DesktopLocation = _QDesktopServices.DesktopLocation
        DocumentsLocation = _QDesktopServices.DocumentsLocation
        FontsLocation = _QDesktopServices.FontsLocation
        ApplicationsLocation = _QDesktopServices.ApplicationsLocation
        MusicLocation = _QDesktopServices.MusicLocation
        MoviesLocation = _QDesktopServices.MoviesLocation
        PicturesLocation = _QDesktopServices.PicturesLocation
        TempLocation = _QDesktopServices.TempLocation
        HomeLocation = _QDesktopServices.HomeLocation
        DataLocation = _QDesktopServices.DataLocation
        CacheLocation = _QDesktopServices.CacheLocation
        writableLocation = _QDesktopServices.storageLocation

    import PySide.QtCore
    __version__ = PySide.QtCore.__version__
else:
    raise PythonQtError('No Qt bindings could be found')