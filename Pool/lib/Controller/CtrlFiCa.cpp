//+=============================================================================
//
// file :         CtrlFiCa.cpp
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
// Revision 1.32  2007/08/20 06:37:32  tcoutinho
// development commit
//
// Revision 1.31  2007/08/17 13:07:30  tcoutinho
// - pseudo motor restructure
// - pool base dev class restructure
// - initial commit for pseudo counters
//
// Revision 1.30  2007/08/08 08:47:55  tcoutinho
// Fix bug 18 : CreateController should be a one step operation
//
// Revision 1.29  2007/07/17 11:41:57  tcoutinho
// replaced comunication with communication
//
// Revision 1.28  2007/07/02 14:46:36  tcoutinho
// first stable comunication channel commit
//
// Revision 1.27  2007/06/28 07:15:34  tcoutinho
// safety commit during comunication channels development
//
// Revision 1.26  2007/06/27 08:56:28  tcoutinho
// first commit for comuncation channels
//
// Revision 1.25  2007/05/10 09:36:24  etaurel
// - Fix some bugs after first test with the real IcePap V2
//
// Revision 1.24  2007/02/08 08:51:14  etaurel
// - Many changes. I don't remember the list
//
// Revision 1.23  2007/01/26 08:36:47  etaurel
// - We now have a first release of ZeroDController
//
// Revision 1.22  2007/01/04 11:55:03  etaurel
// - Added the CounterTimer controller
//
// Revision 1.21  2006/12/18 11:37:09  etaurel
// - Features are only boolean values invisible from the external world
// - ExtraFeature becomes ExtraAttribute with data type of the old features
//
// Revision 1.20  2006/11/07 14:57:08  etaurel
// - Now, the pool really supports different kind of controllers (cpp and py)
//
// Revision 1.19  2006/10/30 08:38:02  etaurel
// - Fix bug in property default value management
//
// Revision 1.18  2006/10/27 14:43:01  etaurel
// - New management of the MaxDevice stuff
// - SendToCtrl cmd added
// - Some bug fixed in prop management
//
// Revision 1.17  2006/10/23 15:12:35  etaurel
// - Fix memory leak in several places
//
// Revision 1.16  2006/10/20 15:37:29  etaurel
// - First release with GetControllerInfo command supported and with
// controller properties
//
// Revision 1.15  2006/10/05 14:53:32  etaurel
// - Test suite of motor controller features is now working
//
// Revision 1.14  2006/10/05 07:59:35  etaurel
// - Controller now supports dynamic features
//
// Revision 1.13  2006/10/02 13:18:57  etaurel
// - Motor extra feature test suite now running OK
//
// Revision 1.12  2006/10/02 09:19:11  etaurel
// - Motor controller now supports extra features (both CPP and Python)
//
// Revision 1.11  2006/09/28 09:22:24  etaurel
// - End of the ControllerClassList attribute implementation
//
// Revision 1.10  2006/09/27 15:15:49  etaurel
// - ExternalFile and CtrlFile has been splitted in several classes:
//   ExternalFile, CppCtrlFile, PyExternalFile and PyCtrlFile
//
// Revision 1.9  2006/09/22 15:35:28  tcoutinho
// access to python is now done throw the xxxFile classes. This reduced the amount of duplicated code in both xxxFile and the corresponding xxxFiCa classes.
//
// Revision 1.8  2006/09/19 09:57:11  etaurel
// - Commit after the controller, motor and motor_group test sequences works after the merge
//
// Revision 1.7  2006/09/18 10:32:11  etaurel
// - Commit after merge with pseudo-motor branch
//
// Revision 1.6  2006/06/19 14:40:40  etaurel
// - Small change in Makefile for new Tango directory tree
// - Now the Controller name in the controller list is returned case dependant
//
// Revision 1.5  2006/06/15 15:36:30  etaurel
// - many changes after due to first test suite only on controller related stuff!!!
//
// Revision 1.4  2006/06/12 10:28:56  etaurel
// - Many changes dur to bug fixes found when writing test units...
//
// Revision 1.3  2006/05/25 09:13:47  etaurel
// - Stop Pool startup sequence in case Python LoadModule failed
// - Add logging possibility in the CtrlFiCa and CtrlFile classes
//
// Revision 1.2  2006/05/24 14:12:49  etaurel
// - Again many changes
// Revision 1.1.2.1  2006/07/03 12:44:33  tcoutinho
// pseudo motor basic operations on the pool done as well as initial python support
//
// Revision 1.1  2006/03/14 14:54:08  etaurel
// - Again new changes in the internal structure
//
// Revision 1.2  2006/03/14 08:25:10  etaurel
// - Change the way objects are aorganized within the pool device
//
// Revision 1.1.1.1  2006/03/10 13:40:57  etaurel
// Initial import
//
//
// copyleft :     Alba synchrotron
//				  Campus Universitari de Bellaterra. Universitat Autònoma de Barcelona
// 				  08193 Bellaterra, Barcelona
//                Spain
//
//-=============================================================================

#include "CtrlFiCa.h"
#include <ltdl.h>
#include "MotorFeatures.h"
#include "Pool.h"
#include "PoolClass.h"

namespace Pool_ns
{

//------------------------------------------------------------------------------
// CtrlFiCa::CtrlFiCa
//
CtrlFiCa::CtrlFiCa(const std::string &type, const std::string &f_name, 
                   const std::string &ctrl_class_name,
                   CtrlType obj_type, Pool *dev):
ExternalFiCa(CtrlTypeStr[obj_type], f_name, ctrl_class_name, dev)
{
    init(type, f_name, ctrl_class_name, obj_type, dev);
}

//------------------------------------------------------------------------------
// CtrlFiCa::~CtrlFiCa
//
CtrlFiCa::~CtrlFiCa()
{
    for (unsigned long loop = 0;loop < ctrl_props.size();loop++)
        delete ctrl_props[loop];
}

//------------------------------------------------------------------------------
// CtrlFiCa::~CtrlFiCa
//
void
CtrlFiCa::init(const std::string &type, const std::string &f_name,
               const std::string &ctrl_class_name, CtrlType obj_type, Pool *dev)
{

//
// Check if the controller file is not already known
//

    bool new_ctrl_file = false;
    bool ctrl_file_constructed = false;

    PoolClass* pool_class = dev->get_pool_class();

    vector<CtrlFile *>::iterator ite;
    try
    {
        ite = pool_class->get_ctrl_file_by_name(f_name);
    }
    catch (Tango::DevFailed &e)
    {
        new_ctrl_file = true;
    }

//
// Create a new controller file if it is not defined
// But first, get controller file name ful path
//

    Language lang;
    try
    {
        if (new_ctrl_file == true)
        {

//
// First, get all the directories in the PoolPath
//

            std::vector<std::string> &paths = dev->get_pool_path();

//
// Get list of .la or .py files in each directories
//

            std::vector<std::string> ext_files;
            std::vector<std::string>::iterator path_ite;
            bool leave_loop = false;
            unsigned long loop = 0;

            lang = CtrlFile::get_language(f_name);
            std::string path_ext;
            if (lang == CPP)
                path_ext = ".la";
            else
                path_ext = ".py";

            for (path_ite = paths.begin();path_ite != paths.end(); path_ite++)
            {
                dev->get_files_with_extension(*path_ite,path_ext.c_str(),ext_files);
                for (loop = 0;loop < ext_files.size();loop++)
                {
                    std::string name_from_path = ext_files[loop].substr(ext_files[loop].find_last_of('/') + 1);
                    if (name_from_path == f_name)
                    {
                        leave_loop = true;
                        break;
                    }
                }

                if (leave_loop == true)
                    break;
            }

            if (path_ite == paths.end())
            {
                TangoSys_OMemStream o;
                o << "File " << f_name << " not found in any of the directory in the Pool device PoolPath property" << ends;

                Tango::Except::throw_exception((const char *)"Pool_ControllerNotFound",o.str(),
                            (const char *)"CtrlFiCa::init");
            }

            ite = pool_class->add_ctrl_file(ext_files[loop],obj_type,dev);
            ctrl_file_constructed = true;
        }
        my_file = (*ite);

//
// For Python controller, check that the controller class is valid
//

        Language lang = (*ite)->get_language();
        if (lang == PYTHON)
        {
            AutoPoolLock lo(monitor);
            check_python(ctrl_class_name);
        }

//
// Get the list of ctrl properties but first clean the vector used to store them
// in case it has been already been used
//

        for (unsigned long loop = 0;loop < ctrl_props.size();loop++)
            delete ctrl_props[loop];
        {
            AutoPoolLock lo(monitor);
            (*ite)->get_prop_info(ctrl_class_name,ctrl_props);
        }

//
// Check all kinds of features
//

        get_features(lang,*ite,ctrl_class_name);

    }
    catch (Tango::DevFailed &e)
    {
        if ((new_ctrl_file == true) && (ctrl_file_constructed == true))
        {
            delete (*ite);
            pool_class->ctrl_files.erase(ite);
        }

        TangoSys_OMemStream o;
        o << "Impossible to create controller " << type << ends;

        Tango::Except::re_throw_exception(e,(const char *)"Pool_ControllerNotCorrect",o.str(),
                        (const char *)"CtrlFiCa::CtrlFiCa");
    }

}

//+--------------------------------------------------------------------------
//
// method : 		CtrlFiCa::get_features()
//
// description : 	Check if the controller features are in the list of
//					pre-defined ones
//
// in : - ctrl_class_name : The controller class name
//
//-----------------------------------------------------------------------------

void CtrlFiCa::get_features(Language lang,CtrlFile *ite,
                            const std::string &ctrl_class_name)
{

//
// Get controller class features and extra attribute list
// For Python controller, check that methods to set/get extra attributes are defined if
// some of them are defined
//

    features_name.clear();
    extra_attributes.clear();

    if (lang == PYTHON)
    {
        AutoPoolLock lo(monitor);

        try
        {
            ite->get_sequence_value(ctrl_class_name,"ctrl_features",features_name);
        }
        catch (Tango::DevFailed &e)
        {
            if (strcmp(e.errors[0].reason.in(),"Pool_PythonSequenceNotFound") != 0)
                throw;
        }

        try
        {
            ite->get_extra_attr_dec(ctrl_class_name,"ctrl_extra_attributes",extra_attributes);
        }
        catch (Tango::DevFailed &e)
        {
            if (strcmp(e.errors[0].reason.in(),"Pool_PythonSequenceNotFound") != 0)
                throw;
        }

//
// If some extra attributes are defined, check that methods used to get/set
// them are also defined
//

        if (extra_attributes.size() != 0)
        {
            PyObject *pClass = NULL;
            pClass = PyObject_GetAttrString(static_cast<PyExternalFile *>(ite)->get_py_module(), (char *)ctrl_class_name.c_str());

            if(pClass == NULL)
            {
                PyErr_Clear();

                TangoSys_OMemStream o;
                o << "Invalid Module: reference to " << ctrl_class_name << " not found" << ends;
                Tango::Except::throw_exception((const char *)"Pool_CantLocatePythonClass",o.str(),
                                                (const char *)"CtrlFica::init()");
            }

            try
            {
                static_cast<PyExternalFile *>(ite)->check_py_method(pClass,"GetExtraAttributePar");
                static_cast<PyExternalFile *>(ite)->check_py_method(pClass,"SetExtraAttributePar");
            }
            catch (Tango::DevFailed &e)
            {
                Py_DECREF(pClass);
                throw;
            }

            Py_DECREF(pClass);
        }
    }
    else
    {
        ite->get_sequence_value(ctrl_class_name,"ctrl_features",features_name);

        ite->get_extra_attr_dec(ctrl_class_name,"ctrl_extra_attributes",extra_attributes);
    }
}


//+----------------------------------------------------------------------------
//
// method : 		CtrlFiCa::check_valid_features()
//
// description : 	Check if the controller features are in the list of
//					pre-defined ones
//
// in : - ctrl_class_name : The controller class name
//
//-----------------------------------------------------------------------------

void CtrlFiCa::check_valid_features(const std::string &ctrl_class_name)
{

//
// Try to find feature in list
//

    for (unsigned long index = 0;index < features_name.size();index++)
    {
        string tmp_str(features_name[index]);
        transform(tmp_str.begin(),tmp_str.end(),tmp_str.begin(),::tolower);

        long loop;
        for (loop = 0;loop < nb_avail_feat;loop++)
        {
            if (tmp_str == avail_feat_lower[loop])
                break;
        }

        if (loop == nb_avail_feat)
        {
            TangoSys_OMemStream o;
            o << "Controller feature " << features_name[index] << " in class " << ctrl_class_name << " is not in the list of pre-defined controller features" << ends;
            Tango::Except::throw_exception((const char *)"Pool_CantFindFeature",o.str(),
                                       (const char *)"CtrlFica::check_valid_features()");
        }
        else
        {

//
// Replace the feature name with the name defined in the list
// of defined features (case letter problem)
//

            features_name[index] = avail_feat[loop];
        }
    }
}

//+----------------------------------------------------------------------------
//
// method : 		CtrlFiCa::check_features()
//
// description : 	Get and check if the controller features are in the list of
//					pre-defined ones
//
// in : - lang : The controller language
//		- file : The controller file
//		- ctrl_class_name : The controller class name
//
//-----------------------------------------------------------------------------

void CtrlFiCa::check_features(Language lang,CtrlFile *file,const std::string &ctrl_class_name)
{
    get_features(lang,file,ctrl_class_name);
    check_valid_features(ctrl_class_name);
    init_special_features(ctrl_class_name);
}

//+----------------------------------------------------------------------------
//
// method : 		MotCtrlFiCa::MotCtrlFiCa()
//
// description : 	constructor for CtrlFiCa class
//
// in : - type : The controller file_class name (crtl_class_name/inst name in lowercase letter)
//      - f_name : The controller class file name (cpp lib or python module)
//		- ctrl_class_name : The controller class name (case dependant)
//      - ob_type : the type of controller. Currently allowed only "Motor"
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

MotCtrlFiCa::MotCtrlFiCa(const std::string &type,const std::string &f_name,const std::string &ctrl_class_name,Pool *dev):
CtrlFiCa(type,f_name,ctrl_class_name,MOTOR_CTRL,dev),
ctrl_backlash(false),ctrl_rounding(false)
{
//
// Get the list of defined features
// and build a list of them with lower case letters
//

    avail_feat = Motor_ns::MotorFeaturesList;

    nb_avail_feat = 0;
    while (avail_feat[nb_avail_feat] != NULL)
        nb_avail_feat++;

    avail_feat_lower.clear();
    for (long loop = 0;loop < nb_avail_feat;loop++)
    {
        string tmp_str(avail_feat[loop]);
        transform(tmp_str.begin(),tmp_str.end(),tmp_str.begin(),::tolower);
        avail_feat_lower.push_back(tmp_str);
    }

//
// Check that the features list contains only valid features
//

    check_valid_features(ctrl_class_name);

//
// Init specific features
//

    init_special_features(ctrl_class_name);

}

//+----------------------------------------------------------------------------
//
// method : 		CtrlFiCa::init_special_features()
//
// description : 	init internal data if controller has one of the
//					special features.
//					Special features are:
//						- Backlash
//						- Rounding
//
//-----------------------------------------------------------------------------

void MotCtrlFiCa::init_special_features(const std::string &ctrl_class_name)
{
    for (unsigned long loop = 0;loop < features_name.size();loop++)
    {
        string tmp_str(features_name[loop]);
        transform(tmp_str.begin(),tmp_str.end(),tmp_str.begin(),::tolower);

//
// Backlash
//

        string f_name;
        f_name = BACKLASH_FEATURE_NAME;
        transform(f_name.begin(),f_name.end(),f_name.begin(),::tolower);

        if (tmp_str == f_name)
            ctrl_backlash = true;

//
// Rounding
//

        f_name = ROUNDING_FEATURE_NAME;
        transform(f_name.begin(),f_name.end(),f_name.begin(),::tolower);

        if (tmp_str == f_name)
            ctrl_rounding = true;
    }
}

//==============================================================================
//
//						PSEUDO MOTOR CONTROLLER FICA CLASS
//
//==============================================================================


//+----------------------------------------------------------------------------
//
// method : 		PseudoMotCtrlFiCa::PseudoMotCtrlFiCa()
//
// description : 	constructor for PseudoMotCtrlFiCa class
//
// in : - type : The controller file_class name (crtl_class_name/inst name in lowercase letter)
//      - f_name : The controller class file name (cpp lib or python module)
//		- ctrl_class_name : The controller class name (case dependant)
//      - ob_type : the type of controller.
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------
PseudoMotCtrlFiCa::PseudoMotCtrlFiCa(const std::string &type,const std::string &f_name,const std::string &ctrl_class_name,Pool *dev):
CtrlFiCa(type,f_name,ctrl_class_name,PSEUDO_MOTOR_CTRL,dev)
{
//
// Init specific features
//
    init_special_features(ctrl_class_name);
}

//+----------------------------------------------------------------------------
//
// method : 		PseudoMotCtrlFiCa::init_special_features()
//
// description : 	init internal data if controller has one of the
//					special features.
//					Special features are:
//
//-----------------------------------------------------------------------------

void PseudoMotCtrlFiCa::init_special_features(const std::string &ctrl_class_name)
{
    pseudo_motor_roles.clear();
    motor_roles.clear();

    Language lang = get_ctrl_file()->get_language();

    if (lang == PYTHON)
    {
        AutoPoolLock lo(monitor);

        try
        {
            get_ctrl_file()->get_sequence_value(ctrl_class_name,"pseudo_motor_roles",
                                    pseudo_motor_roles);
        }
        catch (Tango::DevFailed &e)
        {
            if (strcmp(e.errors[0].reason.in(),"Pool_PythonSequenceNotFound") != 0)
                throw;
        }

        try
        {
            get_ctrl_file()->get_sequence_value(ctrl_class_name,"motor_roles",motor_roles);
        }
        catch (Tango::DevFailed &e)
        {
            if (strcmp(e.errors[0].reason.in(),"Pool_PythonSequenceNotFound") != 0)
                throw;
        }
    }
    else
    {
        get_ctrl_file()->get_sequence_value(ctrl_class_name,"pseudo_motor_roles",
                pseudo_motor_roles);

        get_ctrl_file()->get_sequence_value(ctrl_class_name,"motor_roles",motor_roles);
    }

    // If the pseudo motor roles were not defined it means that there is only
    // one pseudo motor. This pseudo motor role name will be the same as the
    // pseudo motor controller class name
    if(pseudo_motor_roles.empty())
        pseudo_motor_roles.push_back(ctrl_class_name);

}

//==============================================================================
//
//						COUNTER TIMER CONTROLLER FICA CLASS
//
//==============================================================================


//+----------------------------------------------------------------------------
//
// method : 		CoTiCtrlFiCa::CoTiCtrlFiCa()
//
// description : 	constructor for CoTiCtrlFiCa class
//
// in : - type : The controller file_class name (crtl_class_name/inst name in lowercase letter)
//      - f_name : The controller class file name (cpp lib or python module)
//		- ctrl_class_name : The controller class name (case dependant)
//      - ob_type : the type of controller.
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

CoTiCtrlFiCa::CoTiCtrlFiCa(const std::string &type,const std::string &f_name,const std::string &ctrl_class_name,Pool *dev):
CtrlFiCa(type,f_name,ctrl_class_name,COTI_CTRL,dev)
{

}

//+----------------------------------------------------------------------------
//
// method : 		CoTiCtrlFiCa::init_special_features()
//
// description : 	init internal data if controller has one of the
//					special features.
//					Special features are:
//
//-----------------------------------------------------------------------------

void CoTiCtrlFiCa::init_special_features(const std::string &ctrl_class_name)
{
}

//==============================================================================
//
//						ZERO D CONTROLLER FICA CLASS
//
//==============================================================================

//+----------------------------------------------------------------------------
//
// method : 		ZeroDCtrlFiCa::ZeroDCtrlFiCa()
//
// description : 	constructor for ZeroDCtrlFiCa class
//
// in : - type : The controller file_class name (crtl_class_name/inst name in lowercase letter)
//      - f_name : The controller class file name (cpp lib or python module)
//		- ctrl_class_name : The controller class name (case dependant)
//      - ob_type : the type of controller.
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

ZeroDCtrlFiCa::ZeroDCtrlFiCa(const std::string &type,const std::string &f_name,const std::string &ctrl_class_name,Pool *dev):
CtrlFiCa(type,f_name,ctrl_class_name,ZEROD_CTRL,dev)
{

}

//==============================================================================
//
//						ONE D CONTROLLER FICA CLASS
//
//==============================================================================

//+----------------------------------------------------------------------------
//
// method : 		OneDCtrlFiCa::OneDCtrlFiCa()
// 
// description : 	constructor for OneDCtrlFiCa class
//
// in : - type : The controller file_class name (crtl_class_name/inst name in lowercase letter)
//      - f_name : The controller class file name (cpp lib or python module)
//		- ctrl_class_name : The controller class name (case dependant)
//      - ob_type : the type of controller.
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

OneDCtrlFiCa::OneDCtrlFiCa(const std::string &type,const std::string &f_name,const std::string &ctrl_class_name,Pool *dev):
CtrlFiCa(type,f_name,ctrl_class_name,ONED_CTRL,dev)
{
    
}

//==============================================================================
//
//						TWO D CONTROLLER FICA CLASS
//
//==============================================================================

//+----------------------------------------------------------------------------
//
// method : 		TwoDCtrlFiCa::TwoDCtrlFiCa()
// 
// description : 	constructor for TwoDCtrlFiCa class
//
// in : - type : The controller file_class name (crtl_class_name/inst name in lowercase letter)
//      - f_name : The controller class file name (cpp lib or python module)
//		- ctrl_class_name : The controller class name (case dependant)
//      - ob_type : the type of controller.
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

TwoDCtrlFiCa::TwoDCtrlFiCa(const std::string &type,const std::string &f_name,const std::string &ctrl_class_name,Pool *dev):
CtrlFiCa(type,f_name,ctrl_class_name,TWOD_CTRL,dev)
{
    
}

//==============================================================================
//
//						PSEUDO COUNTER CONTROLLER FICA CLASS
//
//==============================================================================


//+----------------------------------------------------------------------------
//
// method : 		PseudoCoCtrlFiCa::PseudoCoCtrlFiCa()
//
// description : 	constructor for PseudoCoCtrlFiCa class
//
// in : - type : The controller file_class name (crtl_class_name/inst name in lowercase letter)
//      - f_name : The controller class file name (cpp lib or python module)
//		- ctrl_class_name : The controller class name (case dependant)
//      - ob_type : the type of controller.
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

PseudoCoCtrlFiCa::PseudoCoCtrlFiCa(const std::string &type,const std::string &f_name,const std::string &ctrl_class_name,Pool *dev):
CtrlFiCa(type,f_name,ctrl_class_name,PSEUDO_COUNTER_CTRL,dev)
{
//
// Init specific features
//
    init_special_features(ctrl_class_name);
}

//+----------------------------------------------------------------------------
//
// method : 		PseudoCoCtrlFiCa::init_special_features()
//
// description : 	init internal data if controller has one of the
//					special features.
//					Special features are:
//
//-----------------------------------------------------------------------------

void PseudoCoCtrlFiCa::init_special_features(const std::string &ctrl_class_name)
{
    pseudo_counter_roles.clear();
    counter_roles.clear();

    Language lang = get_ctrl_file()->get_language();

    if (lang == PYTHON)
    {
        AutoPoolLock lo(monitor);

        try
        {
            get_ctrl_file()->get_sequence_value(ctrl_class_name,
                    "pseudo_counter_roles",	pseudo_counter_roles);
        }
        catch (Tango::DevFailed &e)
        {
            if (strcmp(e.errors[0].reason.in(),"Pool_PythonSequenceNotFound") != 0)
                throw;
        }

        try
        {
            get_ctrl_file()->get_sequence_value(ctrl_class_name,"counter_roles",
                                                counter_roles);
        }
        catch (Tango::DevFailed &e)
        {
            if (strcmp(e.errors[0].reason.in(),"Pool_PythonSequenceNotFound") != 0)
                throw;
        }
    }
    else
    {
        get_ctrl_file()->get_sequence_value(ctrl_class_name,
                "pseudo_counter_roles",	pseudo_counter_roles);

        get_ctrl_file()->get_sequence_value(ctrl_class_name, "counter_roles",
                counter_roles);
    }

    // If the pseudo counter roles were not defined it means that there is only
    // one pseudo counter. This pseudo counter role name will be the same as the
    // pseudo counter controller class name
    if(pseudo_counter_roles.empty())
        pseudo_counter_roles.push_back(ctrl_class_name);
}


//+----------------------------------------------------------------------------
//
// method : 		ZeroDCtrlFiCa::init_special_features()
//
// description : 	init internal data if controller has one of the
//					special features.
//					Special features are:
//
//-----------------------------------------------------------------------------

void ZeroDCtrlFiCa::init_special_features(const std::string &ctrl_class_name)
{
}

//+----------------------------------------------------------------------------
//
// method : 		OneDCtrlFiCa::init_special_features()
// 
// description : 	init internal data if controller has one of the
//					special features.
//					Special features are:
//
//-----------------------------------------------------------------------------

void OneDCtrlFiCa::init_special_features(const std::string &ctrl_class_name)
{
}

//+----------------------------------------------------------------------------
//
// method : 		TwoDCtrlFiCa::init_special_features()
// 
// description : 	init internal data if controller has one of the
//					special features.
//					Special features are:
//
//-----------------------------------------------------------------------------

void TwoDCtrlFiCa::init_special_features(const std::string &ctrl_class_name)
{
}

//==============================================================================
//
//						COMMUNICATION CHANNEL CONTROLLER FICA CLASS
//
//==============================================================================

//+----------------------------------------------------------------------------
//
// method : 		ComCtrlFiCa::ComCtrlFiCa()
//
// description : 	constructor for ComCtrlFiCa class
//
// in : - type : The controller file_class name (crtl_class_name/inst name in lowercase letter)
//      - f_name : The controller class file name (cpp lib or python module)
//		- ctrl_class_name : The controller class name (case dependant)
//      - ob_type : the type of controller.
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

ComCtrlFiCa::ComCtrlFiCa(const std::string &type, const std::string &f_name, const std::string &ctrl_class_name,
                         Pool *dev):
CtrlFiCa(type,f_name,ctrl_class_name,COM_CTRL,dev)
{
}

//+----------------------------------------------------------------------------
//
// method : 		ComCtrlFiCa::init_special_features()
//
// description : 	init internal data if controller has one of the
//					special features.
//					Special features are:
//
//-----------------------------------------------------------------------------

void ComCtrlFiCa::init_special_features(const std::string &ctrl_class_name)
{
}

//==============================================================================
//
//						IOREGISTER CONTROLLER FICA CLASS
//
//==============================================================================

//+----------------------------------------------------------------------------
//
// method : 		IORegisterCtrlFiCa::IORegisterCtrlFiCa()
//
// description : 	constructor for IORegisterCtrlFiCa class
//
// in : - type : The controller file_class name (crtl_class_name/inst name in lowercase letter)
//      - f_name : The controller class file name (cpp lib or python module)
//		- ctrl_class_name : The controller class name (case dependant)
//      - ob_type : the type of controller.
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

IORegisterCtrlFiCa::IORegisterCtrlFiCa(const std::string &type, const std::string &f_name, const std::string &ctrl_class_name,
                                       Pool *dev):
CtrlFiCa(type,f_name,ctrl_class_name,IOREGISTER_CTRL,dev)
{
}

//+----------------------------------------------------------------------------
//
// method : 		IORegisterCtrlFiCa::init_special_features()
//
// description : 	init internal data if controller has one of the
//					special features.
//					Special features are:
//
//-----------------------------------------------------------------------------

void IORegisterCtrlFiCa::init_special_features(const std::string &ctrl_class_name)
{
}

//==============================================================================
//
//						CONSTRAINT FICA CLASS
//
//==============================================================================

//+----------------------------------------------------------------------------
//
// method : 		ConstraintFiCa::ConstraintFiCa()
//
// description : 	constructor for ConstraintFiCa class
//
// in : - type : The controller file_class name (crtl_class_name/inst name in
//               lowercase letter)
//      - f_name : The controller class file name (cpp lib or python module)
//		- ctrl_class_name : The controller class name (case dependant)
//      - ob_type : the type of controller.
//		- pool_class : Pointer to the PoolClass object
//
//-----------------------------------------------------------------------------

ConstraintFiCa::ConstraintFiCa(const std::string &type, const std::string &f_name,
                               const std::string &ctrl_class_name,Pool *dev):
CtrlFiCa(type,f_name,ctrl_class_name,CONSTRAINT_CTRL,dev)
{
//
// Init specific features
//
    init_special_features(ctrl_class_name);
}

//+----------------------------------------------------------------------------
//
// method : 		ConstraintFiCa::init_special_features()
//
// description : 	init internal data if controller has one of the
//					special features.
//					Special features are:
//
//-----------------------------------------------------------------------------

void ConstraintFiCa::init_special_features(const std::string &ctrl_class_name)
{
    roles.clear();

    Language lang = get_ctrl_file()->get_language();

    if (lang == PYTHON)
    {
        AutoPoolLock lo(monitor);

        try
        {
            get_ctrl_file()->get_sequence_value(ctrl_class_name,"roles",roles);
        }
        catch (Tango::DevFailed &e)
        {
            if (strcmp(e.errors[0].reason.in(),"Pool_PythonSequenceNotFound") != 0)
                throw;
        }
    }
    else
    {
        get_ctrl_file()->get_sequence_value(ctrl_class_name,"roles",roles);
    }
}

} // End of Pool_ns namespacce
