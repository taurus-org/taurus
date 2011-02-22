//+=============================================================================
//
// file :         CtrlFile.cpp
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
// Revision 1.18  2007/08/23 10:32:44  tcoutinho
// - basic pseudo counter check
// - some fixes regarding pseudo motors
//
// Revision 1.17  2007/08/17 13:07:30  tcoutinho
// - pseudo motor restructure
// - pool base dev class restructure
// - initial commit for pseudo counters
//
// Revision 1.16  2007/08/08 08:47:55  tcoutinho
// Fix bug 18 : CreateController should be a one step operation
//
// Revision 1.15  2007/07/31 07:55:40  tcoutinho
// fix bug 5 : Additional information for controllers
//
// Revision 1.14  2007/07/30 11:00:59  tcoutinho
// Fix bug 5 : Additional information for controllers
//
// Revision 1.13  2007/01/16 14:32:21  etaurel
// - Coomit after a first release with CT
//
// Revision 1.12  2007/01/04 11:55:03  etaurel
// - Added the CounterTimer controller
//
// Revision 1.11  2006/12/18 11:37:09  etaurel
// - Features are only boolean values invisible from the external world
// - ExtraFeature becomes ExtraAttribute with data type of the old features
//
// Revision 1.10  2006/11/07 14:57:07  etaurel
// - Now, the pool really supports different kind of controllers (cpp and py)
//
// Revision 1.9  2006/10/30 08:38:02  etaurel
// - Fix bug in property default value management
//
// Revision 1.8  2006/10/27 14:43:01  etaurel
// - New management of the MaxDevice stuff
// - SendToCtrl cmd added
// - Some bug fixed in prop management
//
// Revision 1.7  2006/10/23 13:56:48  etaurel
// - A new definition for the Ctrl_class_name field of the C++ controller
//
// Revision 1.6  2006/10/23 13:36:57  etaurel
// - First implementation of controller properties for CPP controller
//
// Revision 1.5  2006/10/16 09:31:28  tcoutinho
// simplified interface for get_info and get_prop_info
//
// Revision 1.4  2006/10/06 13:40:51  tcoutinho
// changed info command names, added properties functionality
//
// Revision 1.3  2006/10/02 09:19:11  etaurel
// - Motor controller now supports extra features (both CPP and Python)
//
// Revision 1.2  2006/09/28 09:22:24  etaurel
// - End of the ControllerClassList attribute implementation
//
// Revision 1.1  2006/09/27 15:15:48  etaurel
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

#include "CPool.h"
#include "CppCtrlFile.h"
#include <ltdl.h>
#include <fstream>

namespace Pool_ns
{

//+----------------------------------------------------------------------------
//
// method : 		CppCtrlFile::CppCtrlFile()
// 
// description : 	constructor for CppCtrlFile class
//
// in : - f_name : The controller class file name (cpp lib or python module)
//		- class_name : The class name (case dependant)
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

CppCtrlFile::CppCtrlFile(const std::string &f_name, const char *dev_type)
:CtrlFile(f_name),lib_ptr(NULL),close_lib(true),include_MaxDevice(true)
{
    string d_type(dev_type);
    ctrl_obj_type = DevicePool::str_2_CtrlType(d_type);
    load_code();
}

CppCtrlFile::CppCtrlFile(CppCtrlFile &undef_ctrl, const char *dev_type)
:CtrlFile(undef_ctrl.get_name()),lib_ptr(undef_ctrl.get_lib_ptr()),close_lib(false),include_MaxDevice(true)
{
    string d_type(dev_type);
    ctrl_obj_type = DevicePool::str_2_CtrlType(d_type);
}


//+----------------------------------------------------------------------------
//
// method : 		CppCtrlFile::load_code()
// 
// description : 	Load the code. For Python controller, also load the
//                  Cpp shared lib cpp to python interface
// 
// arg(s) : - dev_type : The device type (needed only for
//                            python controller
//
//-----------------------------------------------------------------------------
        
void CppCtrlFile::load_code()
{
    std::vector<std::string> &paths = DevicePool::get_instance()->get_pool_path();
    
//
// Get list of .la files in each directories
//

    vector<string> cpp_files;
    vector<string>::iterator path_ite;
    bool leave_loop = false;
            

    for (path_ite = paths.begin();path_ite != paths.end(); path_ite++)
    {
        DevicePool::get_files_with_extension(*path_ite,".la",cpp_files);
        for (vector<string>::size_type loop = 0;loop < cpp_files.size();loop++)
        {
            string &cpp_file = cpp_files[loop];
            string name_from_path = cpp_file.substr(cpp_file.find_last_of('/') + 1);
            if (name_from_path == name)
            {
                
//
// Load the shared lib.
//
                lib_ptr = lt_dlopen(cpp_file.c_str()/*,RTLD_NOW*/);
                if (lib_ptr == NULL)
                {
                    TangoSys_OMemStream o;
                    const char *error = lt_dlerror();
                    cout << "Trying to load shared library " << name << " (" 
                         << cpp_file << ") returns error: " << error << endl;
                    o << "Trying to load shared library " << name << " returns error: " << error << ends;

                    Tango::Except::throw_exception((const char *)"Pool_ControllerNotFound",o.str(),
                                    (const char *)"CppCtrlFile::load_code");
                }
                else
                {
                    
//
// If path is not defined yet, store lib path and exit loop
//

                    if (path.size() == 0)
                        path = cpp_files[loop].substr(0,cpp_files[loop].find_last_of('/'));
                    leave_loop = true;
                    break;
                }
            }
        }
        if (leave_loop == true)
            break;
    }

    if (path_ite == paths.end())
    {
        TangoSys_OMemStream o;
        o << "File " << name << " not found in any of the directory in the Pool device PoolPath property" << ends;
            
        Tango::Except::throw_exception((const char *)"Pool_ControllerNotFound",o.str(),
                            (const char *)"CtrlFile::load_code");
    }
}

//+----------------------------------------------------------------------------
//
// method : 		CppCtrlFile::~CppCtrlFile()
// 
// description : 	destructor for CtrlFile class
//
//-----------------------------------------------------------------------------

CppCtrlFile::~CppCtrlFile()
{
//	cout << "In the CppCtrlFile dtor" << endl;

    if ((lib_ptr != NULL) && (close_lib == true))
        lt_dlclose(lib_ptr);
}

//+----------------------------------------------------------------------------
//
// method : 		CppCtrlFile::get_info()
// 
// description : 	Retrieves the information for a given type of controller class.
//                  
// arg(s) : - ctrl_class [in]: The controller class for which to retrieve the information
//          - info [out]: The controller information related to the given controller class
//
// Returns the controller class information.
//
//-----------------------------------------------------------------------------

void CppCtrlFile::get_info(const std::string &ctrl_class,vector<string> &info)
{
//
// First, get doc string
//
    get_cpp_doc(ctrl_class,info);
    
//
// Get the Family / gender of the controller
//
    get_cpp_gender(ctrl_class,info);

//
// Get the model of the controller
//
    get_cpp_model(ctrl_class,info);
    
//
// Get the organization
//
    get_cpp_organization(ctrl_class,info);

//
// Get class properties
//	
    CtrlFile::get_prop_info(ctrl_class,info);
    
//
// Any particular info that the class may contain
// (e.x.: pseudo classes have information about the roles of their elements here)
//
    get_particular_info(ctrl_class,info);
}

//+----------------------------------------------------------------------------
//
// method : 		CppCtrlFile::get_info()
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

void CppCtrlFile::get_info(const std::string &ctrl_class, const std::string &ctrl_instance, vector<string> &info)
{
//
// First, get doc string
//
    get_cpp_doc(ctrl_class,info);

//
// Get the Family / gender of the controller
//
    get_cpp_gender(ctrl_class,info);

//
// Get the model of the controller
//
    get_cpp_model(ctrl_class,info);
    
//
// Get the organization
//
    get_cpp_organization(ctrl_class,info);

//
// Get class properties
//
    vector<PropertyData*> prop_info;
    get_prop_info(ctrl_class,prop_info);
    
//
// Get database overwritten values
//
    DevicePool* device_pool = DevicePool::get_instance();
    vector<pair<string,string> > prop_pairs;
    device_pool->build_property_data(ctrl_instance, ctrl_class, prop_pairs, prop_info);
    
//
// First place the number of properties as a first element in the string
//	
    stringstream prop_nb;
    prop_nb << prop_info.size();
    info.push_back(prop_nb.str());
    
//
// Split each property into four strings: name, type, description and value
//
    vector<PropertyData*>::iterator ite;
    for(ite = prop_info.begin(); ite != prop_info.end(); ite++)
    {
        (*ite)->append_to_property_vec(info);
        delete (*ite);
    }
    prop_info.clear();
    
//
// Any particular info that the class may contain
// (e.x.: pseudo classes have information about the roles of their elements here)
//
    get_particular_info(ctrl_class,ctrl_instance,info);
}

//+----------------------------------------------------------------------------
//
// method : 		CppCtrlFile::get_info_ex()
// 
// description : 	Retrieves the information for a given type of controller class.
//                  
// arg(s) : - ctrl_class [in]: The controller class for which to retrieve the information
//          - info [out]: The controller information related to the given controller class
//
// Returns the controller class information.
//
//-----------------------------------------------------------------------------

void CppCtrlFile::get_info_ex(const std::string &ctrl_class, Tango::DevVarCharArray *info_ex)
{
    vector<string> info;
    
    get_info(ctrl_class,info);
    get_cpp_image(ctrl_class,info);
    get_cpp_logo(ctrl_class,info);
    get_cpp_icon(ctrl_class,info);

    vecinfo_to_chararray(info,info_ex);
}

//+----------------------------------------------------------------------------
//
// method : 		CppCtrlFile::get_info_ex()
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

void CppCtrlFile::get_info_ex(const std::string &ctrl_class, const std::string &ctrl_instance, 
                              Tango::DevVarCharArray *info_ex)
{
    vector<string> info;
    
    get_info(ctrl_class,ctrl_instance,info);
    get_cpp_image(ctrl_class,info);
    get_cpp_logo(ctrl_class,info);
    get_cpp_icon(ctrl_class,info);
    
    vecinfo_to_chararray(info,info_ex);
}


//+----------------------------------------------------------------------------
//
// method : 		CppCtrlFile::get_prop_info()
// 
// description : 	Retrieves the information about properties for a given type 
//                  of controller class.
//                  
// arg(s) : - ctrl_class [in]: The controller class for which to retrieve the information
//          - info [out]: The controller information related to the given controller class
//
// Returns the controller properties class information.
//
//-----------------------------------------------------------------------------

void CppCtrlFile::get_prop_info(const std::string &ctrl_class, 
                                vector<PropertyData*> &prop_info)
{
//
// Check that the shared lib is correctly openned
//

    if (lib_ptr == NULL)
    {
        Tango::Except::throw_exception(
                (const char *)"Pool_CantUnloadExternalElement",
                (const char *)"The shared library is not correctly loaded !!!",
                (const char *)"CppCtrlFile::get_cpp_doc");
    }
    
//
// Build symbol name
//

    string full_sym_name(ctrl_class);
    full_sym_name = full_sym_name + "_class_prop";

//
// Get symbol
//

    lt_ptr name_sym = lt_dlsym(lib_ptr,full_sym_name.c_str());

//
// Clean vector in case of
//

    if (prop_info.empty() == false)
    {
        vector<PropertyData*>::iterator it;
        for(it = prop_info.begin(); it != prop_info.end(); ++it)
            delete (*it);
        prop_info.clear();
    }
        
//
// Add as first element in the vector the MaxDevice property
//
    if(include_MaxDevice == true)
    {
        string prop_name("MaxDevice");
        string prop_type("DevLong");
        string prop_desc("The maximum number of device supported by the controller");
            
        PropertyData *prop_data = new PropertyData(prop_name,prop_type,prop_desc);
        
        int32_t max_dev = get_MaxDevice(ctrl_class);
        if (max_dev != -1)
        {
            prop_data->has_dft_value = true;
            prop_data->set_value(max_dev);
            prop_data->save_default_value();
        }
        else
            prop_data->has_dft_value = false;
            
        prop_info.push_back(prop_data);
    }
    
//
// Return if no properties are defined
//
    
    if (name_sym == NULL)
    {
        return;
    }

//
// Get property info from Cpp lib and build a PropertyData for each of them
//

    Controller::PropInfo *prop_array = (Controller::PropInfo *)name_sym;
    uint32_t index = 0;
    while (prop_array[index].name != NULL)
    {
        string name_str(prop_array[index].name);
        string type_str(prop_array[index].type);
        string desc_str(prop_array[index].desc);
        string default_val("");
        if (prop_array[index].default_value != NULL)
            default_val = prop_array[index].default_value;
        
        CppPropertyData *prop_data = new CppPropertyData(name_str,type_str,desc_str);
        
        if (default_val.size() == 0)
            prop_data->has_dft_value = false;
        else
        {
            prop_data->has_dft_value = true;
            
            try 
            {
                prop_data->from_cpp(default_val);
                prop_data->save_default_value();
            }
            catch(Tango::DevFailed &e) 
            {
                delete prop_data;
                for(vector<PropertyData*>::iterator prop_ite = prop_info.begin(); prop_ite != prop_info.end(); prop_ite++)
                    delete (*prop_ite);
                prop_info.clear();
                throw e;			
            }
        }
        
        prop_info.push_back(prop_data);
        index++;
    }
}


//+----------------------------------------------------------------------------
//
// method : 		CtrllFile::get_classes()
// 
// description : 	Check that the file given as argument is a valid CPP
//			 controller
//
//-----------------------------------------------------------------------------
        
int32_t CppCtrlFile::get_classes(vector<string> &cl_list,vector<string> &ctrl_type_list)
{
    int32_t cl_ctr = 0;

//
// In case the library is not loaded
//

    if (lib_ptr == NULL)
    {
        Tango::Except::throw_exception(
                (const char *)"Pool_SharedLibraryNotLoaded",
                (const char *)"Shared library is not loaded",
                (const char *)"CppCtrlFile::get_classes()");
    }
                    
//
// Try to find the two symbols in shared lib
//
    string ctrl_type = CtrlTypeStr[ctrl_obj_type];
    string symbol_name = ctrl_type + "_Ctrl_class_name";
    lt_ptr name_sym = lt_dlsym(lib_ptr,symbol_name.c_str());
    if (name_sym == NULL)
    {
        Tango::Except::throw_exception(
            (const char *)"Pool_CantFindClasses",
            (const char *)"Can't find any controller classes in this shared library",
            (const char *)"CppCtrlFile::get_classes()");
    }

    char **cl_array = (char **)name_sym;
    uint32_t index = 0;
    while (cl_array[index] != NULL)
    {
        string one_ctrl(cl_array[index]);

//
// Check if the "creation" function is also defined
//
                
        string func_name("_create_");
        func_name = func_name + one_ctrl;
            
        lt_ptr func_ptr = lt_dlsym(lib_ptr,func_name.c_str());
        if (func_ptr != NULL)
        {
            cl_ctr++;
            cl_list.push_back(one_ctrl);
            ctrl_type_list.push_back(ctrl_type);
        }
    
        index++;
    }

    return cl_ctr;
}

//+----------------------------------------------------------------------------
//
// method : 		CppCtrlFile::reload_lib()
// 
// description : 	Reload a Cpp library
//
//-----------------------------------------------------------------------------

void CppCtrlFile::reload()
{
    if (lib_ptr != NULL)
    {
        if (lt_dlclose(lib_ptr) != 0)
        {  
            TangoSys_OMemStream o;
            o << "Trying to unload shared library " << name;
            o << " returns errror: " << lt_dlerror() << ends;

            Tango::Except::throw_exception(
                    (const char *)"Pool_CantUnloadExternalElement",o.str(),
                    (const char *)"CppCtrlFile::reload_cpp_lib");
        }
    }

    string abs_file_path(path + '/' + name);
    
    lib_ptr = lt_dlopen(abs_file_path.c_str()/*,RTLD_NOW*/);
    if (lib_ptr == NULL)
    {
        TangoSys_OMemStream o;
        o << "Trying to load shared library " << name << " returns error: ";
        o << lt_dlerror() << ends;

        Tango::Except::throw_exception(
                (const char *)"Pool_CantLoadExternalElement",o.str(),
                (const char *)"CppCtrlFile::reload_cpp_lib");
    }
}

//+----------------------------------------------------------------------------
//
// method : 		CppCtrlFile::get_sequence_value()
// 
// description : 	Reload a Cpp library
//
//-----------------------------------------------------------------------------

void CppCtrlFile::get_sequence_value(const std::string &class_name,const char *sym_name,vector<string> &sym_value)
{
    
//
// Check that the shared lib is correctly openned
//

    if (lib_ptr == NULL)
    {
        Tango::Except::throw_exception(
                (const char *)"Pool_CantUnloadExternalElement",
                (const char *)"The shared library is not correctly loaded !!!",
                (const char *)"CppCtrlFile::get_symbol_value");
    }
    
//
// Build symbol name
//

    string full_sym_name(class_name + '_' + sym_name);

//
// Get symbol
//

    sym_value.clear();	
    lt_ptr name_sym = lt_dlsym(lib_ptr,full_sym_name.c_str());
    if (name_sym != NULL)
    {
        char **cl_array = (char **)name_sym;
        uint32_t index = 0;
        while (cl_array[index] != NULL)
        {
            string tmp_str(cl_array[index]);
            sym_value.push_back(tmp_str);
            index++;
        }
    }
}

//+----------------------------------------------------------------------------
//
// method : 		CppCtrllFile::get_extra_attr_dec()
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

void CppCtrlFile::get_extra_attr_dec(const std::string &class_name,const char *sym_name,vector<PoolExtraAttr> &sym_value)
{
    
//
// Check that the shared lib is correctly openned
//

    if (lib_ptr == NULL)
    {
        Tango::Except::throw_exception((const char *)"Pool_CantUnloadExternalElement",
                                       (const char *)"The shared library is not correctly loaded !!!",
                                       (const char *)"CppCtrlFile::get_extra_attr_dec");
    }
    
//
// Build symbol name
//

    string full_sym_name(class_name + '_' + sym_name);

//
// Get symbol
//

    sym_value.clear();	
    lt_ptr name_sym = lt_dlsym(lib_ptr,full_sym_name.c_str());
    if (name_sym != NULL)
    {
        
//
// Get property info from Cpp lib and build a PropertyData for each of them
//

        Controller::ExtraAttrInfo *extra_attr_array = (Controller::ExtraAttrInfo *)name_sym;
        uint32_t index = 0;
        while (extra_attr_array[index].name != NULL)
        {
            PoolExtraAttr x_attr_info;

//
// Get extra attribute name
//
            
            string name_str(extra_attr_array[index].name);
            x_attr_info.ExtraAttr_name = name_str;

//
// Get extra attribute data type
//
            
            string type_str(extra_attr_array[index].type);
            transform(type_str.begin(),type_str.end(),type_str.begin(),::tolower);
            
            if (type_str == "devboolean")
                x_attr_info.ExtraAttr_data_type = BOOLEAN;
            else if (type_str == "devlong")
                x_attr_info.ExtraAttr_data_type = LONG;
            else if (type_str == "devdouble")
                x_attr_info.ExtraAttr_data_type = DOUBLE;
            else if (type_str == "devstring")
                x_attr_info.ExtraAttr_data_type = STRING;
            else
            {
                TangoSys_OMemStream o;
                o << "Invalid extra attribute declaration for extra attribute" << name_str;
                o << ". The extra attribute data type is not one of the allowed data type" << ends;
                Tango::Except::throw_exception((const char *)"Pool_InvalidExtraAttrDecl",o.str(),
                                           (const char *)"CppCtrlFile::get_extra_attr_dec()");				
            }
            
//
// Get extra attribute r/w type
//

            string rw_str(extra_attr_array[index].rw_type);
            transform(rw_str.begin(),rw_str.end(),rw_str.begin(),::tolower);
            
            if (rw_str == "read")
                x_attr_info.ExtraAttr_write_type = READ;
            else if (rw_str == "read_write")
                x_attr_info.ExtraAttr_write_type = READ_WRITE;
            else
            {			
                TangoSys_OMemStream o;
                o << "Invalid extra attribute declaration for extra attribute" << name_str;
                o << ". The extra attribute R/W type is not correctly defined" << ends;
                Tango::Except::throw_exception((const char *)"Pool_InvalidExtraAttrDecl",o.str(),
                                                (const char *)"CppCtrlFile::get_extra_attr_dec()");
            }			
        
            sym_value.push_back(x_attr_info);
            index++;
        }
    }
    
}

//+----------------------------------------------------------------------------
//
// method : 		CppCtrllFile::get_cpp_str_array()
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
bool CppCtrlFile::get_cpp_str_array(const std::string &class_name,const char *sym_name,
                                    vector<string> &sym_value)
{
//
// Check that the shared lib is correctly openned
//

    if (lib_ptr == NULL)
    {
        Tango::Except::throw_exception(
                (const char *)"Pool_CantUnloadExternalElement",
                (const char *)"The shared library is not correctly loaded !!!",
                (const char *)"CppCtrlFile::get_dec_str");
    }
    
    //
    // Build symbol name
    //

    string full_sym_name(class_name + '_' + sym_name);

//
// Get symbol
//

    sym_value.clear();	
    lt_ptr name_sym = lt_dlsym(lib_ptr,full_sym_name.c_str());
    if (name_sym != NULL)
    {
        const char **val_array = (const char**)name_sym;
        
        int i = 0;
        const char *val_elem = val_array[0];
        
        while(val_elem != NULL)
        {
            sym_value.push_back(val_elem);
            val_elem = val_array[++i];
        };
    }
    else
    {
        return false;
    }
    return true;
}

//+----------------------------------------------------------------------------
//
// method : 		CppCtrlFile::get_cpp_elem()
// 
// description : 	Retrieve the class Cpp doc info
//
// args  : - class_name : The class name
//		   - info : reference to string's vector where the doc string
//					will be stored
//
//-----------------------------------------------------------------------------

void CppCtrlFile::get_cpp_elem(const std::string &class_name,const char *elem_name,
                               vector<string> &info, const char *dft)
{
//
// Check that the shared lib is correctly openned
//

    if (lib_ptr == NULL)
    {
        Tango::Except::throw_exception(
                (const char *)"Pool_CantUnloadExternalElement",
                (const char *)"The shared library is not correctly loaded !!!",
                (const char *)"CppCtrlFile::get_cpp_elem");
    }
    
//
// Build symbol name
//

    string full_sym_name(class_name);
    full_sym_name = full_sym_name + "_" + elem_name;

//
// Get symbol
//

    lt_ptr name_sym = lt_dlsym(lib_ptr,full_sym_name.c_str());
    string ctrl_elem;
    
    if (name_sym != NULL)
    {
        const char *cl_elem = *((const char **)name_sym);
        ctrl_elem = cl_elem;
    }
    else
        ctrl_elem = dft;
    
    info.push_back(ctrl_elem);
}

void CppCtrlFile::get_cpp_doc(const std::string &class_name,vector<string> &info)
{
    get_cpp_elem(class_name,"doc",info);
}

void CppCtrlFile::get_cpp_gender(const std::string &class_name,vector<string> &info)
{
    get_cpp_elem(class_name,"gender",info,DEFAULT_GENDER);
}

void CppCtrlFile::get_cpp_model(const std::string &class_name,vector<string> &info)
{
    get_cpp_elem(class_name,"model",info,DEFAULT_MODEL);
}

void CppCtrlFile::get_cpp_image(const std::string &class_name,vector<string> &info)
{
    get_cpp_elem(class_name,"image",info);
}

void CppCtrlFile::get_cpp_organization(const std::string &class_name,vector<string> &info)
{
    get_cpp_elem(class_name,"organization",info,DEFAULT_ORGANIZATION);
}

void CppCtrlFile::get_cpp_logo(const std::string &class_name,vector<string> &info)
{
    get_cpp_elem(class_name,"logo",info);
}

void CppCtrlFile::get_cpp_icon(const std::string &class_name,vector<string> &info)
{
    get_cpp_elem(class_name,"icon",info);
}

//+----------------------------------------------------------------------------
//
// method : 		CppCtrlFile::get_MaxDevice()
// 
// description : 	Retrieve the class MaxDevice field
//
// args  : - class_name : The class name
//
//-----------------------------------------------------------------------------

int32_t CppCtrlFile::get_MaxDevice(const std::string &class_name)
{
//
// Check that the shared lib is correctly openned
//

    if (lib_ptr == NULL)
    {
        Tango::Except::throw_exception((const char *)"Pool_CantUnloadExternalElement",
                                       (const char *)"The shared library is not correctly loaded !!!",
                                       (const char *)"CppCtrlFile::get_MaxDevice()");
    }
    
//
// Build symbol name
//

    string full_sym_name(class_name);
    full_sym_name = full_sym_name + "_MaxDevice";

//
// Get symbol
//

    int32_t max_dev = -1;
    lt_ptr name_sym = lt_dlsym(lib_ptr,full_sym_name.c_str());
    string ctrl_doc;
    
    if (name_sym != NULL)
    {
        int32_t *cl_max = (int32_t *)name_sym;
        max_dev = *cl_max;
    }
    
    return max_dev;
}

} // End of Pool_ns namespacce
