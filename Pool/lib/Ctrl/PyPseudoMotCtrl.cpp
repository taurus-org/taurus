#include "PyUtils.h"
#include "PyPseudoMotCtrl.h"


using namespace std;

PyPseudoMotorController::PyPseudoMotorController(const char *inst,
                                                 const char *cl_name,
                                                 PyObject *module,
                                                 PyObject *prop_dict):
PyController(cl_name, module), PseudoMotorController(inst)
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
            (const char *)"PyPseudoMotorController::PyPseudoMotorController");
    }

    int insert_res = PyTuple_SetItem(arg_tuple,0,arg_str);
    if (insert_res != 0)
    {
        TangoSys_OMemStream o;
        o << "Can't build argument to create Python controller ";
        o << cl_name << ends;

        Tango::Except::throw_exception(
            (const char *)"Pool_CantCreatePyController",o.str(),
            (const char *)"PyPseudoMotorController::PyPseudoMotorController");
    }

    insert_res = PyTuple_SetItem(arg_tuple,1,prop_dict);
    if (insert_res != 0)
    {
        TangoSys_OMemStream o;
        o << "Can't build argument to create Python controller ";
        o << cl_name << ends;

        Tango::Except::throw_exception(
            (const char *)"Pool_CantCreatePyController",o.str(),
            (const char *)"PyPseudoMotorController::PyPseudoMotorController");
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
            CORBA::string_dup("PyPseudoMotorController::PyPseudoMotorController");
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
// method : 		PyPseudoMotorController::~PyPseudoMotorController
//
// description : 	This Python Pseudo Motor Controller class dtor
//
//--------------------------------------------------------------------------

PyPseudoMotorController::~PyPseudoMotorController()
{
    //cout << "[PyPseudoMotorController] class dtor" << endl;
    Py_DECREF(py_obj);
}

//+-------------------------------------------------------------------------
//
// method : 		PyPseudoController::CalcPhysical
//
// description : 	Calculates the physical motor position for the motor
//                  represented by axis based on the pseudo motor position and
//                  on the current physical motor positions.
//                  The calculated motor position will be appended to the end of
//                  the physical_pos vector.
//
// arg(s) : - axis [in]: the physical motor index for which the position will be
//                       calculated
//          - pseudo_pos [in]: the list of pseudo motor positions
//
//--------------------------------------------------------------------------
double PyPseudoMotorController::CalcPhysical(int32_t axis,vector<double> &pseudo_pos)
{
    PyObject *res;

    vector<double>::size_type pm_count = pseudo_pos.size();

    AutoPythonGIL lo;
    
    PyObject *arg_tuple = PyTuple_New(pm_count);

///------------------------------------------------------------------------
/// Build the arguments to call the python method
///
    for(vector<double>::size_type pm_index = 0 ; pm_index < pm_count; pm_index++)
    {
        PyObject *arg_double = PyFloat_FromDouble(pseudo_pos[pm_index]);
        int insert_res = PyTuple_SetItem(arg_tuple,pm_index,arg_double);

        if(insert_res != 0)
        {
            Py_DECREF(arg_tuple);
            Tango::Except::throw_exception(
                (const char *)"PyPseudoCtrl_PythonAllocError",
                (const char *)"Can't build argument to CalcPhysical Pseudo Python controller",
                (const char *)"PyPseudoController::CalcPhysical()");
        }
    }

///------------------------------------------------------------------------
/// Invoke the python method
///
    PyObject *method_name = PyString_FromString(CALC_PHYSICAL_METHOD);
    PyObject *arg_axis = PyLong_FromLong(axis);

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

        string tmp_str("Can't calculate physical position");

        err_list[1].origin = CORBA::string_dup("PyPseudoController::CalcPhysical");
        err_list[1].desc = CORBA::string_dup(tmp_str.c_str());
        err_list[1].reason = CORBA::string_dup("PyPseudoCtrl_CantCalcPhysical");
        err_list[1].severity = Tango::ERR;

        throw Tango::DevFailed(err_list);
    }

    double ret;

    if (get_py_number(res, ret))
    {
        Py_DECREF(res);
        return ret;
    }

    Py_DECREF(res);
    Tango::Except::throw_exception(
        (const char *)"PyPseudoCtrl_BadReturnElementInTuple",
        (const char *)"A tuple element returned by the controller code is not a Python float as expected",
        (const char *)"PyMotorController::CalcPhysical()");

    //quiet the compiler
    return ret;
}

//+-------------------------------------------------------------------------
//
// method : 		PyPseudoController::CalcPseudo
//
// description : 	Calculates the pseudo motor position for the pseudo motor
//                  represented by axis based on the current physical motor
//                  positions
//
// arg(s) : - axis [in]: the pseudo motor index for which the position will be
//                       calculated
//          - physical_pos [in]: the list of current physical motor positions
//          - pseudo_pos [out]: this parameter will contain the new calculated
//                              pseudo motor position
//
//--------------------------------------------------------------------------
double PyPseudoMotorController::CalcPseudo(int32_t axis,vector<double> &physical_pos)
{
    PyObject *res;

    vector<double>::size_type motor_count = physical_pos.size();

    AutoPythonGIL lo;
    
    PyObject *arg_axis = PyLong_FromLong(axis);
    PyObject *arg_tuple = PyTuple_New(motor_count);

    if(arg_tuple == NULL)
    {
        Tango::Except::throw_exception(
            (const char *)"PyPseudoCtrl_PythonAllocError",
            (const char *)"Can't build argument to CalcPseudo Python controller",
            (const char *)"PyPseudoController::CalcPseudo()");
    }

    for(vector<double>::size_type in_pos_index = 0 ; in_pos_index < motor_count; in_pos_index++)
    {
        PyObject *arg_double = PyFloat_FromDouble(physical_pos[in_pos_index]);
        int insert_res = PyTuple_SetItem(arg_tuple,in_pos_index,arg_double);

        if(insert_res != 0)
        {
            Py_DECREF(arg_tuple);
            Tango::Except::throw_exception(
                (const char *)"PyPseudoCtrl_PythonAllocError",
                (const char *)"Can't build argument to CalcPseudo Python controller",
                (const char *)"PyPseudoController::CalcPseudo()");
        }
    }

    PyObject *method_name = PyString_FromString(CALC_PSEUDO_METHOD);

    res = PyObject_CallMethodObjArgs(py_obj,method_name,arg_axis,arg_tuple,NULL);

    Py_DECREF(method_name);
    Py_DECREF(arg_tuple);
    Py_DECREF(arg_axis);

    if(res == NULL)
    {
        PyObject *ex_exec,*ex_value,*ex_tb;
        Tango::DevErrorList err_list;
        err_list.length(2);

        PyErr_Fetch(&ex_exec,&ex_value,&ex_tb);
        this->Py_init_dev_error(ex_exec,ex_value,ex_tb,err_list);

        string tmp_str("Can't calculate pseudo position");

        err_list[1].origin = CORBA::string_dup("PyPseudoController::CalcPseudo");
        err_list[1].desc = CORBA::string_dup(tmp_str.c_str());
        err_list[1].reason = CORBA::string_dup("PyPseudoCtrl_CantCalcPseudo");
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
        (const char *)"PyMotorController::CalcPseudo()");

    //quiet the compiler
    return ret;
}

void PyPseudoMotorController::CalcAllPhysical(vector<double> &pseudo_pos,
                                              vector<double> &physical_pos)
{
    PyObject *res;

    vector<double>::size_type pm_count = pseudo_pos.size();
    
    AutoPythonGIL lo;
    
    PyObject *arg_tuple = PyTuple_New(pm_count);

    if(arg_tuple == NULL)
    {
        Tango::Except::throw_exception(
            (const char *)"PyPseudoCtrl_PythonAllocError",
            (const char *)"Can't build argument to set Pseudo Python controller position",
            (const char *)"PyPseudoController::CalcAllPhysical()");
    }

    for(vector<double>::size_type pm_index = 0 ; pm_index < pm_count; pm_index++)
    {
        PyObject *arg_double = PyFloat_FromDouble(pseudo_pos[pm_index]);
        int insert_res = PyTuple_SetItem(arg_tuple,pm_index,arg_double);

        if(insert_res != 0)
        {
            Py_DECREF(arg_tuple);
            Tango::Except::throw_exception(
                (const char *)"PyPseudoCtrl_PythonAllocError",
                (const char *)"Can't build argument to set Pseudo Python controller position",
                (const char *)"PyPseudoController::CalcAllPhysical()");
        }
    }

    PyObject *method_name = PyString_FromString(CALC_ALL_PHYSICAL_METHOD);

    res = PyObject_CallMethodObjArgs(py_obj,method_name,arg_tuple,NULL);

    Py_DECREF(method_name);
    Py_DECREF(arg_tuple);

    if(res == NULL)
    {
        PyObject *ex_exec,*ex_value,*ex_tb;
        Tango::DevErrorList err_list;
        err_list.length(2);

        PyErr_Fetch(&ex_exec,&ex_value,&ex_tb);
        this->Py_init_dev_error(ex_exec,ex_value,ex_tb,err_list);

        string tmp_str("Can't set the position");

        err_list[1].origin = CORBA::string_dup("PyPseudoController::CalcAllPhysical");
        err_list[1].desc = CORBA::string_dup(tmp_str.c_str());
        err_list[1].reason = CORBA::string_dup("PyPseudoCtrl_CantSetPosition");
        err_list[1].severity = Tango::ERR;

        throw Tango::DevFailed(err_list);
    }

    int32_t motor_count = get_motor_nb_from_py();

    if(PySequence_Check(res) == 1)
    {
        int32_t res_motor_count = PySequence_Size(res);

        if(motor_count != res_motor_count)
        {
            Py_DECREF(res);
            TangoSys_OMemStream o;

            o << py_class_name << "::" << CALC_ALL_PHYSICAL_METHOD <<
                 " returns a sequence of " << res_motor_count << " elements. "
                 "It should return a sequence of " << motor_count << " elements"
                 " instead." << ends;

            Tango::Except::throw_exception(
                (const char *)"PyPseudoCtrl_BadReturnElementInTuple",o.str(),
                (const char *)"PyMotorController::CalcAllPhysical()");
        }

        if((int32_t)physical_pos.capacity() < motor_count)
            physical_pos.reserve(motor_count);

        for(int32_t motor_index = 0; motor_index < motor_count; motor_index++)
        {
            PyObject *pos = PySequence_GetItem(res, motor_index);

            double p;
            if (get_py_number(pos, p))
            {
                physical_pos[motor_index] = p;
            }
            else
            {
                Py_DECREF(pos);
                Py_DECREF(res);
                Tango::Except::throw_exception(
                    (const char *)"PyPseudoCtrl_BadReturnElementInTuple",
                    (const char *)"A tuple element returned by the controller code is not a Python number as expected",
                    (const char *)"PyMotorController::CalcAllPhysical()");
            }
            Py_DECREF(pos);
        }
    }
    else
    {
        // If we expect only one motor position as a result, we support receiving a double directly
        if(motor_count == 1)
        {
            double p;
            if (get_py_number(res, p))
            {
                physical_pos[0] = p;
            }
            else
            {
                Py_DECREF(res);
                Tango::Except::throw_exception(
                    (const char *)"PyPseudoCtrl_BadReturnSingleElement",
                    (const char *)"The return of the controller code is not a Python number as expected",
                    (const char *)"PyMotorController::CalcAllPhysical()");
            }
        }
        else
        {
            Py_DECREF(res);
            Tango::Except::throw_exception(
                (const char *)"PyPseudoCtrl_BadReturnType",
                (const char *)"The value returned by the controller code is not a Python Sequence as expected",
                (const char *)"PyMotorController::CalcAllPhysical()");
        }
    }

    Py_DECREF(res);
}

void PyPseudoMotorController::CalcAllPseudo(vector<double> &physical_pos,
                                            vector<double> &pseudo_pos)
{
    PyObject *res;

    vector<double>::size_type motor_count = physical_pos.size();
    vector<double>::size_type pm_count = get_pseudo_motor_nb_from_py();

    AutoPythonGIL lo;
    
    PyObject *arg_tuple = PyTuple_New(motor_count);

    if(arg_tuple == NULL)
    {
        Tango::Except::throw_exception(
            (const char *)"PyPseudoCtrl_PythonAllocError",
            (const char *)"Can't build argument to read Pseudo Python controller position",
            (const char *)"PyPseudoController::ReadAll()");
    }

    for(vector<double>::size_type motor_index = 0 ; motor_index < motor_count; motor_index++)
    {
        PyObject *arg_double = PyFloat_FromDouble(physical_pos[motor_index]);
        int insert_res = PyTuple_SetItem(arg_tuple,motor_index,arg_double);

        if(insert_res != 0)
        {
            Py_DECREF(arg_tuple);
            Tango::Except::throw_exception(
                (const char *)"PyPseudoCtrl_PythonAllocError",
                (const char *)"Can't build argument to read Pseudo Python controller position",
                (const char *)"PyPseudoController::ReadAll()");
        }
    }

    PyObject *method_name = PyString_FromString(CALC_ALL_PSEUDO_METHOD);

    res = PyObject_CallMethodObjArgs(py_obj,method_name,arg_tuple,NULL);

    Py_DECREF(method_name);
    Py_DECREF(arg_tuple);

    if(res == NULL)
    {
        PyObject *ex_exec,*ex_value,*ex_tb;
        Tango::DevErrorList err_list;
        err_list.length(2);

        PyErr_Fetch(&ex_exec,&ex_value,&ex_tb);
        this->Py_init_dev_error(ex_exec,ex_value,ex_tb,err_list);

        string tmp_str("Can't read the position");

        err_list[1].origin = CORBA::string_dup("PyPseudoController::ReadAll");
        err_list[1].desc = CORBA::string_dup(tmp_str.c_str());
        err_list[1].reason = CORBA::string_dup("PyPseudoCtrl_CantReadAll");
        err_list[1].severity = Tango::ERR;

        throw Tango::DevFailed(err_list);
    }

    if(pseudo_pos.capacity() < pm_count)
        pseudo_pos.reserve(pm_count);

    if(PyTuple_Check(res) == 1)
    {
        for(vector<double>::size_type pm_index = 0; pm_index < pm_count; pm_index++)
        {
            PyObject *pos = PyTuple_GetItem(res, pm_index);

            double p;
            if (get_py_number(pos,p))
            {
                pseudo_pos[pm_index] = p;
            }
            else
            {
                Py_DECREF(res);
                Tango::Except::throw_exception(
                    (const char *)"PyPseudoCtrl_BadReturnElementInTuple",
                    (const char *)"A tuple element returned by the controller code is not a Python number as expected",
                    (const char *)"PyMotorController::ReadAll()");
            }
        }
    }
    else if(PyList_Check(res) == 1)
    {
        for(vector<double>::size_type pm_index = 0; pm_index < pm_count; pm_index++)
        {
            PyObject *pos = PyList_GetItem(res, pm_index);
            double p;
            if (get_py_number(pos,p))
            {
                pseudo_pos[pm_index] = p;
            }
            else
            {
                Py_DECREF(res);
                Tango::Except::throw_exception(
                    (const char *)"PyPseudoCtrl_BadReturnElementInList",
                    (const char *)"A list element returned by the controller code is not a Python number as expected",
                    (const char *)"PyMotorController::ReadAll()");
            }
        }
    }
    else
    {
        // If we expect only one motor position as a result, we support receiving a double directly
        if(pm_count == 1)
        {
            double p;
            if (get_py_number(res,p))
            {
                pseudo_pos[0] = p;
            }
            else
            {
                Py_DECREF(res);
                Tango::Except::throw_exception(
                    (const char *)"PyPseudoCtrl_BadReturnSingleElement",
                    (const char *)"The return of the controller code is not a Python number as expected",
                    (const char *)"PyMotorController::ReadAll()");
            }
        }
        else
        {
            Py_DECREF(res);
            Tango::Except::throw_exception(
                (const char *)"PyPseudoCtrl_BadReturnType",
                (const char *)"The value returned by the controller code is not a Python sequence as expected",
                (const char *)"PyMotorController::ReadAll()");
        }
    }

    Py_DECREF(res);
}


//+-------------------------------------------------------------------------
//
// method : 		PyPseudoMotorController::SetExtraAttributePar
//
// description : 	Call the Python controller "SetExtraAttribute" method
//
// argin : - axis: The Communication channel	 index within the controller
//		   - par_name: The parameter name
//		   - par_value: The parameter value
//
//--------------------------------------------------------------------------

void PyPseudoMotorController::SetExtraAttributePar(int32_t axis,string &par_name,
                                                Controller::CtrlData &par_value)
{
    if (set_extra_attribute == true)
    {
        PyObject *res;
        
        AutoPythonGIL lo;
        
        switch (par_value.data_type)
        {
            case Controller::BOOLEAN:
            res = PySetExtraAttributeBool(py_obj,axis,par_name,
                                          par_value.bo_data);
            break;

            case Controller::INT32:
            res = PyObject_CallMethod(py_obj,
                    (char*)"SetExtraAttributePar",
                    (char*)"isi", axis, par_name.c_str(), par_value.int32_data);
            break;

            case Controller::DOUBLE:
            res = PyObject_CallMethod(py_obj,
                    (char*)"SetExtraAttributePar",
                    (char*)"isd", axis,	par_name.c_str(), par_value.db_data);
            break;

            default:
            res = PyObject_CallMethod(py_obj,
                    (char*)"SetExtraAttributePar",
                    (char*)"iss", axis, par_name.c_str(),
                    par_value.str_data.c_str());
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
// method : 		PyPseudoMotorController::GetExtraAttributePar
//
// description : 	Call the Python controller "GetExtraAttributePar" method
//
// argin : - axis: The Communication channel index within the controller
//		   - par_name: The parameter name
//
//--------------------------------------------------------------------------

Controller::CtrlData PyPseudoMotorController::GetExtraAttributePar(int32_t axis,
                                                        string &extra_par_name)
{
    Controller::CtrlData dres;

    if (get_extra_attribute == true)
    {
        PyObject *res;
    
        AutoPythonGIL lo;
        
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
                    dres.int32_data = (int32_t)PyInt_AsLong(res);
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
// method : 		PyPseudoMotorController::SendToCtrl
//
// description : 	Call the Python controller "SendToCtrl" method
//
// argin : - in_str: The input string to pass to the controller
//
//--------------------------------------------------------------------------

string PyPseudoMotorController::SendToCtrl(string &in_str)
{
    string returned_str(
    "Default string: The controller returns nothing or an invalid data type");

    if (send_to_ctrl == true)
    {
        PyObject *res;
        
        AutoPythonGIL lo;
        
        res = PyObject_CallMethod(py_obj,
                (char*)"SendToCtrl",
                (char*)"s", in_str.c_str());
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
// method : 		PyPseudoMotorController::clear_method_flag
//
// description : 	Clear all the boolean flags used to memorize which
//					pre-defined method are implemented in this controller
//
//--------------------------------------------------------------------------

void PyPseudoMotorController::clear_method_flag()
{
    calc_pseudo = false;
    calc_physical = false;
    calc_all_pseudo = false;
    calc_all_physical = false;
}

//+-------------------------------------------------------------------------
//
// method : 		PyPseudoMotorController::check_existing_method
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

void PyPseudoMotorController::check_existing_methods(PyObject *obj)
{
    base_check_existing_methods(obj);

    PyObject *met;

    if ((met = PyObject_GetAttrString(obj,"calc_pseudo")) != NULL)
    {
        calc_pseudo = true;
        Py_DECREF(met);
    }
    else
        PyErr_Clear();

    if ((met = PyObject_GetAttrString(obj,"calc_physical")) != NULL)
    {
        calc_physical = true;
        Py_DECREF(met);
    }
    else
        PyErr_Clear();

    if ((met = PyObject_GetAttrString(obj,"calc_all_pseudo")) != NULL)
    {
        calc_all_pseudo = true;
        Py_DECREF(met);
    }
    else
        PyErr_Clear();

    if ((met = PyObject_GetAttrString(obj,"calc_all_physical")) != NULL)
    {
        calc_all_physical = true;
        Py_DECREF(met);
    }
    else
        PyErr_Clear();
}

int32_t PyPseudoMotorController::get_pseudo_motor_nb_from_py()
{
    int32_t pseudo_motor_nb;

    AutoPythonGIL lo;
    
    PyObject *py_pm_nb = PyObject_CallMethod(py_obj,
            (char*)GET_PSEUDO_MOTOR_NB, NULL);

    pseudo_motor_nb = PyInt_AsLong(py_pm_nb);

    Py_DECREF(py_pm_nb);

    return pseudo_motor_nb;
}

int32_t PyPseudoMotorController::get_motor_nb_from_py()
{
    int32_t motor_nb;
    
    AutoPythonGIL lo;
    
    PyObject *motor_seq = PyObject_GetAttrString(py_obj,MOTOR_ROLES_ATTR);

    motor_nb = PySequence_Size(motor_seq);

    Py_DECREF(motor_seq);

    return motor_nb;
}

extern "C"
{
    Controller *_create_PyPseudoMotorController(const char *inst,const char *cl_name,PyObject *mo,PyObject *prop)
    {
        return new PyPseudoMotorController(inst,cl_name,mo,prop);
    }
}
