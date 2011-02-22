#include "PyPseudoCoCtrl.h"
#include "PyUtils.h"

using namespace std;

PyPseudoCounterController::PyPseudoCounterController(const char *inst,
                                           const char *cl_name,
                                           PyObject *module,
                                           PyObject *prop_dict):
PyController(cl_name, module), PseudoCounterController(inst)
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
        o << "Can't build argument to create Python controller ";
        o << cl_name << ends;

        Tango::Except::throw_exception(
            (const char *)"Pool_CantCreatePyController",o.str(),
            (const char *)"PyPseudoCounterController::PyPseudoCounterController");
    }

    int insert_res = PyTuple_SetItem(arg_tuple,0,arg_str);
    if (insert_res != 0)
    {
        TangoSys_OMemStream o;
        o << "Can't build argument to create Python controller ";
        o << cl_name << ends;

        Tango::Except::throw_exception(
            (const char *)"Pool_CantCreatePyController",o.str(),
            (const char *)"PyPseudoCounterController::PyPseudoCounterController");
    }

    insert_res = PyTuple_SetItem(arg_tuple,1,prop_dict);
    if (insert_res != 0)
    {
        TangoSys_OMemStream o;
        o << "Can't build argument to create Python controller ";
        o << cl_name << ends;

        Tango::Except::throw_exception(
            (const char *)"Pool_CantCreatePyController",o.str(),
            (const char *)"PyPseudoCounterController::PyPseudoCounterController");
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

        err_list[1].origin =
            CORBA::string_dup("PyPseudoCounterController::PyPseudoCounterController");
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
// method : 		PyPseudoCounterController::~PyPseudoCounterController
//
// description : 	This Python Pseudo Counter Controller class dtor
//
//--------------------------------------------------------------------------

PyPseudoCounterController::~PyPseudoCounterController()
{
    //cout << "[PyPseudoCounterController] class dtor" << endl;
    Py_DECREF(py_obj);
}

//+-------------------------------------------------------------------------
//
// method : 		PyPseudoController::Calc
//
// description : 	Calculates the value for the pseudo counter based on the
//                  current values of the given physical counters
//
// arg(s) : - counter_values [in]: the list of physical counter values
//
//--------------------------------------------------------------------------
double PyPseudoCounterController::Calc(int32_t axis,vector<double> &counter_values)
{
    PyObject *res;

    AutoPythonGIL lo;

    vector<double>::size_type counter_nb = counter_values.size();

    PyObject *arg_axis = PyLong_FromLong(axis);
    PyObject *arg_tuple = PyTuple_New(counter_nb);

    if(arg_tuple == NULL)
    {
        Tango::Except::throw_exception(
            (const char *)"PyPseudoCoCtrl_PythonAllocError",
            (const char *)"Can't build argument to Calc Pseudo Python controller",
            (const char *)"PyPseudoCounterController::Calc()");
    }

///------------------------------------------------------------------------
/// Build the arguments to call the python method
///
    for(vector<double>::size_type counter_index = 0 ; counter_index < counter_nb; counter_index++)
    {
        PyObject *arg_double = PyFloat_FromDouble(counter_values[counter_index]);
        int insert_res = PyTuple_SetItem(arg_tuple,counter_index,arg_double);

        if(insert_res != 0)
        {
            Py_DECREF(arg_tuple);
            Tango::Except::throw_exception(
                (const char *)"PyPseudoCoCtrl_PythonAllocError",
                (const char *)"Can't build argument to Calc Pseudo Python controller",
                (const char *)"PyPseudoCounterController::Calc()");
        }
    }

///------------------------------------------------------------------------
/// Invoke the python method
///
    PyObject *method_name = PyString_FromString(CALC_METHOD);

    res = PyObject_CallMethodObjArgs(py_obj,method_name,arg_axis,arg_tuple,NULL);

    Py_DECREF(method_name);
    Py_DECREF(arg_tuple);
    Py_DECREF(arg_axis);

///------------------------------------------------------------------------
/// Retrieve the result of calling the python method and append it to the
/// end of the output vector
///

    if(res == NULL)
    {
        PyObject *ex_exec,*ex_value,*ex_tb;
        Tango::DevErrorList err_list;
        err_list.length(2);

        PyErr_Fetch(&ex_exec,&ex_value,&ex_tb);
        this->Py_init_dev_error(ex_exec,ex_value,ex_tb,err_list);

        string tmp_str("Can't calculate value");

        err_list[1].origin = CORBA::string_dup("PyPseudoCounterController::Calc");
        err_list[1].desc = CORBA::string_dup(tmp_str.c_str());
        err_list[1].reason = CORBA::string_dup("PyPseudoCoCtrl_CantCalc");
        err_list[1].severity = Tango::ERR;

        throw Tango::DevFailed(err_list);
    }

    double ret;

    if (get_py_number(res,ret))
    {
        Py_DECREF(res);
        return ret;
    }

    Py_DECREF(res);
    Tango::Except::throw_exception(
        (const char *)"PyPseudoCtrl_BadReturnElement",
        (const char *)"The return of the controller code is not a number as expected",
        (const char *)"PyPseudoCounterController::Calc()");

    // quiet the compiler
    return ret;
}

//+-------------------------------------------------------------------------
//
// method : 		PyPseudoCounterController::SetExtraAttributePar
//
// description : 	Call the Python controller "SetExtraAttribute" method
//
// argin : - axis: The Communication channel	 index within the controller
//		   - par_name: The parameter name
//		   - par_value: The parameter value
//
//--------------------------------------------------------------------------

void PyPseudoCounterController::SetExtraAttributePar(int32_t axis,string &par_name,
                                                Controller::CtrlData &par_value)
{
    if (set_extra_attribute == true)
    {
        AutoPythonGIL lo;

        PyObject *res;
        switch (par_value.data_type)
        {
            case Controller::BOOLEAN:
            res = PySetExtraAttributeBool(py_obj,axis,par_name,
                                          par_value.bo_data);
            break;

            case Controller::INT32:
            res = PyObject_CallMethod(py_obj,
                    (char*)"SetExtraAttributePar", (char*)"isi", axis,
                    par_name.c_str(), par_value.int32_data);
            break;

            case Controller::DOUBLE:
            res = PyObject_CallMethod(py_obj,
                    (char*)"SetExtraAttributePar", (char*)"isd", axis,
                    par_name.c_str(), par_value.db_data);
            break;

            default:
            res = PyObject_CallMethod(py_obj,
                    (char*)"SetExtraAttributePar", (char*)"iss", axis,
                    par_name.c_str(), par_value.str_data.c_str());
            break;
        }
        check_void_return(res,
            "Error reported from the controller SetExtraAttributePar method",
            "SetExtraAttributePar");
    }
    else
        throw_simple_exception(
                "Method SetExtraAttributePar is not implemented in controller",
                "SetExtraAttributePar");
}

//+-------------------------------------------------------------------------
//
// method : 		PyPseudoCounterController::GetExtraAttributePar
//
// description : 	Call the Python controller "GetExtraAttributePar" method
//
// argin : - axis: The Communication channel index within the controller
//		   - par_name: The parameter name
//
//--------------------------------------------------------------------------

Controller::CtrlData PyPseudoCounterController::GetExtraAttributePar(int32_t axis,
                                                        string &extra_par_name)
{
    Controller::CtrlData dres;

    if (get_extra_attribute == true)
    {
        AutoPythonGIL lo;

        PyObject *res;

        res = PyObject_CallMethod(py_obj,
                (char*)"GetExtraAttributePar",
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
                    (const char *)"The value returned by the controller code "
                                  "is neither a Python string, a Python float"
                                  " or a Python int as expected",
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

            err_list[1].origin =
                CORBA::string_dup("PyController::GetExtraAttributePar");
            err_list[1].desc = CORBA::string_dup(tmp_str.c_str());
            err_list[1].reason =
                CORBA::string_dup("PyCtrl_CantGetExtraAttrParameter");
            err_list[1].severity = Tango::ERR;

            throw Tango::DevFailed(err_list);
        }
        Py_DECREF(res);
    }
    else
        throw_simple_exception(
                "Method GetExtraAttributePar is not implemented in controller",
                "GetExtraAttributePar");

    return dres;
}

//+-------------------------------------------------------------------------
//
// method : 		PyPseudoCounterController::SendToCtrl
//
// description : 	Call the Python controller "SendToCtrl" method
//
// argin : - in_str: The input string to pass to the controller
//
//--------------------------------------------------------------------------

string PyPseudoCounterController::SendToCtrl(string &in_str)
{
    string returned_str(
    "Default string: The controller returns nothing or an invalid data type");

    if (send_to_ctrl == true)
    {
        AutoPythonGIL lo;

        PyObject *res;
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
        throw_simple_exception(
                "Method SendToCtrl is not implemented in controller",
                "SendToCtrl");

    return returned_str;
}

//+-------------------------------------------------------------------------
//
// method : 		PyPseudoCounterController::clear_method_flag
//
// description : 	Clear all the boolean flags used to memorize which
//					pre-defined method are implemented in this controller
//
//--------------------------------------------------------------------------

void PyPseudoCounterController::clear_method_flag()
{
    calc = false;
}

//+-------------------------------------------------------------------------
//
// method : 		PyPseudoCounterController::check_existing_method
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

void PyPseudoCounterController::check_existing_methods(PyObject *obj)
{
    base_check_existing_methods(obj);

    PyObject *met;

    if ((met = PyObject_GetAttrString(obj,"calc")) != NULL)
    {
        calc = true;
        Py_DECREF(met);
    }
    else
        PyErr_Clear();
}

int32_t PyPseudoCounterController::get_counter_nb_from_py()
{
    int32_t counter_nb;

    AutoPythonGIL lo;
    
    PyObject *counter_seq = PyObject_GetAttrString(py_obj,COUNTER_ROLES_ATTR);

    counter_nb = PySequence_Size(counter_seq);

    Py_DECREF(counter_seq);

    return counter_nb;
}

int32_t PyPseudoCounterController::get_pseudo_counter_nb_from_py()
{
    int32_t pseudo_counter_nb;

    AutoPythonGIL lo;
    
    PyObject *pseudo_counter_seq = PyObject_GetAttrString(py_obj,PSEUDO_COUNTER_ROLES_ATTR);

    pseudo_counter_nb = PySequence_Size(pseudo_counter_seq);

    Py_DECREF(pseudo_counter_seq);

    return pseudo_counter_nb;
}

extern "C"
{
    Controller *_create_PyPseudoCounterController(const char *inst,const char *cl_name,PyObject *mo,PyObject *prop)
    {
        return new PyPseudoCounterController(inst,cl_name,mo,prop);
    }
}
