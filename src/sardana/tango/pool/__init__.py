#!/usr/bin/env python
from sardana.pool.poolextension import ControllerStateTranslator

##############################################################################
##
## This file is part of Sardana
##
## http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
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

""" """

__docformat__ = 'restructuredtext'

def prepare_pool(util):

    import PyTango
    from sardana.pool.poolextension import ControllerValueTranslator, \
        register_controller_value_translator, \
        ControllerStateTranslator, register_controller_state_translator, \
        CannotTranslateException
    from sardana.tango.core.util import from_deviceattribute
    
    class TangoControllerValueTranslator(ControllerValueTranslator):
        
        def translate(self, value):
            if not isinstance(value, PyTango.DeviceAttribute):
                return super(TangoControllerValueTranslator, self).translate(value)
            ret = from_deviceattribute(value)
            return ret
    
    register_controller_value_translator(TangoControllerValueTranslator)
    
    class TangoControllerStateTranslator(ControllerStateTranslator):
        
        def translate(self, value):
            if not isinstance(value, PyTango.DeviceAttribute):
                return super(TangoControllerValueTranslator, self).translate(value)
            if value.type != PyTango.DevState:
                raise CannotTranslateException("Expected DevState got %s" % value.type)
            ret = from_deviceattribute(value)
            return ret

    register_controller_state_translator(TangoControllerStateTranslator)

    from .Controller import ControllerClass, Controller
    from .Motor import MotorClass, Motor
    from .PseudoMotor import PseudoMotorClass, PseudoMotor
    from .MotorGroup import MotorGroupClass, MotorGroup
    from .CTExpChannel import CTExpChannelClass, CTExpChannel
    from .ZeroDExpChannel import ZeroDExpChannelClass, ZeroDExpChannel
    from .OneDExpChannel import OneDExpChannelClass, OneDExpChannel
    from .TwoDExpChannel import TwoDExpChannelClass, TwoDExpChannel
    from .PseudoCounter import PseudoCounterClass, PseudoCounter
    from .MeasurementGroup import MeasurementGroupClass, MeasurementGroup
    from .IORegister import IORegisterClass, IORegister
    from .Pool import PoolClass, Pool

    util.add_class(PoolClass, Pool)
    util.add_class(ControllerClass, Controller)
    util.add_class(MotorClass, Motor)
    util.add_class(IORegisterClass, IORegister)
    util.add_class(CTExpChannelClass, CTExpChannel)
    util.add_class(ZeroDExpChannelClass, ZeroDExpChannel)
    util.add_class(OneDExpChannelClass, OneDExpChannel)
    util.add_class(TwoDExpChannelClass, TwoDExpChannel)
    util.add_class(PseudoMotorClass, PseudoMotor)
    util.add_class(PseudoCounterClass, PseudoCounter)
    util.add_class(MotorGroupClass, MotorGroup)
    util.add_class(MeasurementGroupClass, MeasurementGroup)
    
def main_pool(args=None, start_time=None, mode=None):
    import sardana.tango.core.util
    return sardana.tango.core.util.run(prepare_pool, args=args,
                                       start_time=start_time, mode=mode)

run = main_pool
