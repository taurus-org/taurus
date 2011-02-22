#include <PropertyData.h>
#include <PoolUtil.h>

namespace Pool_ns 
{

//+------------------------------------------------------------------
/**
 *	method:	PropertyData::PropertyData
 *
 *	description: The constructor
 * 
 * argin  prop_name - the name of the property
 * argin  prop_type - the data type for the property
 * argin  prop_descr - the description of the property
 */
//+------------------------------------------------------------------
PropertyData::PropertyData(string &prop_name, string &prop_type, string &prop_descr)
:name(prop_name),descr(prop_descr),value_str(""),found_in_db(false),save_default(NULL)
{
	type = to_CmdArgType(prop_type);
	to_type_str(type_str);
	init();
}

//+------------------------------------------------------------------
/**
 *	method:	PropertyData::PropertyData
 *
 *	description: The copy constructor
 */
//+------------------------------------------------------------------
PropertyData::PropertyData(const PropertyData &cpy)
:type(cpy.type),type_str(cpy.type_str),name(cpy.name),descr(cpy.descr),value_str(cpy.value_str),
found_in_db(false),save_default(NULL)
{
	if(type == Tango::DEV_BOOLEAN)
		bool_v = cpy.bool_v;
	else if(type == Tango::DEV_LONG)
		int32_v = cpy.int32_v;
	else if(type == Tango::DEV_DOUBLE)
		double_v = cpy.double_v;
	else if(type == Tango::DEV_STRING)
	{ /* nothing to do on string. value_str member already contains the value.*/ }
	else if(type == Tango::DEVVAR_BOOLEANARRAY)
		bool_arr_v = new vector<bool>(*cpy.bool_arr_v);
	else if(type == Tango::DEVVAR_LONGARRAY)
		int32_arr_v = new vector<int32_t>(*cpy.int32_arr_v);
	else if(type == Tango::DEVVAR_DOUBLEARRAY)
		double_arr_v = new vector<double>(*cpy.double_arr_v);
	else if(type == Tango::DEVVAR_STRINGARRAY)
		str_arr_v = new vector<string>(*cpy.str_arr_v);	
}

//+------------------------------------------------------------------
/**
 *	method:	PropertyData::~PropertyData
 *
 *	description: The destructor
 */
//+------------------------------------------------------------------
PropertyData::~PropertyData()
{
	if(type == Tango::DEVVAR_BOOLEANARRAY)
	{
		SAFE_DELETE(bool_arr_v);
	}
	else if(type == Tango::DEVVAR_LONGARRAY)
	{
		SAFE_DELETE(int32_arr_v);
	}
	else if(type == Tango::DEVVAR_DOUBLEARRAY)
	{
		SAFE_DELETE(double_arr_v);
	}
	else if(type == Tango::DEVVAR_STRINGARRAY)
	{
		SAFE_DELETE(str_arr_v);
	}
		
	SAFE_DELETE(save_default);
}

//+------------------------------------------------------------------
/**
 *	method: PropertyData::to_type_str
 *
 *	description: Gets a string representation of the data type of this
 *               property
 * 
 * @return a string representation of the data type of this property
 */
//+------------------------------------------------------------------
void PropertyData::to_type_str(string &out) 
{
//	out = "PyTango." + string(Tango::CmdArgTypeName[type]);
	out = string(Tango::CmdArgTypeName[type]);
}

//+------------------------------------------------------------------
/**
 *	method:	PropertyData::init
 *
 *	description: initializes the necessary data depending on the
 *               data type set for this property
 */
//+------------------------------------------------------------------
void PropertyData::init()
{
	if(type == Tango::DEVVAR_BOOLEANARRAY)
		bool_arr_v = new vector<bool>;
	else if(type == Tango::DEVVAR_LONGARRAY)
		int32_arr_v = new vector<int32_t>;
	else if(type == Tango::DEVVAR_DOUBLEARRAY)
		double_arr_v = new vector<double>;
	else if(type == Tango::DEVVAR_STRINGARRAY)
		str_arr_v = new vector<string>;	
}

//+------------------------------------------------------------------
/**
 *	method:	PropertyData::is_simple_type
 *
 *	description:	returns if the data type for this property is simple.
 *                  Simple types are:  DevBoolean, DevLong, DevDouble, DevString
 *                  Non simple types are: DevVarBooleanArray, DevVarLongArray, DevVarDoubleArray, DevVarStringArray
 *
 * @return true if the current property type is simple or false otherwise
 */
//+------------------------------------------------------------------
bool PropertyData::is_simple_type()
{
	return (type == Tango::DEV_BOOLEAN) || (type == Tango::DEV_LONG) || (type == Tango::DEV_DOUBLE) || (type == Tango::DEV_STRING);
}

//+------------------------------------------------------------------
/**
 *	method:	PropertyData::append_to_property_vec
 *
 *	description:	appends this property data to the given vector.
 *                  The vector will contain four new elements corresponding
 *                  to the name, type, description and value of this property.
 *
 * @param	argin	info [in,out] - the vector which will contain at its end the
 *                                  details for this property 
 */
//+------------------------------------------------------------------
void PropertyData::append_to_property_vec(vector<string> &info)
{
	info.push_back(name);
	info.push_back(type_str);
	info.push_back(descr);
	info.push_back(value_str);
}

//+------------------------------------------------------------------
/**
 *	method:	PropertyData::to_CmdArgType
 *
 *	description:	translates a string into a type.
 *                  Supported types are: DevBoolean, DevLong, DevDouble, DevString,
 * 					DevVarBooleanArray, DevVarLongArray, DevVarDoubleArray, DevVarStringArray
 *
 * @return an enum representing the data type by the given string
 */
//+------------------------------------------------------------------
Tango::CmdArgType PropertyData::to_CmdArgType(string &in)
{
	string::size_type pos = in.find('.');
	
	string str_type;
	Tango::CmdArgType arg_type = Tango::DEV_VOID;
	
	if(pos == string::npos)
		str_type = in;
	else
		str_type = in.substr(pos+1);
	
	if(str_type == Tango::CmdArgTypeName[Tango::DEV_BOOLEAN]) arg_type = Tango::DEV_BOOLEAN;
	else if(str_type == Tango::CmdArgTypeName[Tango::DEV_LONG]) arg_type = Tango::DEV_LONG;
	else if(str_type == Tango::CmdArgTypeName[Tango::DEV_DOUBLE]) arg_type = Tango::DEV_DOUBLE;
	else if(str_type == Tango::CmdArgTypeName[Tango::DEV_STRING]) arg_type = Tango::DEV_STRING;
	else if(str_type == Tango::CmdArgTypeName[Tango::DEVVAR_BOOLEANARRAY]) arg_type = Tango::DEVVAR_BOOLEANARRAY;
	else if(str_type == Tango::CmdArgTypeName[Tango::DEVVAR_LONGARRAY]) arg_type = Tango::DEVVAR_LONGARRAY;
	else if(str_type == Tango::CmdArgTypeName[Tango::DEVVAR_DOUBLEARRAY]) arg_type = Tango::DEVVAR_DOUBLEARRAY;
	else if(str_type == Tango::CmdArgTypeName[Tango::DEVVAR_STRINGARRAY]) arg_type = Tango::DEVVAR_STRINGARRAY;
	else 
	{
		TangoSys_OMemStream o;
		
		o << "Invalid property type for property " << name << ends;
		Tango::Except::throw_exception((const char *)"Pool_InvalidCppPropertyValue",o.str(),
	    							   (const char *)"PropertyData::to_CmdArgType()");		
	}
	
	return arg_type;
}

//+------------------------------------------------------------------
/**
 *	method:	PropertyData::save_default_value
 *
 *	description:	Save the property default value in order that
 * 					it could be restored in case the property
 * 					is defined in db for one of the object
 */
//+------------------------------------------------------------------

void PropertyData::save_default_value()
{
	if (save_default == NULL)
		save_default = new PropertyData(name, type_str, descr);
	
	save_default->value_str = value_str;
	
	if(type == Tango::DEV_BOOLEAN)
		save_default->bool_v = bool_v;
	else if(type == Tango::DEV_LONG)
		save_default->int32_v = int32_v;
	else if(type == Tango::DEV_DOUBLE)
		save_default->double_v = double_v;
	else if(type == Tango::DEV_STRING)
	{ /* nothing to do on string. value_str member already contains the value.*/ }
	else if(type == Tango::DEVVAR_BOOLEANARRAY)
		(*save_default->bool_arr_v) = *bool_arr_v;
	else if(type == Tango::DEVVAR_LONGARRAY)
		(*save_default->int32_arr_v) = *int32_arr_v;
	else if(type == Tango::DEVVAR_DOUBLEARRAY)
		(*save_default->double_arr_v) = *double_arr_v;
	else if(type == Tango::DEVVAR_STRINGARRAY)
		(*save_default->str_arr_v) = *str_arr_v;	
}

//+------------------------------------------------------------------
/**
 *	method:	PropertyData::restore_default_value
 *
 *	description:	Restore the default_value into the property
 */
//+------------------------------------------------------------------

void PropertyData::restore_default_value()
{
	value_str = save_default->value_str;
	
	if(type == Tango::DEV_BOOLEAN)
		bool_v = save_default->bool_v;
	else if(type == Tango::DEV_LONG)
		int32_v = save_default->int32_v;
	else if(type == Tango::DEV_DOUBLE)
		double_v = save_default->double_v;
	else if(type == Tango::DEV_STRING)
	{ /* nothing to do on string. value_str member already contains the value.*/ }
	else if(type == Tango::DEVVAR_BOOLEANARRAY)
	{
		delete bool_arr_v;
		bool_arr_v = new vector<bool>(*(save_default->bool_arr_v));
	}
	else if(type == Tango::DEVVAR_LONGARRAY)
	{
		delete int32_arr_v;
		int32_arr_v = new vector<int32_t>(*(save_default->int32_arr_v));
	}
	else if(type == Tango::DEVVAR_DOUBLEARRAY)
	{
		delete double_arr_v;
		double_arr_v = new vector<double>(*(save_default->double_arr_v));
	}
	else if(type == Tango::DEVVAR_STRINGARRAY)
	{
		delete str_arr_v;
		str_arr_v = new vector<string>(*(save_default->str_arr_v));
	}
}

//+------------------------------------------------------------------
/**
 *	method:	PyPropertyData::to_py
 *
 *	description:	Creates a new python object with type and value compatible 
 *                  with the type and value of this property. 
 *
 * @return a python object representing the value of the property
 * @attention the method creates a new python object with a new reference.
 *            Do not forget to decrement the reference count when you don't need it
 *            anymore.
 */
//+------------------------------------------------------------------
PyObject *PyPropertyData::to_py()
{
	PyObject *value = NULL;
	if(type == Tango::DEV_BOOLEAN)
	{
		value = PyBool_FromLong(bool_v);
	}
	else if(type == Tango::DEV_LONG)
	{
		value = PyLong_FromLong(int32_v);
	}
	else if(type == Tango::DEV_DOUBLE)
	{
		value = PyFloat_FromDouble(double_v);
	}
	else if(type == Tango::DEV_STRING)
	{
		value = PyString_FromString(value_str.c_str());
	}
	else if(type == Tango::DEVVAR_BOOLEANARRAY)
	{
		int len = bool_arr_v->size();
		value = PyTuple_New(len);
		
		for(int i = 0; i < len; i++)
			PyTuple_SetItem(value, i, PyBool_FromLong((long)(*bool_arr_v)[i]));
	}
	else if(type == Tango::DEVVAR_LONGARRAY)
	{
		vector<int32_t>::size_type len = int32_arr_v->size();
		value = PyTuple_New(len);
		
		for(vector<int32_t>::size_type i = 0; i < len; i++)
			PyTuple_SetItem(value, i, PyLong_FromLong((*int32_arr_v)[i]));
	}
	else if(type == Tango::DEVVAR_DOUBLEARRAY)
	{ 
		vector<double>::size_type len = double_arr_v->size();
		value = PyTuple_New(len);
		
		for(vector<double>::size_type i = 0; i < len; i++)
			PyTuple_SetItem(value, i, PyFloat_FromDouble((*double_arr_v)[i]));
	}
	else if(type == Tango::DEVVAR_STRINGARRAY)
	{ 
		vector<string>::size_type len = str_arr_v->size();
		value = PyTuple_New(len);
		
		for(vector<string>::size_type i = 0; i < len; i++)
			PyTuple_SetItem(value, i, PyString_FromString((*str_arr_v)[i].c_str()));			
	}
	return value;
}

//+------------------------------------------------------------------
/**
 *	method:	PyPropertyData::from_py
 *
 *	description:	Sets value of this property to the one found in the python object.
 *                  The python object will be interpreted according to the current property type
 *
 * @param	argin	value [in] - the python object containning the value that will be assigned to this property
 *
 */
//+------------------------------------------------------------------
void PyPropertyData::from_py(PyObject *value)
{
	bool type_mismatch = false;
	PyObject *mismatch_type = NULL;
	string expected;
	
	if(type == Tango::DEV_BOOLEAN)
	{
		if(!PyBool_Check(value))
		{
			type_mismatch = true;
			mismatch_type = PyObject_Type(value);
			expected = "Boolean";
		}
		else
		{
			bool_v = PyObject_IsTrue(value) == 1 ? true : false;
			toString(bool_v, value_str);
		}	
	}
	else if(type == Tango::DEV_LONG)
	{
		if(PyLong_Check(value))
		{
			int32_v = PyLong_AsLong(value);
			toString(int32_v, value_str);
		}
		else if(PyInt_Check(value))
		{
			int32_v = PyInt_AsLong(value);
			toString(int32_v, value_str);
		}
		else 
		{
			type_mismatch = true;
			mismatch_type = PyObject_Type(value);
			expected = "Long";
		}
	}
	else if(type == Tango::DEV_DOUBLE)
	{
		if(PyLong_Check(value))
		{
			double_v = PyLong_AsDouble(value);
			toString(double_v, value_str);
		}
		else if(PyInt_Check(value))
		{
			double_v = (double)PyInt_AsLong(value);
			toString(double_v, value_str);
		}
		else if(PyFloat_Check(value))
		{
			double_v = PyFloat_AsDouble(value);
			toString(double_v, value_str);
		}
		else
		{
			type_mismatch = true;
			mismatch_type = PyObject_Type(value);
			expected = "Float";
		}
	}
	else if(type == Tango::DEV_STRING)
	{
		if(!PyString_Check(value))
		{
			type_mismatch = true;
			mismatch_type = PyObject_Type(value);
			expected = "String";
		}
		else
			value_str = PyString_AsString(value);
	}
	else if(type == Tango::DEVVAR_BOOLEANARRAY)
	{
		if(!PySequence_Check(value) || PyString_Check(value))
		{
			type_mismatch = true;
			mismatch_type = PyObject_Type(value);
			expected = "Sequence of Boolean";
		}
		else
		{
			int32_t len = PySequence_Size(value);
			for(int32_t i = 0; i < len; i++)
			{
				PyObject *valueb = PySequence_GetItem(value,i);
				if(!PyBool_Check(valueb))
				{
					type_mismatch = true;
					mismatch_type = PyObject_Type(valueb);
					expected = "Sequence of Boolean";
					Py_DECREF(valueb);
					break;
				}
				bool_arr_v->push_back(PyObject_IsTrue(valueb) == 1 ? true : false);
				Py_DECREF(valueb);
			}
			toString(*bool_arr_v, value_str);
		}			
	}
	else if(type == Tango::DEVVAR_LONGARRAY)
	{
		if(!PySequence_Check(value) || PyString_Check(value))
		{
			type_mismatch = true;
			mismatch_type = PyObject_Type(value);
			expected = "Sequence of Long";
		}
		else
		{
			int32_t len = PySequence_Size(value);
			for(int32_t i = 0; i < len; i++)
			{
				PyObject *valuel = PySequence_GetItem(value,i);
				
				if(PyLong_Check(valuel))
				{
					int32_arr_v->push_back(PyLong_AsLong(valuel));	
				}
				else if(PyInt_Check(valuel))
				{
					int32_arr_v->push_back(PyInt_AsLong(valuel));
				}
				else
				{
					type_mismatch = true;
					mismatch_type = PyObject_Type(valuel);
					expected = "Sequence of Long";
					Py_DECREF(valuel);
					break;
				}
				
				Py_DECREF(valuel);
			}
			toString(*int32_arr_v, value_str);
		}			
	}
	else if(type == Tango::DEVVAR_DOUBLEARRAY)
	{
		if(!PySequence_Check(value) || PyString_Check(value))
		{
			type_mismatch = true;
			mismatch_type = PyObject_Type(value);
			expected = "Sequence of Float";
		}
		else
		{
			int32_t len = PySequence_Size(value);
			for(int32_t i = 0; i < len; i++)
			{
				PyObject *valued = PySequence_GetItem(value,i);

				if(PyLong_Check(valued))
					double_arr_v->push_back(PyLong_AsDouble(valued));
				else if(PyInt_Check(valued))
					double_arr_v->push_back((double)PyInt_AsLong(valued));
				else if(PyFloat_Check(valued))
					double_arr_v->push_back(PyFloat_AsDouble(valued));
				else
				{
					type_mismatch = true;
					mismatch_type = PyObject_Type(valued);
					expected = "Sequence of Float";
					Py_DECREF(valued);
					break;
				}
				Py_DECREF(valued);
			}
			toString(*double_arr_v, value_str);
		}		
	}
	else if(type == Tango::DEVVAR_STRINGARRAY)
	{
		if(!PySequence_Check(value) || PyString_Check(value))
		{
			type_mismatch = true;
			mismatch_type = PyObject_Type(value);
			expected = "Sequence of String";
		}
		else
		{
			int32_t len = PySequence_Size(value);
			for(int32_t i = 0; i < len; i++)
			{
				PyObject *values = PySequence_GetItem(value,i);
				if(!PyString_Check(values))
				{
					type_mismatch = true;
					mismatch_type = PyObject_Type(values);
					expected = "Sequence of String";
					Py_DECREF(values);
					break;
				}
				str_arr_v->push_back(string(PyString_AsString(values)));
				Py_DECREF(values);
			}
			toString(*str_arr_v, value_str);
		}	
	}
	
	if(type_mismatch)
	{
		TangoSys_OMemStream o;
		PyObject *mismatch_type_str = PyObject_GetAttrString(mismatch_type,"__name__");
		
		o << "Invalid property value for '" << name << "': expected " << expected << " but found ";
		if(!is_simple_type())
			o << "Sequence containning ";
		o << PyString_AsString(mismatch_type_str) << " instead" << ends;
		Py_DECREF(mismatch_type_str);
		Py_DECREF(mismatch_type);
		Tango::Except::throw_exception((const char *)"Pool_InvalidPythonPropertyValue",o.str(),
	    							   (const char *)"PyPropertyData::from_py()");		
	}
	else
	{
//
// Do not use python string default representation for tuples/lists. Instead use a new line separator.
// The only restriction is that in a property which is a list of strings, each string must not contain any new line character.  
//
		if(!is_simple_type())
		{
			value_str = "";
			int32_t len = PySequence_Size(value);
			for(int32_t i = 0; i < len; i++)
			{
				PyObject *values = PySequence_GetItem(value,i);
				PyObject *obj_str = PyObject_Str(values);
				value_str += PyString_AsString(obj_str);
				if ( i < len-1 ) value_str += "\n";
				Py_DECREF(obj_str);
				Py_DECREF(values);
			}
		}
		else if(type != Tango::DEV_STRING)
		{
			PyObject *obj_str = PyObject_Str(value);
			value_str = PyString_AsString(obj_str);
			Py_DECREF(obj_str);
		}

	}
}

//+------------------------------------------------------------------
/**
 *	method:	CppPropertyData::from_cpp
 *
 *	description:	Sets value of this property to the one found in the python object.
 *                  The python object will be interpreted according to the current property type
 *
 * @param	argin	value [in] - the python object containning the value that will be assigned to this property
 *
 */
//+------------------------------------------------------------------
void CppPropertyData::from_cpp(string &value)
{
	bool type_mismatch = false;
	string expected;
	Tango::DbDatum tmp_datum;

//
// Init the value_str field
// If property is an array, extract each element
//

	if (is_simple_type())
	{
		value_str = value;
		tmp_datum.value_string.push_back(value);
	}
	else
	{
		bool first = true;
		string::size_type pos,start;
		start = pos = 0;
		while ((pos = value.find(',',pos)) != string::npos)
		{
			string tmp = value.substr(start,pos - start);
			tmp_datum.value_string.push_back(tmp);
			pos++;
			start = pos;
			if (first == true)
			{
				value_str = tmp;
				first = false;
			}
			else
				value_str = value_str + '\n' + tmp;
		}
		string tmp_plus = value.substr(start);
		tmp_datum.value_string.push_back(tmp_plus);
		if (first == true)
			value_str = tmp_plus;
		else
			value_str = value_str + '\n' + tmp_plus;
	}

//
// Convert each value
//

	switch (type)
	{
        case Tango::DEV_LONG:
        {
            Tango::DevLong tmp_v;
            if ((tmp_datum >> tmp_v) == false)
            {
                type_mismatch = true;
                expected = "Long";
            }
            int32_v = (int32_t)tmp_v;
            break;
        }    
        case Tango::DEV_BOOLEAN:
        {
            if ((tmp_datum >> bool_v) == false)
            {
                type_mismatch = true;
                expected = "Boolean";
            }
            break;
        }    
        case Tango::DEV_DOUBLE:
        {
            if ((tmp_datum >> double_v) == false)
            {
                type_mismatch = true;
                expected = "Double";
            }
            break;
        }    
        case Tango::DEVVAR_LONGARRAY:
        {
            std::vector<Tango::DevLong> tmp_v;
            if ((tmp_datum >> tmp_v) == false)
            {
                type_mismatch = true;
                expected = "Int32 Array";
            }
            int32_arr_v->clear();
            for(std::vector<Tango::DevLong>::iterator it = tmp_v.begin();
                it != tmp_v.end(); ++it)
                int32_arr_v->push_back((int32_t)(*it));
            break;
        }    
        case Tango::DEVVAR_DOUBLEARRAY:
        {
            if ((tmp_datum >> (*double_arr_v)) == false)
            {
                type_mismatch = true;
                expected = "Double Array";
            }
            break;
        }    
        case Tango::DEVVAR_BOOLEANARRAY:
        {
            vector<Tango::DevLong> tmp_v;
            if ((tmp_datum >> tmp_v) == false)
            {
                type_mismatch = true;
                expected = "Boolean Array";
            }
            bool_arr_v->clear();
            for(vector<Tango::DevLong>::iterator it = tmp_v.begin();
                it != tmp_v.end(); ++it)
                bool_arr_v->push_back((bool)(*it));
            break;
        }    
        case Tango::DEVVAR_STRINGARRAY:
        {
            if ((tmp_datum >> (*str_arr_v)) == false)
            {
                type_mismatch = true;
                expected = "String Array";
            }
            break;
        }
    //
    // Note that the STRING case is managed in another way
    //
            
        case Tango::DEV_STRING:
            break;
            
        default:
        {
            Tango::Except::throw_exception((const char *)"Pool_InvalidCppPropertyType",
                                           (const char *)"Invalid Cpp Property Data Type",
                                           (const char *)"CppPropertyData::from_cpp()");	
            break;	
        }
	}
	
	if(type_mismatch)
	{
		TangoSys_OMemStream o;
		
		o << "Invalid property value for '" << name << "': Expected data type is " << expected << ends;
		Tango::Except::throw_exception((const char *)"Pool_InvalidCppPropertytype",o.str(),
	    							   (const char *)"CppPropertyData::from_cpp()");		
	}
	
}

//+------------------------------------------------------------------
/**
 *	method:	CppPropertyData::to_cpp
 *
 *	description:	Creates a new python object with type and value compatible 
 *                  with the type and value of this property. 
 *
 * @return a python object representing the value of the property
 * @attention the method creates a new python object with a new reference.
 *            Do not forget to decrement the reference count when you don't need it
 *            anymore.
 */
//+------------------------------------------------------------------
Controller::Properties CppPropertyData::to_cpp()
{
	Controller::Properties cp;

	cp.name = name;	
	switch (type)
	{
	case Tango::DEV_LONG:
		cp.value.int32_prop.push_back(int32_v);
		break;
		
	case Tango::DEV_BOOLEAN:
		cp.value.bool_prop.push_back(bool_v);
		break;
		
	case Tango::DEV_DOUBLE:
		cp.value.double_prop.push_back(double_v);
		break;

	case Tango::DEV_STRING:
		cp.value.string_prop.push_back(value_str);
		break;
				
	case Tango::DEVVAR_LONGARRAY:
		cp.value.int32_prop = *int32_arr_v;
		break;
		
	case Tango::DEVVAR_DOUBLEARRAY:
		cp.value.double_prop = *double_arr_v;
		break;
		
	case Tango::DEVVAR_BOOLEANARRAY:
		cp.value.bool_prop = *bool_arr_v;
		break;
		
	case Tango::DEVVAR_STRINGARRAY:
		cp.value.string_prop = *str_arr_v;
		break;

	default:
		Tango::Except::throw_exception((const char *)"Pool_InvalidCppPropertyType",
									   (const char *)"Invalid Cpp Property Data Type",
	    							   (const char *)"CppPropertyData::to_cpp()");	
		break;		
	}
	
	return cp;
}

} // End of namespace
