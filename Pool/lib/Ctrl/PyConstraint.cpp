#include "PyConstraint.h"
#include "PyUtils.h"

using namespace std;

PyConstraint::PyConstraint(const char *inst,const char *cl_name,
                           PyObject *module,PyObject *prop_dict):
PyController(cl_name, module), Constraint(inst)
{
    clear_method_flag();

//
// Build the string to create the Python controller object
//

    string py_cmd(cl_name);
    py_cmd = py_cmd + "('" + inst_name + "')";
    
//
// Create the controller object
//

    PyObject *ctrl_class = PyObject_GetAttrString(mod,(char *)cl_name);
    PyObject *arg_tuple = PyTuple_New(2);
    PyObject *arg_str = PyString_FromString(inst);
    
    if ((ctrl_class == NULL) || (arg_tuple == NULL) || (arg_str == NULL))
    {
        TangoSys_OMemStream o;
        o << "Can't build argument to create Python constraint ";
        o << cl_name << ends;

        Tango::Except::throw_exception(
                    (const char *)"Pool_CantCreatePyConstraint",o.str(),
                    (const char *)"PyConstraint::PyConstraint");
    }
    
    int insert_res = PyTuple_SetItem(arg_tuple,0,arg_str);
    if (insert_res != 0)
    {
        TangoSys_OMemStream o;
        o << "Can't build argument to create Python constraint ";
        o << cl_name << ends;

        Tango::Except::throw_exception(
                        (const char *)"Pool_CantCreatePyConstraint",o.str(),
                        (const char *)"PyConstraint::PyConstraint");
    }
    
    insert_res = PyTuple_SetItem(arg_tuple,1,prop_dict);
    if (insert_res != 0)
    {
        TangoSys_OMemStream o;
        o << "Can't build argument to create Python constraint ";
        o << cl_name << ends;

        Tango::Except::throw_exception(
                        (const char *)"Pool_CantCreatePyConstraint",o.str(),
                        (const char *)"PyConstraint::PyConstraint");
    }
        
    py_obj = PyObject_Call(ctrl_class,arg_tuple,NULL);
    if (py_obj == NULL)
    {
        PyObject *ex_exec,*ex_value,*ex_tb;
        Tango::DevErrorList err_list;
        err_list.length(2);
        
        PyErr_Fetch(&ex_exec,&ex_value,&ex_tb);
        this->Py_init_dev_error(ex_exec,ex_value,ex_tb,err_list);

        string tmp_str("Can't create Python constraint ");
        tmp_str += cl_name;

        err_list[1].origin = 
            CORBA::string_dup("PyConstraint::PyConstraint");
        err_list[1].desc = CORBA::string_dup(tmp_str.c_str());
        err_list[1].reason = CORBA::string_dup("PyCtrl_CantCreatePyConstraint");
        err_list[1].severity = Tango::ERR;
        
        Py_DECREF(ctrl_class);
        Py_DECREF(arg_tuple);

        throw Tango::DevFailed(err_list);
    }
    
    Py_DECREF(ctrl_class);
    Py_DECREF(arg_tuple);

//
// Check which methods are defined within this class
//

    check_existing_methods(py_obj);	
}

PyConstraint::~PyConstraint()
{
    //cout << "[PyComController] class dtor" << endl;
    Py_DECREF(py_obj);	
}


bool PyConstraint::isAllowed(std::vector<double> &pos, std::string &descr)
{
    PyObject *res;
    
    unsigned long pos_count = pos.size();
    
    AutoPythonGIL lo;
    
    PyObject *arg_tuple = PyTuple_New(pos_count);
    
///------------------------------------------------------------------------
/// Build the arguments to call the python method
///
    for(unsigned long pos_index = 0 ; pos_index < pos_count; pos_index++)
    {
        PyObject *arg_double = PyFloat_FromDouble(pos[pos_index]);
        int insert_res = PyTuple_SetItem(arg_tuple,pos_index,arg_double);
        
        if(insert_res != 0)
        {
            Py_DECREF(arg_tuple);
            Tango::Except::throw_exception(
                (const char *)"PyPseudoCtrl_PythonAllocError",
                (const char *)"Can't build argument",
                (const char *)"PyConstraint::isAllowed()");	  		
        }
    }
    
///------------------------------------------------------------------------
/// Invoke the python method
///
    PyObject *method_name = PyString_FromString(IS_ALLOWED);
    
    res = PyObject_CallMethodObjArgs(py_obj,method_name,arg_tuple,NULL);
    
    Py_DECREF(method_name);
    Py_DECREF(arg_tuple);

///------------------------------------------------------------------------
/// Retrieve the result of calling the python method  
///
    if(res == NULL)
    {
        PyObject *ex_exec,*ex_value,*ex_tb;
        Tango::DevErrorList err_list;
        err_list.length(2);
        
        PyErr_Fetch(&ex_exec,&ex_value,&ex_tb);
        this->Py_init_dev_error(ex_exec,ex_value,ex_tb,err_list);
    
        string tmp_str("Can't invoke isAllowed");
    
        err_list[1].origin = CORBA::string_dup("PyConstraint::isAllowed");
        err_list[1].desc = CORBA::string_dup(tmp_str.c_str());
        err_list[1].reason = CORBA::string_dup("PyConstraint_CantIsAllowed");
        err_list[1].severity = Tango::ERR;
        
        throw Tango::DevFailed(err_list); 
    }
    
    bool b;
    if (get_py_bool(res, b))
    {
        Py_DECREF(res);
        return b;
    }
    else if (PySequence_Check(res) == 1)
    {
        if (PySequence_Size(res) != 2)
        {
            Py_DECREF(res);
            Tango::Except::throw_exception(
                (const char *)"PyConstraint_BadReturn",
                (const char *)"The return value sequence doesn't have two elements as expected",
                (const char *)"PyConstraint::isAllowed()");
        }
        
        PyObject *py_bool = PySequence_GetItem(res, 0);
        
        if (!get_py_bool(res, b))
        {
            Py_DECREF(py_bool);
            Py_DECREF(res);
            Tango::Except::throw_exception(
                (const char *)"PyConstraint_BadReturn",
                (const char *)"The first element of the return sequence is not a Python boolean as expected",
                (const char *)"PyConstraint::isAllowed()");
            
        }
        Py_DECREF(py_bool);
        
        PyObject *py_descr = PySequence_GetItem(res, 1);
        PyObject *py_descr_str = PyObject_Str(py_descr);
        Py_DECREF(py_descr);
        
        if (py_descr_str == NULL)
        {
            Py_DECREF(res);
            Tango::Except::throw_exception(
                (const char *)"PyConstraint_BadReturn",
                (const char *)"The second element of the return sequence could not be converted to a string",
                (const char *)"PyConstraint::isAllowed()");
        }
        
        descr = PyString_AS_STRING(py_descr_str);
        Py_DECREF(py_descr_str);
        Py_DECREF(res);
        return b;
    }

    Py_DECREF(res);
    Tango::Except::throw_exception(
        (const char *)"PyConstraint_BadReturn",
        (const char *)"The return value is not a Python boolean as expected",
        (const char *)"PyConstraint::isAllowed()");
    
    // quiet the compiler
    return false;
}

bool PyConstraint::isDynamic()
{
    if(!is_dynamic)
        return Constraint::isDynamic();
    
    AutoPythonGIL lo;
    
    ///------------------------------------------------------------------------
    /// Invoke the python method
    ///
    PyObject *method_name = PyString_FromString(IS_DYNAMIC);
    
    PyObject *res = PyObject_CallMethodObjArgs(py_obj,method_name,NULL);
    
    if(res == NULL)
    {
        PyObject *ex_exec,*ex_value,*ex_tb;
        Tango::DevErrorList err_list;
        err_list.length(2);
        
        PyErr_Fetch(&ex_exec,&ex_value,&ex_tb);
        this->Py_init_dev_error(ex_exec,ex_value,ex_tb,err_list);
    
        string tmp_str("Can't invoke isDynamic");
    
        err_list[1].origin = CORBA::string_dup("PyConstraint::isDynamic");
        err_list[1].desc = CORBA::string_dup(tmp_str.c_str());
        err_list[1].reason = CORBA::string_dup("PyConstraint_CantIsDynamic");
        err_list[1].severity = Tango::ERR;
        
        throw Tango::DevFailed(err_list); 
    }
    
    bool b;
    if (!get_py_bool(res, b))
    {
        Py_DECREF(res);
        Tango::Except::throw_exception(
            (const char *)"PyConstraint_BadReturn",
            (const char *)"The return value is not a Python boolean as expected",
            (const char *)"PyConstraint::isDynamic()");
    }	
    Py_DECREF(res);
    return b;
}

//+-------------------------------------------------------------------------
//
// method : 		PyConstraint::clear_method_flag
// 
// description : 	Clear all the boolean flags used to memorize which
//					pre-defined method are implemented in this constraint
//
//--------------------------------------------------------------------------

void PyConstraint::clear_method_flag()
{
    is_dynamic = false;
}

//+-------------------------------------------------------------------------
//
// method : 		PyConstraint::check_existing_method
// 
// description : 	Check which pre-defined methods are implemented in this
//					constraint and set the method flag according to the
//					check result
//					It is not necesseray to check for 
//						isAllowed()
//					because the pool refuses to load controller code if this
//					method is not defined
//
// argin : - obj : The python constraint object
//
//--------------------------------------------------------------------------

void PyConstraint::check_existing_methods(PyObject *obj)
{
    base_check_existing_methods(obj);
    
    PyObject *met;

    if ((met = PyObject_GetAttrString(obj,IS_DYNAMIC)) != NULL)
    {
        is_dynamic = true;
        Py_DECREF(met);
    }
    else
        PyErr_Clear();
}

extern "C"
{
    Controller *_create_PyConstraint(const char *inst,const char *cl_name,PyObject *mo,PyObject *prop)
    {
        return new PyConstraint(inst,cl_name,mo,prop);
    }
}
