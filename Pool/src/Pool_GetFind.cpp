//+=============================================================================
//
// file :         Pool_GetFind.cpp
//
// description :  C++ source for Pool methods related to getting & finding
//                elements
//
// project :      TANGO Device Server
//
// $Author: tcoutinho $
//
// copyleft :     CELLS/ALBA
//				  Edifici Ciències Nord. Mòdul C-3 central.
//  			  Campus Universitari de Bellaterra. Universitat Autònoma de Barcelona
//  			  08193 Bellaterra, Barcelona
//  			  Spain
//
//+=============================================================================


#include "Pool.h"

#include <pool/Ctrl.h>
#include <pool/ComCtrl.h>
#include <pool/MotCtrl.h>
#include <pool/CoTiCtrl.h>
#include <pool/ZeroDCtrl.h>
#include <pool/OneDCtrl.h>
#include <pool/TwoDCtrl.h>
#include <pool/PseudoCoCtrl.h>
#include <pool/IORegisterCtrl.h>
#include <dirent.h>

namespace Pool_ns
{

PoolClass* Pool::get_pool_class()
{
    return (PoolClass*)get_device_class();
}

//------------------------------------------------------------------------------
// Pool::get_path_subdirs
//
void Pool::get_path_subdirs(string &dir, vector<string> &paths)
{
    DIR *pdir = opendir(dir.c_str());
    
    if(pdir != NULL)
    {
        // If dir is already in the list of known directories, skip it
        if(find(paths.begin(),paths.end(),dir) != paths.end())
            return;
        paths.push_back(dir);
    
        // this is done to avoid having many file descriptors opened since this
        // is a recursive method
        vector<string> pending_dirs;
        
        struct dirent *pent;
        struct stat buf;
        while((pent = readdir(pdir)))
        {
            if(pent->d_name[0] == '.')
                continue;

            string element = dir + "/";
            element += pent->d_name;	
            
            stat(element.c_str(), &buf);
            
            if(!S_ISDIR(buf.st_mode))
                continue;
            
            pending_dirs.push_back(element);
        }
        closedir(pdir);
        
        vector<string>::iterator pd_it = pending_dirs.begin();
        for(;pd_it != pending_dirs.end(); ++pd_it)
        {
            get_path_subdirs(*pd_it, paths);
        }
    }
}

//------------------------------------------------------------------------------
// Pool::get_pool_path
//
vector<string> &Pool::get_pool_path()
{
    
//
// Immediately returns, if the PoolPath has already been splitted
//

    if (poolPath_splitted == false)
    {
        pool_path.clear();

//
// Throws exception if PoolPath property is not defined
//
        
        if (poolPath.size() == 0 || poolPath[0] == "NotDefined")
        {
            TangoSys_OMemStream o;
            o << "The PoolPath device property is not defined. "
                 "Please, define one.";
        
            Tango::Except::throw_exception(
                    (const char *)"Pool_PoolPathNotDefined",o.str(),
                    (const char *)"Pool::get_pool_path");
        }
                
        const char delims = ':';
        string::size_type beg_pos, end_pos;
        
        vector<string>::iterator pp_it = poolPath.begin();
        for(;pp_it != poolPath.end(); ++pp_it)
        {
            string &poolPathElem = *pp_it;
            
            // Empty string: skip it
            if (poolPathElem.size() == 0)
                continue;
            
            beg_pos = poolPathElem.find_first_not_of(delims);
            
            // Empty string: skip it
            if (beg_pos == string::npos)
                continue;
            
            while(true)
            {
                end_pos = poolPathElem.find(delims,beg_pos);
    
                string path_elem;
                if(end_pos == string::npos)
                {
                    if(beg_pos == string::npos)
                        break;
                    path_elem = poolPathElem.substr(beg_pos);
                }
                else
                    path_elem = poolPathElem.substr(beg_pos,end_pos - beg_pos);
                
                if(path_elem[0] != '/') 
                {
                    TangoSys_OMemStream o;
                    o << path_elem << " is not an absolute path. Please give "
                         "an absolute path in the PoolPath property" << ends;
            
                    Tango::Except::throw_exception(
                            (const char *)"Pool_DirUnsupportedType",o.str(),
                            (const char *)"Pool::get_pool_path");
                }
                
                get_path_subdirs(path_elem, pool_path);
                
                if(end_pos == string::npos)
                    break;   		
                beg_pos = poolPathElem.find_first_not_of(delims, end_pos);
            }
        }
        poolPath_splitted = true;
//		DEBUG_STREAM << "PP IS:"<<endl;
//		for(unsigned long ul = 0; ul < pool_path.size(); ++ul)
//			DEBUG_STREAM << pool_path[ul] << endl;
    }
    
    return pool_path;
}

//------------------------------------------------------------------------------
// Pool::find_file_in_pool_path
//
bool Pool::find_file_in_pool_path(string &f_name, string &f_path,Language lang)
{
    vector<string> &path = get_pool_path();
    string name;
    
    if (lang == PYTHON)	
        name = f_name.rfind(".py") == string::npos ? f_name + ".py" : f_name;
    else
        name = f_name.rfind(".la") == string::npos ? f_name + ".la" : f_name;
    
    for(vector<string>::iterator path_ite = path.begin(); path_ite != path.end(); path_ite++)
    {
        vector<string> files;
        
        if (lang == PYTHON)
            get_files_with_extension(*path_ite,".py",files);
        else
            get_files_with_extension(*path_ite,".la",files);
            
        for(vector<string>::iterator ite = files.begin(); ite != files.end(); ite++)
        {	
            string curr_file = (*ite).substr((*ite).rfind("/")+1);
            if(curr_file == name)
            {
                f_path = (*ite);
                return true;	
            }
        }
    }
    return false;
}

//------------------------------------------------------------------------------
// Pool::find_file_in_pool_path
//
bool Pool::find_file_in_pool_path(string &f_name, string &f_path)
{
    vector<string> &path = get_pool_path();
    
    for(vector<string>::iterator path_ite = path.begin(); 
        path_ite != path.end(); path_ite++)
    {
        vector<string> files;
        
        get_files_with_extension(*path_ite,".*",files);
            
        for(vector<string>::iterator ite = files.begin(); 
            ite != files.end(); ite++)
        {	
            string curr_file = (*ite).substr((*ite).rfind("/")+1);
            if(curr_file == f_name)
            {
                f_path = (*ite);
                return true;	
            }
        }
    }
    return false;
}

//------------------------------------------------------------------------------
// Pool::get_ghost_motor_group_ptr
//
MotorGroup_ns::MotorGroup* Pool::get_ghost_motor_group_ptr()
{	
    std::vector<Tango::DeviceImpl *> &dev_list = 
        Tango::Util::instance()->get_device_list_by_class("MotorGroup");
    
    for (vector<Tango::DeviceImpl *>::iterator it = dev_list.begin();
         it != dev_list.end(); ++it)
    {
        MotorGroup_ns::MotorGroup *grp_ptr = 
            static_cast<MotorGroup_ns::MotorGroup *>(*it);
        if(grp_ptr->is_ghost())
            return grp_ptr;
    }
    
    TangoSys_OMemStream o;
    o << "No ghost group found in motor group devices" << ends;

    Tango::Except::throw_exception(
            (const char *)"Pool_MotorGroupNotFound", o.str(),
            (const char *)"Pool::get_ghost_motor_group_ptr");	

    // To quiet the compiler
    return NULL;
}

//------------------------------------------------------------------------------
// Pool::get_ghost_measurement_group_ptr
//
MeasurementGroup_ns::MeasurementGroup* Pool::get_ghost_measurement_group_ptr()
{
    std::vector<Tango::DeviceImpl *> &dev_list = 
        Tango::Util::instance()->get_device_list_by_class("MeasurementGroup");

    for (vector<Tango::DeviceImpl *>::iterator it = dev_list.begin();
         it != dev_list.end(); ++it)
    {
        MeasurementGroup_ns::MeasurementGroup *grp_ptr = 
            static_cast<MeasurementGroup_ns::MeasurementGroup *>(*it);
        if(grp_ptr->is_ghost())
            return grp_ptr;
    }
    
    TangoSys_OMemStream o;
    o << "No ghost group found in measurement group devices" << ends;

    Tango::Except::throw_exception(
                (const char *)"Pool_MeasurementGroupNotFound", o.str(),
                (const char *)"Pool::get_ghost_measurement_group_ptr");

    // To quiet the compiler
    return NULL;
}

//------------------------------------------------------------------------------
// Pool::get_pseudo_motors_that_use_mg
//
bool Pool::get_pseudo_motors_that_use_mg(ElementId mg_id, vector<string> &mgs)
{
    bool any = false;
    PoolElementTypeIt beg, end;
    get_all_elements(PSEUDO_MOTOR_ELEM, beg, end);
    for (PoolElementTypeIt elem_it = beg; elem_it != end; ++elem_it)
    {
        PseudoMotorPool &pmp = get_pseudo_motor(elem_it->second);

        if(pmp.motor_group_id == mg_id)
        {
            mgs.push_back(pmp.name);
            any = true;
        }
    }
    return any;
}

//------------------------------------------------------------------------------
// Pool::get_motor_group_in_hierarchy_containing_elt
//
bool Pool::get_motor_groups_in_hierarchy_containing_elt(MotorGroupPool &mg,
                                                        std::string &elt_name,
                                                        std::vector<std::string> &mgs)
{
    PoolElement *elt = get_element(elt_name);
    if(mg.is_member(elt->get_id()))
    {
        mgs.push_back(mg.name);
        return true;
    }

    vector<MotorGroupPool*> mg_mgs;
    bool res = get_motor_groups_containing_elt(mg.get_id(), mg_mgs);

    if(res == false)
        return false;

    res = false;
    vector<MotorGroupPool*>::iterator ite = mg_mgs.begin();
    for(;ite != mg_mgs.end(); ite++)
    {
        res |= get_motor_groups_in_hierarchy_containing_elt(*(*ite), elt_name, mgs);
    }
    return res;
}

Tango::Attribute &Pool::get_attr_by_elem_type(ElementType type)
{
    std::string attr_name = "unknown";
    
    switch(type)
    {
        case COTI_ELEM:
        case ZEROD_ELEM:
        case ONED_ELEM:
        case TWOD_ELEM:
            attr_name = "ExpChannel";
            break;
        case UNDEF_ELEM:
        case numElementType:
        case CTRL_ELEM:
        case COM_ELEM:
        case MOTOR_ELEM:
        case IOREGISTER_ELEM:
        case PSEUDO_MOTOR_ELEM:
        case PSEUDO_COUNTER_ELEM:
        case CONSTRAINT_ELEM:
        case MOTOR_GROUP_ELEM:
        case MEASUREMENT_GROUP_ELEM:
        default:
            attr_name = ElementTypeStr[type];
            break;
    }
    
    attr_name += "List";
    
    return dev_attr->get_attr_by_name(attr_name.c_str());
}

Tango::Attribute &Pool::get_attr_by_elem(PoolElement &elem)
{
    return get_attr_by_elem(&elem);
}

Tango::Attribute &Pool::get_attr_by_elem(PoolElement* elem)
{
    return get_attr_by_elem_type(elem->get_type());
}

}
