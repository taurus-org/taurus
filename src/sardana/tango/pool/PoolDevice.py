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

"""Generic Tango Pool Device base classes"""

__all__ = ["PoolDevice", "PoolDeviceClass",
           "PoolElementDevice", "PoolElementDeviceClass",
           "PoolGroupDevice", "PoolGroupDeviceClass"]

__docformat__ = 'restructuredtext'

import time

from PyTango import Util, DevVoid, DevLong64, DevBoolean, DevString, \
    DevVarStringArray, DispLevel, DevState, SCALAR, SPECTRUM, \
    IMAGE, READ_WRITE, READ, AttrData, CmdArgType, DevFailed, seqStr_2_obj

from taurus.core.util.containers import CaselessDict

from sardana import InvalidId, InvalidAxis, ElementType
from sardana.pool.poolmetacontroller import DataInfo
from sardana.tango.core.SardanaDevice import SardanaDevice, SardanaDeviceClass
from sardana.tango.core.util import GenericScalarAttr, GenericSpectrumAttr, \
    GenericImageAttr, to_tango_attr_info


class PoolDevice(SardanaDevice):
    """Base Tango Pool device class"""

    #: list of extreme error states
    ExtremeErrorStates = DevState.FAULT, DevState.UNKNOWN

    #: list of busy states
    BusyStates = DevState.MOVING, DevState.RUNNING

    #: Maximum number of retries in a busy state
    BusyRetries = 3

    def __init__(self, dclass, name):
        """Constructor"""
        SardanaDevice.__init__(self, dclass, name)

    def init(self, name):
        """initialize the device once in the object lifetime. Override when
        necessary but **always** call the method from your super class
        
        :param str name: device name"""
        SardanaDevice.init(self, name)
        util = Util.instance()
        self._pool_device = util.get_device_list_by_class("Pool")[0]
        self._element = None

    @property
    def pool_device(self):
        """The tango pool device"""
        return self._pool_device

    @property
    def pool(self):
        """The sardana pool object"""
        return self.pool_device.pool

    def get_element(self):
        """Returns the underlying pool element object
        
        :return: the underlying pool element object
        :rtype: :class:`~sardana.pool.poolelement.PoolElement`"""
        return self._element

    def set_element(self, element):
        """Associates this device with the sardana element
        
        :param element: the sardana element
        :type element: :class:`~sardana.pool.poolelement.PoolElement`"""
        self._element = element

    element = property(get_element, set_element, doc="The underlying sardana element")

    def init_device(self):
        """Initialize the device. Called during startup after :meth:`init` and
        every time the tango ``Init`` command is executed.
        Override when necessary but **always** call the method from your super
        class"""
        SardanaDevice.init_device(self)

    def delete_device(self):
        """Clean the device. Called during shutdown and every time the tango
        ``Init`` command is executed.
        Override when necessary but **always** call the method from your super
        class"""
        SardanaDevice.delete_device(self)

    def Abort(self):
        """The tango abort command. Aborts the active operation"""
        self.element.abort()
        try:
            self.element.get_state(cache=False, propagate=2)
        except:
            self.warning("Abort: failed to read state")

    def is_Abort_allowed(self):
        """Returns True if it is allowed to execute the tango abort command
        
        :return: True if it is allowed to execute the tango abort command or
                 False otherwise
        :rtype: bool"""
        return self.get_state() != DevState.UNKNOWN

    def Stop(self):
        """The tango stop command. Stops the active operation"""
        self.element.stop()
        try:
            self.element.get_state(cache=False, propagate=2)
        except:
            self.info("Stop: failed to read state")

    def is_Stop_allowed(self):
        """Returns True if it is allowed to execute the tango stop command
        
        :return: True if it is allowed to execute the tango stop command or
                 False otherwise
        :rtype: bool"""
        return self.get_state() != DevState.UNKNOWN

    def _is_allowed(self, req_type):
        """Generic is_allowed"""
#        state = self.get_state()
#        if state in self.ExtremeErrorStates:
#            return False
#        if req_type == AttReqType.WRITE_REQ:
#            if state in self.BusyStates:
#                return False
        return True

    def get_dynamic_attributes(self):
        """Returns the standard dynamic and fully dynamic attributes for this
        device. The return is a tuple of two dictionaries:
        
        - standard attributes: caseless dictionary with key being the attribute
          name and value is a tuple of attribute name(str), tango information,
          attribute information
        - dynamic attributes: caseless dictionary with key being the attribute
          name and value is a tuple of attribute name(str), tango information,
          attribute information
        
        **tango information**
            seq< :class:`~PyTango.CmdArgType`, :class:`~PyTango.AttrDataFormat`, :class:`~PyTango.AttrWriteType` >
        
        **attribute information**
            attribute information as returned by the sardana controller
        
        :return: the standard dynamic and fully dynamic attributes
        :rtype: seq< :class:`~taurus.core.util.CaselessDict`, :class:`~taurus.core.util.CaselessDict`\>
        """
        return CaselessDict(), CaselessDict()

    def initialize_dynamic_attributes(self):
        """Initializes this device dynamic attributes"""
        self._attributes = attrs = CaselessDict()

        attr_data = self.get_dynamic_attributes()

        std_attrs, dyn_attrs = attr_data
        self.remove_unwanted_dynamic_attributes(std_attrs, dyn_attrs)

        if std_attrs is not None:
            read = self.__class__._read_DynamicAttribute
            write = self.__class__._write_DynamicAttribute
            is_allowed = self.__class__._is_DynamicAttribute_allowed
            for attr_name, data_info in std_attrs.items():
                attr_name, data_info, attr_info = data_info
                attr = self.add_standard_attribute(attr_name, data_info,
                                                   attr_info, read,
                                                   write, is_allowed)
                attrs[attr.get_name()] = None

        if dyn_attrs is not None:
            read = self.__class__._read_DynamicAttribute
            write = self.__class__._write_DynamicAttribute
            is_allowed = self.__class__._is_DynamicAttribute_allowed
            for attr_name, data_info in dyn_attrs.items():
                attr_name, data_info, attr_info = data_info
                attr = self.add_dynamic_attribute(attr_name, data_info,
                                                  attr_info, read,
                                                  write, is_allowed)
                attrs[attr.get_name()] = None
        return attrs

    def remove_unwanted_dynamic_attributes(self, new_std_attrs, new_dyn_attrs):
        """Removes unwanted dynamic attributes from previous device creation"""

        dev_class = self.get_device_class()
        multi_attr = self.get_device_attr()
        multi_class_attr = dev_class.get_class_attr()
        static_attr_names = map(str.lower, dev_class.attr_list.keys())
        static_attr_names.extend(('state', 'status'))

        new_attrs = CaselessDict(new_std_attrs)
        new_attrs.update(new_dyn_attrs)

        device_attr_names = []
        for i in range(multi_attr.get_attr_nb()):
            device_attr_names.append(multi_attr.get_attr_by_ind(i).get_name())

        for attr_name in device_attr_names:
            attr_name_lower = attr_name.lower()
            if attr_name_lower in static_attr_names:
                continue
            try:
                self.remove_attribute(attr_name)
            except:
                self.warning("Error removing dynamic attribute %s",
                             attr_name_lower)
                self.debug("Details:", exc_info=1)

        klass_attr_names = []
        klass_attrs = multi_class_attr.get_attr_list()
        for ind in range(len(klass_attrs)):
            klass_attr_names.append(klass_attrs[ind].get_name())

        for attr_name in klass_attr_names:
            attr_name_lower = attr_name.lower()
            if attr_name_lower in static_attr_names:
                continue
            # if new dynamic attribute is in class attribute then delete it
            # from class attribute to be later on added again (eventually
            # with diffent data type or data format)
            if attr_name_lower in new_attrs:
                try:
                    attr = multi_class_attr.get_attr(attr_name)

                    old_type = CmdArgType(attr.get_type())
                    old_format = attr.get_format()
                    old_access = attr.get_writable()

                    new_attr = new_attrs[attr_name]
                    new_type, new_format, new_access = new_attr[1][0][:3]
                    differ = new_type != old_type or \
                             new_format != old_format or \
                             new_access != old_access
                    if differ:
                        self.info("Replacing dynamic attribute %s", attr_name)
                        self.debug("old type: %s, new type: %s",
                                   old_type, new_type)
                        self.debug("old format: %s, new format: %s",
                                   old_format, new_format)
                        self.debug("old access: %s, new access: %s",
                                   old_access, new_access)
                        multi_class_attr.remove_attr(attr.get_name(),
                                                     attr.get_cl_name())
                except:
                    self.warning("Error removing dynamic attribute %s from "\
                                 " device class", attr_name)
                    self.debug("Details:", exc_info=1)

    def add_dynamic_attribute(self, attr_name, data_info, attr_info, read,
                              write, is_allowed):
        """Adds a single dynamic attribute
        
        :param str attr_name: the attribute name
        :param data_info: tango attribute information
        :type data_info: seq< :class:`~PyTango.CmdArgType`, :class:`~PyTango.AttrDataFormat`, :class:`~PyTango.AttrWriteType` >
        :param attr_info: attribute information
        :param read: read method for the attribute
        :param write: write method for the attribute
        :param is_allowed: is allowed method"""
        tg_type, tg_format, tg_access = data_info[0]

        if tg_access == READ:
            write = None
        if tg_format == SCALAR:
            attr = GenericScalarAttr(attr_name, tg_type, tg_access)
        if tg_format == SPECTRUM:
            dim_x = attr_info.maxdimsize[0]
            attr = GenericSpectrumAttr(attr_name, tg_type, tg_access,
                                       dim_x=dim_x)
        elif tg_format == IMAGE:
            dim_x, dim_y = attr_info.maxdimsize
            attr = GenericImageAttr(attr_name, tg_type, tg_access,
                                    dim_x=dim_x, dim_y=dim_y)

        if tg_access == READ_WRITE and tg_format == SCALAR:
            memorized = attr_info.memorized.lower()
            if memorized == 'true':
                attr.set_memorized()
                attr.set_memorized_init(True)
            elif memorized == 'true_without_hard_applied':
                attr.set_memorized()
                attr.set_memorized_init(False)
        attr.set_disp_level(DispLevel.EXPERT)
        return self.add_attribute(attr, read, write, is_allowed)

    def add_standard_attribute(self, attr_name, data_info, attr_info, read,
                               write, is_allowed):
        """Adds a single standard dynamic attribute
        
        :param str attr_name: the attribute name
        :param data_info: tango attribute information
        :type data_info: seq< :class:`~PyTango.CmdArgType`, :class:`~PyTango.AttrDataFormat`, :class:`~PyTango.AttrWriteType` >
        :param attr_info: attribute information
        :param read: read method for the attribute
        :param write: write method for the attribute
        :param is_allowed: is allowed method"""
        dev_class = self.get_device_class()
        attr_data = AttrData(attr_name, dev_class.get_name(), data_info)
        attr = self.add_attribute(attr_data, read, write, is_allowed)
        return attr

    def read_DynamicAttribute(self, attr):
        """Generic read dynamic attribute.
        Default implementation raises :exc:`NotImplementedError`
        
        :param attr: attribute to be read
        :type attr: :class:`~PyTango.Attribute`
        
        :raises: :exc:`NotImplementedError`"""
        raise NotImplementedError

    def write_DynamicAttribute(self, attr):
        """Generic write dynamic attribute.
        Default implementation raises :exc:`NotImplementedError`
        
        :param attr: attribute to be written
        :type attr: :class:`~PyTango.Attribute`
        
        :raises: :exc:`NotImplementedError`"""
        raise NotImplementedError

    def is_DynamicAttribute_allowed(self, req_type):
        """Generic is dynamic attribute allowed.
        Default implementation calls :meth:`_is_allowed`
        
        :param req_type: request type
        :type attr: :class:`~PyTango.AttrRequestType`"""
        return self._is_allowed(req_type)

    def _read_DynamicAttribute(self, attr):
        """Generic internal read dynamic attribute.
        Checks if this object has a 'read_'+<attr_name> method and calls it.
        If not calls :meth:`read_DynamicAttribute`.
        
        :param attr: attribute to be read
        :type attr: :class:`~PyTango.Attribute`"""
        name = attr.get_name()

        read_name = "read_" + name
        if hasattr(self, read_name):
            read = getattr(self, read_name)
            return read(attr)

        return self.read_DynamicAttribute(attr)

    def _write_DynamicAttribute(self, attr):
        """Generic internal write dynamic attribute.
        Checks if this object has a 'write_'+<attr_name> method and calls it.
        If not calls :meth:`write_DynamicAttribute`.
        
        :param attr: attribute to be written
        :type attr: :class:`~PyTango.Attribute`"""
        name = attr.get_name()
        write_name = "write_" + name
        if hasattr(self, write_name):
            write = getattr(self, write_name)
            return write(attr)
        return self.write_DynamicAttribute(attr)

    def _is_DynamicAttribute_allowed(self, req_type):
        """Generic is dynamic attribute allowed.
        Default implementation calls :meth:`is_DynamicAttribute_allowed`
        
        :param req_type: request type
        :type attr: :class:`~PyTango.AttrRequestType`"""
        return self.is_DynamicAttribute_allowed(req_type)

    def dev_state(self):
        """Calculates and returns the device state. Called by Tango on a read
        state request.
        
        :return: the device state
        :rtype: :class:`~PyTango.DevState`"""
        element = self.element
        try:
            use_cache = element.is_in_operation() and not self.Force_HW_Read
            ctrl_state = element.get_state(cache=use_cache, propagate=0)
            state = self.calculate_tango_state(ctrl_state)
            return state
        except:
            self.error("Exception trying to return state")
            self.debug("Details:", exc_info=1)
            return DevState.FAULT

    def dev_status(self):
        """Calculates and returns the device status. Called by Tango on a read
        status request.
        
        :return: the device status
        :rtype: str"""
        element = self.element
        try:
            use_cache = element.is_in_operation() and not self.Force_HW_Read
            ctrl_status = self.element.get_status(cache=use_cache, propagate=0)
            status = self.calculate_tango_status(ctrl_status)
            return status
        except Exception, e:
            msg = "Exception trying to return status: %s" % str(e)
            self.error(msg)
            self.debug("Details:", exc_info=1)
            return msg

    def wait_for_operation(self):
        """Waits for an operation to finish. It uses the maxumum number of
        retries. Sleeps 0.01s between retries.
        
        :raises: :exc:`Exception` in case of a timeout"""
        element, n = self.element, self.BusyRetries
        while element.is_in_operation():
            if n == 0:
                raise Exception("Wait for operation timedout")
            time.sleep(0.01)
            self.warning("waited for operation")
            n = n - 1

    def Restore(self):
        """Restore tango command. Restores the attributes to their former glory.
        This applies to memorized writable attributes which have a set point
        stored in the database"""
        restore_attributes, db_values = self.get_restore_data()
        multi_attribute = self.get_device_attr()

        for attr_name in restore_attributes:
            props = db_values[attr_name]
            if props is None or not "__value" in props:
                continue
            attribute = multi_attribute.get_w_attr_by_name(attr_name)
            write_meth_name = "write_" + attr_name
            write_meth = getattr(self, write_meth_name, None)
            if write_meth is None:
                self.warning("Could not recover %s: %s does not exist",
                             attr_name, write_meth_name)
                continue
            self.restore_attribute(attribute, write_meth, props['__value'])

    def get_restore_data(self):
        restore_attributes = self.get_attributes_to_restore()
        db = Util.instance().get_database()
        db_values = db.get_device_attribute_property(self.get_name(),
                                                     restore_attributes)
        return restore_attributes, db_values

    def get_attributes_to_restore(self):
        std_attrs, dyn_attrs = self.get_dynamic_attributes()
        multi_attribute = self.get_device_attr()

        restore = []
        for attr_name in std_attrs:
            try:
                attribute = multi_attribute.get_w_attr_by_name(attr_name)
            except DevFailed:
                continue
            restore.append(attribute.get_name())
        for attr_name in dyn_attrs:
            try:
                attribute = multi_attribute.get_w_attr_by_name(attr_name)
            except DevFailed:
                continue
            restore.append(attribute.get_name())
        return restore

    def _get_attribute_value_from_db_value(self, attribute, db_value):
        value = seqStr_2_obj(db_value, attribute.get_data_type(),
                             attribute.get_data_format())
        return value

    def restore_attribute(self, attribute, write_meth, db_value):
        value = self._get_attribute_value_from_db_value(attribute, db_value)
        attr_name = attribute.get_name()
        try:
            attribute.set_write_value(value)
            self.info("Restoring %s", attr_name)
            write_meth(attribute)
        except:
            self.warning("Could not recover %s: Error in write", attr_name)
            self.debug("Details:", exc_info=1)



class PoolDeviceClass(SardanaDeviceClass):
    """Base Tango Pool Device Class class"""

    #:
    #: Sardana device class properties definition
    #:
    #: .. seealso:: :ref:`server`
    #:
    class_property_list = SardanaDeviceClass.class_property_list

    #:
    #: Sardana device properties definition
    #:
    #: .. seealso:: :ref:`server`
    #:
    device_property_list = {
        'Id'            : [DevLong64, "Internal ID", InvalidId ],
        'Force_HW_Read' : [DevBoolean, "Force a hardware read of value even "
                                       "when in operation (motion/acquisition",
                           False],
    }
    device_property_list.update(SardanaDeviceClass.device_property_list)

    #:
    #: Sardana device command definition
    #:
    #: .. seealso:: :ref:`server`
    #:
    cmd_list = {
        'Stop'    : [ [DevVoid, ""], [DevVoid, ""] ],
        'Abort'   : [ [DevVoid, ""], [DevVoid, ""] ],
        'Restore' : [ [DevVoid, ""], [DevVoid, ""] ],
    }
    cmd_list.update(SardanaDeviceClass.cmd_list)

    #:
    #: Sardana device attribute definition
    #:
    #: .. seealso:: :ref:`server`
    #:
    attr_list = {
    }
    attr_list.update(SardanaDeviceClass.attr_list)

    standard_attr_list = {}

    def _get_class_properties(self):
        ret = SardanaDeviceClass._get_class_properties(self)
        ret['Description'] = "Generic Pool device class"
        ret['InheritedFrom'].insert(0, 'SardanaDevice')
        return ret


class PoolElementDevice(PoolDevice):
    """Base Tango Pool Element Device class"""

    def init_device(self):
        """Initialize the device. Called during startup after :meth:`init` and
        every time the tango ``Init`` command is executed.
        Override when necessary but **always** call the method from your super
        class"""
        PoolDevice.init_device(self)

        self.instrument = None
        self.ctrl = None
        try:
            instrument_id = int(self.Instrument_id)
            if instrument_id != InvalidId:
                instrument = self.pool.get_element_by_id(instrument_id)
                self.instrument = instrument
        except ValueError:
            pass
        try:
            ctrl_id = int(self.Ctrl_id)
            if ctrl_id != InvalidId:
                ctrl = self.pool.get_element_by_id(ctrl_id)
                self.ctrl = ctrl
        except ValueError:
            pass

    def read_Instrument(self, attr):
        """Read the value of the ``Instrument`` tango attribute.
        Returns the instrument full name or empty string if this element doesn't
        belong to any instrument
        
        :param attr: tango instrument attribute
        :type attr: :class:`~PyTango.Attribute`"""
        instrument = self.element.instrument
        if instrument is None:
            attr.set_value('')
        else:
            attr.set_value(instrument.full_name)

    def write_Instrument(self, attr):
        """Write the value of the ``Instrument`` tango attribute.
        Sets a new instrument full name or empty string if this element doesn't
        belong to any instrument.
        The instrument **must** have been previously created.
        
        :param attr: tango instrument attribute
        :type attr: :class:`~PyTango.Attribute`"""
        name = attr.get_write_value()
        instrument = None
        if name:
            instrument = self.pool.get_element(full_name=name)
            if instrument.get_type() != ElementType.Instrument:
                raise Exception("%s is not an instrument" % name)
        self.element.instrument = instrument
        db = Util.instance().get_database()
        db.put_device_property(self.get_name(), { "Instrument_id" : instrument.id })

    def get_dynamic_attributes(self):
        """Override of :class:`PoolDevice.get_dynamic_attributes`.
        Returns the standard dynamic and fully dynamic attributes for this
        device. The return is a tuple of two dictionaries:
        
        - standard attributes: caseless dictionary with key being the attribute
          name and value is a tuple of attribute name(str), tango information,
          attribute information
        - dynamic attributes: caseless dictionary with key being the attribute
          name and value is a tuple of attribute name(str), tango information,
          attribute information
        
        **tango information**
            seq< :class:`~PyTango.CmdArgType`, :class:`~PyTango.AttrDataFormat`, :class:`~PyTango.AttrWriteType` >
        
        **attribute information**
            attribute information as returned by the sardana controller
        
        :return: the standard dynamic and fully dynamic attributes
        :rtype: seq< :class:`~taurus.core.util.CaselessDict`, :class:`~taurus.core.util.CaselessDict`\>
        """

        if hasattr(self, "_dynamic_attributes_cache"):
            return self._standard_attributes_cache, self._dynamic_attributes_cache
        ctrl = self.ctrl
        if ctrl is None:
            self.warning("no controller: dynamic attributes NOT created")
            return PoolDevice.get_dynamic_attributes(self)
        if not ctrl.is_online():
            self.warning("controller offline: dynamic attributes NOT created")
            return PoolDevice.get_dynamic_attributes(self)

        self._dynamic_attributes_cache = dyn_attrs = CaselessDict()
        self._standard_attributes_cache = std_attrs = CaselessDict()
        dev_class = self.get_device_class()
        axis_attrs = ctrl.get_axis_attributes(self.element.axis)

        std_attrs_lower = [ attr.lower() for attr in dev_class.standard_attr_list ]
        for attr_name, attr_info in axis_attrs.items():
            attr_name_lower = attr_name.lower()
            if attr_name_lower in std_attrs_lower:
                data_info = DataInfo.toDataInfo(attr_name, attr_info)
                tg_info = dev_class.standard_attr_list[attr_name]
                std_attrs[attr_name] = attr_name, tg_info, data_info
            else:
                data_info = DataInfo.toDataInfo(attr_name, attr_info)
                name, tg_info = to_tango_attr_info(attr_name, data_info)
                dyn_attrs[attr_name] = name, tg_info, data_info
        return std_attrs, dyn_attrs

    def read_DynamicAttribute(self, attr):
        """Read a generic dynamic attribute. Calls the controller of this
        element to get the dynamic attribute value
        
        :param attr: tango attribute
        :type attr: :class:`~PyTango.Attribute`"""
        name = attr.get_name()
        ctrl = self.ctrl
        if ctrl is None:
            raise Exception("Cannot read %s. Controller not build!" % name)
        v = ctrl.get_axis_attr(self.element.axis, name)
        if v is None:
            raise TypeError("Cannot read %s. Controller returns None" % (name,))
        attr.set_value(v)

    def write_DynamicAttribute(self, attr):
        """Write a generic dynamic attribute. Calls the controller of this
        element to get the dynamic attribute value
        
        :param attr: tango attribute
        :type attr: :class:`~PyTango.Attribute`"""
        name = attr.get_name()
        value = attr.get_write_value()
        self.debug("writing dynamic attribute %s with value %s", name, value)
        ctrl = self.ctrl
        if ctrl is None:
            raise Exception("Cannot write %s. Controller not build!" % name)
        ctrl.set_axis_attr(self.element.axis, name, value)

    def read_SimulationMode(self, attr):
        """Read the current simulation mode. 
        
        :param attr: tango attribute
        :type attr: :class:`~PyTango.Attribute`"""
        attr.set_value(self.element.simulation_mode)

    def write_SimulationMode(self, attr):
        """Sets the simulation mode. 
        
        :param attr: tango attribute
        :type attr: :class:`~PyTango.Attribute`"""
        self.element.simulation_mode = attr.get_write_value()


class PoolElementDeviceClass(PoolDeviceClass):
    """Base Tango Pool Element Device Class class"""

    #:
    #: Sardana device properties definition
    #:
    #: .. seealso:: :ref:`server`
    #:
    device_property_list = {
        "Axis"          : [ DevLong64, "Axis in the controller", [ InvalidAxis ] ],
        "Ctrl_id"       : [ DevLong64, "Controller ID", [ InvalidId ] ],
        "Instrument_id" : [ DevLong64, "Controller ID", [ InvalidId ] ],
    }
    device_property_list.update(PoolDeviceClass.device_property_list)

    #:
    #: Sardana device attribute definition
    #:
    #: .. seealso:: :ref:`server`
    #:
    attr_list = {
        'Instrument' :    [ [DevString, SCALAR, READ_WRITE],
                          { 'label'         : "Instrument",
                            'Display level' : DispLevel.EXPERT } ],
        'SimulationMode': [ [DevBoolean, SCALAR, READ_WRITE],
                          { 'label'         : "Simulation mode" } ],
    }
    attr_list.update(PoolDeviceClass.attr_list)

    cmd_list = {
    }
    cmd_list.update(PoolDeviceClass.cmd_list)

    def get_standard_attr_info(self, attr):
        """Returns information about the standard attribute
        
        :param str attr: attribute name
        :return: a sequence of tango data_type, data format"""
        return self.standard_attr_list[attr]

    def _get_class_properties(self):
        ret = PoolDeviceClass._get_class_properties(self)
        ret['Description'] = "Generic Pool element device class"
        ret['InheritedFrom'].insert(0, 'PoolDevice')
        return ret


class PoolGroupDevice(PoolDevice):
    """Base Tango Pool Group Device class"""

    def read_ElementList(self, attr):
        """Read the element list. 
        
        :param attr: tango attribute
        :type attr: :class:`~PyTango.Attribute`"""
        attr.set_value(self.get_element_names())

    def get_element_names(self):
        """Returns the list of element names. 
        
        :return: a list of attribute names"""
        elements = self.element.get_user_elements()
        return [ element.name for element in elements ]

    def elements_changed(self, evt_src, evt_type, evt_value):
        """Callback for when the elements of this group changed"""
        self.push_change_event("ElementList", self.get_element_names())


class PoolGroupDeviceClass(PoolDeviceClass):
    """Base Tango Pool Group Device Class class"""

    #:
    #: Sardana device properties definition
    #:
    #: .. seealso:: :ref:`server`
    #:
    device_property_list = {
        "Elements" :    [ DevVarStringArray, "elements in the group", [ ] ],
    }
    device_property_list.update(PoolDeviceClass.device_property_list)

    #:
    #: Sardana device command definition
    #:
    #: .. seealso:: :ref:`server`
    #:
    cmd_list = {
    }
    cmd_list.update(PoolDeviceClass.cmd_list)

    #:
    #: Sardana device attribute definition
    #:
    #: .. seealso:: :ref:`server`
    #:
    attr_list = {
        'ElementList'  : [ [ DevString, SPECTRUM, READ, 4096] ],
    }
    attr_list.update(PoolDeviceClass.attr_list)

    def _get_class_properties(self):
        ret = PoolDeviceClass._get_class_properties(self)
        ret['Description'] = "Generic Pool group device class"
        ret['InheritedFrom'].insert(0, 'PoolDevice')
        return ret
