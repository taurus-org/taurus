//+=============================================================================
//
// file :         Pool_AddRemove.cpp
//
// description :  C++ source for Pool methods related to adding / removing
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

#include "PoolClass.h"
#include "PoolUtil.h"
#include "Motor.h"
#include "MotorGroup.h"
#include "PseudoMotor.h"
#include "CTExpChannel.h"
#include "ZeroDExpChannel.h"
#include "OneDExpChannel.h"
#include "TwoDExpChannel.h"
#include "PseudoCounter.h"
#include "MeasurementGroup.h"
#include "CommunicationChannel.h"
#include "IORegister.h"

#include <pool/Ctrl.h>
#include <pool/ComCtrl.h>
#include <pool/MotCtrl.h>
#include <pool/CoTiCtrl.h>
#include <pool/ZeroDCtrl.h>
#include <pool/OneDCtrl.h>
#include <pool/TwoDCtrl.h>
#include <pool/PseudoCoCtrl.h>

namespace Pool_ns
{

struct PoolElementComp: public binary_function<PoolElement,PoolElement,bool>
{
    bool operator() (PoolElement &mp1,PoolElement &mp2)
    {
        return mp1.id < mp2.id;
    }
};

struct PseudoMotorComp: public binary_function<PseudoMotorPool,PseudoMotorPool,bool>
{
    bool operator() (PseudoMotorPool &pmp1,PseudoMotorPool &pmp2)
    {
        return pmp1.id < pmp2.id;
    }
};

//------------------------------------------------------------------------------
// Pool::add_element
//
void Pool::add_element(PoolElement *pe)
{
    DevicePool::add_element(pe);

    reserve_id(pe->id);

    PoolElementProxy *proxy = pe->get_proxy();
    if(proxy)
    {
        Tango::Device_4Impl *dev = dynamic_cast<PoolBaseDev*> (proxy);

        set_tango_element(pe->id, NULL, dev);
    }
//
// It is necessary to force proxy creation after this method.
// This method can be called when creating the specific tango device (where the
// proxy will be created by the Pool afterwards) but also in case of Init
// command on the device. If a write of the Position attribute
// is executed just after, we need to create the proxy
//
    proxy_created = false;
}

PoolElement* Pool::rename_element(const std::string &old_alias, 
                                  const std::string &new_alias, ElemSet &deps)
{
    // Lock to not allow any operations while the name is changed
    Tango::AutoTangoMonitor mon(this);

    PoolElement *pe = DevicePool::rename_element(old_alias, new_alias, deps);
    
    Tango::Util *tg = Tango::Util::instance();
    Tango::Database *db = tg->get_database();

    string dev_name;
    bool new_alias_exists = false;
    try
    {
        db->get_device_alias(new_alias, dev_name);
        new_alias_exists = true;
    }
    catch(Tango::DevFailed &df)
    { }

    if (new_alias_exists)
    {
        //restore the original name
        DevicePool::rename_element(new_alias, old_alias, deps);
        
        TangoSys_OMemStream o;
        
        o << "Could not rename element '" << old_alias << "' to '" << new_alias
          << "' because this name is already assigned to device '" << dev_name
          << "'" << ends;
        
        Tango::Except::throw_exception(
            (const char *)"Pool_ElementExists", o.str(),
            (const char *)"Pool::rename_element");
    }
    
    // Delete the old alias
    try
    {
        db->delete_device_alias(const_cast<std::string &>(old_alias));
    }
    catch(Tango::DevFailed &df)
    {}
 
    dev_name = pe->get_full_name();
    try
    {
        db->put_device_alias(dev_name, const_cast<std::string &>(new_alias));
    }
    catch(Tango::DevFailed &df1)
    {
        //restore the original name
        DevicePool::rename_element(new_alias, old_alias, deps);
                
        // Try to restore old alias if an error occured
        try
        { 
            db->put_device_alias(dev_name, const_cast<std::string &>(old_alias));
        }
        catch(Tango::DevFailed &df2) 
        {
            // Pool is in an inconsistent state
            Tango::Except::re_throw_exception(df2,
                "Pool_ErrorSetDeviceAlias",
                "An error occured trying to set the new alias. Recovery was not"
                "possible. Please set the alias manually before restarting "
                "the Pool",
                "Pool::rename_element");
        }
        Tango::Except::re_throw_exception(df1,
            "Pool_ErrorSetDeviceAlias",
            "An error occured trying to set the new alias. Maintained old name",
            "Pool::rename_element");
    }

    // Find which element types were affected so we can send events on the 
    // necessary attributes
    ElemTypeSet types;
    get_element_types(deps, types);
    
    // Special case for pseudo motors: Also include the motor list
    if (pe->get_type() == PSEUDO_MOTOR_ELEM)
        types.insert(MOTOR_ELEM);
    
    for(ElemTypeSetIt it = types.begin(); it != types.end(); ++it)
    {
        Tango::Attribute& attr_list = get_attr_by_elem_type(*it);
        
        // Send a tango event to the corresponding list but first update
        // the attribute value by invoking the read
        AttributeReadMethod read_attr = attr_read_method_map[&attr_list];
        (this->*read_attr)(attr_list);
        attr_list.fire_change_event();
    }
    return pe;
}

//------------------------------------------------------------------------------
// Pool::remove_element
//
bool Pool::remove_element(ElementId id)
{
    tango_elements.erase(id);
    return DevicePool::remove_element(id);
}

//------------------------------------------------------------------------------
// Pool::remove_all_elements
//
void Pool::remove_all_elements(ElementType type)
{
    DevicePool::remove_all_elements(type);
}

//------------------------------------------------------------------------------
// Pool::add_ctrl
//
void Pool::add_ctrl(const Tango::DevVarStringArray *argin,
                    bool internal /*= false*/)
{
//
// Check if we are called from a client or from init_device
//
    int32_t ctrl_id_db = internal ? atol((*argin)[4]) : 0;

    if (argin->length() <= 3)
    {
        Tango::Except::throw_exception(
            (const char *)"Pool_WrongArgumentNumber",
            (const char *)"Wrong number of argument for command "
                          "CreateController. Needs at least 4 strings",
            (const char *)"Pool::create_controller");
    }

//
// Create strings to manage name
//

    string f_name;
    string f_name_we((*argin)[1].in());
    string::size_type pos;

    if ((pos = f_name_we.find('/')) != string::npos)
    {
        TangoSys_OMemStream o;
        o << f_name_we << " is not simply a file name. Just give the file name";
        o << ", not the path";
        o << "\nPath will be taken from env. variables LD_LIBRARY_PATH or ";
        o << "device property PoolPath" << ends;

        Tango::Except::throw_exception(
                (const char *)"Pool_FileUnsupportedType",o.str(),
                (const char *)"Pool::create_controller");
    }


    if ((pos = f_name_we.find('.')) == string::npos)
    {
        TangoSys_OMemStream o;
        o << f_name_we << " does not have file type extension. Please define ";
        o << "one (.py or .la)" << ends;

        Tango::Except::throw_exception(
                (const char *)"Pool_FileUnsupportedType",o.str(),
                (const char *)"Pool::create_controller");
    }
    else
    {
        if ((pos = f_name_we.find(".la")) != string::npos)
            f_name = f_name_we.substr(0,pos);
        else if ((pos = f_name_we.find(".py")) != string::npos)
            f_name = f_name_we.substr(0,pos);
        else
        {
            TangoSys_OMemStream o;
            o << "File " << f_name_we << " is from one unsupported type"
              << ends;

            Tango::Except::throw_exception(
                    (const char *)"Pool_FileUnsupportedType",o.str(),
                    (const char *)"Pool::create_controller");
        }
    }

    string f_name_lower(f_name);
    transform(f_name_lower.begin(),f_name_lower.end(),f_name_lower.begin(),
              ::tolower);

    string ctrl_class_name((*argin)[2].in());
    string ctrl_class_name_lower = ctrl_class_name;
    transform(ctrl_class_name_lower.begin(),
              ctrl_class_name_lower.end(),
              ctrl_class_name_lower.begin(),
              ::tolower);

    string inst_name((*argin)[3].in());
    string inst_name_lower = inst_name;
    transform(inst_name_lower.begin(),
              inst_name_lower.end(),
              inst_name_lower.begin(),
              ::tolower);

    string ctrl_name = f_name_lower + '.' + ctrl_class_name_lower + '/' +
                       inst_name_lower;


//
// Check controller type
//

    PoolClass *cl_ptr = static_cast<PoolClass *>(this->get_device_class());

    string ob_type((*argin)[0].in());
    transform(ob_type.begin(),ob_type.end(),ob_type.begin(),::tolower);
    ob_type[0] = ::toupper(ob_type[0]);
    CtrlType type = str_2_CtrlType(ob_type);

    if (type == COTI_CTRL)
    {
        ob_type[7] = ::toupper(ob_type[7]);
    }
    else if (type == ZEROD_CTRL)
    {
        ob_type[4] = ::toupper(ob_type[4]);
        ob_type[5] = ::toupper(ob_type[5]);
        ob_type[8] = ::toupper(ob_type[8]);
    }
    else if (type == ONED_CTRL)
    {
        ob_type[3] = ::toupper(ob_type[3]);
        ob_type[4] = ::toupper(ob_type[4]);
        ob_type[7] = ::toupper(ob_type[7]);
    }
    else if (type == TWOD_CTRL)
    {
        ob_type[3] = ::toupper(ob_type[3]);
        ob_type[4] = ::toupper(ob_type[4]);
        ob_type[7] = ::toupper(ob_type[7]);
    }
    else if (type == PSEUDO_MOTOR_CTRL || type == PSEUDO_COUNTER_CTRL)
    {
        ob_type[6] = ::toupper(ob_type[6]);
    }
    else if (type == IOREGISTER_CTRL)
    {
        ob_type[1] = ::toupper(ob_type[1]);
        ob_type[2] = ::toupper(ob_type[2]);
    }

//
// Check that we do not have already the max number of controllers
//
    int32_t ctrl_nb = get_controller_nb();
    if (ctrl_nb == MAX_CTRL)
    {
        Tango::Except::throw_exception(
                (const char *)"Pool_TooManyController",
                (const char *)"Too many controller in your pool",
                (const char *)"Pool::create_controller");
    }

//
// Check that the instance name is not already used
//
    if(controller_exists(inst_name, true))
    {
        Tango::Except::throw_exception(
                (const char *)"Pool_ControllerAlreadyCreated",
                (const char *)"A controller with that name already exists",
                (const char *)"Pool::create_controller");
    }

//
// Check if the same controller is not already defined in the control system
//

    bool throw_ex = false;
    TangoSys_OMemStream ex_mess;

    if (internal == false)
    {
        try
        {
            Tango::Util *tg = Tango::Util::instance();
            Tango::Database *db = tg->get_database();

 //
 // Ask Db for the list of Pool device server defined
 //

            Tango::DeviceData din,dout;
            Tango::ConstDevString cl_name = "Pool/*";
            din << cl_name;
            dout = db->command_inout("DbGetServerList",din);

            vector<string> pool_serv_list;
            dout >> pool_serv_list;

            vector<string>::iterator str_ite;
            vector<string> pool_list;

//
// Ask db for the pool device of each pool DS
//

            string cla_name("Pool");
            for (str_ite = pool_serv_list.begin();str_ite != pool_serv_list.end();++str_ite)
            {
                Tango::DbDatum db_res = db->get_device_name(*str_ite,cla_name);
                vector<string> tmp_vect;
                db_res >> tmp_vect;
                vector<string>::iterator ite_dev_name;
                for (ite_dev_name = tmp_vect.begin();
                     ite_dev_name != tmp_vect.end();++ite_dev_name)
                    pool_list.push_back(*ite_dev_name);
            }

//
// All device names in lower case
//

            for (str_ite = pool_list.begin();str_ite != pool_list.end();++str_ite)
                transform((*str_ite).begin(),(*str_ite).end(),(*str_ite).begin(),::tolower);

//
// Remove ourself from list
//

            string & low_dev_name = this->get_name_lower();
            pool_list.erase(std::remove(pool_list.begin(),pool_list.end(),
                            low_dev_name),pool_list.end());


//
// Search for the new controller in pool devices controller list
//

            if (pool_list.size() != 0)
            {
                for (unsigned long loop = 0;loop < pool_list.size();loop++)
                {
                    Tango::DbData db_data;
                    db_data.push_back(Tango::DbDatum(CTRL_PROP));
                    db->get_device_property(pool_list[loop],db_data);
                    vector<string> ct_list;
                    if (db_data[0].is_empty() == false)
                    {
                        db_data[0] >> ct_list;
                        long nb_ctrl = ct_list.size() / PROP_BY_CTRL;

                        for (long l = 0;l < nb_ctrl;l++)
                        {
                            if (ct_list[(l * PROP_BY_CTRL) + 3] == inst_name)
                            {
                                throw_ex = true;
                                ex_mess << "Controller " << (*argin)[2].in()
                                        << "/";
                                ex_mess << (*argin)[3].in() << " already "
                                           "created in your control system.";
                                ex_mess << "\n. It belongs to pool device "
                                        << pool_list[loop] << "."  << ends;

                                break;
                            }
                        }

                        if (throw_ex == true)
                            break;
                    }
                }
            }
        }
        catch (Tango::DevFailed &e)
        {
            Tango::Except::re_throw_exception(e,
                    (const char *)"Pool_CantCreateController",
                    (const char *)"Can't create controller!!!",
                    (const char *)"Pool::create_controller");
        }
    }


    if (throw_ex == true)
    {
        Tango::Except::throw_exception(
                (const char *)"Pool_ControllerAlreadyCreated",ex_mess.str(),
                (const char *)"Pool::create_controller");
    }

//
// Starting from this point, we might change the device state
//

    PoolStateEvent pse(this);

//
// Check if the controller fica is not already defined
//

    string ctrl_type = f_name_lower + '/' + ctrl_class_name_lower;
    bool ctrl_fica_constructed = false;
    bool new_ctrl_fica = false;
    Tango::DevFailed save_exception;
    Controller *ct = NULL;

    vector<CtrlFiCa *>::iterator ctrlFiCa_ite;
    try
    {
        ctrlFiCa_ite = cl_ptr->get_ctrl_fica_by_name(ctrl_type,type);
        ctrl_fica_constructed = true;
    }
    catch (Tango::DevFailed &e)
    {
        new_ctrl_fica = true;
    }

//
// Check that the file is not already known for another
// type of controller
//

    if (new_ctrl_fica == false)
    {
        CtrlType ty = UNDEF_CTRL;
        try
        {
            vector<CtrlFile *>::iterator CtrlFile_it =
                cl_ptr->get_ctrl_file_by_name(f_name_we);
            ty = (*CtrlFile_it)->get_ctrl_type();
        }
        catch (Tango::DevFailed &e) {}

        if (ty != type)
        {
            TangoSys_OMemStream o;
            o << "file << " << f_name_we << " already used as ";
            o << CtrlTypeStr[ty] << " controller" << ends;

            Tango::Except::throw_exception("Pool_ControllerAlreadyCreated", 
                                           o.str(), "Pool::create_controller");
        }
    }

//
// Create a new controller fica if it is not defined
// Get its properties and check that they have a defined value
//
    vector<pair<string,string> > value_pairs;

    Language lang;
    vector<Controller::Properties> *prop = NULL;

    if (new_ctrl_fica == true)
    {
        try
        {
            ctrlFiCa_ite = cl_ptr->add_ctrl_fica(ctrl_type,f_name_we,
                                                 ctrl_class_name,
                                                 type,this);
            if(!internal)
            {
                int start = 4;
                if(type == PSEUDO_MOTOR_CTRL)
                {
                    PseudoMotCtrlFiCa* pm_fica =
                        static_cast<PseudoMotCtrlFiCa*>(*ctrlFiCa_ite);
                    int m_nb = pm_fica->get_motor_role_nb();
                    int pm_nb = pm_fica->get_pseudo_motor_role_nb();

                    start += m_nb + pm_nb;

                    int len = argin->length();
                    int min = 4 + m_nb + pm_nb;
                    if( (len < min) || ( ((len-min) % 2) != 0 ) )
                    {
                        TangoSys_OMemStream o;
                        o << "Insuficient arguments: Pseudo motor controller '";
                        o << ctrl_class_name << "' requires:\n";
                        o << "- controller instance name\n";
                        o << "- " << m_nb << " motor name(s) and\n";
                        o << "- " << pm_nb << " pseudo motor name(s)";

                        Tango::Except::throw_exception(
                                (const char *)"Pool_WrongArgumentNumber",o.str(),
                                (const char *)"Pool::create_controller");
                    }
                }
                else if(type == PSEUDO_COUNTER_CTRL)
                {
                    PseudoCoCtrlFiCa* co_fica =
                        static_cast<PseudoCoCtrlFiCa*>(*ctrlFiCa_ite);
                    int co_nb = co_fica->get_counter_role_nb();
                    int pc_nb = co_fica->get_pseudo_counter_role_nb();

                    start += co_nb + pc_nb;

                    int len = argin->length();
                    int min = 4 + co_nb + pc_nb;
                    if( (len < min) || ( ((len-min) % 2) != 0 ) )
                    {
                        TangoSys_OMemStream o;
                        o << "Insuficient arguments: Pseudo counter controller '";
                        o << ctrl_class_name << "' requires:\n";
                        o << "- controller instance name\n";
                        o << "- " << co_nb << " counter name(s) and\n";
                        o << "- " << pc_nb << " pseudo counter name(s)";

                        Tango::Except::throw_exception(
                                (const char *)"Pool_WrongArgumentNumber",o.str(),
                                (const char *)"Pool::create_controller");
                    }
                }
                else if(type == CONSTRAINT_CTRL)
                {
                    ConstraintFiCa* co_fica =
                        static_cast<ConstraintFiCa*>(*ctrlFiCa_ite);
                    int co_nb = co_fica->get_role_nb();
                    start += co_nb;

                    int len = argin->length();
                    int min = 4 + co_nb;
                    if( (len < min) || ( ((len-min) % 2) != 0 ) )
                    {
                        TangoSys_OMemStream o;
                        o << "Insuficient arguments: Constraint '";
                        o << ctrl_class_name << "' requires:\n";
                        o << "- instance name and\n";
                        o << "- " << co_nb << " role name(s)";

                        Tango::Except::throw_exception(
                                (const char *)"Pool_WrongArgumentNumber",o.str(),
                                (const char *)"Pool::create_controller");
                    }
                }

                build_property_params(argin, value_pairs, start);
            }
            build_property_data(inst_name,ctrl_class_name, value_pairs,
                                (*ctrlFiCa_ite)->get_ctrl_prop_list());
            check_property_data((*ctrlFiCa_ite)->get_ctrl_prop_list());

            ctrl_fica_constructed = true;
        }
        catch (Tango::DevFailed &e)
        {
            if (internal == true)
            {
                ct = NULL;
                save_exception = e;

                string err_reason = e.errors[0].reason.in();
                if (err_reason.find("Python") != string::npos)
                    lang = PYTHON;
                else
                    lang = CPP;
            }
            else
            {
                TangoSys_OMemStream o;
                o << "Impossible to create controller " << ctrl_class_name;
                o << " from file " << f_name_we << ends;

                Tango::Except::re_throw_exception(e,
                        (const char *)"Pool_ControllerNotFound",o.str(),
                        (const char *)"Pool::create_controller");
            }
        }
    }
    else
    {
//
// Even if the FiCa is already there, we need to check the property of this
// instance
//
        try
        {
            if(!internal)
            {
                int start = 4;
                if(type == PSEUDO_MOTOR_CTRL)
                {
                    PseudoMotCtrlFiCa* pm_fica =
                        static_cast<PseudoMotCtrlFiCa*>(*ctrlFiCa_ite);
                    int m_nb = pm_fica->get_motor_role_nb();
                    int pm_nb = pm_fica->get_pseudo_motor_role_nb();
                    start += m_nb + pm_nb;

                    int len = argin->length();
                    int min = 4 + m_nb + pm_nb;
                    if( (len < min) || ( ((len-min) % 2) != 0 ) )
                    {
                        TangoSys_OMemStream o;
                        o << "Insuficient arguments: Pseudo motor controller '";
                        o << ctrl_class_name << "' requires:\n";
                        o << "- controller instance name\n";
                        o << "- " << m_nb << " motor name(s) and\n";
                        o << "- " << pm_nb << " pseudo motor name(s)";

                        Tango::Except::throw_exception(
                                (const char *)"Pool_WrongArgumentNumber",o.str(),
                                (const char *)"Pool::create_controller");
                    }
                }
                else if(type == PSEUDO_COUNTER_CTRL)
                {
                    PseudoCoCtrlFiCa* co_fica =
                        static_cast<PseudoCoCtrlFiCa*>(*ctrlFiCa_ite);
                    int co_nb = co_fica->get_counter_role_nb();
                    int pc_nb = co_fica->get_pseudo_counter_role_nb();
                    start += co_nb + pc_nb;

                    int len = argin->length();
                    int min = 4 + co_nb + pc_nb;
                    if( (len < min) || ( ((len-min) % 2) != 0 ) )
                    {
                        TangoSys_OMemStream o;
                        o << "Insuficient arguments: Pseudo counter controller '";
                        o << ctrl_class_name << "' requires:\n";
                        o << "- controller instance name\n";
                        o << "- " << co_nb << " counter name(s) and\n";
                        o << "- " << pc_nb << " pseudo counter name(s)";

                        Tango::Except::throw_exception(
                                (const char *)"Pool_WrongArgumentNumber",o.str(),
                                (const char *)"Pool::create_controller");
                    }
                }
                else if(type == CONSTRAINT_CTRL)
                {
                    ConstraintFiCa* co_fica =
                        static_cast<ConstraintFiCa*>(*ctrlFiCa_ite);
                    int co_nb = co_fica->get_role_nb();
                    start += co_nb;

                    int len = argin->length();
                    int min = 4 + co_nb;
                    if( (len < min) || ( ((len-min) % 2) != 0 ) )
                    {
                        TangoSys_OMemStream o;
                        o << "Insuficient arguments: Constraint '";
                        o << ctrl_class_name << "' requires:\n";
                        o << "- instance name and\n";
                        o << "- " << co_nb << " role name(s)";

                        Tango::Except::throw_exception(
                                (const char *)"Pool_WrongArgumentNumber",o.str(),
                                (const char *)"Pool::create_controller");
                    }
                }

                build_property_params(argin, value_pairs, start);
            }

            build_property_data(inst_name,ctrl_class_name,value_pairs,
                                (*ctrlFiCa_ite)->get_ctrl_prop_list());
            check_property_data((*ctrlFiCa_ite)->get_ctrl_prop_list());
        }
        catch (Tango::DevFailed &e)
        {
            if (internal == true)
            {
                ct = NULL;
                ctrl_fica_constructed = false;
                save_exception = e;

                string err_reason = e.errors[0].reason.in();
                if (err_reason.find("Python") != string::npos)
                    lang = PYTHON;
                else
                    lang = CPP;
            }
            else
            {
                TangoSys_OMemStream o;
                o << "Impossible to create controller " << ctrl_class_name;
                o << " from file " << f_name_we << ends;

                Tango::Except::re_throw_exception(e,
                        (const char *)"Pool_ControllerNotFound",o.str(),
                        (const char *)"Pool::create_controller");
            }
        }
    }


    if (ctrl_fica_constructed == true)
    {
        lang = (*ctrlFiCa_ite)->get_language();
        if (lang == CPP)
        {
//
// Retrieve the controller object creator C function
//
            lt_ptr sym;

            string sym_name("_create_");
            sym_name = sym_name + ctrl_class_name;

            DEBUG_STREAM << "Symbol name = " << sym_name << endl;

            sym = lt_dlsym((*ctrlFiCa_ite)->get_lib_ptr(),sym_name.c_str());
            if (sym == NULL)
            {
                TangoSys_OMemStream o;
                o << "Controller library " << (*argin)[1].in();
                o << " does not have the C creator function ";
                o << "(_create_<Controller name>)" << ends;

                Tango::Except::throw_exception(
                        (const char *)"Pool_CCreatorFunctionNotFound",o.str(),
                        (const char *)"Pool::create_controller");
            }

            DEBUG_STREAM << "lt_dlsym is a success" << endl;

//
// Create the controller
//

            Ctrl_creator_ptr ct_ptr = (Ctrl_creator_ptr)sym;
            try
            {

                AutoPoolLock lo((*ctrlFiCa_ite)->get_mon());
                ct = NULL;
                prop = properties_2_cpp_vect((*ctrlFiCa_ite)->get_ctrl_prop_list());
                ct = (*ct_ptr)(inst_name_lower.c_str(),*prop);
            }
            catch (Tango::DevFailed &e)
            {
                if (prop != NULL)
                    delete prop;

                if (internal == true)
                {
                    if (ct != NULL)
                    {
                        AutoPoolLock lo((*ctrlFiCa_ite)->get_mon());
                        delete ct;
                    }
                    ct = NULL;
                    save_exception = e;
                }
                else
                {
                    Tango::Except::re_throw_exception(e,
                    (const char *)"Pool_CantCreateController",
                    (const char *)"Can't create controller class instance!!!",
                    (const char *)"Pool::create_controller");
                }
            }
        }
        else
        {

//
// Retrieve the controller object creator C function
//

            lt_ptr sym;

            string sym_name("_create_Py");
            sym_name = sym_name + ob_type;

            if(type != CONSTRAINT_CTRL)
                sym_name += "Controller";

            DEBUG_STREAM << "Symbol name = " << sym_name << endl;

            lt_dlhandle tmp_lib_ptr = (*ctrlFiCa_ite)->get_py_inter_lib_ptr();
            sym = lt_dlsym(tmp_lib_ptr,sym_name.c_str());
            if (sym == NULL)
            {
                TangoSys_OMemStream o;
                o << "Controller library " << (*argin)[1].in();
                o << " does not have the C creator function ";
                o << "(_create_<Controller name>)" << ends;

                Tango::Except::throw_exception(
                        (const char *)"Pool_CCreatorFunctionNotFound",o.str(),
                        (const char *)"Pool::create_controller");
            }

            DEBUG_STREAM << "lt_dlsym is a success" << endl;

//
// Create the Python controller object
//

            PyCtrl_creator_ptr ct_ptr = (PyCtrl_creator_ptr)sym;
            try
            {
                AutoPoolLock lo((*ctrlFiCa_ite)->get_mon());
                PyObject *prop_dict =
                    properties_2_py_dict((*ctrlFiCa_ite)->get_ctrl_prop_list());
                ct = (*ct_ptr)(inst_name_lower.c_str(),
                               ctrl_class_name.c_str(),
                               (*ctrlFiCa_ite)->get_py_module(),prop_dict);
            }
            catch (Tango::DevFailed &e)
            {
                if (internal == true)
                {
                    ct = NULL;
                    save_exception = e;
                }
                else
                {
                    Tango::Except::re_throw_exception(e,
                    (const char *)"Pool_CantCreateController",
                    (const char *)"Can't create controller class instance!!!",
                    (const char *)"Pool::create_controller");
                }
            }
        }
    }
    else
    {

//
// The FiCa is not constructed. Deduce controller language
// from file name extension
//

        if ((pos = f_name_we.find(".la")) != string::npos)
            lang = CPP;
        else
            lang = PYTHON;
    }

//
// Retrieve MaxDevice property
//
    int32_t MaxDevice = ctrl_fica_constructed == true ? (*ctrlFiCa_ite)->get_MaxDevice(): -1;

//
// Save controller info
//
    ControllerPool *cp_ptr = new ControllerPool;
    ControllerPool &cp = *cp_ptr;
    cp.set_proxy(NULL);
    cp.set_controller(ct);
    cp.name = inst_name;
    cp.full_name = f_name_lower + '.' + ctrl_class_name_lower + '/' +
              inst_name_lower;
    cp.user_full_name = inst_name + " (" + f_name + '.' + ctrl_class_name +
                        '/' + inst_name + ')';
    cp.ite_ctrl_class = ctrlFiCa_ite;
    cp.ctrl_class_built = ctrl_fica_constructed;
    cp.ctrl_class_name = ctrl_class_name;
    cp.full_ctrl_class_name = ctrl_type;
    cp.MaxDevice = MaxDevice;

    if (lang == PYTHON)
    {
        cp.user_full_name += " - ";
        cp.user_full_name += ob_type;
        cp.user_full_name += " Python ctrl (";
        cp.user_full_name += f_name_we;

        if (f_name_we.find('.') == string::npos)
            cp.user_full_name = cp.user_full_name + ".py";
        cp.user_full_name = cp.user_full_name + ")";
    }
    else
    {
        cp.cpp_ctrl_prop = prop;
        cp.user_full_name = cp.user_full_name + " - ";
        cp.user_full_name += ob_type;
        cp.user_full_name += " Cpp ctrl (";
        cp.user_full_name += f_name_we;

        if (f_name_we.find('.') == string::npos)
            cp.user_full_name = cp.user_full_name + ".la";
        cp.user_full_name = cp.user_full_name + ")";
    }

//
// Manage controller id (from db or a new one)
//

    if (internal == true)
    {
        cp.id = ctrl_id_db;
        reserve_id(ctrl_id_db);
    }
    else
    {
        cp.id = get_new_id();
    }
//
// Add this controller to the controller list
//
    add_element(cp_ptr);

//
// Update info in DB
//

    ctrl_info.push_back(ob_type.c_str());
    ctrl_info.push_back(f_name_we.c_str());
    ctrl_info.push_back(ctrl_class_name.c_str());
    ctrl_info.push_back(inst_name.c_str());

    if (internal == false)
    {
        stringstream s;
        s << get_last_assigned_id();
        ctrl_info.push_back(s.str().c_str());
    }
    else
        ctrl_info.push_back((*argin)[4].in());

    if (upd_db == true)
    {
        Tango::DbDatum ctrl(CTRL_PROP);
        Tango::DbData db_data;

        ctrl << ctrl_info;
        db_data.push_back(ctrl);

        try
        {
            get_db_device()->put_property(db_data);
        }
        catch (Tango::DevFailed &e)
        {
            for (long loop = 0;loop < PROP_BY_CTRL;loop++)
                ctrl_info.pop_back();

            remove_controller(cp.id);

            TangoSys_OMemStream o;
            o << "Can't update Db for controller " << (*argin)[2].in();
            o << "/" << (*argin)[3].in() << ends;

            Tango::Except::re_throw_exception(e,
                    (const char *)"Pool_CantUpdateDb",o.str(),
                    (const char *)"Pool::create_controller");
        }
    }

//
// If needed create controller elements
//
    if(internal == false)
    {
        if(type == PSEUDO_MOTOR_CTRL)
        {
            vector<string> pseudo_mot_names, mot_names;

            PseudoMotCtrlFiCa* pm_fica =
                static_cast<PseudoMotCtrlFiCa*>(*ctrlFiCa_ite);
            int m_nb = pm_fica->get_motor_role_nb();
            int pm_nb = pm_fica->get_pseudo_motor_role_nb();

            for(int i = 4; i < m_nb + 4; i++)
                mot_names.push_back((*argin)[i].in());

            for(int i = 4 + m_nb; i < m_nb + pm_nb + 4; i++)
                pseudo_mot_names.push_back((*argin)[i].in());

            try
            {
                create_pseudo_motor_ctrl_elems(inst_name, pm_fica,
                                               pseudo_mot_names, mot_names);
            }
            catch (Tango::DevFailed &e)
            {
                // restore 'Controller' property internally and in the DB
                for (long loop = 0;loop < PROP_BY_CTRL;loop++)
                    ctrl_info.pop_back();

                Tango::DbDatum ctrl(CTRL_PROP);
                Tango::DbData db_data;

                ctrl << ctrl_info;
                db_data.push_back(ctrl);

                get_db_device()->put_property(db_data);

                // Restore controller info
                remove_controller(cp.id);

                TangoSys_OMemStream o;
                o << "Can't update Db for controller " << (*argin)[2].in();
                o << "/" << (*argin)[3].in() << ends;

                Tango::Except::re_throw_exception(e,
                    (const char *)"Pool_CantCreateControllerElements",o.str(),
                    (const char *)"Pool::create_controller");
            }
        }
        else if(type == PSEUDO_COUNTER_CTRL)
        {
            vector<string> counter_names, pseudo_counter_names;

            PseudoCoCtrlFiCa* co_fica =
                static_cast<PseudoCoCtrlFiCa*>(*ctrlFiCa_ite);
            int co_nb = co_fica->get_counter_role_nb();
            int pc_nb = co_fica->get_pseudo_counter_role_nb();

            for(int i = 4; i < co_nb + 4; i++)
                counter_names.push_back((*argin)[i].in());

            for(int i = 4 + co_nb; i < co_nb + pc_nb + 4; i++)
                pseudo_counter_names.push_back((*argin)[i].in());

            try
            {
                create_pseudo_counter_ctrl_elems(inst_name, co_fica,
                        pseudo_counter_names, counter_names);
            }
            catch (Tango::DevFailed &e)
            {
                // restore 'Controller' property internally and in the DB
                for (long loop = 0;loop < PROP_BY_CTRL;loop++)
                    ctrl_info.pop_back();

                Tango::DbDatum ctrl(CTRL_PROP);
                Tango::DbData db_data;

                ctrl << ctrl_info;
                db_data.push_back(ctrl);

                get_db_device()->put_property(db_data);

                remove_controller(cp.id);

                TangoSys_OMemStream o;
                o << "Can't update Db for controller " << (*argin)[2].in();
                o << "/" << (*argin)[3].in() << ends;

                Tango::Except::re_throw_exception(e,
                    (const char *)"Pool_CantCreateControllerElements",o.str(),
                    (const char *)"Pool::create_controller");
            }
        }
    }

//
// Throw exception if the controller creation failed during the device
// init phase
//

    if ((internal == true) && (ct == NULL))
    {
        Tango::Except::re_throw_exception(save_exception,
                (const char *)"Pool_CantCreateController",
                (const char *)"Can't create controller class instance!!!",
                (const char *)"Pool::create_controller");
    }

//
// Inform client listennig on event but only if the controller are not
// created due to init command. In this case, the event is sent at the end
// of the init_device code
//

    if (internal != true)
    {
        Tango::Attribute &cl = dev_attr->get_attr_by_name("ControllerList");
        read_ControllerList(cl);
        cl.fire_change_event();

        if(type == PSEUDO_MOTOR_CTRL)
        {
            Tango::Attribute &pml = dev_attr->get_attr_by_name("PseudoMotorList");
            read_PseudoMotorList(pml);
            pml.fire_change_event();
        }
        else if(type == PSEUDO_COUNTER_CTRL)
        {
            Tango::Attribute &pcl = dev_attr->get_attr_by_name("PseudoCounterList");
            read_PseudoCounterList(pcl);
            pcl.fire_change_event();
        }
    }
}

}
