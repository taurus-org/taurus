//+=============================================================================
//
// file :         PyExternalFile.cpp
//
// description :
//
// project :      TANGO Device Server
//
// $Author: tiagocoutinho $
//
// $Revision: 298 $
//
// $Log$
// Revision 1.25  2007/08/23 10:29:42  tcoutinho
// code rearanged
//
// Revision 1.24  2007/08/20 06:37:32  tcoutinho
// development commit
//
// Revision 1.23  2007/08/17 13:07:30  tcoutinho
// - pseudo motor restructure
// - pool base dev class restructure
// - initial commit for pseudo counters
//
// Revision 1.22  2007/07/31 07:55:40  tcoutinho
// fix bug 5 : Additional information for controllers
//
// Revision 1.21  2007/07/30 11:00:59  tcoutinho
// Fix bug 5 : Additional information for controllers
//
// Revision 1.20  2007/07/23 11:44:41  tcoutinho
// small bug fix
//
// Revision 1.19  2007/07/16 11:00:24  tcoutinho
// - fix problem with communication controller information
// - fix problem reloading python modules
//
// Revision 1.18  2007/07/04 15:06:38  tcoutinho
// first commit with stable Pool API
//
// Revision 1.17  2007/06/13 15:18:58  etaurel
// - Fix memory leak
//
// Revision 1.16  2007/05/10 09:36:24  etaurel
// - Fix some bugs after first test with the real IcePap V2
//
// Revision 1.15  2007/05/07 09:47:15  etaurel
// - Small changes for Python 2.5 compatibility
//
// Revision 1.14  2007/02/08 08:51:17  etaurel
// - Many changes. I don't remember the list
//
// Revision 1.13  2007/01/04 11:55:04  etaurel
// - Added the CounterTimer controller
//
// Revision 1.12  2006/12/18 11:37:10  etaurel
// - Features are only boolean values invisible from the external world
// - ExtraFeature becomes ExtraAttribute with data type of the old features
//
// Revision 1.11  2006/12/13 10:32:27  tcoutinho
// -comment python module tracer code
//
// Revision 1.10  2006/12/12 11:09:16  tcoutinho
// - support for pseudo motors and motor groups in a motor group
//
// Revision 1.9  2006/11/07 14:57:10  etaurel
// - Now, the pool really supports different kind of controllers (cpp and py)
//
// Revision 1.8  2006/10/27 14:43:03  etaurel
// - New management of the MaxDevice stuff
// - SendToCtrl cmd added
// - Some bug fixed in prop management
//
// Revision 1.7  2006/10/27 14:01:47  tcoutinho
// removed some garbage output
//
// Revision 1.6  2006/10/20 15:37:31  etaurel
// - First release with GetControllerInfo command supported and with
// controller properties
//
// Revision 1.5  2006/10/16 09:31:28  tcoutinho
// simplified interface for get_info and get_prop_info
//
// Revision 1.4  2006/10/06 13:35:42  tcoutinho
// changed info command names, added properties functionality
//
// Revision 1.3  2006/10/05 14:53:33  etaurel
// - Test suite of motor controller features is now working
//
// Revision 1.2  2006/10/02 09:19:12  etaurel
// - Motor controller now supports extra features (both CPP and Python)
//
//
// copyleft :     Alba synchrotron
//                  Campus Universitari de Bellaterra. Universitat Autònoma de Barcelona
//                   08193 Bellaterra, Barcelona
//                Spain
//
//-=============================================================================

#include "PyExternalFile.h"
#include "CPool.h"
#include <ltdl.h>

namespace Pool_ns
{

//-----------------------------------------------------------------------------
//
//                    The PyExternalFile class
//
//-----------------------------------------------------------------------------

//+----------------------------------------------------------------------------
//
// method :         PyExternalFile::PyExternalFile()
//
// description :     constructor for PyExternalFile class
//
// in : - f_name : The class file name (cpp lib or python module)
//        - class_name : The class name (case dependant)
//        - pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

PyExternalFile::PyExternalFile(const string &f_name)
:CtrlFile(f_name), mod_dec_ref(true)
{
    //cout << "In the PyExternalFile ctor" << endl;
    module = NULL;

//
// For Python module, init Python if not already done
//
    PythonUtils::instance()->initialize();

//
// Update Python PATH with contents of PoolPath
//

    update_py_path();

//
// Open module and keep a reference on it
//

    string::size_type pos = name.find('.');
    string mod_name = name.substr(0,pos);

    module = load_py_module(mod_name);
}

PyExternalFile::PyExternalFile(PyExternalFile &undef_ctrl)
:CtrlFile(undef_ctrl.get_full_name()), mod_dec_ref(false)
{
    module = undef_ctrl.get_py_module();
}

//+----------------------------------------------------------------------------
//
// method :         PyExternalFile::~PyExternalFile()
//
// description :     destructor for PyExternalFile class
//
//-----------------------------------------------------------------------------

PyExternalFile::~PyExternalFile()
{
    if ((module != NULL) && (mod_dec_ref == true))
    {
        Py_DECREF(module);
    }
}

//+----------------------------------------------------------------------------
//
// method :         PyExternalFile::update_py_path()
//
// description :     updates the python sys.path
//
//-----------------------------------------------------------------------------

void PyExternalFile::update_py_path()
{
    AutoPythonGIL gil;

    PyObject *mod_dir,*sys_mod_name,*sys_module;
    mod_dir = PyImport_GetModuleDict();
    sys_mod_name = PyString_FromString("sys");
    bool new_sys_import = false;
    if (PyDict_Contains(mod_dir,sys_mod_name) == 1)
    {
        sys_module = PyImport_AddModule("sys");
    }
    else
    {
        sys_module = PyImport_Import(sys_mod_name);
        new_sys_import = true;
    }

    Py_DECREF(sys_mod_name);

    if(sys_module == NULL)
    {
        PyErr_Clear();
        TangoSys_OMemStream o;
        o << "Essencial python module 'sys' could not be imported" << ends;
        Tango::Except::throw_exception((const char *)"Pool_CantImportPythonModule",o.str(),
                                          (const char *)"PyExternalFile::update_py_path()");
    }

    PyObject *sys_path = PyObject_GetAttrString_(sys_module, "path");

    if(sys_path == NULL)
    {
        PyErr_Clear();

        TangoSys_OMemStream o;
        o << "Essencial python structure 'sys.path' could not be imported" << ends;
        Tango::Except::throw_exception((const char *)"Pool_CantImportPythonElement",o.str(),
                                          (const char *)"PyExternalFile::update_py_path()");
    }
    
    DevicePool *device_pool = DevicePool::get_instance();
    vector<string> &python_path = device_pool->get_pool_path();

    vector<string>::reverse_iterator ite = python_path.rbegin();
    for(; ite != python_path.rend(); ite++)
    {
        PyObject *py_path_str = PyString_FromString((*ite).c_str());

        int pos = PySequence_Index(sys_path,py_path_str);
        if(pos > 0)
            PySequence_DelItem(sys_path, pos);
        PyList_Insert(sys_path,0,py_path_str);
        Py_DECREF(py_path_str);
    }

    Py_DECREF(sys_path);

    if(new_sys_import)
    {
        Py_DECREF(sys_module);
    }
}

//+----------------------------------------------------------------------------
//
// method :         PyExternalFile::reload_allowed()
//
// description :     Determines if it is allowed to reload the given module.
//                  Usually, it should not be allowed to reload the Controller
//                  super class modules.
//
// in : - mod_name : The name of the python module to be opened
//
// Returns a pointer to a Python module object.
//
//-----------------------------------------------------------------------------
bool PyExternalFile::reload_allowed(const string &mod_name)
{
    return mod_name != "CommunicationController" &&
           mod_name != "MotorController" &&
           mod_name != "CounterTimerController" &&
           mod_name != "ZeroDController" &&
           mod_name != "OneDController" &&
           mod_name != "TwoDController" &&
           mod_name != "PseudoMotorController" &&
           mod_name != "PseudoCounterController";
}

//+----------------------------------------------------------------------------
//
// method :         PyExternalFile::load_py_module()
//
// description :     creates a new reference to a Python module.
//
// in : - mod_name : The name of the python module to be opened
//
// Returns a pointer to a Python module object.
//
//-----------------------------------------------------------------------------
PyObject *PyExternalFile::load_py_module(const string &mod_name)
{
    PyObject
        *mod_dict = NULL,
        *py_mod_name = NULL,
        *tmp_mod = NULL,
        *py_module = NULL;

    AutoPythonGIL gil;

    PyErr_Clear();
    mod_dict = PyImport_GetModuleDict();

    py_mod_name = PyString_FromString(mod_name.c_str());

    if (PyDict_Contains(mod_dict, py_mod_name) == 1)
    {
        if(reload_allowed(mod_name))
        {
            DEBUG_STREAM << "\tadding/reloading module " << mod_name << "..." << endl;
            tmp_mod = PyDict_GetItemString(mod_dict,mod_name.c_str());
            py_module = PyImport_ReloadModule(tmp_mod);
            if (py_module != NULL)
            {
                DEBUG_STREAM << "\t[DONE]. New ref count = " 
                             << py_module->ob_refcnt << endl;
            }
        }
        else
        {
            py_module = PyImport_ImportModule_(mod_name);
            if(py_module != NULL)
            {
                DEBUG_STREAM << "\t[DONE]. New ref count = " 
                             << py_module->ob_refcnt << endl;
            }
            else
            {
                PyErr_Clear();
                DEBUG_STREAM << "\t[DONE]. Import of module NOT sucessfull" << endl;
            }
        }
    }
    else
    {
        DEBUG_STREAM << "\tImporting module for module " << mod_name << "..." << endl;
        py_module = PyImport_ImportModule_(mod_name);
        if(py_module != NULL)
        {
            DEBUG_STREAM << "\t[DONE]. New ref count = " << py_module->ob_refcnt << endl;
        }
        else
        {
            PyErr_Clear();
            DEBUG_STREAM << "\t[DONE]. Import of module NOT sucessfull" << endl;
        }
    }

    Py_DECREF(py_mod_name);

    if (py_module == NULL)
    {
        throw_dev_failed_from_py();
    }

    return py_module;
}


//+----------------------------------------------------------------------------
//
// method :         PyExternalFile::reload()
//
// description :     Unload a Python module and set its ptr to NULL
//
//-----------------------------------------------------------------------------

void PyExternalFile::reload()
{
    string::size_type pos = name.find('.');
    string mod_name = name.substr(0,pos);

    PyObject *new_module = PyImport_ReloadModule(module);

    if (new_module == NULL)
        throw_dev_failed_from_py();

    module = new_module;
}


//+----------------------------------------------------------------------------
//
// method :         PyExternalFile::get_classes()
//
// description :     retrieves a list of valid classes within the file
// arg(s) : - classes [out]: will be filled with the valid classes within the file
//
// Returns the number of valid classes.
//
//-----------------------------------------------------------------------------

int32_t PyExternalFile::get_classes(vector<string> &classes,vector<string> &types)
{
    AutoPythonGIL gil;

    PyObject *pDict = PyModule_GetDict(get_py_module());
    PyObject *pContentList = PyObject_Dir(get_py_module());

    if(!pContentList || PyList_Check(pContentList) == 0)
    {
        cout << "Module does not contain any members. I wonder why!?" << endl;
        Py_DECREF(pContentList);
        return 0;
    }

    int32_t class_count = 0;
    int32_t element_count = PyList_Size(pContentList);

    string module_name;
    string::size_type pos = name.find('.');

    if(pos != string::npos)
        module_name = name.substr(0,pos);
    else
        module_name = name;

    string ctrl_type = CtrlTypeStr[ctrl_obj_type];
    const char *super_class = get_super_class();

    PyObject *pSuperClass;
    try
    {
        pSuperClass = get_py_class(super_class);
    }
    catch(Tango::DevFailed &e)
    {
        Tango::Except::re_throw_exception(e,
                        (const char *)"Pool_CantLocatePythonSuperClass",
                        (const char *)"Can't get classes",
                        (const char *)"PyExternalFile::get_classes()");
    }

    for(int32_t i = 0; i < element_count ; i++)
    {
        PyObject *pElemStr = PyList_GetItem(pContentList, i);
        char *pElemName = PyString_AsString(pElemStr);

        // Avoid returning the actual superclass
        if(strcmp(pElemName,super_class) == 0)
            continue;

        PyObject *pElem = PyDict_GetItem(pDict, pElemStr);

        if(pElem == NULL)
            continue;

        try
        {
            check_py_class(pElem,pSuperClass);
            check_py_methods(pElem);

            string elem = module_name + "." + const_cast<char *>(pElemName);
            classes.push_back(elem);
            types.push_back(ctrl_type);
            class_count++;
        }
        catch(Tango::DevFailed &e) {}
    }
    Py_DECREF(pSuperClass);
    Py_DECREF(pContentList);

    return class_count;
}

//+----------------------------------------------------------------------------
//
// method :         PyExternalFile::get_prop_info()
//
// description :     Retrieves the information about properties for a given class.
//
// arg(s) : - class_name [in]: The class for which to retrieve the information
//          - info [out]: The properties information related to the given class
//
// Returns the properties class information.
//
//-----------------------------------------------------------------------------

void PyExternalFile::get_prop_info(const string &class_name,
                                   vector<PropertyData*> &info)
{
    PyObject *class_obj = get_py_valid_class(class_name.c_str());

//
// Obtain the class attribute 'class_prop' which should be a dictionary
// containning the properties of the class
//

    PyObject *class_prop = PyObject_GetAttrString_(class_obj, CLASS_PROP_ATTR);

    if(class_prop == NULL  || !PyDict_Check(class_prop))
    {
        PyErr_Clear();

        Py_DECREF(class_obj);
        Py_XDECREF(class_prop);
        TangoSys_OMemStream o;
        o << "Invalid Class: reference to " << class_name;
        o << " does not contain a class_prop information dictionary" << ends;
        Tango::Except::throw_exception(
                (const char *)"Pool_InvalidPythonClass",o.str(),
                (const char *)"PyExternalFile::get_prop_info()");
    }

    PyObject *key, *dict_value;
#if PY_VERSION_HEX < 0x02050000
    int pos = 0;
#else
    Py_ssize_t pos = 0;
#endif

    while(PyDict_Next(class_prop, &pos, &key, &dict_value))
    {

//
// Get the name of the current property
//
        PyObject *key_name = PyObject_Str(key);
        string name_str = PyString_AsString(key_name);

//
// Check if the value of the current property is a dictionary containning at
// least the keys for 'Type' and 'Description'. Optionally it can contain a
// 'DefaultValue'.
//

        if(!PyDict_Check(dict_value))
        {
            TangoSys_OMemStream o;
            o << "Invalid class_prop: " << class_name << " class_prop ";
            o << "dictionary value for key " << name_str << " is not a ";
            o << "dictionary" << ends;
            Py_DECREF(key_name);
            Py_DECREF(class_obj);
            Py_DECREF(class_prop);
            Tango::Except::throw_exception(
                    (const char *)"Pool_InvalidPythonClassProperty",o.str(),
                    (const char *)"PyExternalFile::get_prop_info()");
        }

//
// Get the 'Type'
//

        PyObject *type_value = PyDict_GetItemString(dict_value,TYPE_KEY);
        if(type_value == NULL || !PyString_Check(type_value))
        {
            TangoSys_OMemStream o;
            o << "Invalid class_prop: " << class_name << " class_prop ";
            o << "dictionary value for key " << name_str << " is missing the ";
            o << "mandatory 'Type' key." << ends;
            Py_DECREF(key_name);
            Py_DECREF(class_obj);
            Py_DECREF(class_prop);
            Tango::Except::throw_exception(
                    (const char *)"Pool_InvalidPythonClassProperty",o.str(),
                    (const char *)"PyExternalFile::get_prop_info()");
        }
        PyObject *type_name = PyObject_Str(type_value);
        string type_str = PyString_AsString(type_name);

//
// Get the 'Description'
//
        PyObject *descr_value = PyDict_GetItemString(dict_value,DESCR_KEY);
        if(descr_value == NULL || !PyString_Check(descr_value))
        {
            TangoSys_OMemStream o;
            o << "Invalid class_prop: " << class_name << " class_prop ";
            o << "dictionary value for key " << name_str << " is missing the ";
            o << "mandatory 'Description' key." << ends;
            Py_DECREF(type_name);
            Py_DECREF(key_name);
            Py_DECREF(class_obj);
            Py_DECREF(class_prop);
            Tango::Except::throw_exception(
                    (const char *)"Pool_InvalidPythonClassProperty",o.str(),
                    (const char *)"PyExternalFile::get_prop_info()");
        }
        PyObject *descr_name = PyObject_Str(descr_value);
        string descr_str = PyString_AsString(descr_name);

        PyPropertyData *prop_data =
                            new PyPropertyData(name_str,type_str,descr_str);
//
// Get the optional 'DefaultValue'
//
        PyObject *dft_value = PyDict_GetItemString(dict_value,DFT_VALUE_KEY);
        if(dft_value == NULL)
        {
            prop_data->has_dft_value = false;
        }
        else
        {
            prop_data->has_dft_value = true;

            try
            {
                prop_data->from_py(dft_value);
                prop_data->save_default_value();
            }
            catch(Tango::DevFailed &e)
            {
                delete prop_data;
                for(vector<PropertyData*>::iterator prop_ite = info.begin();
                    prop_ite != info.end(); prop_ite++)
                {
                    delete (*prop_ite);
                }
                info.clear();
                Py_DECREF(descr_name);
                Py_DECREF(type_name);
                Py_DECREF(key_name);
                throw e;
            }
        }

        info.push_back(prop_data);

        Py_DECREF(descr_name);
        Py_DECREF(type_name);
        Py_DECREF(key_name);
    }
    Py_DECREF(class_obj);
}

//+----------------------------------------------------------------------------
//
// method :         PyExternalFile::get_prop_info()
//
// description :     Retrieves the information about properties for a given object.
//
// arg(s) : - instance [in]: The object for which to retrieve the properties.
//                           Attention: This object must be a valid instance of
//                           a valid python class according to the defined rules.
//          - info [out]: The properties information related to the given instance
//
// Returns the properties information of the given instance.
//
//-----------------------------------------------------------------------------

void PyExternalFile::get_prop_info(PyObject *instance, vector<string> &info)
{
    vector<PropertyData*> prop_data;
    get_prop_info(instance,prop_data);

//
// First place the number of properties as a first element in the string
//
    stringstream prop_nb;
    prop_nb << prop_data.size();
    info.push_back(prop_nb.str());

    vector<PropertyData*>::iterator ite;
    for(ite = prop_data.begin(); ite != prop_data.end(); ite++)
    {
        (*ite)->append_to_property_vec(info);
        delete (*ite);
    }
    prop_data.clear();
}

//+----------------------------------------------------------------------------
//
// method :         PyExternalFile::get_prop_info()
//
// description :     Retrieves the information about properties for a given object.
//
// arg(s) : - instance [in]: The object for which to retrieve the properties.
//                           Attention: This object must be a valid instance of
//                           a valid python class according to the defined rules.
//          - info [out]: The properties information related to the given instance
//
// Returns the properties information of the given instance.
//
//-----------------------------------------------------------------------------

void PyExternalFile::get_prop_info(PyObject *instance, vector<PropertyData*> &info)
{
    PyObject *inst_name_obj = PyObject_GetAttrString_(instance, INST_NAME_ATTR);

//
// Obtain instance name of the class to be used in case of an error.
//

    if(inst_name_obj == NULL)
    {
        PyErr_Clear();

        TangoSys_OMemStream o;
        o << "Invalid object: does not contain '" << INST_NAME_ATTR << "' attribute" << ends;
        Tango::Except::throw_exception((const char *)"Pool_InvalidPythonObject",o.str(),
                                       (const char *)"PyExternalFile::get_prop_info()");
    }

    string inst_name(PyString_AsString(inst_name_obj));
    Py_DECREF(inst_name_obj);

    PyObject *class_obj = PyObject_GetAttrString_(instance, "__class__");
    PyObject *class_name_obj = PyObject_Str(class_obj);

    string full_class_name(PyString_AsString(class_name_obj));

    string::size_type pos = full_class_name.find('.');

    string class_name;
    if(pos == string::npos)
        class_name = full_class_name;
    else
        class_name = full_class_name.substr(pos+1);


    Py_DECREF(class_name_obj);
    Py_DECREF(class_obj);

//
// Get the class properties
//

    get_prop_info(class_name, info);

//
// Now check which properties where overwritten at the instance level.
// At least the properties that don't have default value at class level must be
// defined at instance level.
//

    vector<PropertyData*>::iterator ite;
    for(ite = info.begin(); ite != info.end(); ite++)
    {
        PyPropertyData *prop = (PyPropertyData*)(*ite);

        PyObject *attr = PyObject_GetAttrString_(instance, prop->name.c_str());

        if(attr == NULL)
        {
            PyErr_Clear();

//
// if it is not defined at the instance level then it is better to have a default value at the class level
//

            if(!prop->has_dft_value)
            {
                TangoSys_OMemStream o;
                o << "Invalid object: does not contain mandatory '" << prop->name << "' attribute" << ends;
                Tango::Except::throw_exception((const char *)"Pool_InvalidPythonObject",o.str(),
                                               (const char *)"PyExternalFile::get_prop_info()");
            }
        }
        else
        {
//
// if it is defined at the instance level then overwrite the default value set at the class level (if any)
//
            prop->dft_overwritten = true;

            try
            {
                prop->from_py(attr);
            }
            catch(Tango::DevFailed &e)
            {
                for(vector<PropertyData*>::iterator prop_ite = info.begin(); prop_ite != info.end(); prop_ite++)
                    delete (*prop_ite);
                info.clear();
                Py_DECREF(attr);
                throw e;
            }
            Py_DECREF(attr);
        }
    }
}

//+----------------------------------------------------------------------------
//
// method :         PyExternalFile::get_py_class()
//
// description :     returns a python object representing the class given by the
//                      class name.
//
// arg(s) : - class_name[in]: the class name
//
// Returns a python class object for the given class name.
// throws an exception if class is not found.
//
//-----------------------------------------------------------------------------

PyObject *PyExternalFile::get_py_class(const char *class_name)
{
    PyObject *pClass;

    PyObject *pUnknown = PyObject_GetAttrString_(get_py_module(), class_name);

    if(pUnknown == NULL)
    {
        PyErr_Clear();

        TangoSys_OMemStream o;
        o << "Invalid Module: reference to " << class_name << " not found" << ends;
        Tango::Except::throw_exception((const char *)"Pool_CantLocatePythonClass",o.str(),
                                       (const char *)"PyExternalFile::get_py_class()");
    }

    // The given name can be either the name of the Module or the name of the Class
    // depending if the user wrote 'import xxx' or 'from xxx import xxx'
    if(!PyObject_TypeCheck(pUnknown, &PyClass_Type))
    {
        PyObject *pModule = pUnknown;
        pClass = PyObject_GetAttrString_(pModule, class_name);
        if(pClass == NULL)
        {
            PyErr_Clear();

            Py_DECREF(pModule);
            TangoSys_OMemStream o;
            o << "Invalid Module: << '" << class_name << "' module does not contain a valid " << class_name << " Class" << ends;
            Tango::Except::throw_exception((const char *)"Pool_CantLocatePythonClass",o.str(),
                                           (const char *)"PyExternalFile::get_py_class()");
        }

        Py_DECREF(pModule);

        if(!PyObject_TypeCheck(pClass, &PyClass_Type))
        {
            PyErr_Clear();

            Py_DECREF(pClass);
            TangoSys_OMemStream o;
            o << "Invalid Module: reference to '" << class_name << "' is not a Python class" << ends;
            Tango::Except::throw_exception((const char *)"Pool_CantLocatePythonClass",o.str(),
                                           (const char *)"PyExternalFile::get_py_class()");
        }
    }
    else
    {
        pClass = pUnknown;
        pUnknown = NULL;
    }

    return pClass;
}

//+----------------------------------------------------------------------------
//
// method :         PyExternalFile::check_py_class()
//
// description :     checks if the given class object is a subclass of the given
//                  super class.
// arg(s) : - class_obj[in]: the class object to be checked
//            super_class_obj[in]: the super class object
//
// throws an exception if some of the mandatory requirements have not been met.
//
//-----------------------------------------------------------------------------

void PyExternalFile::check_py_class(PyObject *class_obj, PyObject *super_class_obj)
{
    if(!PyObject_TypeCheck(class_obj,&PyClass_Type))
    {
        TangoSys_OMemStream o;
        PyObject *py_class_str = PyObject_Str(class_obj);
	if(py_class_str != NULL){
	    o << "Reference to '" << PyString_AsString(py_class_str) << "' is not a Python class" << ends;
	    Py_DECREF(py_class_str);
	    Tango::Except::throw_exception((const char *)"Pool_CantLocatePythonClass",o.str(),
					   (const char *)"PyExternalFile::check_py_class()");
	}
    }

    if(!PyObject_IsSubclass(class_obj,super_class_obj))
    {
        TangoSys_OMemStream o;
        PyObject *py_class_str = PyObject_Str(class_obj);
        PyObject *py_super_class_str = PyObject_Str(super_class_obj);
        o << "Reference to '" << PyString_AsString(py_class_str) << "' is not a subclass of '" << PyString_AsString(py_super_class_str) << "'" << ends;
        Py_DECREF(py_class_str);
//        Py_DECREF(super_class_obj);
        Tango::Except::throw_exception((const char *)"Pool_CantLocatePythonClass",o.str(),
                                       (const char *)"PyExternalFile::check_py_class()");
    }
}


//+----------------------------------------------------------------------------
//
// method :         PyExternalFile::check_py_method()
//
// description :     checks if the given class object implements all necessary
//                  methods
// arg(s) : - class_obj[in]: the class object to be checked
//
// throws an exception if some of the mandatory requirements have not been met.
//
//-----------------------------------------------------------------------------

void PyExternalFile::check_py_method(PyObject *class_obj,const char *meth_name)
{
    PyObject *meth = PyObject_GetAttrString_(class_obj, meth_name);
    if (meth == NULL)
    {
        PyErr_Clear();
        TangoSys_OMemStream o;
        o << "Method " << meth_name << " does not exist" << ends;

        Tango::Except::throw_exception((const char *)"Pool_PythonMethodNotFound",o.str(),
                (const char *)"PyExternalFile::check_py_method");
    }

    if (PyMethod_Check(meth) == false)
    {
        PyErr_Clear();
        Py_DECREF(meth);
        TangoSys_OMemStream o;
        o << meth_name << " is defined but is not a valid method" << ends;

        Tango::Except::throw_exception((const char *)"Pool_PythonMethodNotFound",o.str(),
                (const char *)"PyExternalFile::check_py_method");
    }
    Py_DECREF(meth);
}

//+----------------------------------------------------------------------------
//
// method :         PyExternalFile::check_py()
//
// description :     checks if the given class name is valid in this file.
//
// arg(s) : - class_name[in]: the class to be checked
//
// throws an exception if some of the mandatory requirements have not been met.
//
//-----------------------------------------------------------------------------

void PyExternalFile::check_py(const char *class_name)
{
    PyObject *class_obj = get_py_class((char *)class_name);

    try
    {
        check_py(class_obj);
    }
    catch(Tango::DevFailed &e)
    {
        Py_XDECREF(class_obj);
        throw e;
    }

    Py_DECREF(class_obj);
}

//+----------------------------------------------------------------------------
//
// method :         PyExternalFile::check_py()
//
// description :     checks if the given class object is valid in this file.
//
// arg(s) : - class_name[in]: the class object to be checked
//
// throws an exception if some of the mandatory requirements have not been met.
//
//-----------------------------------------------------------------------------

void PyExternalFile::check_py(PyObject *class_obj)
{
    PyObject *super_class_obj = get_py_class(get_super_class());

    if(class_obj == NULL || super_class_obj == NULL)
    {
        Py_XDECREF(super_class_obj);
        TangoSys_OMemStream o;
        o << "Illegal (null) Reference to a Python class" << ends;
        Tango::Except::throw_exception((const char *)"Pool_CantLocatePythonClass",o.str(),
                                       (const char *)"PyExternalFile::check_py");
    }

    try
    {
        check_py_class(class_obj,super_class_obj);
        check_py_methods(class_obj);
    }
    catch(Tango::DevFailed &e)
    {
        Py_XDECREF(super_class_obj);
        throw;
    }

    Py_DECREF(super_class_obj);
}


//+----------------------------------------------------------------------------
//
// method :         PyExternalFile::get_py_valid_class()
//
// description :     returns a python object representing the super class
//                  from which every valid classes must inherit.
// arg(s) : - super_class[in]: the super class name
//
// Returns a python class object for the given super class name.
// throws an exception if some of the mandatory requirements have not been met.
//
//-----------------------------------------------------------------------------

PyObject *PyExternalFile::get_py_valid_class(const char *class_name)
{
    PyObject *class_obj = get_py_class(class_name);
    PyObject *super_class_obj = get_py_class(get_super_class());

    if(class_obj == NULL || super_class_obj == NULL)
    {
        Py_XDECREF(class_obj);
        Py_XDECREF(super_class_obj);
        TangoSys_OMemStream o;
        o << "Illegal (null) Reference to a Python class" << ends;
        Tango::Except::throw_exception((const char *)"Pool_CantLocatePythonClass",o.str(),
                                       (const char *)"PyExternalFile::get_py_valid_class");
    }

    try
    {
        check_py_class(class_obj,super_class_obj);
        check_py_methods(class_obj);
        Py_DECREF(super_class_obj);
        return class_obj;
    }
    catch(Tango::DevFailed &e)
    {
        Py_XDECREF(class_obj);
        Py_XDECREF(super_class_obj);
        throw e;
    }
}

//+----------------------------------------------------------------------------
//
// method :         PyExternalFile::throw_dev_failed_from_py
//
// description :     Throw a DevFailed exception built from the info returned
//                    by Python after an error occurs
//
//-----------------------------------------------------------------------------

void PyExternalFile::throw_dev_failed_from_py()
{
    PyObject *ex_exec,*ex_value,*ex_tb;
    Tango::DevErrorList err_list;
    err_list.length(2);

    PyErr_Fetch(&ex_exec,&ex_value,&ex_tb);
    Py_init_dev_error(ex_exec,ex_value,ex_tb,err_list);

    string tmp_str("Can't import module ");
    tmp_str += name;

    err_list[1].origin = CORBA::string_dup("PyExternalFile::load_code");
    err_list[1].desc = CORBA::string_dup(tmp_str.c_str());
    err_list[1].reason = CORBA::string_dup("Pool_PythonError");
    err_list[1].severity = Tango::ERR;

    throw Tango::DevFailed(err_list);
}

//+-------------------------------------------------------------------------
//
// function :         PyExternalFile::Py_init_dev_error
//
// description :     This method creates a Tango DevError
//                    from a Python exception
//
// argin : - exec_ptr : The python exception type pbject
//       - value_ptr : The ipython exception value object
//       - tb_ptr ; The python exception traceback object
//       - dev_err : Reference to the DevError list used by the
//               Tango exception. This list is supposed to have
//               at least a size of 1
//
//--------------------------------------------------------------------------
void PyExternalFile::Py_init_dev_error(PyObject *exec_ptr,PyObject *value_ptr,PyObject *tb_ptr,Tango::DevErrorList &dev_err)
{

//
// Send a default exception in case Python does not send us infornation
//

    if (value_ptr == NULL)
    {
        Py_XDECREF(exec_ptr);
        Py_XDECREF(value_ptr);
        Py_XDECREF(tb_ptr);

           dev_err[0].origin = CORBA::string_dup("PyExternalFile::Py_init_dev_error");
        dev_err[0].desc = CORBA::string_dup("A badly formed exception has been received");
        dev_err[0].reason = CORBA::string_dup("Pool_BadPythonException");
        dev_err[0].severity = Tango::ERR;

        return;
    }

//
// Populate a one level DevFailed exception
//

    PyObject *tracebackModule = PyImport_ImportModule("traceback");
    if (tracebackModule != NULL)
    {
        PyObject *tbList, *emptyString, *strRetval;

//
// Format the traceback part of the Python exception
// and store it in the origin part of the Tango exception
//

        tbList = PyObject_CallMethod(tracebackModule,
                (char*)"format_tb",
                (char*)"O",
                tb_ptr == NULL ? Py_None : tb_ptr);

        emptyString = PyString_FromString("");

        strRetval = PyObject_CallMethod(emptyString,
                (char*)"join",
                (char*)"O", tbList);

        dev_err[0].origin = CORBA::string_dup(PyString_AsString(strRetval));

        Py_DECREF(tbList);
        Py_DECREF(emptyString);
        Py_DECREF(strRetval);

//
// Format the exec and value part of the Python exception
// and store it in the desc part of the Tango exception
//

        tbList = PyObject_CallMethod(tracebackModule,
                (char*)"format_exception_only",
                (char*)"OO",
                exec_ptr,value_ptr == NULL ? Py_None : value_ptr);

        emptyString = PyString_FromString("");

        strRetval = PyObject_CallMethod(emptyString,
                (char*)"join",
                (char*)"O", tbList);

        dev_err[0].desc = CORBA::string_dup(PyString_AsString(strRetval));

        Py_DECREF(tbList);
        Py_DECREF(emptyString);
        Py_DECREF(strRetval);
        Py_DECREF(tracebackModule);

        dev_err[0].reason = CORBA::string_dup("Pool_PythonControllerError");
        dev_err[0].severity = Tango::ERR;
    }
    else
    {

//
// Send a default exception because we can't format the
// different parts of the Python's one !
//

        dev_err[0].origin = CORBA::string_dup("PyExternalFile::Py_init_dev_error");
        dev_err[0].desc = CORBA::string_dup("Can't import Python traceback module. Can't extract info from Python exception");
        dev_err[0].reason = CORBA::string_dup("Pool_PythonControllerError");
        dev_err[0].severity = Tango::ERR;
    }

    Py_XDECREF(exec_ptr);
    Py_XDECREF(value_ptr);
    Py_XDECREF(tb_ptr);
}

//+----------------------------------------------------------------------------
//
// method :         PyExternalFile::get_sequence_value()
//
// description :     Retrieve the content of a Python list of strings into a Cpp vector
//                    of strings
//
// args  : - class_name : The Python class name
//           - sym_name : The list name
//           - sym_value : Reference to the vector of strings which will be
//                           initialized with the list content
//
//-----------------------------------------------------------------------------

void PyExternalFile::get_sequence_value(const string &class_name,const char *sym_name,
                                        vector<string> &sym_value)
{
    sym_value.clear();
    append_sequence_value(class_name, sym_name, sym_value);
}

//+----------------------------------------------------------------------------
//
// method :         PyExternalFile::append_sequence_value()
//
// description :     Retrieve the content of a Python list of strings into a Cpp vector
//                    of strings
//
// args  : - class_name : The Python class name
//           - sym_name : The list name
//           - sym_value : Reference to the vector of strings which will be
//                           initialized with the list content
//
//-----------------------------------------------------------------------------

void PyExternalFile::append_sequence_value(const string &class_name,const char *sym_name,
                                           vector<string> &sym_value)
{
    PyObject *py_class = get_py_class(class_name.c_str());

    PyObject *sequence = PyObject_GetAttrString_(py_class, sym_name);
    if (sequence == NULL)
    {
        Py_DECREF(py_class);

        PyErr_Clear();
        TangoSys_OMemStream o;
        o << "Sequence " << sym_name << " does not exist" << ends;

        Tango::Except::throw_exception(
                (const char *)"Pool_PythonSequenceNotFound",o.str(),
                (const char *)"PyExternalFile::get_sequence_value");
    }

    if (PySequence_Check(sequence) == false)
    {
        Py_DECREF(sequence);
        Py_DECREF(py_class);

        TangoSys_OMemStream o;
        o << "Object " << sym_name << " is not a sequence!!!" << ends;

        Tango::Except::throw_exception(
                (const char *)"Pool_PythonSequenceNotFound",o.str(),
                (const char *)"PyExternalFile::get_sequence_value");
    }

    int nb_elt = PySequence_Size(sequence);
    for (int loop = 0;loop < nb_elt;loop++)
    {
        PyObject *sequence_elt = PySequence_GetItem(sequence,loop);

        if(sequence_elt == NULL)
        {
            Py_DECREF(sequence);
            Py_DECREF(py_class);

            TangoSys_OMemStream o;
            o << "Unexpected error trying to retrieve element number ";
            o << loop + 1 << " in sequence " << sym_name;

            Tango::Except::throw_exception(
                    (const char *)"Pool_PythonBadArgument",o.str(),
                    (const char *)"PyExternalFile::get_sequence_value");
        }

        if (PyString_Check(sequence_elt) == false)
        {
            Py_DECREF(sequence_elt);
            Py_DECREF(sequence);
            Py_DECREF(py_class);

            TangoSys_OMemStream o;
            o << "Element number " << loop + 1 << " in sequence ";
            o << sym_name << " is not a string!" << ends;

            Tango::Except::throw_exception(
                    (const char *)"Pool_PythonBadArgument",o.str(),
                    (const char *)"PyExternalFile::get_sequence_value");
        }

        char *tmp_ptr = PyString_AsString(sequence_elt);
        string tmp_str(tmp_ptr);
        sym_value.push_back(tmp_str);

        Py_DECREF(sequence_elt);
    }

    Py_DECREF(sequence);
    Py_DECREF(py_class);
}

//+----------------------------------------------------------------------------
//
// method :         PyExternalFile::get_py_doc()
//
// description :     Retrieve the class Python __doc__ attribute
//
// args  : - class_name : The Python class name
//           - info : reference to string's vector where the __doc__ string
//                    will be stored
//
//-----------------------------------------------------------------------------

void PyExternalFile::get_py_doc(const string &class_name,vector<string> &info)
{

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
                (const char *)"PyExternalFile::get_py_doc()");
    }

//
// Build the description
//

    PyObject *descr = PyObject_GetAttrString_(pPyClass, "__doc__");

    if(descr != NULL && PyString_Check(descr))
    {
        info.push_back(string(PyString_AsString(descr)));
    }
    else
    {
        PyErr_Clear();
        info.push_back(string(""));
    }

    Py_XDECREF(descr);
    Py_DECREF(pPyClass);
}

} // End of Pool_ns namespacce
