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
from builtins import str

from . import PYQT5, PYSIDE2, PYQT4, PYSIDE, PythonQtError

# Deprecated. QString is kept for now to facilitate transition, of existing
# codebut using QString should be avoided since it was deprecated
QString = str
# TODO: remove all occurrences of QString in taurus

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
    from PySide2.QtCore import Property as pyqtProperty
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
    from PyQt4.QtCore import qInstallMsgHandler as qInstallMessageHandler

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

elif PYSIDE:
    from PySide.QtCore import *
    from PySide.QtCore import Signal as pyqtSignal
    from PySide.QtCore import Slot as pyqtSlot
    from PySide.QtCore import Property as pyqtProperty
    from PySide.QtGui import (QItemSelection, QItemSelectionModel,
                              QItemSelectionRange, QSortFilterProxyModel,
                              QStringListModel)
    from PySide.QtCore import qInstallMsgHandler as qInstallMessageHandler

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