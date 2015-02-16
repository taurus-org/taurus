#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.sardana-controls.org/
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""Device pool extension for taurus Qt"""

__all__ = ["QPool", "QMeasurementGroup",
           "registerExtensions"]

import json

from taurus.external.qt import Qt

from taurus.core.taurusbasetypes import TaurusEventType
from taurus.core.tango import TangoDevice

CHANGE_EVTS = TaurusEventType.Change, TaurusEventType.Periodic


class QPool(Qt.QObject, TangoDevice):

    def __init__(self, name, qt_parent=None, **kw):
        self.call__init__wo_kw(Qt.QObject, qt_parent)
        self.call__init__(TangoDevice, name, **kw)


class QMeasurementGroup(Qt.QObject, TangoDevice):

    def __init__(self, name, qt_parent=None, **kw):
        self.call__init__wo_kw(Qt.QObject, qt_parent)
        self.call__init__(TangoDevice, name, **kw)

        self._config = None
        configuration = self.getAttribute("Configuration")
        configuration.addListener(self._configurationChanged)

    def __getattr__(self, name):
        try:
            return Qt.QObject.__getattr__(self, name)
        except AttributeError:
            return TangoDevice.__getattr__(self, name)

    def _configurationChanged(self, s, t, v):
        if t == TaurusEventType.Config:
            return
        if TaurusEventType.Error:
            self._config = None
        else:
            self._config = json.loads(v.value)
        self.emit(Qt.SIGNAL("configurationChanged"))

    def getConfiguration(self, cache=True):
        if self._config is None or not cache:
            try:
                v = self.read_attribute("configuration")
                self._config = json.loads(v.value)
            except:
                self._config = None
        return self._config

    def setConfiguration(self, config):
        self.write_attribute("configuration", json.dumps(config))


def registerExtensions():
    """Registers the pool extensions in the :class:`taurus.core.tango.TangoFactory`"""
    import taurus
    #import sardana.taurus.core.tango.sardana.pool
    #sardana.taurus.core.tango.sardana.pool.registerExtensions()
    factory = taurus.Factory()
    #factory.registerDeviceClass('Pool', QPool)
    factory.registerDeviceClass('MeasurementGroup', QMeasurementGroup)
