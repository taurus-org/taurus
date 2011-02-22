//+=============================================================================
//
// file :         PyMotCtrlFile.cpp
//
// description :  C++ source for the Pool and its commands.
//                The class is derived from Device. It represents the
//                CORBA servant object which will be accessed from the
//                network. All commands which can be executed on the
//                Pool are implemented in this file.
//
// project :      TANGO Device Server
//
// $Author: tiagocoutinho $
//
// $Revision: 298 $
//
// $Log$
// Revision 1.10  2007/08/20 06:37:32  tcoutinho
// development commit
//
// Revision 1.9  2007/08/17 13:07:30  tcoutinho
// - pseudo motor restructure
// - pool base dev class restructure
// - initial commit for pseudo counters
//
// Revision 1.8  2007/07/17 11:41:57  tcoutinho
// replaced comunication with communication
//
// Revision 1.7  2007/07/12 13:14:51  tcoutinho
// - added Open, Close, ReadLine methods
//
// Revision 1.6  2007/07/02 14:46:37  tcoutinho
// first stable comunication channel commit
//
// Revision 1.5  2007/06/27 08:56:28  tcoutinho
// first commit for comuncation channels
//
// Revision 1.4  2007/02/08 08:51:17  etaurel
// - Many changes. I don't remember the list
//
// Revision 1.3  2007/01/26 08:37:01  etaurel
// - We now have a first release of ZeroDController
//
// Revision 1.2  2007/01/04 11:55:04  etaurel
// - Added the CounterTimer controller
//
// Revision 1.1  2006/11/07 15:06:35  etaurel
// - Now, the pool really supports different kind of controllers (cpp and py)
//
//
// copyleft :     Alba synchrotron
//				  Campus Universitari de Bellaterra. Universitat Autònoma de Barcelona
// 				  08193 Bellaterra, Barcelona
//                Spain
//
//-=============================================================================

#include "PyMotCtrlFile.h"
#include "Pool.h"
#include "PyUtils.h"

namespace Pool_ns
{

//+----------------------------------------------------------------------------
//
// method : 		PyUndefCtrlFile::PyUndefCtrlFile()
//
// description : 	constructor for PyUndefCtrlFile class
//
// in : - f_name : The controller class file name (cpp lib or python module)
//		- class_name : The class name (case dependant)
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

PyUndefCtrlFile::PyUndefCtrlFile(const string &f_name)
:PyCtrlFile(f_name,"Undefined")
{
}

//+----------------------------------------------------------------------------
//
// method : 		PyUndefCtrlFile::~PyUndefCtrlFile()
//
// description : 	destructor for PyUndefCtrlFile class
//
//-----------------------------------------------------------------------------

PyUndefCtrlFile::~PyUndefCtrlFile()
{
//	cout << "In the PyUndefCtrlFile dtor for " << name << endl;
}

//+----------------------------------------------------------------------------
//
// method : 		PyUndefCtrlFile::get_super_class()
//
// description : 	Returns the super class name which all the valid classes
//                  in this file must inherit in order to be considered valid classes
//
// Returns the super class name.
//
//-----------------------------------------------------------------------------

const char *PyUndefCtrlFile::get_super_class()
{
    return "Undefined";
}

//+----------------------------------------------------------------------------
//
// method : 		PyUndefCtrlFile::check_py_methods()
//
// description : 	Returns the super class name which all the valid classes
//                  in this file must inherit in order to be considered valid classes
//
// Returns the super class name.
//
//-----------------------------------------------------------------------------

void PyUndefCtrlFile::check_py_methods(PyObject *class_obj)
{
}


//+----------------------------------------------------------------------------
//
// method : 		PyMotCtrlFile::PyMotCtrlFile()
//
// description : 	constructor for PyMotCtrlFile class
//
// in : - f_name : The controller class file name (cpp lib or python module)
//		- class_name : The class name (case dependant)
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

PyMotCtrlFile::PyMotCtrlFile(const string &f_name)
:PyCtrlFile(f_name,"Motor")
{
}

PyMotCtrlFile::PyMotCtrlFile(PyUndefCtrlFile &undef_ctrl)
:PyCtrlFile(undef_ctrl,"Motor")
{
}

//+----------------------------------------------------------------------------
//
// method : 		PyMotCtrlFile::~PyMotCtrlFile()
//
// description : 	destructor for CtrlFile class
//
//-----------------------------------------------------------------------------

PyMotCtrlFile::~PyMotCtrlFile()
{
//	cout << "In the PyMotCtrlFile dtor for " << name << endl;
}

//+----------------------------------------------------------------------------
//
// method : 		PyMotCtrlFile::get_super_class()
//
// description : 	Returns the super class name which all the valid classes
//                  in this file must inherit in order to be considered valid classes
//
// Returns the super class name.
//
//-----------------------------------------------------------------------------

const char *PyMotCtrlFile::get_super_class()
{
    return "MotorController";
}

//+----------------------------------------------------------------------------
//
// method : 		PyMotCtrlFile::check_py_methods()
//
// description : 	Returns the super class name which all the valid classes
//                  in this file must inherit in order to be considered valid classes
//
// Returns the super class name.
//
//-----------------------------------------------------------------------------

void PyMotCtrlFile::check_py_methods(PyObject *class_obj)
{
//
// Check that methods AddDevice, DeleteDevice, ReadOne and StateOne
// are defined and that they are callable
//

    check_py_method(class_obj,"AddDevice");
    check_py_method(class_obj,"DeleteDevice");
    check_py_method(class_obj,"ReadOne");
    check_py_method(class_obj,"StateOne");

//
// Check that either StartOne or StartAll methods are defined (and callable)
//

    int nb_except = 0;
    try
    {
        check_py_method(class_obj,"StartOne");
    }
    catch (Tango::DevFailed &) {nb_except++;}

    try
    {
        check_py_method(class_obj,"StartAll");
    }
    catch (Tango::DevFailed &) {nb_except++;}

    if (nb_except == 2)
    {
        TangoSys_OMemStream o;
        o << "Neither methods StartOne or StartAll are defined in class ";
        o << PyString_AsString(class_obj) << ends;

        Tango::Except::throw_exception(
                (const char *)PY_CONTROLLER_NOT_VALID,o.str(),
                (const char *)"PyCtrlFile::check_py_methods");
    }
}


//+----------------------------------------------------------------------------
//
// method : 		PyPseudoMotCtrlFile::PyPseudoMotCtrlFile()
//
// description : 	constructor for PyPseudoMotCtrlFile class
//
// in : - f_name : The controller class file name (cpp lib or python module)
//		- class_name : The class name (case dependant)
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

PyPseudoMotCtrlFile::PyPseudoMotCtrlFile(const string &f_name)
:PyCtrlFile(f_name, "PseudoMotor")
{
    include_MaxDevice = false;
}

PyPseudoMotCtrlFile::PyPseudoMotCtrlFile(PyUndefCtrlFile &undef_ctrl)
:PyCtrlFile(undef_ctrl, "PseudoMotor")
{
    include_MaxDevice = false;
}

//+----------------------------------------------------------------------------
//
// method : 		PyPseudoMotCtrlFile::~PyPseudoMotCtrlFile()
//
// description : 	destructor for CtrlFile class
//
//-----------------------------------------------------------------------------

PyPseudoMotCtrlFile::~PyPseudoMotCtrlFile()
{
//	cout << "In the PyPseudoMotCtrlFile dtor for " << name << endl;
}

//+----------------------------------------------------------------------------
//
// method : 		PyPseudoMotCtrlFile::get_super_class()
//
// description : 	Returns the super class name which all the valid classes
//                  in this file must inherit in order to be considered valid classes
//
// Returns the super class name.
//
//-----------------------------------------------------------------------------

const char *PyPseudoMotCtrlFile::get_super_class()
{
    return "PseudoMotorController";
}

//+----------------------------------------------------------------------------
//
// method : 		PyPseudoMotCtrlFile::get_info()
//
// description : 	Retrieves the pseudo information for a given type of pseudo
//                  motors (ex.: pseudo description, number and description
//                  of motors, parameters, etc)
//
// arg(s) : - class_name : The pseudo motor class for which to retrieve the
//                         information
//
// Returns the pseudo information.
//
//-----------------------------------------------------------------------------

void PyPseudoMotCtrlFile::get_info(const string &class_name,vector<string> &info)
{
    PyCtrlFile::get_info(class_name, info);
    get_pseudo_info(class_name,info);
}

//+----------------------------------------------------------------------------
//
// method : 		PyPseudoMotCtrlFile::get_info()
//
// description : 	Retrieves the pseudo information for a given type of pseudo
//                  motors (ex.: pseudo description, number and description
//                  of motors, parameters, etc)
//
// arg(s) : - class_name : The pseudo motor class for which to retrieve the
//                         information
//
// Returns the pseudo information.
//
//-----------------------------------------------------------------------------

void PyPseudoMotCtrlFile::get_info(const string &ctrl_class,const string &ctrl_instance,
                                   vector<string> &info)
{
    PyCtrlFile::get_info(ctrl_class,ctrl_instance,info);
    get_pseudo_info(ctrl_class,info);
}

//+----------------------------------------------------------------------------
//
// method : 		PyPseudoMotCtrlFile::get_pseudo_info()
//
// description : 	Helper method. Retrieves the pseudo information for a
//                  specific pseudo motor (ex.: number of motors and their roles
//                  and number of pseudo motors and their roles)
//
// arg(s) : - instance : The python pseudo motor instance object
//
// Returns the pseudo information.
//
//-----------------------------------------------------------------------------
void PyPseudoMotCtrlFile::get_pseudo_info(const string &class_name,vector<string> &info)
{
    AutoPythonGIL apl = AutoPythonGIL();

    vector<string> motor_roles;
    get_sequence_value(class_name, MOTOR_ROLES_ATTR, motor_roles);

    stringstream motor_roles_nb;
    motor_roles_nb << motor_roles.size();
    info.push_back(motor_roles_nb.str());

    info.insert(info.end(),motor_roles.begin(),motor_roles.end());
    //for(unsigned long ul = 0; ul < motor_roles.size(); ul++)
    //	info.push_back(motor_roles[ul]);

    vector<string> pseudo_motor_roles;
    get_sequence_value(class_name, PSEUDO_MOTOR_ROLES_ATTR, pseudo_motor_roles);

    if (pseudo_motor_roles.size() == 0)
    {
        pseudo_motor_roles.push_back(class_name);
    }

    stringstream pseudo_motor_roles_nb;
    pseudo_motor_roles_nb << pseudo_motor_roles.size();
    info.push_back(pseudo_motor_roles_nb.str());

    info.insert(info.end(),pseudo_motor_roles.begin(),pseudo_motor_roles.end());
}

//+----------------------------------------------------------------------------
//
// method : 		PyPseudoMotCtrlFile::check_py_methods()
//
// description : 	Returns the super class name which all the valid classes
//                  in this file must inherit in order to be considered valid classes
//
// Returns the super class name.
//
//-----------------------------------------------------------------------------

void PyPseudoMotCtrlFile::check_py_methods(PyObject *class_obj)
{
    check_py_method(class_obj,CALC_PSEUDO_METHOD);
    check_py_method(class_obj,CALC_PHYSICAL_METHOD);
}

//+----------------------------------------------------------------------------
//
// method : 		PyCoTiCtrlFile::PyCoTiCtrlFile()
//
// description : 	constructor for PyCoTiCtrlFile class
//
// in : - f_name : The controller class file name (cpp lib or python module)
//		- class_name : The class name (case dependant)
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

PyCoTiCtrlFile::PyCoTiCtrlFile(const string &f_name)
:PyCtrlFile(f_name,"CounterTimer")
{
}

PyCoTiCtrlFile::PyCoTiCtrlFile(PyUndefCtrlFile &undef_ctrl)
:PyCtrlFile(undef_ctrl,"CounterTimer")
{
}

//+----------------------------------------------------------------------------
//
// method : 		PyCoTiCtrlFile::~PyCoTiCtrlFile()
//
// description : 	destructor for CtrlFile class
//
//-----------------------------------------------------------------------------

PyCoTiCtrlFile::~PyCoTiCtrlFile()
{
//	cout << "In the PyCoTiCtrlFile dtor for " << name << endl;
}

//+----------------------------------------------------------------------------
//
// method : 		PyCoTiCtrlFile::get_super_class()
//
// description : 	Returns the super class name which all the valid classes
//                  in this file must inherit in order to be considered valid classes
//
// Returns the super class name.
//
//-----------------------------------------------------------------------------

const char *PyCoTiCtrlFile::get_super_class()
{
    return "CounterTimerController";
}

//+----------------------------------------------------------------------------
//
// method : 		PyCoTiCtrlFile::check_py_methods()
//
// description : 	Returns the super class name which all the valid classes
//                  in this file must inherit in order to be considered valid classes
//
// Returns the super class name.
//
//-----------------------------------------------------------------------------

void PyCoTiCtrlFile::check_py_methods(PyObject *class_obj)
{
//
// Check that methods AddDevice, DeleteDevice, ReadOne and StateOne
// are defined and that they are callable
//

    check_py_method(class_obj,"AddDevice");
    check_py_method(class_obj,"DeleteDevice");
    check_py_method(class_obj,"ReadOne");
    check_py_method(class_obj,"StateOne");

//
// Check that either StartOneCT or StartAllCT methods are defined (and callable)
//

    int nb_except = 0;
    try
    {
        check_py_method(class_obj,"StartOneCT");
    }
    catch (Tango::DevFailed &) {nb_except++;}

    try
    {
        check_py_method(class_obj,"StartAllCT");
    }
    catch (Tango::DevFailed &) {nb_except++;}

    if (nb_except == 2)
    {
        TangoSys_OMemStream o;
        o << "Neither methods StartOneCT or StartAllCT are defined in class " << PyString_AsString(class_obj) << ends;

        Tango::Except::throw_exception((const char *)PY_CONTROLLER_NOT_VALID,o.str(),
                                       (const char *)"PyCoTiCtrlFile::check_py_methods");
    }

//
// Check that either LoadOne or LoadAll methods are defined (and callable)
//

    nb_except = 0;
    try
    {
        check_py_method(class_obj,"LoadOne");
    }
    catch (Tango::DevFailed &) {nb_except++;}

    try
    {
        check_py_method(class_obj,"LoadAll");
    }
    catch (Tango::DevFailed &) {nb_except++;}

    if (nb_except == 2)
    {
        TangoSys_OMemStream o;
        o << "Neither methods LoadOne or LoadAll are defined in class " << PyString_AsString(class_obj) << ends;

        Tango::Except::throw_exception((const char *)PY_CONTROLLER_NOT_VALID,o.str(),
                                       (const char *)"PyCoTiCtrlFile::check_py_methods");
    }
}

//+----------------------------------------------------------------------------
//
// method : 		PyZeroDCtrlFile::PyZeroDCtrlFile()
//
// description : 	constructor for PyZeroDCtrlFile class
//
// in : - f_name : The controller class file name (cpp lib or python module)
//		- class_name : The class name (case dependant)
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

PyZeroDCtrlFile::PyZeroDCtrlFile(const string &f_name)
:PyCtrlFile(f_name,"ZeroDExpChannel")
{
}

PyZeroDCtrlFile::PyZeroDCtrlFile(PyUndefCtrlFile &undef_ctrl)
:PyCtrlFile(undef_ctrl,"ZeroDExpChannel")
{
}

//+----------------------------------------------------------------------------
//
// method : 		PyZeroDCtrlFile::~PyZeroDCtrlFile()
//
// description : 	destructor for CtrlFile class
//
//-----------------------------------------------------------------------------

PyZeroDCtrlFile::~PyZeroDCtrlFile()
{
//	cout << "In the PyZeroDCtrlFile dtor for " << name << endl;
}

//+----------------------------------------------------------------------------
//
// method : 		PyZeroDCtrlFile::get_super_class()
//
// description : 	Returns the super class name which all the valid classes
//                  in this file must inherit in order to be considered valid classes
//
// Returns the super class name.
//
//-----------------------------------------------------------------------------

const char *PyZeroDCtrlFile::get_super_class()
{
    return "ZeroDController";
}

//+----------------------------------------------------------------------------
//
// method : 		PyZeroDCtrlFile::check_py_methods()
//
// description : 	Returns the super class name which all the valid classes
//                  in this file must inherit in order to be considered valid classes
//
// Returns the super class name.
//
//-----------------------------------------------------------------------------

void PyZeroDCtrlFile::check_py_methods(PyObject *class_obj)
{
//
// Check that methods AddDevice, DeleteDevice, ReadOne and StateOne
// are defined and that they are callable
//

    check_py_method(class_obj,"AddDevice");
    check_py_method(class_obj,"DeleteDevice");
    check_py_method(class_obj,"ReadOne");
    check_py_method(class_obj,"StateOne");
}



//+----------------------------------------------------------------------------
//
// method : 		PyOneDCtrlFile::PyOneDCtrlFile()
// 
// description : 	constructor for PyOneDCtrlFile class
//
// in : - f_name : The controller class file name (cpp lib or python module)
//		- class_name : The class name (case dependant)
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

PyOneDCtrlFile::PyOneDCtrlFile(const string &f_name)
:PyCtrlFile(f_name,"OneDExpChannel")
{
}

PyOneDCtrlFile::PyOneDCtrlFile(PyUndefCtrlFile &undef_ctrl)
:PyCtrlFile(undef_ctrl,"OneDExpChannel")
{
}

//+----------------------------------------------------------------------------
//
// method : 		PyOneDCtrlFile::~PyOneDCtrlFile()
// 
// description : 	destructor for CtrlFile class
//
//-----------------------------------------------------------------------------

PyOneDCtrlFile::~PyOneDCtrlFile()
{
//	cout << "In the PyOneDCtrlFile dtor for " << name << endl;
}

//+----------------------------------------------------------------------------
//
// method : 		PyOneDCtrlFile::get_super_class()
// 
// description : 	Returns the super class name which all the valid classes 
//                  in this file must inherit in order to be considered valid classes
//                  
// Returns the super class name.
//
//-----------------------------------------------------------------------------

const char *PyOneDCtrlFile::get_super_class()
{
    return "OneDController";
}

//+----------------------------------------------------------------------------
//
// method : 		PyOneDCtrlFile::check_py_methods()
//
//-----------------------------------------------------------------------------

void PyOneDCtrlFile::check_py_methods(PyObject *class_obj)
{
//
// Check that methods AddDevice, DeleteDevice, ReadOne and StateOne
// are defined and that they are callable
//

    check_py_method(class_obj,"AddDevice");
    check_py_method(class_obj,"DeleteDevice");
    check_py_method(class_obj,"ReadOne");
    check_py_method(class_obj,"StateOne");
}



//+----------------------------------------------------------------------------
//
// method : 		PyTwoDCtrlFile::PyTwoDCtrlFile()
// 
// description : 	constructor for PyTwoDCtrlFile class
//
// in : - f_name : The controller class file name (cpp lib or python module)
//		- class_name : The class name (case dependant)
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

PyTwoDCtrlFile::PyTwoDCtrlFile(const string &f_name)
:PyCtrlFile(f_name,"TwoDExpChannel")
{
}

PyTwoDCtrlFile::PyTwoDCtrlFile(PyUndefCtrlFile &undef_ctrl)
:PyCtrlFile(undef_ctrl,"TwoDExpChannel")
{
}

//+----------------------------------------------------------------------------
//
// method : 		PyTwoDCtrlFile::~PyTwoDCtrlFile()
// 
// description : 	destructor for CtrlFile class
//
//-----------------------------------------------------------------------------

PyTwoDCtrlFile::~PyTwoDCtrlFile()
{
//	cout << "In the PyTwoDCtrlFile dtor for " << name << endl;
}

//+----------------------------------------------------------------------------
//
// method : 		PyTwoDCtrlFile::get_super_class()
// 
// description : 	Returns the super class name which all the valid classes 
//                  in this file must inherit in order to be considered valid classes
//                  
// Returns the super class name.
//
//-----------------------------------------------------------------------------

const char *PyTwoDCtrlFile::get_super_class()
{
    return "TwoDController";
}

//+----------------------------------------------------------------------------
//
// method : 		PyTwoDCtrlFile::check_py_methods()
//
//-----------------------------------------------------------------------------

void PyTwoDCtrlFile::check_py_methods(PyObject *class_obj)
{
//
// Check that methods AddDevice, DeleteDevice, ReadOne and StateOne
// are defined and that they are callable
//

    check_py_method(class_obj,"AddDevice");
    check_py_method(class_obj,"DeleteDevice");
    check_py_method(class_obj,"ReadOne");
    check_py_method(class_obj,"StateOne");
}


//+----------------------------------------------------------------------------
//
// method : 		PyPseudoCoCtrlFile::PyPseudoCoCtrlFile()
//
// description : 	constructor for PyPseudoCoCtrlFile class
//
// in : - f_name : The controller class file name (cpp lib or python module)
//		- class_name : The class name (case dependant)
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

PyPseudoCoCtrlFile::PyPseudoCoCtrlFile(const string &f_name)
:PyCtrlFile(f_name, "PseudoCounter")
{
    include_MaxDevice = false;
}

PyPseudoCoCtrlFile::PyPseudoCoCtrlFile(PyUndefCtrlFile &undef_ctrl)
:PyCtrlFile(undef_ctrl, "PseudoCounter")
{
    include_MaxDevice = false;
}

//+----------------------------------------------------------------------------
//
// method : 		PyPseudoCoCtrlFile::~PyPseudoCoCtrlFile()
//
// description : 	destructor for CtrlFile class
//
//-----------------------------------------------------------------------------

PyPseudoCoCtrlFile::~PyPseudoCoCtrlFile()
{
//	cout << "In the PyPseudoCoCtrlFile dtor for " << name << endl;
}

//+----------------------------------------------------------------------------
//
// method : 		PyPseudoCoCtrlFile::get_super_class()
//
// description : 	Returns the super class name which all the valid classes
//                  in this file must inherit in order to be considered valid classes
//
// Returns the super class name.
//
//-----------------------------------------------------------------------------

const char *PyPseudoCoCtrlFile::get_super_class()
{
    return "PseudoCounterController";
}

//+----------------------------------------------------------------------------
//
// method : 		PyPseudoCoCtrlFile::get_info()
//
// description : 	Retrieves the pseudo information for a given type of pseudo
//                  motors (ex.: pseudo description, number and description
//                  of motors, parameters, etc)
//
// arg(s) : - class_name : The pseudo motor class for which to retrieve the
//                         information
//
// Returns the pseudo information.
//
//-----------------------------------------------------------------------------

void PyPseudoCoCtrlFile::get_info(const string &class_name,vector<string> &info)
{
    PyCtrlFile::get_info(class_name,info);
    get_pseudo_info(class_name,info);
}

//+----------------------------------------------------------------------------
//
// method : 		PyPseudoCoCtrlFile::get_info()
//
// description : 	Retrieves the pseudo information for a given type of pseudo
//                  motors (ex.: pseudo description, number and description
//                  of motors, parameters, etc)
//
// arg(s) : - class_name : The pseudo motor class for which to retrieve the
//                         information
//
// Returns the pseudo information.
//
//-----------------------------------------------------------------------------

void PyPseudoCoCtrlFile::get_info(const string &ctrl_class,const string &ctrl_instance,
                                   vector<string> &info)
{
    PyCtrlFile::get_info(ctrl_class,ctrl_instance,info);
    get_pseudo_info(ctrl_class,info);
}

//+----------------------------------------------------------------------------
//
// method : 		PyPseudoCoCtrlFile::get_pseudo_info()
//
// description : 	Helper method.
//                  Retrieves the pseudo information for a given type of pseudo
//                  counter (ex.: description, counter number and roles, etc).
//                  In summary, everything except the properties.
//
// arg(s) : - class_name : The pseudo counter class for which to retrieve the
//                         information
//
// Returns the pseudo information.
//
//-----------------------------------------------------------------------------
void PyPseudoCoCtrlFile::get_pseudo_info(const string &class_name,vector<string> &info)
{
    AutoPythonGIL apl = AutoPythonGIL();

    vector<string> counter_roles;
    get_sequence_value(class_name, COUNTER_ROLES_ATTR, counter_roles);

    stringstream counter_roles_nb;
    counter_roles_nb << counter_roles.size();
    info.push_back(counter_roles_nb.str());

    info.insert(info.end(),counter_roles.begin(),counter_roles.end());
    //for(unsigned long ul = 0; ul < counter_roles.size(); ul++)
    //	info.push_back(counter_roles[ul]);

    vector<string> pseudo_counter_roles;
    get_sequence_value(class_name, PSEUDO_COUNTER_ROLES_ATTR, pseudo_counter_roles);

    if (pseudo_counter_roles.size() == 0)
    {
        pseudo_counter_roles.push_back(class_name);
    }

    stringstream pseudo_counter_roles_nb;
    pseudo_counter_roles_nb << pseudo_counter_roles.size();
    info.push_back(pseudo_counter_roles_nb.str());

    info.insert(info.end(),pseudo_counter_roles.begin(),pseudo_counter_roles.end());
}

//+----------------------------------------------------------------------------
//
// method : 		PyPseudoCoCtrlFile::check_py_methods()
//
// description : 	Returns the super class name which all the valid classes
//                  in this file must inherit in order to be considered valid classes
//
// Returns the super class name.
//
//-----------------------------------------------------------------------------

void PyPseudoCoCtrlFile::check_py_methods(PyObject *class_obj)
{
    check_py_method(class_obj,CALC_METHOD);
}

//+----------------------------------------------------------------------------
//
// method : 		PyComCtrlFile::PyComCtrlFile()
//
// description : 	constructor for PyComCtrlFile class
//
// in : - f_name : The controller class file name (cpp lib or python module)
//		- class_name : The class name (case dependant)
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

PyComCtrlFile::PyComCtrlFile(const string &f_name)
:PyCtrlFile(f_name,"Communication")
{
}

PyComCtrlFile::PyComCtrlFile(PyUndefCtrlFile &undef_ctrl)
:PyCtrlFile(undef_ctrl,"Communication")
{
}

//+----------------------------------------------------------------------------
//
// method : 		PyComCtrlFile::~PyComCtrlFile()
//
// description : 	destructor for CtrlFile class
//
//-----------------------------------------------------------------------------

PyComCtrlFile::~PyComCtrlFile()
{
//	cout << "In the PyComCtrlFile dtor for " << name << endl;
}


//+----------------------------------------------------------------------------
//
// method : 		PyComCtrlFile::get_super_class()
//
// description : 	Returns the super class name which all the valid classes
//                  in this file must inherit in order to be considered valid classes
//
// Returns the super class name.
//
//-----------------------------------------------------------------------------

const char *PyComCtrlFile::get_super_class()
{
    return "CommunicationController";
}

//+----------------------------------------------------------------------------
//
// method : 		PyComCtrlFile::check_py_methods()
//
// description : 	Returns the super class name which all the valid classes
//                  in this file must inherit in order to be considered valid classes
//
// Returns the super class name.
//
//-----------------------------------------------------------------------------

void PyComCtrlFile::check_py_methods(PyObject *class_obj)
{
//
// Check that methods AddDevice, DeleteDevice, ReadOne and StateOne
// are defined and that they are callable
//

    check_py_method(class_obj,"AddDevice");
    check_py_method(class_obj,"DeleteDevice");
    check_py_method(class_obj,"OpenOne");
    check_py_method(class_obj,"CloseOne");
    check_py_method(class_obj,"ReadOne");
    check_py_method(class_obj,"ReadLineOne");
    check_py_method(class_obj,"WriteOne");
    check_py_method(class_obj,"WriteReadOne");
    check_py_method(class_obj,"StateOne");
}


//+----------------------------------------------------------------------------
//
// method : 		PyIORegisterCtrlFile::PyIORegisterCtrlFile()
//
// description : 	constructor for PyIORegisterCtrlFile class
//
// in : - f_name : The controller class file name (cpp lib or python module)
//		- class_name : The class name (case dependant)
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

PyIORegisterCtrlFile::PyIORegisterCtrlFile(const string &f_name)
:PyCtrlFile(f_name,"IORegister")
{
}

PyIORegisterCtrlFile::PyIORegisterCtrlFile(PyUndefCtrlFile &undef_ctrl)
:PyCtrlFile(undef_ctrl,"IORegister")
{
}

//+----------------------------------------------------------------------------
//
// method : 		PyIORegisterCtrlFile::~PyIORegisterCtrlFile()
//
// description : 	destructor for CtrlFile class
//
//-----------------------------------------------------------------------------

PyIORegisterCtrlFile::~PyIORegisterCtrlFile()
{
//	cout << "In the PyIORegisterCtrlFile dtor for " << name << endl;
}


//+----------------------------------------------------------------------------
//
// method : 		PyIORegisterCtrlFile::get_super_class()
//
// description : 	Returns the super class name which all the valid classes
//                  in this file must inherit in order to be considered valid classes
//
// Returns the super class name.
//
//-----------------------------------------------------------------------------

const char *PyIORegisterCtrlFile::get_super_class()
{
    return "IORegisterController";
}


//+----------------------------------------------------------------------------
//
// method : 		PyIORegisterCtrlFile::get_info()
//
// description : 	Retrieves the information about predefined values for a given type of 
//                  input/output register.
//
// arg(s) : - class_name : The input/output register class for which to retrieve the
//                         information
//
// Returns the information.
//
//-----------------------------------------------------------------------------

void PyIORegisterCtrlFile::get_info(const string &class_name,vector<string> &info)
{
    PyCtrlFile::get_info(class_name, info);
    get_ioregister_info(class_name,info);
}

//+----------------------------------------------------------------------------
//
// method : 		PyIORegisterCtrlFile::get_info()
//
// description : 	Retrieves the information about predefined values for a given type of
//                  input/output register
//
// arg(s) : - class_name : The input/output register class for which to retrieve the
//                         information
//
// Returns the information.
//
//-----------------------------------------------------------------------------

void PyIORegisterCtrlFile::get_info(const string &ctrl_class,const string &ctrl_instance,
                                   vector<string> &info)
{
    PyCtrlFile::get_info(ctrl_class,ctrl_instance,info);
    get_ioregister_info(ctrl_class,info);
}

//+----------------------------------------------------------------------------
//
// method : 		PyIORegisterCtrlFile::get_ioregister_info()
//
// description : 	Helper method. Retrieves the information about predefined values for a
//                  specific input/output register.
//
// arg(s) : - instance : The python input/output register instance object
//
// Returns the information.
//
//-----------------------------------------------------------------------------

void PyIORegisterCtrlFile::get_ioregister_info(const string &class_name,vector<string> &info)
{
    AutoPythonGIL apl = AutoPythonGIL();

    vector<string> predefined_values;

    stringstream predefined_values_nb;

    try{
        get_sequence_value(class_name, IOREGISTER_PREDEFINED_VALUES_ATTR, predefined_values);

        predefined_values_nb << predefined_values.size()/2;
        info.push_back(predefined_values_nb.str());

        info.insert(info.end(),predefined_values.begin(),predefined_values.end());
    } catch (Tango::DevFailed &) {

        predefined_values_nb << 0;
        info.push_back(predefined_values_nb.str());

    }

}




//+----------------------------------------------------------------------------
//
// method : 		PyIORegisterCtrlFile::check_py_methods()
//
// description : 	Returns the super class name which all the valid classes
//                  in this file must inherit in order to be considered valid classes
//
// Returns the super class name.
//
//-----------------------------------------------------------------------------

void PyIORegisterCtrlFile::check_py_methods(PyObject *class_obj)
{
//
// Check that methods AddDevice, DeleteDevice, ReadOne and StateOne
// are defined and that they are callable
//

    check_py_method(class_obj,"AddDevice");
    check_py_method(class_obj,"DeleteDevice");
    check_py_method(class_obj,"ReadOne");
    check_py_method(class_obj,"WriteOne");
    check_py_method(class_obj,"StateOne");
}


//+----------------------------------------------------------------------------
//
// method : 		PyConstraintFile::PyConstraintFile()
//
// description : 	constructor for PyConstraintFile class
//
// in : - f_name : The controller class file name (cpp lib or python module)
//		- class_name : The class name (case dependant)
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

PyConstraintFile::PyConstraintFile(const string &f_name)
:PyCtrlFile(f_name,"Constraint")
{
}

PyConstraintFile::PyConstraintFile(PyUndefCtrlFile &undef_ctrl)
:PyCtrlFile(undef_ctrl,"Constraint")
{
}

//+----------------------------------------------------------------------------
//
// method : 		PyConstraintFile::~PyConstraintFile()
//
// description : 	destructor for CtrlFile class
//
//-----------------------------------------------------------------------------

PyConstraintFile::~PyConstraintFile()
{
//	cout << "In the PyConstraintFile dtor for " << name << endl;
}

//+----------------------------------------------------------------------------
//
// method : 		PyConstraintFile::get_super_class()
//
// description : 	Returns the super class name which all the valid classes
//                  in this file must inherit in order to be considered valid classes
//
// Returns the super class name.
//
//-----------------------------------------------------------------------------

const char *PyConstraintFile::get_super_class()
{
    return "Constraint";
}

//+----------------------------------------------------------------------------
//
// method : 		PyConstraintFile::check_py_methods()
//
// description : 	Returns the super class name which all the valid classes
//                  in this file must inherit in order to be considered valid classes
//
// Returns the super class name.
//
//-----------------------------------------------------------------------------

void PyConstraintFile::check_py_methods(PyObject *class_obj)
{
//
// Check that methods AddDevice, DeleteDevice, ReadOne and StateOne
// are defined and that they are callable
//

    check_py_method(class_obj,"isAllowed");
}

} // End of Pool_ns namespacce
