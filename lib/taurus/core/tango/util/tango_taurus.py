# -*- coding: utf-8 -*-

##############################################################################
##
# This file is part of Taurus, a Tango User Interface Library
##
# http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
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
##############################################################################

'''Utility functions to convert between tango and Taurus types'''

import PyTango

from taurus.core.units import Quantity, UR
from pint import UndefinedUnitError
from taurus.core.taurusbasetypes import (AttrQuality, DisplayLevel,
                                         TaurusAttrValue, DataType, DataFormat)


__NO_STR_VALUE = PyTango.constants.AlrmValueNotSpec, PyTango.constants.StatusNotSet

FROM_TANGO_TO_TAURUS_DFORMAT = {PyTango.AttrDataFormat.SCALAR: DataFormat._0D,
                                PyTango.AttrDataFormat.SPECTRUM: DataFormat._1D,
                                PyTango.AttrDataFormat.IMAGE: DataFormat._2D}

FROM_TANGO_TO_TAURUS_TYPE = {PyTango.CmdArgType.DevVoid: None,
                             PyTango.CmdArgType.DevBoolean: DataType.Boolean,
                             PyTango.CmdArgType.DevShort: DataType.Integer,
                             PyTango.CmdArgType.DevLong: DataType.Integer,
                             PyTango.CmdArgType.DevFloat: DataType.Float,
                             PyTango.CmdArgType.DevDouble: DataType.Float,
                             PyTango.CmdArgType.DevUShort: DataType.Integer,
                             PyTango.CmdArgType.DevULong: DataType.Integer,
                             PyTango.CmdArgType.DevString: DataType.String,
                             PyTango.CmdArgType.DevVarCharArray: DataType.Bytes,
                             PyTango.CmdArgType.DevVarShortArray: DataType.Integer,
                             PyTango.CmdArgType.DevVarLongArray: DataType.Integer,
                             PyTango.CmdArgType.DevVarFloatArray: DataType.Float,
                             PyTango.CmdArgType.DevVarDoubleArray: DataType.Float,
                             PyTango.CmdArgType.DevVarUShortArray: DataType.Integer,
                             PyTango.CmdArgType.DevVarULongArray: DataType.Integer,
                             PyTango.CmdArgType.DevVarStringArray: DataType.String,
                             PyTango.CmdArgType.DevVarLongStringArray: DataType.Object,
                             PyTango.CmdArgType.DevVarDoubleStringArray: DataType.Object,
                             PyTango.CmdArgType.DevState: DataType.DevState,
                             PyTango.CmdArgType.ConstDevString: DataType.String,
                             PyTango.CmdArgType.DevVarBooleanArray: DataType.Boolean,
                             PyTango.CmdArgType.DevUChar: DataType.Bytes,
                             PyTango.CmdArgType.DevLong64: DataType.Integer,
                             PyTango.CmdArgType.DevULong64: DataType.Integer,
                             PyTango.CmdArgType.DevVarLong64Array: DataType.Integer,
                             PyTango.CmdArgType.DevVarULong64Array: DataType.Integer,
                             PyTango.CmdArgType.DevInt: DataType.Integer,
                             PyTango.CmdArgType.DevEncoded: DataType.DevEncoded,
                             }

if hasattr(PyTango, "str_2_obj"):
    str_2_obj = PyTango.str_2_obj
else:

    # Old PyTango
    import PyTango.utils

    bool_ = lambda value_str: value_str.lower() == "true"

    def str_2_obj(obj_str, tg_type=None):
        f = str
        if PyTango.utils.is_scalar_type(tg_type):
            if PyTango.utils.is_numerical_type(tg_type):
                if obj_str in __NO_STR_VALUE:
                    return None

            if PyTango.utils.is_int_type(tg_type):
                f = int
            elif PyTango.utils.is_float_type(tg_type):
                f = float
            elif PyTango.utils.is_bool_type(tg_type):
                f = bool_
        return f(obj_str)


def get_quantity(value, units=None, fmt=None):
    if value is None:
        return None
    res = Quantity(value, units=units)
    if fmt is not None:
        res.default_format = fmt + res.default_format
    return res


def quantity_from_tango_str(value_str, dtype=None, units=None, fmt=None,
                            ignore_exception=True):
    try:
        return get_quantity(str_2_obj(value_str, dtype), units=units, fmt=fmt)
    except ValueError:
        if not ignore_exception:
            raise
        return None


def unit_from_tango(unit):
    from taurus import deprecated
    deprecated(dep='unit_from_tango', rel='4.0.4', alt="pint's parse_units")

    if unit == PyTango.constants.UnitNotSpec or unit == "No unit":
        unit = None
    try:
        return UR.parse_units(unit)
    except (UndefinedUnitError, UnicodeDecodeError):
        # TODO: Maybe we could dynamically register the unit in the UR
        from taurus import warning
        warning('Unknown unit "%s" (will be treated as unitless)', unit)
        return UR.parse_units(None)


def ndim_from_tango(data_format):
    return int(data_format)


def data_format_from_tango(data_format):
    return FROM_TANGO_TO_TAURUS_DFORMAT[data_format]


def data_type_from_tango(data_type):
    return FROM_TANGO_TO_TAURUS_TYPE[data_type]


def display_level_from_tango(disp_level):
    return DisplayLevel(disp_level)


def quality_from_tango(quality):
    return AttrQuality(int(quality))


__NULL_DESC = PyTango.constants.DescNotSet, PyTango.constants.DescNotSpec


def description_from_tango(desc):
    if desc in __NULL_DESC:
        desc = ''
    return desc

__S_TYPES = (PyTango.CmdArgType.DevString,
             PyTango.CmdArgType.DevVarStringArray,
             PyTango.CmdArgType.DevEncoded,)


def standard_display_format_from_tango(dtype, fmt):
    if fmt == 'Not specified':
        return '!s'

    # %6.2f is the default value that Tango sets when the format is
    # unassigned in tango < 8. This is only good for float types! So for other
    # types I am changing this value.
    if fmt == '%6.2f':
        if PyTango.is_float_type(dtype, inc_array=True):
            pass
        elif PyTango.is_int_type(dtype, inc_array=True):
            fmt = '%d'
        elif dtype in __S_TYPES:
            fmt = '%s'
    return fmt


def display_format_from_tango(dtype, fmt):
    fmt = standard_display_format_from_tango(dtype, fmt)
    return fmt.replace('%s', '!s').replace('%r', '!r').replace('%', '')


