#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""This module exposes PyQt4.Qt module"""

from taurusqtoptions import QT_API, QT_API_PYQT, QT_API_PYSIDE

def __to_qvariant_1(pyobj=None):
    """Properly converts a python object into a proper QVariant according to
    the PySide or PyQt4 API version in use
    
    :param pyobj: object to be converted
    :return: A proper QVariant"""
    from PyQt4.QtCore import QVariant
    if pyobj is None:
        return QVariant()  # PyQt 4.4 doesn't accept QVariant(None)
    return QVariant(pyobj)

def __from_qvariant_1(qobj=None, convfunc=None):
    """Properly converts a QVariant/QVariant equivalent to a python object
    according to the PySide or PyQt4 API version in use
    
    :param qobj: object to be converted
    :param convfunc:
        conversion function. Not used if QVariant is not available.
        If QVariant is available:  [default: None, meaning use
        qobj.toPyObject()]. Can be a function like str, int, bool, float or
        a string containing the conversion method (ex.: 'toByteArray') will
        call qobj.toByteArray()
    :return: A proper python object"""
    if convfunc is None:
        return qobj.toPyObject()
    elif callable(convfunc):
        if convfunc in (unicode, str):
            return convfunc(qobj.toString())
        elif convfunc is bool:
            return qobj.toBool()
        elif convfunc is int:
            return qobj.toInt()[0]
        elif convfunc is float:
            return qobj.toDouble()[0]
    elif isinstance(convfunc, (str, unicode)):
        return getattr(qobj, convfunc)()
    
def __QVariant_2(pyobj=None):
    return pyobj
    
def __to_qvariant_2(pyobj=None):
    """Properly converts a python object into a proper QVariant according to
    the PySide or PyQt4 API version in use
    
    :param pyobj: object to be converted
    :return: A proper QVariant"""
    return pyobj

def __from_qvariant_2(qobj=None, convfunc=None):
    """Properly converts a QVariant/QVariant equivalent to a python object
    according to the PySide or PyQt4 API version in use
    
    :param qobj: object to be converted
    :param convfunc:
        conversion function. Not used if QVariant is not available.
        If QVariant is available:  [default: None, meaning use
        qobj.toPyObject()]. Can be a function like str, int, bool, float or
        a string containing the conversion method (ex.: 'toByteArray') will
        call qobj.toByteArray()
    :return: A proper python object"""
    return qobj

#def __QString_2(pyobj=""):
#    return str(pyobj)

__QString_2 = str

#def __QStringList_2(pyobj=None):
#    if pyobj is None:
#        return list()
#    if isinstance(pyobj, (str, unicode)):
#        return [pyobj]
#    return list(pyobj)

__QStringList_2 = list

# Now peform the imports.
if QT_API == QT_API_PYQT:
    import PyQt4.Qt
    import PyQt4.QtCore
    from QtCore import *  #required to import tweaks done in taurus.qt.QtCore
    from PyQt4.Qt import *
    from PyQt4.Qt import Qt
    
    import sip
    try:
        PYQT_QVARIANT_API_1 = sip.getapi('QVariant') == 1
    except AttributeError:
        # PyQt <v4.6
        PYQT_QVARIANT_API_1 = True
    
    if PYQT_QVARIANT_API_1:
        to_qvariant = __to_qvariant_1
        from_qvariant = __from_qvariant_1
    else:
        PyQt4.QtCore.QVariant = PyQt4.Qt.QVariant = QVariant = __QVariant_2
        to_qvariant = __to_qvariant_2
        from_qvariant = __from_qvariant_2
    
    try:
        PYQT_QSTRING_API_1 = sip.getapi('QString') == 1
    except AttributeError:
        # PyQt <v4.6
        PYQT_QSTRING_API_1 = True
    
    if not PYQT_QSTRING_API_1:
        PyQt4.QtCore.QString = PyQt4.Qt.QString = QString = __QString_2
        PyQt4.QtCore.QStringList = PyQt4.Qt.QStringList = QStringList = __QStringList_2
    
elif QT_API == QT_API_PYSIDE:
    #from PySide.Qt import *
    from QtCore import *
    from QtGui import *


    QVariant = __QVariant_2
    to_qvariant = __to_qvariant_2
    from_qvariant = __from_qvariant_2
    QString = __QString_2
    QStringList = __QStringList_2

