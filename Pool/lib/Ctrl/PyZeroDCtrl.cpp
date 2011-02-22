#include "PyZeroDCtrl.h"
#include "PyUtils.h"

using namespace std;

//+-------------------------------------------------------------------------
//
// method : 		PyZeroDController::PyZeroDController
//
// description : 	This Python CounterTimer Controller class ctor
//
// argin : - inst : The controller instance name
//	   	   - cl_name : The controller class name
//	  	   - module : The python module object
//		   - prop_dict : The python properties dictionnary
//
//--------------------------------------------------------------------------

PyZeroDController::PyZeroDController(const char *inst,const char *cl_name,PyObject *module,PyObject *prop_dict)
:PyController(cl_name, module), ZeroDController(inst)
{
    //cout << "[PyZeroDController] class ctor with instance = " << inst << endl;

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
        o << "Can't build argument to create Python controller " << cl_name << ends;

        Tango::Except::throw_exception((const char *)"Pool_CantCreatePyController",o.str(),
                        (const char *)"PyZeroDController::PyZeroDController");
    }

    int insert_res = PyTuple_SetItem(arg_tuple,0,arg_str);
    if (insert_res != 0)
    {
        TangoSys_OMemStream o;
        o << "Can't build argument to create Python controller " << cl_name << ends;

        Tango::Except::throw_exception((const char *)"Pool_CantCreatePyController",o.str(),
                        (const char *)"PyZeroDController::PyZeroDController");
    }

    insert_res = PyTuple_SetItem(arg_tuple,1,prop_dict);
    if (insert_res != 0)
    {
        TangoSys_OMemStream o;
        o << "Can't build argument to create Python controller " << cl_name << ends;

        Tango::Except::throw_exception((const char *)"Pool_CantCreatePyController",o.str(),
                        (const char *)"PyZeroDController::PyZeroDController");
    }

    py_obj = PyObject_Call(ctrl_class,arg_tuple,NULL);
    if (py_obj == NULL)
    {
        PyObject *ex_exec,*ex_value,*ex_tb;
        Tango::DevErrorList err_list;
        err_list.length(2);

        PyErr_Fetch(&ex_exec,&ex_value,&ex_tb);
        this->Py_init_dev_error(ex_exec,ex_value,ex_tb,err_list);

        string tmp_str("Can't create Python controller ");
        tmp_str += cl_name;

        err_list[1].origin = CORBA::string_dup("PyZeroDController::PyZeroDController");
        err_list[1].desc = CORBA::string_dup(tmp_str.c_str());
        err_list[1].reason = CORBA::string_dup("PyCtrl_CantCreatePyController");
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

//+-------------------------------------------------------------------------
//
// method : 		PyZeroDController::~PyZeroDController
//
// description : 	This Python ZeroD Experiment Channel Controller class dtor
//
//--------------------------------------------------------------------------

PyZeroDController::~PyZeroDController()
{
    //cout << "[PyZeroDController] class dtor" << endl;
    Py_DECREF(py_obj);
}

//+-------------------------------------------------------------------------
//
// method : 		PyZeroDController::AddDevice
//
// description : 	Creates a new ZeroD Experiment Channel for the controller
//
// argin : - ind : The ZeroDExpChannel index within the controller
//
//--------------------------------------------------------------------------

void PyZeroDController::AddDevice(int32_t ind)
{
    //cout << "[PyZeroDController] Creating a new ZeroDExpChannel with index " << ind << " on controller PyZeroDController/" << inst_name  << endl;

    AutoPythonGIL lo;

    PyObject *res = NULL;
    res = PyObject_CallMethod(py_obj, (char*)"AddDevice", (char*)"i", ind);
    check_void_return(res,"Error reported from the controller AddDevice method","AddDevice");
}

//+-------------------------------------------------------------------------
//
// method : 		PyZeroDController::DeleteDevice
//
// description : 	Delete a ZeroD Experiment Channel from the controller
//
// argin : - ind : The ZeroDExpChannel index within the controller
//
//--------------------------------------------------------------------------

void PyZeroDController::DeleteDevice(int32_t ind)
{
    //cout << "[PyZeroDController] Deleting  ZeroDExpChannel with index " << ind << " on controller PyZeroDController/" << inst_name  << endl;

    AutoPythonGIL lo;

    PyObject *res = NULL;
    res = PyObject_CallMethod(py_obj, (char*)"DeleteDevice", (char*)"i", ind);
    check_void_return(res,"Error reported from the controller DeleteDevice method","DeleteDevice");
}

//+-------------------------------------------------------------------------
//
// method : 		PyZeroDController::PreReadAll
//
// description : 	Call the Python controller "PreReadAll" method
//
//--------------------------------------------------------------------------

void PyZeroDController::PreReadAll()
{
    if (pre_read_all == true)
    {
        AutoPythonGIL lo;

        PyObject *res = NULL;
        res = PyObject_CallMethod(py_obj, (char*)"PreReadAll", NULL);
        check_void_return(res,"Error reported from the controller PreReadAll method","PreReadAll");
    }
}

//+-------------------------------------------------------------------------
//
// method : 		PyZeroDController::PreReadOne
//
// description : 	Call the Python controller "PreReadOne" method
//
// argin : - ind: The ZeroDExpChannel index within the controller
//
//--------------------------------------------------------------------------

void PyZeroDController::PreReadOne(int32_t ind)
{
    if (pre_read_one == true)
    {
        AutoPythonGIL lo;

        PyObject *res = NULL;
        res = PyObject_CallMethod(py_obj, (char*)"PreReadOne", (char*)"i", ind);
        check_void_return(res,"Error reported from the controller PreReadOne method","PreReadOne");
    }
}

//+-------------------------------------------------------------------------
//
// method : 		PyZeroDController::ReadAll
//
// description : 	Call the Python controller "ReadAll" method
//
//--------------------------------------------------------------------------

void PyZeroDController::ReadAll()
{
    if (read_all == true)
    {
        AutoPythonGIL lo;

        PyObject *res = NULL;
        res = PyObject_CallMethod(py_obj, (char*)"ReadAll", NULL);
        check_void_return(res,"Error reported from the controller ReadAll method","ReadAll");
    }
}

//+-------------------------------------------------------------------------
//
// method : 		PyZeroDController::ReadOne
//
// description : 	Read a ZeroDExpChannel value from the Python controller
//
// argin : - ind : The ZeroDExpChannel index within the controller
//
//--------------------------------------------------------------------------

double PyZeroDController::ReadOne(int32_t ind)
{
    double dres = NULL;

    AutoPythonGIL lo;

    PyObject *res = PyObject_CallMethod(py_obj, (char*)"ReadOne", (char*)"i", ind);
    if (res != NULL)
    {
        if (PyNumber_Check(res) == 1)
        {
            if (PyFloat_Check(res) == true)
                dres = PyFloat_AsDouble(res);
            else
                dres = (double)PyInt_AsLong(res);
        }
        else
        {
            Py_DECREF(res);
            Tango::Except::throw_exception(
                    (const char *)"PyCtrl_BadType",
                    (const char *)"The value returned by the controller code is not a Python number as expected",
                     (const char *)"PyZeroDController::ReadOne()");
        }
    }
    else
    {
        PyObject *ex_exec,*ex_value,*ex_tb;
        Tango::DevErrorList err_list;
        err_list.length(2);

        PyErr_Fetch(&ex_exec,&ex_value,&ex_tb);
        this->Py_init_dev_error(ex_exec,ex_value,ex_tb,err_list);

        string tmp_str("Can't read the ZeroDExpChannel value");

        err_list[1].origin = CORBA::string_dup("PyZeroDController::ReadOne");
        err_list[1].desc = CORBA::string_dup(tmp_str.c_str());
        err_list[1].reason = CORBA::string_dup("PyCtrl_CantReadValue");
        err_list[1].severity = Tango::ERR;

        throw Tango::DevFailed(err_list);
    }

    Py_DECREF(res);
    return dres;
}

//+-------------------------------------------------------------------------
//
// method : 		PyZeroDController::PreStateAll
//
// description : 	Call the Python controller "PreReadAll" method
//
//--------------------------------------------------------------------------

void PyZeroDController::PreStateAll()
{
    if (pre_state_all == true)
    {
        AutoPythonGIL lo;

        PyObject *res = NULL;
        res = PyObject_CallMethod(py_obj, (char*)"PreStateAll", NULL);
        check_void_return(res,"Error reported from the controller PreStateAll method","PreStateAll");
    }
}

//+-------------------------------------------------------------------------
//
// method : 		PyZeroDController::PreStateOne
//
// description : 	Call the Python controller "PreStateOne" method
//
// argin : - axis: The motor index within the controller
//
//--------------------------------------------------------------------------

void PyZeroDController::PreStateOne(int32_t axis)
{
    if (pre_state_one == true)
    {
        AutoPythonGIL lo;

        PyObject *res = NULL;
        res = PyObject_CallMethod(py_obj, (char*)"PreStateOne", (char*)"i", axis);
        check_void_return(res,"Error reported from the controller PreStateOne method","PreStateOne");
    }
}

//+-------------------------------------------------------------------------
//
// method : 		PyZeroDController::StateAll
//
// description : 	Call the Python controller "StateAll" method
//
//--------------------------------------------------------------------------

void PyZeroDController::StateAll()
{
    if (state_all == true)
    {
        AutoPythonGIL lo;

        PyObject *res = NULL;
        res = PyObject_CallMethod(py_obj, (char*)"StateAll", NULL);
        check_void_return(res,"Error reported from the controller StateAll method","StateAll");
    }
}

//+-------------------------------------------------------------------------
//
// method : 		PyZeroDController::StateOne
//
// description : 	Call the Python controller "StateOne" method
//
// argin : - ind: The ZeroDExpChannel index within the controller
//		   - ptr: Pointer to the structure used to returned a ZeroD Experiment Channel state
//
//--------------------------------------------------------------------------

void PyZeroDController::StateOne(int32_t axis, Controller::CtrlState *ptr)
{
    _StateOne(axis, ptr);
}

//+-------------------------------------------------------------------------
//
// method : 		PyZeroDController::SetExtraAttributePar
//
// description : 	Call the Python controller "SetExtraAttribute" method
//
// argin : - axis: The motor index within the controller
//		   - par_name: The parameter name
//		   - par_value: The parameter value
//
//--------------------------------------------------------------------------

void PyZeroDController::SetExtraAttributePar(int32_t axis,string &par_name,Controller::CtrlData &par_value)
{
    if (set_extra_attribute == true)
    {
        AutoPythonGIL lo;

        PyObject *res = NULL;
        switch (par_value.data_type)
        {
            case Controller::BOOLEAN:
            res = PySetExtraAttributeBool(py_obj,axis,par_name,par_value.bo_data);
            break;

            case Controller::INT32:
            res = PyObject_CallMethod(py_obj, (char*)"SetExtraAttributePar",
                    (char*)"isi", axis, par_name.c_str(), par_value.int32_data);
            break;

            case Controller::DOUBLE:
            res = PyObject_CallMethod(py_obj, (char*)"SetExtraAttributePar",
                    (char*)"isd", axis, par_name.c_str() ,par_value.db_data);
            break;

            default:
            res = PyObject_CallMethod(py_obj, (char*)"SetExtraAttributePar",
                    (char*)"iss", axis, par_name.c_str(),
                    par_value.str_data.c_str());
            break;
        }
        check_void_return(res,"Error reported from the controller SetExtraAttributePar method","SetExtraAttributePar");
    }
    else
        throw_simple_exception("Method SetExtraAttributePar is not implemented in controller","SetExtraAttributePar");
}

//+-------------------------------------------------------------------------
//
// method : 		PyZeroDController::GetExtraAttributePar
//
// description : 	Call the Python controller "GetExtraAttributePar" method
//
// argin : - axis: The motor index within the controller
//		   - par_name: The parameter name
//
//--------------------------------------------------------------------------

Controller::CtrlData PyZeroDController::GetExtraAttributePar(int32_t axis,string &extra_par_name)
{
    Controller::CtrlData dres;

    if (get_extra_attribute == true)
    {
        AutoPythonGIL lo;

        PyObject *res = NULL;

        res = PyObject_CallMethod(py_obj, (char*)"GetExtraAttributePar",
                (char*)"is", axis, extra_par_name.c_str());
        if (res != NULL)
        {
            if (PyString_Check(res) == 1)
            {
                dres.str_data = PyString_AsString(res);
                dres.data_type = Controller::STRING;
            }
            else if (PyFloat_Check(res) == 1)
            {
                dres.db_data = PyFloat_AsDouble(res);
                dres.data_type = Controller::DOUBLE;
            }
            else if (PyInt_Check(res) == 1)
            {
                if (PyBool_Check(res) == 1)
                {
                    if (res == Py_False)
                        dres.bo_data = false;
                    else
                        dres.bo_data = true;
                    dres.data_type = Controller::BOOLEAN;
                }
                else
                {
                    dres.int32_data = (int32_t) PyInt_AsLong(res);
                    dres.data_type = Controller::INT32;
                }
            }
            else
            {
                Py_DECREF(res);
                Tango::Except::throw_exception(
                    (const char *)"PyCtrl_BadType",
                    (const char *)"The value returned by the controller code is neither a Python string, a Python float or a Python int as expected",
                    (const char *)"PyController::GetExtraAttributePar()");
            }
        }
        else
        {
            PyObject *ex_exec,*ex_value,*ex_tb;
            Tango::DevErrorList err_list;
            err_list.length(2);

            PyErr_Fetch(&ex_exec,&ex_value,&ex_tb);
            this->Py_init_dev_error(ex_exec,ex_value,ex_tb,err_list);

            string tmp_str("Can't get extra attribute parameter");

            err_list[1].origin = CORBA::string_dup("PyController::GetExtraAttributePar");
            err_list[1].desc = CORBA::string_dup(tmp_str.c_str());
            err_list[1].reason = CORBA::string_dup("PyCtrl_CantGetExtraAttrParameter");
            err_list[1].severity = Tango::ERR;

            throw Tango::DevFailed(err_list);
        }
        Py_DECREF(res);
    }
    else
        throw_simple_exception("Method GetExtraAttributePar is not implemented in controller","GetExtraAttributePar");

    return dres;
}

//+-------------------------------------------------------------------------
//
// method : 		PyZeroDController::SendToCtrl
//
// description : 	Call the Python controller "SendToCtrl" method
//
// argin : - in_str: The input string to pass to the controller
//
//--------------------------------------------------------------------------

string PyZeroDController::SendToCtrl(string &in_str)
{
    string returned_str("Default string: The controller returns nothing or an invalid data type");

    if (send_to_ctrl == true)
    {
        AutoPythonGIL lo;

        PyObject *res = NULL;
        res = PyObject_CallMethod(py_obj,
                (char*)"SendToCtrl", (char*)"s",
                in_str.c_str());

        if (res != NULL)
        {
            if (PyString_Check(res) == 1)
            {
                returned_str = PyString_AsString(res);
            }
            Py_DECREF(res);
        }
    }
    else
        throw_simple_exception("Method SendToCtrl is not implemented in controller","SendToCtrl");

    return returned_str;
}

//+-------------------------------------------------------------------------
//
// method : 		PyZeroDController::clear_method_flag
//
// description : 	Clear all the boolean flags used to memorize which
//					pre-defined method are implemented in this controller
//
//--------------------------------------------------------------------------

void PyZeroDController::clear_method_flag()
{
    base_clear_method_flag();

    pre_read_all = false;
    pre_read_one = false;
    read_all = false;
}

//+-------------------------------------------------------------------------
//
// method : 		PyZeroDController::check_existing_method
//
// description : 	Check which pre-defined methods are implemented in this
//					controller and set the method flag according to the
//					check result
//					It is not necesseray to check for
//						GetState()
//						ReadOne()
//					because the pool refuses to load controller code if these
//					methods are not defined
//
// argin : - obj : The python controller object
//
//--------------------------------------------------------------------------

void PyZeroDController::check_existing_methods(PyObject *obj)
{
    base_check_existing_methods(obj);

    PyObject *met = NULL;

    if ((met = PyObject_GetAttrString(obj,"PreReadAll")) != NULL)
    {
        pre_read_all = true;
        Py_DECREF(met);
    }
    else
        PyErr_Clear();

    if ((met = PyObject_GetAttrString(obj,"PreReadOne")) != NULL)
    {
        pre_read_one = true;
        Py_DECREF(met);
    }
    else
        PyErr_Clear();

    if ((met = PyObject_GetAttrString(obj,"ReadAll")) != NULL)
    {
        read_all = true;
        Py_DECREF(met);
    }
    else
        PyErr_Clear();
}

extern "C"
{
Controller *_create_PyZeroDExpChannelController(const char *inst,const char *cl_name,PyObject *mo,PyObject *prop)
{
    return new PyZeroDController(inst,cl_name,mo,prop);
}
}
