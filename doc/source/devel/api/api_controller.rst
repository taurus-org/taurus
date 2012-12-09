
.. currentmodule:: sardana.pool.controller

.. _sardana-controller-api:

========================
Controller API reference
========================

    * :class:`Controller` - Base API for all controller types
    * :class:`MotorController` - Motor controller API
    * :class:`CounterTimerController` - Counter/Timer controller API
    * :class:`ZeroDController` - 0D controller API
    * :class:`PseudoMotorController` - PseudoMotor controller API
    * :class:`PseudoCounterController` - PseudoCounter controller API
    * :class:`IORegisterController` - IORegister controller API

.. _sardana-controller-data-type:

Data Type definition
----------------------

When writing a new controller you may need to specify extra attributes (per
controller or/and per axis) as well as extra properties. This chapter describes
how to describe the data type for each of this additional members.
Controller data type definition has the following equivalences. This means you
can use any of the given possibilities to describe a field data type. The
possibilities are ordered by preference (example: usage of :obj:`int` is
preferred to "int" or "PyTango.DevLong"):

- for 0D data types:
   - **integer**: :obj:`int`   | :data:`DataType.Integer <sardana.sardanadefs.DataType>` | "int"    | "integer" | "long" | :obj:`long` | [ "PyTango." ] "DevLong"
   - **double**:  :obj:`float` | :data:`DataType.Double <sardana.sardanadefs.DataType>`  | "double" | "float"   | [ "PyTango." ] "DevDouble"
   - **string**:  :obj:`str`   | :data:`DataType.String <sardana.sardanadefs.DataType>`  | "str"    | "string"  | [ "PyTango." ] "DevString"
   - **boolean**: :obj:`bool`  | :data:`DataType.Boolean <sardana.sardanadefs.DataType>` | "bool"   | "boolean" | [ "PyTango." ] "DevBoolean"
- for 1D data types:
   - **integer**: (:obj:`int`,)   | (:data:`DataType.Integer <sardana.sardanadefs.DataType>`,) | ("int",)    | ("integer",) | (:obj:`long`,) | ("long",) | [ "PyTango." ] "DevVarLongArray" | ([ "PyTango." ] "DevLong",)
   - **double**:  (:obj:`float`,) | (:data:`DataType.Double <sardana.sardanadefs.DataType>`,)  | ("double",) | ("float",)   | [ "PyTango." ] "DevVarDoubleArray"  | ([ "PyTango." ] "DevDouble",)
   - **string**:  (:obj:`str`,)   | (:data:`DataType.String <sardana.sardanadefs.DataType>`,)  | ("str",)    | ("string",)  | [ "PyTango." ] "DevVarStringArray"  | ([ "PyTango." ] "DevString",)
   - **boolean**: (:obj:`bool`,)  | (:data:`DataType.Boolean <sardana.sardanadefs.DataType>`,) | ("bool",)   | ("boolean",) | [ "PyTango." ] "DevVarBooleanArray" | ([ "PyTango." ] "DevBoolean",)

.. deprecated:: 1.0
  [ "PyTango." ] "Dev"<concrete type string> types are considered deprecated.
  
.. note:: when string, types are case insensitive. This means "long" is the same as "LONG"

Here is an example on how to define extra attributes per axis:

    1. EncoderSource: a scalar r/w string
    2. ReflectionMatrix: a 2D readable float with customized getter method
    
::
    
    from sardana import State, DataAccess
    from sardana.pool.controller import MotorController, \
        Type, Description, DefaultValue, Access, FGet, FSet
        
    class MyMotorCtrl(MotorController):

        axis_attributes = \
        {
            'EncoderSource' : { Type : str,
                                Description : 'motor encoder source', },

            'ReflectionMatrix' : { Type : ( (float,), ),
                                   Access : DataAccess.ReadOnly,
                                   FGet : 'getReflectionMatrix', },
        }
        
        def getAxisExtraPar(self, axis, name):
            name = name.lower()
            if name == 'encodersource':
                return self._encodersource[axis]
        
        def setAxisPar(self, axis, name, value):
            name = name.lower()
            if name == 'encodersource':
                self._encodersource[axis] = value
        
        def getReflectionMatrix(self, axis):
            return ( (1.0, 0.0), (0.0, 1.0) )
