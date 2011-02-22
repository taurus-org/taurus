//+=============================================================================
//
// file :         PyCtrlFile.cpp
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
// Revision 1.19  2007/08/23 10:32:44  tcoutinho
// - basic pseudo counter check
// - some fixes regarding pseudo motors
//
// Revision 1.18  2007/08/17 13:07:30  tcoutinho
// - pseudo motor restructure
// - pool base dev class restructure
// - initial commit for pseudo counters
//
// Revision 1.17  2007/07/31 13:27:02  tcoutinho
// improved error message
//
// Revision 1.16  2007/07/31 07:55:40  tcoutinho
// fix bug 5 : Additional information for controllers
//
// Revision 1.15  2007/07/30 11:01:00  tcoutinho
// Fix bug 5 : Additional information for controllers
//
// Revision 1.14  2007/06/13 15:18:58  etaurel
// - Fix memory leak
//
// Revision 1.13  2007/05/10 09:36:24  etaurel
// - Fix some bugs after first test with the real IcePap V2
//
// Revision 1.12  2007/05/07 09:46:44  etaurel
// - Small changes for Python 2.5 compatibility
//
// Revision 1.11  2007/02/08 08:51:17  etaurel
// - Many changes. I don't remember the list
//
// Revision 1.10  2007/01/16 14:32:22  etaurel
// - Coomit after a first release with CT
//
// Revision 1.9  2006/12/18 11:37:10  etaurel
// - Features are only boolean values invisible from the external world
// - ExtraFeature becomes ExtraAttribute with data type of the old features
//
// Revision 1.8  2006/11/07 14:57:10  etaurel
// - Now, the pool really supports different kind of controllers (cpp and py)
//
// Revision 1.7  2006/11/03 15:48:59  etaurel
// - Miscellaneous changes that I don't remember
//
// Revision 1.6  2006/10/30 08:38:02  etaurel
// - Fix bug in property default value management
//
// Revision 1.5  2006/10/27 14:43:03  etaurel
// - New management of the MaxDevice stuff
// - SendToCtrl cmd added
// - Some bug fixed in prop management
//
// Revision 1.4  2006/10/20 15:37:31  etaurel
// - First release with GetControllerInfo command supported and with
// controller properties
//
// Revision 1.3  2006/10/06 13:36:40  tcoutinho
// changed info command names, added properties functionality
//
// Revision 1.2  2006/09/28 09:22:25  etaurel
// - End of the ControllerClassList attribute implementation
//
// Revision 1.1  2006/09/27 15:15:50  etaurel
// - ExternalFile and CtrlFile has been splitted in several classes:
//   ExternalFile, CppCtrlFile, PyExternalFile and PyCtrlFile
//
// Revision 1.15  2006/09/22 15:31:00  etaurel
// - Miscellaneous changes
//
// Revision 1.14  2006/09/22 09:57:55  tcoutinho
// bug fix: check_py_methods should return void and should throw an exception.
//
// Revision 1.13  2006/09/22 07:57:07  tcoutinho
// - Changes to the python in xxxFile classes
//
// Revision 1.12  2006/09/19 09:57:11  etaurel
// - Commit after the controller, motor and motor_group test sequences works after the merge
//
// Revision 1.11  2006/09/18 10:32:18  etaurel
// - Commit after merge with pseudo-motor branch
//
// Revision 1.10  2006/06/15 15:36:30  etaurel
// - many changes after due to first test suite only on controller related stuff!!!
//
// Revision 1.9  2006/06/12 10:28:57  etaurel
// - Many changes dur to bug fixes found when writing test units...
//
// Revision 1.8  2006/05/25 09:13:47  etaurel
// - Stop Pool startup sequence in case Python LoadModule failed
// - Add logging possibility in the CtrlFiCa and CtrlFile classes
//
// Revision 1.7  2006/05/24 14:12:49  etaurel
// - Again many changes
//
// Revision 1.6  2006/04/27 07:29:41  etaurel
// - Many changes after the travel to Boston
//
// Revision 1.5  2006/03/20 08:25:52  etaurel
// - Commit changes before changing the Motor interface
//
// Revision 1.4  2006/03/17 13:39:53  etaurel
// - Before modifying commands
//
// Revision 1.3  2006/03/16 08:05:44  etaurel
// - Added code for the ControllerCode load and unload commands
// - Test and debug InnitController cmd with motor attached to the controller
//
// Revision 1.2  2006/03/14 14:54:09  etaurel
// - Again new changes in the internal structure
//
// Revision 1.1  2006/03/14 08:25:09  etaurel
// - Change the way objects are aorganized within the pool device
//
//
// copyleft :     Alba synchrotron
//				  Campus Universitari de Bellaterra. Universitat Autònoma de Barcelona
// 				  08193 Bellaterra, Barcelona
//                Spain
//
//-=============================================================================

#include "PyCtrlFile.h"
#include "Pool.h"
#include <ltdl.h>

namespace Pool_ns
{

//+----------------------------------------------------------------------------
//
// method : 		PyCtrlFile::PyCtrlFile()
// 
// description : 	constructor for CtrlFile class
//
// in : - f_name : The controller class file name (cpp lib or python module)
//		- class_name : The class name (case dependant)
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

PyCtrlFile::PyCtrlFile(const string &f_name,const char *ctrl_dev_type)
:PyExternalFile(f_name), py_inter_lib_ptr(NULL), include_MaxDevice(true)
{
    string ctrl_type(ctrl_dev_type);
    ctrl_obj_type = DevicePool::str_2_CtrlType(ctrl_type);
    
//
// Build Python interface shared lib name from the
// device type
//

    if (ctrl_obj_type != UNDEF_CTRL)
        load_py_inter_lib(ctrl_type);
}

PyCtrlFile::PyCtrlFile(PyCtrlFile &undef_ctrl, const char *ctrl_dev_type)
:PyExternalFile(undef_ctrl),py_inter_lib_ptr(NULL),include_MaxDevice(true)
{
    string ctrl_type(ctrl_dev_type);
    ctrl_obj_type = DevicePool::str_2_CtrlType(ctrl_type);
}

//+----------------------------------------------------------------------------
//
// method : 		PyCtrlFile::~PyCtrlFile()
// 
// description : 	destructor for CtrlFile class
//
//-----------------------------------------------------------------------------

PyCtrlFile::~PyCtrlFile()
{
//	cout << "In the PyCtrlFile dtor for " << name << endl;

    if (py_inter_lib_ptr != NULL)
        lt_dlclose(py_inter_lib_ptr);
}

//+----------------------------------------------------------------------------
//
// method : 		PyCtrlFile::load_code()
// 
// description : 	Load the code. Also load the Cpp shared lib cpp 
//                  to python interface
//
//-----------------------------------------------------------------------------
        
void PyCtrlFile::load_code()
{
    // Nothing to be done here.
}

//+----------------------------------------------------------------------------
//
// method : 		PyCtrlFile::get_info()
// 
// description : 	Retrieves the information for a given type of controller class.
//                  
// arg(s) : - ctrl_class [in]: The controller class for which to retrieve the information
//          - info [out]: The controller information related to the given controller class
//
// Returns the controller class information.
//
//-----------------------------------------------------------------------------

void PyCtrlFile::get_info(const std::string &ctrl_class,vector<string> &info)
{
    AutoPythonGIL apl = AutoPythonGIL();
    
    get_py_doc(ctrl_class,info);
    get_py_gender(ctrl_class,info);
    get_py_model(ctrl_class,info);
    get_py_organization(ctrl_class,info);
    
    CtrlFile::get_prop_info(ctrl_class,info);
}

//+----------------------------------------------------------------------------
//
// method : 		PyCtrlFile::get_info()
// 
// description : 	Retrieves the information for a given type of controller class.
//                  
// arg(s) : - ctrl_class [in]: The controller class for which to retrieve the information
//          - ctrl_instance [in]: The controller instance for which to retrieve the information
//          - info [out]: The controller information related to the given controller class
//
// Returns the controller class information.
//
//-----------------------------------------------------------------------------

void PyCtrlFile::get_info(const std::string &ctrl_class, const std::string &ctrl_instance, 
                          std::vector<std::string> &info)
{
    AutoPythonGIL apl = AutoPythonGIL();
    
    get_py_doc(ctrl_class,info);
    get_py_gender(ctrl_class,info);
    get_py_model(ctrl_class,info);
    get_py_organization(ctrl_class,info);
    
    ControllerPool &ctrl_pool = DevicePool::get_instance()->get_controller(ctrl_instance, true);
    Controller *ctrl = ctrl_pool.get_controller();
    PyMotorController *my_ctrl = static_cast<PyMotorController *>(ctrl);
    
    if (my_ctrl != NULL)
    {
        PyObject *instance_obj = my_ctrl->get_ctrl_py_obj();
        PyExternalFile::get_prop_info(instance_obj,info);
    }
    else
    {
        TangoSys_OMemStream o;
        o << "Controller for class " << ctrl_class << " with instance ";
        o << ctrl_instance << " is NULL !"  << ends;

        Tango::Except::throw_exception(
                (const char *)PY_CONTROLLER_NOT_VALID,o.str(),
                (const char *)"PyCtrlFile::get_info");
    }
}

//+----------------------------------------------------------------------------
//
// method : 		PyCtrlFile::get_info_ex()
// 
// description : 	Retrieves the information for a given type of controller 
//                  class.
//                  
// arg(s) : - ctrl_class [in]: The controller class for which to retrieve the 
//                             information
//          - info [out]: The controller information related to the given 
//                        controller class
//
// Returns the controller class information.
//
//-----------------------------------------------------------------------------

void PyCtrlFile::get_info_ex(const std::string &ctrl_class, Tango::DevVarCharArray *info_ex)
{
    vector<string> info;
    get_info(ctrl_class,info);
    
    {
        AutoPythonGIL apl = AutoPythonGIL();
        
        get_py_image(ctrl_class,info);
        get_py_logo(ctrl_class,info);
        get_py_icon(ctrl_class,info);
    }
    
    vecinfo_to_chararray(info,info_ex);
    
}

//+----------------------------------------------------------------------------
//
// method : 		PyCtrlFile::get_info_ex()
// 
// description : 	Retrieves the information for a given type of controller 
//                  class.
//                  
// arg(s) : - ctrl_class [in]: The controller class for which to retrieve the 
//                             information
//          - ctrl_instance [in]: The controller instance for which to retrieve 
//                                the information
//          - info [out]: The controller information related to the given 
//                        controller class
//
// Returns the controller class information.
//
//-----------------------------------------------------------------------------

void PyCtrlFile::get_info_ex(const std::string &ctrl_class, const std::string &ctrl_instance, 
                             Tango::DevVarCharArray *info_ex)
{
    vector<string> info;
    get_info(ctrl_class,ctrl_instance,info);

    {
        AutoPythonGIL apl = AutoPythonGIL();

        get_py_image(ctrl_class,info);
        get_py_logo(ctrl_class,info);
        get_py_icon(ctrl_class,info);
    }
    
    vecinfo_to_chararray(info,info_ex);
}

void PyCtrlFile::get_py_elem(const std::string &class_name, const char *elem_name,
                             vector<string> &info, const char *dft)
{
    PyObject *class_obj = get_py_valid_class(class_name.c_str());

    if(class_obj == NULL)
    {
        TangoSys_OMemStream o;
        o << "The python class " << class_name << " was not found" << ends;
        Tango::Except::throw_exception(
                (const char *)"Pool_CantLocatePythonClass",o.str(),
                (const char *)"PyCtrlFile::get_py_elem()");	
    }	
    
    PyObject *elem = PyObject_GetAttrString(class_obj, (char*)elem_name);
    
    if(elem == NULL)
    {
        PyErr_Clear();
        Py_DECREF(class_obj);
        info.push_back(dft);
    }
    else
    {
        PyObject *py_str = PyObject_Str(elem);
        string value = PyString_AsString(py_str);
        
        info.push_back(value);
        
        Py_DECREF(elem);
        Py_DECREF(py_str);
        Py_DECREF(class_obj);
    }
}

void PyCtrlFile::get_py_gender(const std::string &class_name,vector<string> &info)
{
    get_py_elem(class_name,"gender",info,DEFAULT_GENDER);
}

void PyCtrlFile::get_py_model(const std::string &class_name,vector<string> &info)
{
    get_py_elem(class_name,"model",info,DEFAULT_MODEL);
}

void PyCtrlFile::get_py_organization(const std::string &class_name,vector<string> &info)
{
    get_py_elem(class_name,"organization",info,DEFAULT_ORGANIZATION);
}

void PyCtrlFile::get_py_image(const std::string &class_name,vector<string> &info)
{
    get_py_elem(class_name,"image",info,"");
}

void PyCtrlFile::get_py_logo(const std::string &class_name,vector<string> &info)
{
    get_py_elem(class_name,"logo",info,"");
}

void PyCtrlFile::get_py_icon(const std::string &class_name,vector<string> &info)
{
    get_py_elem(class_name,"icon",info,"");
}

//+----------------------------------------------------------------------------
//
// method : 		PyCtrlFile::load_py_inter_lib()
// 
// description : 	Build Python interface shared lib name from the device 
//                  type name.
//
//-----------------------------------------------------------------------------
void PyCtrlFile::load_py_inter_lib(const std::string &dev_type)
{
    if (py_inter_lib_ptr == NULL)
    {
        string lib_name = get_py_inter_lib_name(dev_type);
        
//
// Load the Python cpp interface shared lib
//

        py_inter_lib_ptr = lt_dlopen(lib_name.c_str()/*,RTLD_NOW*/);
        if (py_inter_lib_ptr == NULL)
        {
            TangoSys_OMemStream o;

            cout << "Trying to load Python interface shared library " << lib_name;
            o << "Trying to load Python interface shared library " << lib_name;
            const char *err = lt_dlerror();
            
            if(err != NULL)
            {
                cout << " returns error: " << err << endl;
                o << " returns error: " << err << ends;
            }
            else
            {
                cout << " returns unknown error!" << endl;
                o << " returns unknown error!" << ends;
            }

            Tango::Except::throw_exception(
                (const char *)"Pool_CantLoadPyControllerInterLibrary",o.str(),
                (const char *)"PyCtrlFile::load_py_inter_lib");
        }
    }
}

//+----------------------------------------------------------------------------
//
// method :             PyCtrlFile::get_py_inter_lib_name()
//
// description :        Build Python controller interface shared lib name from controller
//                  device type name.
//
// arg(s) : - ctrl_dev_type : The controller device type.
//
// Returns the python interface shared library name.
//
//-----------------------------------------------------------------------------

string PyCtrlFile::get_py_inter_lib_name(const std::string &ctrl_dev_type)
{

//
// Build lib name
//

    string lib_name("Py" + ctrl_dev_type + "Ctrl.la");

//
// Get all the directories in the PoolPath
//

    vector<string> &paths = DevicePool::get_instance()->get_pool_path();
        
//
// Get list of .la files in each directories of the pool path
//

    vector<string> cpp_files;
    vector<string>::iterator path_ite;
            
    for (path_ite = paths.begin();path_ite != paths.end(); path_ite++)
    {
        DevicePool::get_files_with_extension(*path_ite,".la",cpp_files);
        for (unsigned long loop = 0;loop < cpp_files.size();loop++)
        {
            string name_from_path = cpp_files[loop].substr(cpp_files[loop].find_last_of('/') + 1);
            if (name_from_path == lib_name)
            {
                return cpp_files[loop];
            }
        }
    }
    
    if (path_ite == paths.end())
    {
        TangoSys_OMemStream o;
        o << "No Python interface library found for device of type " << ctrl_dev_type << " in your PoolPath!";
        o << "Check that " << lib_name << " is in your PoolPath" << ends;

        Tango::Except::throw_exception((const char *)"Pool_CantLoadPyControllerInterLibrary",o.str(),
                                       (const char *)"PyCtrlFile::get_py_inter_lib_name");
    }
    
    string quiet_compil;
    return quiet_compil;
}

//+----------------------------------------------------------------------------
//
// method : 		PyCtrlFile::get_MaxDevice()
// 
// description : 	Retrieves the MaxDevice data member from python controller
//					class
//                  
// arg(s) : - class_name [in]: The controller class for which to retrieve the information
//
//-----------------------------------------------------------------------------

int32_t PyCtrlFile::get_MaxDevice(const std::string &class_name)
{
    //AutoPythonGIL apl = AutoPythonGIL();
    
//
// Obtain the python class object 
//
    
    PyObject *pPyClass = get_py_valid_class(class_name.c_str());
    
    if(pPyClass == NULL)
    {
        TangoSys_OMemStream o;
        o << "The python class " << class_name << " was not found" << ends;
        Tango::Except::throw_exception(
                (const char *)"Pool_CantLocatePythonClass",o.str(),
                (const char *)"PyCtrlFile::get_MaxDevice()");	
    }

//
// Build the description
// 

    int32_t max_dev;
    PyObject *descr = PyObject_GetAttrString(pPyClass, "MaxDevice");
     
    if (descr == NULL)
    {
        PyErr_Clear();
        
        descr = PyObject_CallMethod(pPyClass,(char*)"get_MaxDevice", NULL);
        
        if (descr == NULL)
        {
            PyErr_Clear();
            max_dev = -1;
        }
    }

    if (descr != NULL)
    {
        if (PyInt_Check(descr) == 0)
            max_dev = -1;
        else
        {
            max_dev = PyInt_AsLong(descr);
        }
    }
    
    Py_XDECREF(descr);
    Py_DECREF(pPyClass);
    
    return max_dev;
}

//+----------------------------------------------------------------------------
//
// method : 		PyCtrllFile::get_prop_info()
// 
// description : 	Retrieves the information about properties for a given class.
//                  
// arg(s) : - class_name [in]: The class for which to retrieve the information
//          - info [out]: The properties information related to the given class
//
// Returns the properties class information.
//
//-----------------------------------------------------------------------------

void PyCtrlFile::get_prop_info(const std::string &class_name, vector<PropertyData*> &info)
{

//
// Clean vector in case of
//

    if (info.empty() == false)
    {
        for (unsigned long loop = 0;loop < info.size();loop++)
            delete info[loop];
        info.clear();
    }
        
//
// First, get the MaxDevice property
//
    if(include_MaxDevice == true)
    {
        string prop_name("MaxDevice");
        string prop_type("DevLong");
        string prop_desc("The maximum number of device supported by the controller");
            
        PropertyData *prop_data = new PropertyData(prop_name,prop_type,prop_desc);
            
        int32_t max_dev = get_MaxDevice(class_name);
        if (max_dev != -1)
        {
            prop_data->has_dft_value = true;
            prop_data->set_value(max_dev);
            prop_data->save_default_value();
        }
        else
            prop_data->has_dft_value = false;
            
        info.push_back(prop_data);
    }

//
// Then, add other properties
//
    
    PyExternalFile::get_prop_info(class_name,info);
}

//+----------------------------------------------------------------------------
//
// method : 		PyCtrllFile::get_extra_attr_dec()
// 
// description : 	Retrieves all the definition of the controller extra
//					attributes
//                  
// arg(s) : - class_name [in]: The class for which to retrieve the information
//          - sym_name [in]: The dictionnary name
//			- sym_value [out] : The vector where extra attribute definition has to be
//								stored
//
//-----------------------------------------------------------------------------

void PyCtrlFile::get_extra_attr_dec(const std::string &class_name,const char *sym_name,vector<PoolExtraAttr> &sym_value)
{
    sym_value.clear();	
    PyObject *py_class = get_py_class(class_name.c_str());
    
    PyObject *dict = PyObject_GetAttrString(py_class,(char *)sym_name);
    if (dict == NULL)
    {
        PyErr_Clear();
        Py_DECREF(py_class);
        return;
    }
    
    if (PyDict_Check(dict) == false)
    {
        Py_DECREF(dict);
        Py_DECREF(py_class);
        
        TangoSys_OMemStream o;
        o << "Object " << sym_name << " is not a dictionnary!!!" << ends;
        
        Tango::Except::throw_exception((const char *)"Pool_PythonDictNotFound",o.str(),
                (const char *)"PyExternalFile::get_extra_attr_dec");
    }

//
// Iterate over the dictionnary
//
    
    PyObject *key, *dict_value;
#if PY_VERSION_HEX < 0x02050000
    int pos= 0;
#else
    Py_ssize_t pos = 0;
#endif
    
    while(PyDict_Next(dict, &pos, &key, &dict_value)) 
    {
        PoolExtraAttr x_attr_info;
            
//
// Get the name of the extra attribute
//
        PyObject *key_name = PyObject_Str(key);
        string name_ext_attr = PyString_AsString(key_name);
        
//
// Check if the dictionnary value is itself a dictionary containning at least the keys for 
// 'Type' and 'R/W Type'.
//

        if(!PyDict_Check(dict_value))
        {
            Py_DECREF(key_name);
            Py_DECREF(dict);
            Py_DECREF(py_class);
            
            TangoSys_OMemStream o;
            o << "Invalid extra attribute declaration for extra attribute  " << name_ext_attr;
            o << ". The dictionary value is not itself a dictionary" << ends;			
            Tango::Except::throw_exception((const char *)"Pool_InvalidPythonDict",o.str(),
                                           (const char *)"PyCtrlFile::get_extra_attr_dec()");
        }
        x_attr_info.ExtraAttr_name = name_ext_attr;
        
//
// Get the extra attribute data 'Type'
//	
    
        PyObject *type_value = PyDict_GetItemString(dict_value,EXT_ATTR_TYPE_KEY);
        if(type_value == NULL || !PyString_Check(type_value))
        {
            Py_DECREF(key_name);
            Py_DECREF(dict);
            Py_DECREF(py_class);
            
            TangoSys_OMemStream o;
            o << "Invalid extra attribute declaration for extra attribute " << name_ext_attr;
            o << ". The extra attribute data type is not correctly defined" << ends;
            Tango::Except::throw_exception((const char *)"Pool_InvalidPythonDict",o.str(),
                                           (const char *)"PyCtrlFile::get_extra_attr_dec()");				
        }
        PyObject *type_name = PyObject_Str(type_value);
        string type_str = PyString_AsString(type_name);
        
//
// Check that the data type is correct
//

        transform(type_str.begin(),type_str.end(),type_str.begin(),::tolower);
        string::size_type pos = type_str.find('.');
        string real_type;
        if (pos != string::npos)
            real_type = type_str.substr(pos + 1);
        else
            real_type = type_str;

        if (real_type == "devboolean")
            x_attr_info.ExtraAttr_data_type = BOOLEAN;
        else if (real_type == "devlong")
            x_attr_info.ExtraAttr_data_type = LONG;
        else if (real_type == "devdouble")
            x_attr_info.ExtraAttr_data_type = DOUBLE;
        else if (real_type == "devstring")
            x_attr_info.ExtraAttr_data_type = STRING;
        else
        {
            Py_DECREF(key_name);
            Py_DECREF(type_name);
            Py_DECREF(dict);
            Py_DECREF(py_class);
            
            TangoSys_OMemStream o;
            o << "Invalid extra attribute declaration for extra attribute " << name_ext_attr;
            o << ". The extra attribute data type is not one of the allowed data type" << ends;
            Tango::Except::throw_exception((const char *)"Pool_InvalidPythonDict",o.str(),
                                           (const char *)"PyCtrlFile::get_extra_attr_dec()");				
        }
                
//
// Get the extra attribute 'R/W Type'
//	
            
        PyObject *rw_type_value = PyDict_GetItemString(dict_value,EXT_ATTR_RWTYPE_KEY);
        if(rw_type_value == NULL || !PyString_Check(rw_type_value))
        {
            Py_DECREF(key_name);
            Py_DECREF(type_name);
            Py_DECREF(dict);
            Py_DECREF(py_class);
            
            TangoSys_OMemStream o;
            o << "Invalid extra attribute declaration for extra attribute" << name_ext_attr;
            o << ". The extra attribute R/W type is not correctly defined" << ends;
            Tango::Except::throw_exception((const char *)"Pool_InvalidPythonDict",o.str(),
                                           (const char *)"PyExternalFile::get_extra_attr_dec()");				
        }
        PyObject *rw_type_str = PyObject_Str(rw_type_value);
        string rw_type = PyString_AsString(rw_type_str);

//
// Check that the R/W type is correct
//

        transform(rw_type.begin(),rw_type.end(),rw_type.begin(),::tolower);
        pos = rw_type.find('.');
        string real_rw_type;
        if (pos != string::npos)
            real_rw_type = rw_type.substr(pos + 1);
        else
            real_rw_type = type_str;
            
        if (real_rw_type == "read")
            x_attr_info.ExtraAttr_write_type = READ;
        else if (real_rw_type == "read_write")
            x_attr_info.ExtraAttr_write_type = READ_WRITE;
        else
        {
            Py_DECREF(key_name);
            Py_DECREF(type_name);
            Py_DECREF(rw_type_str);
            Py_DECREF(dict);
            Py_DECREF(py_class);
            
            TangoSys_OMemStream o;
            o << "Invalid extra attribute declaration for extra attribute" << name_ext_attr;
            o << ". The extra attribute R/W type is not correctly defined" << ends;
            Tango::Except::throw_exception((const char *)"Pool_InvalidPythonDict",o.str(),
                                           (const char *)"PyExternalFile::get_extra_attr_dec()");
        }			
        
        Py_DECREF(rw_type_str);
        Py_DECREF(type_name);
        Py_DECREF(key_name);
        
        sym_value.push_back(x_attr_info);
    }
    
    Py_DECREF(dict);
    Py_DECREF(py_class);
}


} // End of Pool_ns namespacce
