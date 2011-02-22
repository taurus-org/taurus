#include "CPool.h"
#include "config.h"
#include <dirent.h>

namespace Pool_ns
{

DevicePool* DevicePool::singleton_instance = NULL;

DevicePool::DevicePool(PoolThrower *t): PoolElementContainer(t),
last_id(InvalidId), last_ghost_id(InvalidId), last_internal_id(InvalidId), 
pool_version_str(VERSION)
{
    assert(singleton_instance == NULL);
    singleton_instance = this;
    pool_version_nb = to_version_nb(pool_version_str);
}

DevicePool::~DevicePool()
{}

CtrlType DevicePool::str_2_CtrlType(const std::string& type_str)
{
    std::string type_str_l(type_str);
    std::transform(type_str_l.begin(), type_str_l.end(), type_str_l.begin(), ::tolower);

    CtrlType type = UNDEF_CTRL;

    if (type_str_l == "motor")
        type = MOTOR_CTRL;
    else if (type_str_l == "pseudomotor")
        type = PSEUDO_MOTOR_CTRL;
    else if (type_str_l == "countertimer")
        type = COTI_CTRL;
    else if (type_str_l == "zerodexpchannel")
        type = ZEROD_CTRL;
    else if (type_str_l == "onedexpchannel")
        type = ONED_CTRL;
    else if (type_str_l == "twodexpchannel")
        type = TWOD_CTRL;
    else if (type_str_l == "pseudocounter")
        type = PSEUDO_COUNTER_CTRL;
    else if (type_str_l == "communication")
        type = COM_CTRL;
    else if (type_str_l == "ioregister")
        type = IOREGISTER_CTRL;
    else if (type_str_l == "undefined")
        type = UNDEF_CTRL;
    else
    {
        std::ostringstream o;
        o << "Controller of type " << type_str << " unsupported" << std::ends;
        PoolThrower *t = get_instance()->thrower;
        t->throw_exception("DevicePool_UnknownControllerType", o.str(), 
                           "DevicePool::str_2_CtrlType");
    }
    
    return type;
}

//------------------------------------------------------------------------------
// DevicePool::get_controller_from_inst_name
//
ControllerPool &DevicePool::_get_controller_from_inst_name(const std::string &name)
{
    std::string name_lower(name);
    transform(name_lower.begin(), name_lower.end(), name_lower.begin(), ::tolower);
    
    ElemTypeMultiMapIt ctrl_ite, ctrl_end;
    get_all_controller(ctrl_ite, ctrl_end);
    for(; ctrl_ite != ctrl_end; ++ctrl_ite)
    {
        ControllerPool &ctrl = get_controller(ctrl_ite->second);
        
        string tmp_str(ctrl.name);
        tmp_str.erase(0,tmp_str.find('/') + 1);
        if (tmp_str == name_lower)
            return ctrl;
    }

    std::ostringstream o;
    o << "No Controller with name '" << name << "' found." << std::ends;
    thrower->throw_exception("DevicePool_ControllerNotFound", o.str(), 
                             "DevicePool::_get_ctrl_from_inst_name");
    // Just to quiet the compiler
    return *((ControllerPool *)(NULL));
}

//------------------------------------------------------------------------------
// DevicePool::get_controller_nb_by_class_name
//
int32_t DevicePool::get_controller_nb_by_class_name(const std::string &class_name)
{
    int32_t ctr = 0;

    ElemTypeMultiMapIt ctrl_ite, ctrl_end;
    get_all_controller(ctrl_ite, ctrl_end);
    for(; ctrl_ite != ctrl_end; ++ctrl_ite)
    {
        ControllerPool &ctrl = get_controller(ctrl_ite->second);
        if (ctrl.ctrl_class_name == class_name)
            ctr++;
    }
    return ctr;
}

//------------------------------------------------------------------------------
// DevicePool::motor_group_exists
//
bool DevicePool::motor_group_exists(std::vector<ElementId> &g_in, std::string &g_name)
{
    ElemTypeMultiMapIt elem_ite, elem_end;
    get_all_motor_group(elem_ite, elem_end);
    for(; elem_ite != elem_end; ++elem_ite)
    {
        MotorGroupPool &mgp = get_motor_group(elem_ite->second);
        if (mgp.matches_user_members(g_in))
        {
            g_name = mgp.name;
            return true;
        }
    }
    return false;
}

//------------------------------------------------------------------------------
// DevicePool::motor_group_exists
//
bool DevicePool::motor_group_exists(std::vector<std::string> &g_in, std::string &g_name)
{
    ElemTypeMultiMapIt elem_ite, elem_end;
    get_all_motor_group(elem_ite, elem_end);
    for(; elem_ite != elem_end; ++elem_ite)
    {
        MotorGroupPool &mgp = get_motor_group(elem_ite->second);
        if (mgp.matches_user_members(g_in))
        {
            g_name = mgp.name;
            return true;
        }
    }
    return false;
}

//------------------------------------------------------------------------------
// DevicePool::measurement_group_exists
//
bool DevicePool::measurement_group_exists(std::vector<std::string> &g_in, std::string &g_name)
{
    ElemTypeMultiMapIt elem_ite, elem_end;
    get_all_measurement_group(elem_ite, elem_end);
    for(; elem_ite != elem_end; ++elem_ite)
    {
        MeasurementGroupPool &mgp = get_measurement_group(elem_ite->second);
        if (mgp.matches_user_members(g_in))
        {
            g_name = mgp.name;
            return true;
        }
    }
    return false;
}

//------------------------------------------------------------------------------
// DevicePool::to_version_nb
//
int32_t DevicePool::to_version_nb(const std::string &v)
{
    std::ostringstream o;
    o << "The version string '" << v << "' is not in the format 'm.n.r'" << std::ends;
    
    if(v.size() < 5)
    {
        thrower->throw_exception("DevicePool_WrongVersionString", o.str(),
                                 "DevicePool::to_version_nb");
    }

    std::string::size_type p1 = v.find('.');
    std::string::size_type p2 = v.rfind('.');

    if(p1 == std::string::npos || p2 == std::string::npos || p1 == p2)
    {
        thrower->throw_exception("DevicePool_WrongVersionString", o.str(),
                                 "DevicePool::to_version_nb");
    }

    std::istringstream m_str(v.substr(0,p1));
    std::istringstream n_str(v.substr(p1+1,p2-(p1+1)));
    std::istringstream r_str(v.substr(p2+1));

    int32_t m,n,r;
    if(!(m_str >> m) || !(n_str >> n) || !(r_str >> r))
    {
        thrower->throw_exception("DevicePool_WrongVersionString", o.str(),
                                 "DevicePool::to_version_nb");
    }

    return m*10000 + n*100 + r;
}

//------------------------------------------------------------------------------
// DevicePool::get_motor_groups_containing_elt
//
bool DevicePool::get_motor_groups_containing_elt(ElementId elem_id, ElemIdVector &mgs)
{
    bool any = false;
    
    for (PoolElementTypeIt elem_it = element_types.lower_bound(MOTOR_GROUP_ELEM);
         elem_it != element_types.upper_bound(MOTOR_GROUP_ELEM); ++elem_it)
    {
        MotorGroupPool &mgp = get_motor_group(elem_it->second);
        if (mgp.is_member(elem_id) == true)
        {
            mgs.push_back(mgp.get_id());
            any = true;
        }
    }
    return any;
}

//------------------------------------------------------------------------------
// DevicePool::get_motor_groups_containing_elt
//
bool DevicePool::get_motor_groups_containing_elt(ElementId elem_id, 
                                                 std::vector<std::string> &mgs)
{
    ElemIdVector v;
    bool any = get_motor_groups_containing_elt(elem_id, v);
    for(ElemIdVectorIt it = v.begin(); it != v.end(); ++it)
        mgs.push_back(get_motor_group(*it).get_name());
    return any;
}

//------------------------------------------------------------------------------
// DevicePool::get_motor_groups_containing_elt
//
bool DevicePool::get_motor_groups_containing_elt(std::string &elt_name, 
                                                 std::vector<std::string> &mgs)
{
    PoolElement *elem = get_element(elt_name);
    return get_motor_groups_containing_elt(elem->get_id(), mgs);
}

//------------------------------------------------------------------------------
// DevicePool::get_motor_groups_containing_elt
//
bool DevicePool::get_motor_groups_containing_elt(ElementId elem_id,
                                                 std::vector<MotorGroupPool*> &mgs)
{
    ElemIdVector v;
    bool any = get_motor_groups_containing_elt(elem_id, v);
    for(ElemIdVectorIt it = v.begin(); it != v.end(); ++it)
        mgs.push_back(&get_motor_group(*it));
    return any;
}

//------------------------------------------------------------------------------
// DevicePool::get_motor_groups_containing_elt
//
bool DevicePool::get_motor_groups_containing_elt(std::string &elem_name, 
                                                 std::vector<MotorGroupPool*> &mgs)
{
    ElementId elem_id = get_element_id(elem_name);
    return get_motor_groups_containing_elt(elem_id, mgs);
}

//------------------------------------------------------------------------------
// DevicePool::get_measurement_groups_containing_elt
//
bool DevicePool::get_measurement_groups_containing_elt(ElementId elem_id, 
                                                       ElemIdVector &mgs)
{
    bool any = false;
    
    for (PoolElementTypeIt elem_it = element_types.lower_bound(MEASUREMENT_GROUP_ELEM);
         elem_it != element_types.upper_bound(MEASUREMENT_GROUP_ELEM); ++elem_it)
    {
        MeasurementGroupPool &mgp = get_measurement_group(elem_it->second);
        if (mgp.is_member(elem_id) == true)
        {
            mgs.push_back(mgp.get_id());
            any = true;
        }
    }
    return any;
}

//------------------------------------------------------------------------------
// DevicePool::get_measurement_groups_containing_elt
//
bool DevicePool::get_measurement_groups_containing_elt(ElementId elem_id, 
                                                       std::vector<std::string> &mgs)
{
    ElemIdVector v;
    bool any = get_measurement_groups_containing_elt(elem_id, v);
    for(ElemIdVectorIt it = v.begin(); it != v.end(); ++it)
        mgs.push_back(get_measurement_group(*it).get_name());
    return any;
}

//------------------------------------------------------------------------------
// DevicePool::get_measurement_groups_containing_elt
//
bool DevicePool::get_measurement_groups_containing_elt(std::string &elt_name, 
                                                       std::vector<std::string> &mgs)
{
    PoolElement *elem = get_element(elt_name);
    return get_measurement_groups_containing_elt(elem->get_id(), mgs);
}

//------------------------------------------------------------------------------
// DevicePool::get_measurement_groups_containing_elt
//
bool DevicePool::get_measurement_groups_containing_elt(std::string &elem_name, 
                                                       std::vector<MeasurementGroupPool*> &mgs)
{
    ElementId elem_id = get_element_id(elem_name);
    ElemIdVector v;
    bool any = get_measurement_groups_containing_elt(elem_id, v);
    for(ElemIdVectorIt it = v.begin(); it != v.end(); ++it)
        mgs.push_back(&get_measurement_group(*it));
    return any;
}

CtrlType DevicePool::str_2_CtrlType(std::string &type)
{
    std::string type_l(type);
    std::transform(type_l.begin(), type_l.end(), type_l.begin(), ::tolower);

//
// Convert string to one value of the CtrlType enumeration
//
    
    CtrlType o_type = UNDEF_CTRL;

    if (type_l == "motor")
        o_type = MOTOR_CTRL;
    else if (type_l == "pseudomotor")
        o_type = PSEUDO_MOTOR_CTRL;
    else if (type_l == "countertimer")
        o_type = COTI_CTRL;
    else if (type_l == "zerodexpchannel")
        o_type = ZEROD_CTRL;
    else if (type_l == "onedexpchannel")
        o_type = ONED_CTRL;
    else if (type_l == "twodexpchannel")
        o_type = TWOD_CTRL;
    else if (type_l == "pseudocounter")
        o_type = PSEUDO_COUNTER_CTRL;
    else if (type_l == "communication")
        o_type = COM_CTRL;
    else if (type_l == "ioregister")
        o_type = IOREGISTER_CTRL;
    else if (type_l == "undefined")
        o_type = UNDEF_CTRL;
    else
        o_type = UNDEF_CTRL;
    
    return o_type;
}

//------------------------------------------------------------------------------
// DevicePool::get_files_with_extension
//
void DevicePool::get_files_with_extension(std::string &dir, const char *f_ext,
                                          std::vector<std::string> &lst)
{
    //DEBUG_STREAM << "Entering get_files_with_extension for " << f_ext 
    //             << " files in directory " << dir << endl;
    errno = 0;
    
    DIR *pdir = opendir(dir.c_str());
    
    std::string ext(f_ext);
    
    bool any_ext;
    {
        std::string ext(f_ext);
        any_ext = ext == ".*" || ext == "*";
    }
    
    
    if(pdir != NULL)
    {
        struct dirent *pent;
        while((pent = readdir(pdir)))
        {
            if(pent->d_name[0] == '.')
                continue;
                
            std::string element = dir + "/";
            element += pent->d_name;
            
            if(pent->d_type == DT_DIR)
            {
                // ignore directories
            }
            else if(any_ext ||(element.rfind(f_ext, element.size()-1) == element.size() - 3))
            {
                bool new_file = true;
                for(vector<string>::iterator ite = lst.begin(); ite != lst.end(); ite++)
                {
                    std::string curr_name = ite->substr(ite->rfind('/')+1);
                    if( curr_name == pent->d_name )
                    {
                        new_file = false;
                        break;
                    }
                }
                if(new_file == true)
                {
                    lst.push_back(element);
                }
            }
        }
        
        closedir(pdir);
    }
    
    /* TODO
    if(errno) 
    {
        if(EACCES == errno)
        {
            INFO_STREAM << "Permission denied on directory " << dir.c_str();
        }
        else if(EMFILE == errno)
        {   
            INFO_STREAM << "Too many file descriptors in use by process";
        }
        else if(ENFILE == errno)
        {
            INFO_STREAM << "Too many files are currently open in the system";
        }
        else if(ENOENT == errno)
        {
            INFO_STREAM << "Directory does not exist: " << dir.c_str();
        }
        else if(ENOTDIR == errno)
        {
            INFO_STREAM << dir.c_str() << "is not a directory";
        }
    }
    */
}

InstrumentPool *DevicePool::add_instrument(const std::string &type,
                                           const std::string &full_name,
                                           ElementId id /*= InvalidId*/)
{
    // Check for valid type
    if(type.empty())
    {
        thrower->throw_exception("DevicePool_InvalidInstrumentType",
            "Instrument type must not be empty. "
            "Instrument name must be in the format <name>('<type>')' where <name> "
            "is a '/' separated string and <type> a single word",
            "DevicePool::add_instrument");
    }
    
    // Check for valid name
    if(full_name.empty() || full_name[0] != '/')
    {
        thrower->throw_exception("DevicePool_InvalidInstrumentName",
            "Instrument name must be in the format <name>('<type>')' where <name> "
            "is a '/' separated string and <type> a single word",
            "DevicePool::add_instrument");
    }
    
    // Check for existing element
    try
    {
        get_element_by_full_name(full_name);

        std::ostringstream o;
        o << "An instrument named '" << full_name << "' already exists" << std::ends;
        thrower->throw_exception("DevicePool_InstrumentExists", o.str(),
                                 "DevicePool::add_instrument");
    }
    catch(...) {}
    
    size_t sep = full_name.rfind('/');
    std::string parent = sep == 0 ? "" : full_name.substr(0, sep),
                name   = sep == 0 ? full_name : full_name.substr(sep+1);
    
    // Check for existing element
    if (element_exists(name))
    {
        std::ostringstream o;
        o << "An element named '" << name << "' already exists" << std::ends;
        thrower->throw_exception("DevicePool_ElementExists", o.str(),
                                 "DevicePool::add_instrument");
    }
    
    // Check that ID does not exist yet
    if (id != InvalidId)
    {
        try 
        { 
            PoolElement *elem = get_element(id);
            
            std::ostringstream o;
            o << "An element with ID " << id << " named '" << elem->get_name() 
              << "' already exists" << std::ends;
            thrower->throw_exception("DevicePool_ElementIDExists", o.str(),
                                     "DevicePool::add_instrument");
        }
        catch(...) {}
    }
    
    // Check that the parent instrument exists
    if (!parent.empty() && !instrument_exists(parent))
    {
        std::ostringstream o;
        o << "The parent instrument '" << parent << "' does not exist."
          << " You must create the parent instrument first" << std::ends;
        thrower->throw_exception("DevicePool_ParentInstrumentMissing", o.str(),
                                 "DevicePool::add_instrument");
    }
    
    InstrumentPool *instrument = new InstrumentPool(this, type, full_name, id);
    add_element(instrument);
    return instrument;
}

}
