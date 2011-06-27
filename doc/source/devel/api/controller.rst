
.. currentmodule:: sardana.pool

.. _controller-api:

==================
Controller API
==================

.. _controller-data-type:
       
Data Type definition
----------------------

When writting a new controller you may need to specify extra attributes (per 
controller or/and per axis) as well as extra properties. This chapter describes
how to describe the data type for each of this additional members.
Controller data type definition has the following equivalences. This means you
can use any of the given possibilities to describe a field data type. The possibilities
are ordered by preference (example: usage of int is prefered to "int" or "PyTango.DevLong"):

- for 0D data types:
   - **integer**: int   | DataType.Integer | "int"    | "integer" | "long" | long | [ "PyTango." ] "DevLong"
   - **double**:  float | DataType.Double  | "double" | "float"   | [ "PyTango." ] "DevDouble"
   - string**:  str   | DataType.String  | "str"    | "string"  | [ "PyTango." ] "DevString"
   - **boolean**: bool  | DataType.Boolean | "bool"   | "boolean" | [ "PyTango." ] "DevBoolean"
- for 1D data types:
   - **integer**: (int,)   | (DataType.Integer,) | ("int",)    | ("integer",) | (long,) | ("long",) | [ "PyTango." ] "DevVarLongArray" | ([ "PyTango." ] "DevLong",)
   - **double**:  (float,) | (DataType.Double,)  | ("double",) | ("float",)   | [ "PyTango." ] "DevVarDoubleArray"  | ([ "PyTango." ] "DevDouble",)
   - **string**:  (str,)   | (DataType.String,)  | ("str",)    | ("string",)  | [ "PyTango." ] "DevVarStringArray"  | ([ "PyTango." ] "DevString",)
   - **boolean**: (bool,)  | (DataType.Boolean,) | ("bool",)   | ("boolean",) | [ "PyTango." ] "DevVarBooleanArray" | ([ "PyTango." ] "DevBoolean",)

.. deprecated:: 1.0
  [ "PyTango." ] "Dev"<concrete type string> types are considered deprecated.
  
.. note:: when string, types are case insensitive. This means "long" is the same as "LONG"

.. autoclass:: Controller
    :inherited-members:
    :members:
    :undoc-members:
    
.. autoclass:: MotorController
    :inherited-members:
    :members:
    :undoc-members:
    
.. autoclass:: CounterTimerController
    :inherited-members:
    :members:
    :undoc-members:
    
.. autoclass:: PseudoMotorController
    :members:
    :undoc-members: