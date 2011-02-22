//+=============================================================================
//
// file :         ExternalFiCa.cpp
//
// description :  C++ source for the Pool and its commands. 
//                The class is derived from Device. It represents the
//                CORBA servant object which will be accessed from the
//                network. All commands which can be executed on the
//                Pool are implemented in this file.
//
// project :      TANGO Device Server
//
// copyleft :     Alba synchrotron
//				  Campus Universitari de Bellaterra. Universitat Autònoma de Barcelona
// 				  08193 Bellaterra, Barcelona
//                Spain
//
//-=============================================================================

#include "PyUtils.h"
#include "ExternalFiCa.h"
#include "PoolClass.h"
#include <ltdl.h>

namespace Pool_ns
{

#ifndef D_STREAM
#define D_STREAM cout5
#endif

//-----------------------------------------------------------------------------
//
//					The ExternalFiCa class
//
//-----------------------------------------------------------------------------

//+----------------------------------------------------------------------------
//
// method : 		ExternalFiCa::ExternalFiCa()
// 
// description : 	constructor for ExternalFiCa class
//
// in : - type : The generic file_class name (class_name/inst name in lowercase letter)
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------
ExternalFiCa::ExternalFiCa(const string &type, Pool *dev):
Tango::LogAdapter(dev), name(type), monitor(type.c_str(),this),
 my_file(NULL), id(Pool_ns::InvalidId)
{
//	cout << "In the ExternalFiCa ctor" << endl;
}

//+----------------------------------------------------------------------------
//
// method : 		ExternalFiCa::ExternalFiCa()
// 
// description : 	constructor for ExternalFiCa class
//
// in : - type : The generic file_class name (class_name/inst name in lowercase letter)
//      - f_name : The class file name (cpp lib or python module)
//		- class_name : The class name (case dependant)
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

ExternalFiCa::ExternalFiCa(const string &type, const string &f_name, const string &class_name, Pool *dev):
Tango::LogAdapter(dev), name(type), monitor(type.c_str(), this),
my_file(NULL), id(Pool_ns::InvalidId)
{
//	cout << "In the ExternalFiCa ctor" << endl;

}

//+----------------------------------------------------------------------------
//
// method : 		ExternalFiCa::~ExternalFiCa()
// 
// description : 	destructor for ExternalFiCa class
//
//-----------------------------------------------------------------------------

ExternalFiCa::~ExternalFiCa()
{
//	cout << "In the ExternalFiCa dtor" << endl;
}

Language ExternalFiCa::get_language()
{
    return my_file->get_language();
}

//+----------------------------------------------------------------------------
//
// method : 		ExternalFiCa::check_python()
// 
// description : 	check if a file name is defined within all the
//					directories defined in the PYTHONPATH env.
//					variable. It throws an exception if the file does
//					not exist
//
// in : - class_name : The Python class name
//		- f_name : The module file name
// 
//-----------------------------------------------------------------------------

void ExternalFiCa::check_python(const std::string &class_name)
{
    static_cast<PyExternalFile *>(my_file)->check_py(class_name.c_str());
}

//-----------------------------------------------------------------------------
//
//					The PoolLock class
//
//-----------------------------------------------------------------------------

void PoolLock::get_monitor()
{
    int th_id = omni_thread::self()->id();
    D_STREAM << "\t[START] PoolLock::get_monitor() for "
             << my_external_fica->get_name()
             << " " << my_external_fica->get_file()->get_name()
             << " in TH " << th_id
             << " lock_count "<< lock_count << "..." << endl;

    if (is_lock_enabled())
        mon.get_monitor(); 

    ++lock_count;

    if (my_external_fica->get_language() == PYTHON)
    {
        try
        {
            if (lock_count == 1)
                pygil = new AutoPythonGIL;
        }
        catch(...)
        {
            if (is_lock_enabled())
                mon.rel_monitor();
            throw;
        }
    }
    D_STREAM << "\t[DONE] PoolLock::get_monitor() for "
             << my_external_fica->get_name()
             << " " << my_external_fica->get_file()->get_name()
             << " in TH " << th_id
             << " lock_count "<< lock_count << endl;;
}

void PoolLock::rel_monitor()
{
    int th_id = omni_thread::self()->id();
    D_STREAM << "\t[START] PoolLock::rel_monitor() for "
             << my_external_fica->get_name()
             << " " << my_external_fica->get_file()->get_name()
             << " in TH " << th_id
             << " lock_count "<< lock_count << "..." << endl;

    --lock_count;

    if (my_external_fica->get_language() == PYTHON)
    {
        try
        {
            if (lock_count == 0)
                SAFE_DELETE(pygil);
        }
        catch(...)
        {
            if (is_lock_enabled())
                mon.rel_monitor();
            throw;
        }
    }
    
    if (is_lock_enabled())
        mon.rel_monitor();

    D_STREAM << "\t[DONE] PoolLock::rel_monitor() for "
             << my_external_fica->get_name()
             << " " << my_external_fica->get_file()->get_name()
             << " in TH " << th_id
             << " lock_count "<< lock_count << endl;;
}

} // End of Pool_ns namespacce
