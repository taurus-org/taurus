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
comunications.py:
"""

from __future__ import print_function

from taurus.external.qt import QtCore, compat

import weakref

_DEBUG = False


def get_signal(obj, signalname):
    """Return signal from object and signal name."""
    if '(' not in signalname:
        return getattr(obj, signalname)
    name, dtype = signalname.strip(')').split('(')
    dtype = tuple(dtype.split(','))
    return getattr(obj, name)[dtype]


class DataModel(QtCore.QObject):
    '''
    An object containing one piece of data which is intended to be shared. The
    data will be identified by its UID (a unique identifier known to objects
    that intend to access the data)

    In general, you are not supposed to instantiate objects of this class
    directly. Instead, you should interact via the :class:`SharedDataManager`,
    which uses :meth:`SharedDataManager.__getDataModel` to ensure that the
    DataModels are singletons.
    '''

    dataChanged = QtCore.pyqtSignal(compat.PY_OBJECT)

    def __init__(self, parent, dataUID, defaultData=None):
        '''
        creator
        :param parent: (QObject) the object's parent
        :param dataUID: (str) a unique identifier for the Data Model
        '''
        QtCore.QObject.__init__(self, parent)
        self.__dataUID = dataUID
        self.__data = defaultData
        self.__isDataSet = False

        self.__readerSlots = []
        self.__writerSignals = []

    def __repr__(self):
        return '<DataModel object with dataUID="%s">' % self.dataUID()

    def dataUID(self):
        '''
        returns the data unique identifier

        :return: (str)
        '''
        return self.__dataUID

    def getData(self):
        '''
        Returns the data object.

        :return: (object) the data object
        '''
        return self.__data

    def setData(self, data):
        '''
        sets the data object and emits a "dataChanged" signal with the data as the parameter

        :param data: (object) the new value for the Model's data
        '''
        self.__data = data
        self.__isDataSet = True
        self.dataChanged.emit(self.__data)

    def connectReader(self, slot, readOnConnect=True):
        '''
        Registers the given slot method to receive notifications whenever the
        data is changed.

        :param slot: (callable) a method that will be called when the data changes.
                     This slot will be the receiver of a signal which has the
                     data as its first argument.
        :param readOnConnect: (bool) if True (default) the slot will be called
                              immediately with the current value of the data
                              if the data has been already initialized

        .. seealso:: :meth:`connectWriter`, :meth:`getData`
        '''
        self.dataChanged.connect(slot)

        if readOnConnect and self.__isDataSet:
            slot(self.__data)
        obj = getattr(slot, '__self__', slot)
        self.__readerSlots.append((weakref.ref(obj), slot.__name__))

    def connectWriter(self, writer, signalname):
        '''
        Registers the given writer object as a writer of the data. The writer is
        then expected to emit a `QtCore.SIGNAL(signalname)` with the new data as the
        first parameter.

        :param writer: (QObject) object that will change the data
        :param signalname: (str) the signal name that will notify changes
                           of the data

        .. seealso:: :meth:`connectReader`, :meth:`setData`
        '''
        try:
            get_signal(writer, signalname).connect(self.setData)
        except AttributeError:
            # support old-style signal
            self.connect(writer, QtCore.SIGNAL(signalname), self.setData)
        self.__writerSignals.append((weakref.ref(writer), signalname))

    def disconnectWriter(self, writer, signalname):
        '''unregister a writer from this data model

        :param writer: (QObject) object to unregister
        :param signalname: (str) the signal that was registered

        .. seealso:: :meth:`SharedDataManager.disconnectWriter`
        '''
        ok = get_signal(writer, signalname).disconnect(self.setData)
        self.__writerSignals.remove((weakref.ref(writer), signalname))

    def disconnectReader(self, slot):
        '''
        unregister a reader

        :param slot: (callable) the slot to which this was connected

        .. seealso:: :meth:`SharedDataManager.disconnectReader`, :meth:`getData`
        '''
        ok = self.dataChanged.disconnect(slot)
        self.__readerSlots.remove((weakref.ref(slot.__self__), slot.__name__))

    def isDataSet(self):
        '''Whether the data has been set at least once or if it is uninitialized

        :return: (bool) True if the data has been set. False it is uninitialized'''
        return self.__isDataSet

    def info(self):
        readers = ["%s::%s" % (repr(r()), s) for r, s in self.__readerSlots]
        writers = ["%s::%s" % (repr(r()), s) for r, s in self.__writerSignals]
        return "UID: %s\n\t Readers (%i):%s\n\t Writers (%i):%s\n" % (self.__dataUID, len(readers),
                                                                      readers, len(writers), writers)

    def readerCount(self):
        '''returns the number of currently registered readers of this model

        :return: (int)
        '''
        return len(self.__readerSlots)

    def writerCount(self):
        '''returns the number of currently registered writers of this model

        :return: (int)
        '''
        return len(self.__writerSignals)


class SharedDataManager(QtCore.QObject):
    '''
    A Factory of :class:`DataModel` objects. The :meth:`__getDataModel` method
    ensures that the created DataModels are singletons. DataModels are not kept
    alive unless there at least some Reader or Writer registered to it (or
    another object referencing them)
    '''

    def __init__(self, parent):
        QtCore.QObject.__init__(self, parent)
        self.__models = {}

    def __getDataModel(self, dataUID):
        '''
        Returns the :class:`DataModel` object for the given data UID (which is a singleton).
        If it does not previously exist, it creates one).

        .. note:: This is a private method. You are probably more interested
                  in using :meth:`connectReader` and :meth:`connectWriter`

        :param dataUID: (str) the unique identifier of the data

        :return: (DataModel)

        .. seealso:: :meth:`connectReader`,  :meth:`connectWriter`, :class:`DataModel`
        '''
        if dataUID not in self.__models:
            self.__models[dataUID] = DataModel(self, dataUID)
        return self.__models[dataUID]

    def getDataModelProxy(self, dataUID, callback=None):
        '''
        Returns a :class:`weakref.proxy` to a :class:`DataModel` object for the
        given data UID or None if the UID is not registered.

        .. note:: The underlying :class:`DataModel` object may cease to exist if
                  all its readers and writers are unregistered.

        :param dataUID: (str) the unique identifier of the data
        :param callback: (callable) same as in :class:`weakref.ref` callback parameter

        :return: (weakref.proxy or None)

        .. seealso:: :meth:`connectReader`,  :meth:`connectWriter`, :class:`DataModel`
        '''
        if dataUID not in self.__models:
            return None
        dm = self.__getDataModel(dataUID)
        return weakref.proxy(dm, callback)

    def connectReader(self, dataUID, slot, readOnConnect=True):
        '''
        Registers the given slot method to receive notifications whenever the
        data identified by dataUID is changed.

        Note that it returns the :meth:`DataModel.getData` method for the given data
        UID, which can be used for reading the data at any moment.

        :param dataUID: (str) the unique identifier of the data
        :param slot: (callable) a method that will be called when the data changes
                     this slot will be the receiver of a signal which has the
                     data as its first argument.
        :param readOnConnect: (bool) if True (default) the slot will be called
                              immediately with the current value of the data
                              if the data has been already initialized

        :return: (callable) a callable that can be used for reading the data

        .. seealso:: :meth:`connectWriter`, :meth:`__getDataModel`
        '''
        m = self.__getDataModel(dataUID)
        m.connectReader(slot, readOnConnect=True)
        if _DEBUG:
            # @todo: comment this line out. ONLY FOR DEBUGGING
            m.connectReader(self.debugReader)
        return m.getData

    def connectWriter(self, dataUID, writer, signalname):
        '''
        Registers the given writer object as a changer of the shared data
        identified by dataUID. The writer is then expected to emit a
        `QtCore.SIGNAL(signalname)` with the new data as the first parameter

        Note that it returns the :meth:`DataModel.setData` method for the given data
        UID, which can be used for changing the data at any moment.

        :param dataUID: (str) the unique identifier of the data
        :param writer: (QObject) object that will change the data
        :param signalname: (str) the signal name that will notify changes
                           of the data

        :return: (callable) a callable that can be used for setting the data.
                 When using it, one parameter has to be passed containing the
                 new data

        .. seealso:: :meth:`connectWriter`, :meth:`__getDataModel`
        '''
        m = self.__getDataModel(dataUID)
        m.connectWriter(writer, signalname)
        if _DEBUG:
            # @todo: comment this line out. ONLY FOR DEBUGGING
            m.connectReader(self.debugReader)
        return m.setData

    def disconnectWriter(self, dataUID, writer, signalname):
        '''Unregister the given object as writer of the shared data

        :param dataUID: (str) the unique identifier of the data
        :param writer: (QObject) object to unregister
        :param signalname: (str) the signal that was registered

        .. seealso:: :meth:`DataModel.disconnectWriter`
        '''
        m = self.__getDataModel(dataUID)
        m.disconnectWriter(writer, signalname)
        if m.readerCount() < 1 and m.writerCount() < 1:
            self.__models.pop(dataUID)

    def disconnectReader(self, dataUID, slot):
        '''Unregister the given method as data receiver

        :param dataUID: (str) the unique identifier of the data
        :param slot: (str) the slot that was registered

        .. seealso:: :meth:`DataModel.disconnectReader`
        '''
        m = self.__getDataModel(dataUID)
        m.disconnectReader(slot)
        if m.readerCount() < 1 and m.writerCount() < 1:
            self.__models.pop(dataUID)

    def activeDataUIDs(self):
        '''
        Returns a list of currently shared data. Note that this list only
        reflects the situation at the moment of calling this method: a given
        DataModel may die at any moment if there are no references to it.

        :returns: (list<str>) UIDs of currently shared data.
        '''
        return list(self.__models.keys())

    def debugReader(self, data):
        '''
        A slot which you can connect as a reader for debugging. It will print info to the stdout
        '''
        print("SharedDataManager: \n\tSender=: %s\n\tData=%s" % (self.sender(), repr(data)))

    def info(self):
        s = ""
        for uid, m in sorted(self.__models.items()):
            s += m.info() + '\n'
        return s
