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

import math

import PyTango

from taurus.core.util.containers import CaselessDict

from sardana import State, DataAccess
from sardana.pool.controller import MotorController, CounterTimerController, \
    ZeroDController, \
    Type, Access, Description, DefaultValue

TangoAttribute = "TangoAttribute"
Formula = "Formula"

class ReadTangoAttributes(object):
    """ Generic class that has as many devices as the user wants.
    Each device has a tango attribute and a formula and the 'hardware' tango calls
    are optimized in the sense that only one call per tango device is issued.
    """
    axis_attributes = {
        TangoAttribute : { Type : str, Access : DataAccess.ReadWrite,
                           Description : 'Attribute to read (e.g. a/b/c/attr)' },
        Formula        : { Type : str, Access : DataAccess.ReadWrite,
                           DefaultValue : "VALUE",
                           Description  : 'The Formula to get the desired value.\n'
                                          'e.g. "math.sqrt(VALUE)"' },
    }

    def __init__(self):
        #: dict<int(axis), str(reason for being in pending)>
        self._pending = {}

        #: dict<str(dev name), tuple<DeviceProxy, list<str(attributes name)>>>
        self._devices = CaselessDict()

        #: dict<int(axis), seq<str<tango full attribute name>, str<attr name>, DeviceProxy>>
        self._axis_tango_attributes = {}

        #: dict<int(axis), str<formula>>
        self._axis_formulas = {}

    def add_device(self, axis):
        self._pending[axis] = "No tango attribute associated to this device yet"
        self._axis_formulas[axis] = self.axis_attribute[Formula][DefaultValue]

    def delete_device(self, axis):
        if axis in self._pending:
            del self._pending[axis]
        else:
            del self._axis_tango_attributes[axis]
            del self._axis_formulas[axis]

    def state_one(self, axis):
        pending_info = self._pending.get(axis)
        if pending_info is not None:
            return State.Fault, pending_info
        return State.On, 'Always ON, just reading tango attribute'

    def pre_read_all(self):
        self._devices_read = {}

    def pre_read_one(self, axis):
        attr_name, dev = self._axis_tango_attributes[axis][1:]
        dev_attrs = self._devices_read.get(dev)
        if dev_attrs is None:
            self._
            self._devices_read[dev] = dev_attrs = []
        dev_attrs.append(attr_name)

    def read_all(self):
        pass

    def read_one(self, axis):
        pass

    def get_extra_attribute_par(self, axis, name):
        if name == TangoAttribute:
            return self._axis_tango_attributes[axis][0]
        elif name == Formula:
            return self._axis_formulas[axis]

    def set_extra_attribute_par(self, axis, name, value):
        if name == TangoAttribute:
            value = value.lower()
            self._axis_tango_attributes[axis] = data = value, None, None
            try:
                dev_name, attr_name = value.rsplit("/", 1)
                data[1] = attr_name
            except:
                self._pending[axis] = "invalid device name " + value
                raise Exception(self._pending[axis])
            dev_info = self._devices.get(dev_name)
            if dev_info is None:
                try:
                    proxy = PyTango.DeviceProxy(dev_name)
                except PyTango.DevFailed, df:
                    if len(df):
                        self._pending[axis] = df[0].reason + ": " + df[0].desc
                    else:
                        self._pending[axis] = "Unknwon PyTango Error: " + str(df)
                    raise
                self._devices[dev_name] = dev_info = proxy, []
            data[2] = dev_info[0]
            dev_info[1].append(attr_name)

        elif name == Formula:
            self._axis_formulas[axis] = value

class TangoCounterTimerController(ReadTangoAttributes, CounterTimerController):
    """This controller offers as many channels as the user wants.
    Each channel has two _MUST_HAVE_ extra attributes:
    +) TangoAttribute - Tango attribute to retrieve the value of the counter
    +) Formula - Formula to evaluate using 'VALUE' as the tango attribute value
    As examples you could have:
    ch1.TangoExtraAttribute = 'my/tango/device/attribute1'
    ch1.Formula = '-1 * VALUE'
    ch2.TangoExtraAttribute = 'my/tango/device/attribute2'
    ch2.Formula = 'math.sqrt(VALUE)'
    ch3.TangoExtraAttribute = 'my_other/tango/device/attribute1'
    ch3.Formula = 'math.cos(VALUE)'
    """

    gender = ""
    model = ""
    organization = "Sardana team"

    MaxDevice = 1024

    def __init__(self, inst, props, *args, **kwargs):
        ReadTangoAttributes.__init__(self)
        CounterTimerController.__init__(self, inst, props, *args, **kwargs)

    def AddDevice(self, axis):
        self.add_device(axis)

    def DeleteDevice(self, axis):
        self.delete_device(axis)

    def StateOne(self, axis):
        return self.state_one(axis)

    def PreReadAll(self):
        self.pre_read_all()

    def PreReadOne(self, axis):
        self.pre_read_one(axis)

    def ReadAll(self):
        self.read_all()

    def ReadOne(self, axis):
        return self.read_one(axis)

    def GetExtraAttributePar(self, axis, name):
        return self.get_extra_attribute_par(axis, name)

    def SetExtraAttributePar(self, axis, name, value):
        self.set_extra_attribute_par(axis, name, value)

    def SendToCtrl(self, in_data):
        return ""

    def AbortOne(self, axis):
        pass

    def PreStartAllCT(self):
        pass

    def StartOneCT(self, axis):
        pass

    def StartAllCT(self):
        pass

    def LoadOne(self, axis, value):
        pass

