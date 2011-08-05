//+=============================================================================
//
// file :         MotorGroup.cpp
//
// description :  C++ source for the MotorGroup and its commands.
//                The class is derived from Device. It represents the
//                CORBA servant object which will be accessed from the
//                network. All commands which can be executed on the
//                MotorGroup are implemented in this file.
//
// project :      TANGO Device Server
//
// $Author$
//
// $Revision$
//
// $Log$
// Revision 1.58  2007/08/30 12:40:39  tcoutinho
// - changes to support Pseudo counters.
//
// Revision 1.57  2007/08/24 15:55:26  tcoutinho
// safety weekend commit
//
// Revision 1.56  2007/08/20 06:37:32  tcoutinho
// development commit
//
// Revision 1.55  2007/08/17 13:07:29  tcoutinho
// - pseudo motor restructure
// - pool base dev class restructure
// - initial commit for pseudo counters
//
// Revision 1.54  2007/08/07 09:51:06  tcoutinho
// Fix bug 24: Motor.state() and ghostGroup.state() return different states
//
// Revision 1.53  2007/07/26 10:25:15  tcoutinho
// - Fix bug 1 :  Automatic temporary MotorGroup/MeasurementGroup deletion
//
// Revision 1.52  2007/05/31 09:53:54  etaurel
// - Fix some memory leaks
//
// Revision 1.51  2007/05/30 14:56:35  etaurel
// - Change the way the group state_array is populated when element are
// added/removed from the group
// - Do not get state from hardware while the pool is executing an Init
// command on the pool device
//
// Revision 1.50  2007/05/25 07:20:02  tcoutinho
// - fix internal event propagation to ghost motor group when client asks for state and the new calculated state is different from the one previously stored
//
// Revision 1.49  2007/05/24 09:24:07  tcoutinho
// - fixes to the position attribute quality
//
// Revision 1.48  2007/05/23 12:58:00  tcoutinho
// - fix bug in abort command: abort does not send state event anymore. Because deceleration can be very slow this is now done by the PoolThread.
// - fix position quality due to internal events
//
// Revision 1.47  2007/05/22 12:57:13  etaurel
// - Fix some bugs in event propagation
//
// Revision 1.46  2007/05/17 13:02:46  etaurel
// - Fix bug in reading_position and in state computation
//
// Revision 1.45  2007/05/17 09:31:36  tcoutinho
// - fix potential bug.
//
// Revision 1.44  2007/05/17 07:01:34  etaurel
// - Some tabs....
//
// Revision 1.43  2007/05/16 16:26:22  tcoutinho
// - fix dead lock
//
// Revision 1.42  2007/05/16 09:41:56  tcoutinho
// small code changes. No change in behaviour
//
// Revision 1.41  2007/05/15 15:02:40  tcoutinho
// - fix bugs
//
// Revision 1.40  2007/05/15 07:21:14  etaurel
// - Add a lock to protect the call to "update_state_from_ctrl" method
//
// Revision 1.39  2007/05/11 08:08:31  tcoutinho
// - fixed bugs
//
// Revision 1.38  2007/04/30 14:51:20  tcoutinho
// - make possible to Add/Remove elements on motorgroup that are part of other motor group(s)
//
// Revision 1.37  2007/04/26 08:23:04  tcoutinho
// - implemented add/remove elements feature
//
// Revision 1.36  2007/04/23 15:18:59  tcoutinho
// - first changes according to Sardana metting 26-03-2007: identical motor groups can be created, Add/Remove element from a MG, etc
//
// Revision 1.35  2007/02/22 11:57:41  tcoutinho
// - fix missing clear of containers
//
// Revision 1.34  2007/02/19 09:36:26  tcoutinho
// - Fix status bug
//
// Revision 1.33  2007/02/16 10:03:16  tcoutinho
// - development checkin related with measurement group
//
// Revision 1.32  2007/02/13 14:39:42  tcoutinho
// - fix bug in motor group when a motor or controller are recreated due to an InitController command
//
// Revision 1.31  2007/02/08 09:40:17  etaurel
// - MAny changes after compilation -Wall
//
// Revision 1.30  2007/02/06 19:11:23  tcoutinho
// safe guard commit
//
// Revision 1.29  2007/02/06 09:37:45  tcoutinho
// - Motor Group now uses PoolGroupBaseDev
//
// Revision 1.28  2007/01/26 08:36:17  etaurel
// - We now have a first release of ZeroDController
//
// Revision 1.27  2007/01/23 08:30:12  tcoutinho
// -fixed error when user does not specify the pseudo_motor_roles attribute (case of only one pseudo motor)
//
// Revision 1.26  2007/01/16 14:27:36  etaurel
// - Change some names in the Pool structures
//
// Revision 1.25  2007/01/12 12:39:39  tcoutinho
// fix wrong commented line
//
// Revision 1.24  2007/01/12 12:03:02  tcoutinho
// fixed event changes
//
// Revision 1.23  2007/01/05 14:58:23  etaurel
// - Remove some print
//
// Revision 1.22  2007/01/05 13:03:56  tcoutinho
// -changes to internal event mechanism
// -support for gcc 4.1.1 compilation without errors
//
// Revision 1.21  2007/01/04 11:54:31  etaurel
// - Added the CounterTimer controller
//
// Revision 1.20  2006/12/28 15:35:13  etaurel
// - Clear group implied controllers vector during a "Init" command
//
// Revision 1.19  2006/12/20 10:40:21  tcoutinho
// - change: when an internal state change is received, the MG asks the Ctrl(s) for their state. This improves state changes event times in case some motors are in wrong state
//
// Revision 1.18  2006/12/20 10:26:08  tcoutinho
// - changes to support internal event propagation
// - bug fix in motor groups containing other motor groups or pseudo motors
//
// Revision 1.17  2006/12/18 11:39:45  etaurel
// - Add a print message
//
// Revision 1.16  2006/12/12 11:09:20  tcoutinho
// - support for pseudo motors and motor groups in a motor group
//
// Revision 1.15  2006/12/11 16:37:29  tcoutinho
// - safety commit (before supporting pseudo motors in motor groups)
//
// Revision 1.14  2006/12/05 10:13:45  etaurel
// - Add a check on ctrl validity in the always_executed_hook() and a dev_status() method
//
// Revision 1.13  2006/11/24 08:46:45  tcoutinho
// - support for pseudo motors in motor group
//
// Revision 1.12  2006/11/20 14:35:16  etaurel
// - Add ghost group and event on group position
//
// Revision 1.11  2006/11/07 15:07:57  etaurel
// - Now, the pool really supports different kind of controllers (cpp and py)
//
// Revision 1.10  2006/11/03 15:48:27  etaurel
// - Miscellaneous changes that I don't remember
//
// Revision 1.9  2006/10/25 10:05:20  etaurel
// - Complete implementation of the ReloadControllerCode command
// - Handle end of movment when reading position in polling mode
//
// Revision 1.8  2006/10/20 15:42:38  etaurel
// - First release with GetControllerInfo command supported and with
// controller properties
//
// Revision 1.7  2006/09/21 10:21:10  etaurel
// - The motor group do not ID any more
//
// Revision 1.6  2006/09/21 08:02:15  etaurel
// - Now all test suite is OK withou ID on motor interface
//
// Revision 1.5  2006/09/21 07:26:38  etaurel
// - Changes due to the removal of Motor ID in the Tango interface
//
// Revision 1.4  2006/08/08 12:16:54  etaurel
// - It now uses the multi-motor controller interface
//
// Revision 1.3  2006/07/07 13:39:50  etaurel
// - Fix a small bug in the init_device() method
//
// Revision 1.2  2006/07/07 12:40:18  etaurel
// - Commit after implementing the group multi motor read
//
// Revision 1.1  2006/03/29 07:09:58  etaurel
// - Added motor group features
//
//
// copyleft :     CELLS/ALBA
//				  Edifici Ciències Nord. Mòdul C-3 central.
//  			  Campus Universitari de Bellaterra. Universitat Autònoma de Barcelona
//  			  08193 Bellaterra, Barcelona
//  			  Spain
//
//-=============================================================================
//
//  		This file is generated by POGO
//	(Program Obviously used to Generate tango Object)
//
//         (c) - Software Engineering Group - ESRF
//=============================================================================



//===================================================================
//
//	The following table gives the correspondance
//	between commands and method's name.
//
//  Command's name|  Method's name
//	----------------------------------------
//  State         |  dev_state()
//  Status        |  dev_status()
//  Abort         |  abort()
//  AddElement    |  add_element()
//  RemoveElement |  remove_element()
//
//===================================================================

#include "CtrlFiCa.h"
#include <tango.h>
#include "MotorGroup.h"
#include "MotorGroupClass.h"
#include "MotorGroupUtil.h"
#include "Pool.h"
#include "PoolUtil.h"
#include "PyUtils.h"
#include "MotorThread.h"
#include "Motor.h"
#include "PseudoMotor.h"

#include "pool/Ctrl.h"
#include "pool/MotCtrl.h"
#include "pool/PseudoMotCtrl.h"

#include "CPoolMotorGroup.h"

namespace MotorGroup_ns
{

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::MotorGroup(string &s)
//
// description : 	constructor for simulated MotorGroup
//
// in : - cl : Pointer to the DeviceClass object
//      - s : Device name
//
//-----------------------------------------------------------------------------
MotorGroup::MotorGroup(Tango::DeviceClass *cl,string &s)
//:Tango::Device_4Impl(cl,s.c_str())
:Pool_ns::PoolGroupBaseDev(cl,s.c_str())
{
    init_device();
}

MotorGroup::MotorGroup(Tango::DeviceClass *cl,const char *s)
//:Tango::Device_4Impl(cl,s)
:Pool_ns::PoolGroupBaseDev(cl,s)
{
    init_device();
}

MotorGroup::MotorGroup(Tango::DeviceClass *cl,const char *s,const char *d)
//:Tango::Device_4Impl(cl,s,d)
:Pool_ns::PoolGroupBaseDev(cl,s,d)
{
    init_device();
}
//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::delete_device()
//
// description : 	will be called at device destruction or at init command.
//
//-----------------------------------------------------------------------------
void MotorGroup::delete_device()
{
    //	Delete device's allocated object

    DEBUG_STREAM << "Entering delete_device for dev " << get_name() << endl;

//
// A trick to inform client(s) listening on events that the pool device is down.
// Without this trick, the clients will have to wait for 3 seconds before being informed
// This is the Tango device time-out.
// To know that we are executing this code due to a pool shutdown and not due to a
// "Init" command, we are using the polling thread ptr which is cleared in the DS
// shutdown sequence before the device destruction
//

    Tango::Util *tg = Tango::Util::instance();
    if (tg->get_polling_thread_object() == NULL)
    {
        struct timespec req_sleep;
        req_sleep.tv_sec = 0;
        req_sleep.tv_nsec = 500000000;

        pool_dev->set_moving_state();

        while(get_state() == Tango::MOVING)
        {
            nanosleep(&req_sleep,NULL);
        }
    }
    else
    {
        if (get_state() == Tango::MOVING)
        {
            TangoSys_OMemStream o;
            o << "Init command on group device is not allowed while a group is moving" << ends;

            Tango::Except::throw_exception((const char *)"Group_InitNotAllowed",o.str(),
                    (const char *)"Group::delete_device");
        }
    }

    SAFE_DELETE_ARRAY(attr_Position_read);
    SAFE_DELETE_ARRAY(phys_mot_pos);

    SAFE_DELETE_ARRAY(attr_Elements_read);
    SAFE_DELETE_ARRAY(attr_Motors_read);
    SAFE_DELETE_ARRAY(attr_MotorGroups_read);
    SAFE_DELETE_ARRAY(attr_PseudoMotors_read);

    delete_from_pool();
    delete_utils();

    PoolGroupBaseDev::delete_device();
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::init_device()
//
// description : 	will be called at device initialization.
//
//-----------------------------------------------------------------------------
void MotorGroup::init_device()
{
    DEBUG_STREAM << "MotorGroup::MotorGroup() create device " << device_name << endl;

    // Initialise variables to default values
    //--------------------------------------------
    PoolGroupBaseDev::init_device();

//
// If we are called due to a init command, re-init variables in the
// base class
//

    if (!init_cmd)
    {
        // if first time make sure that the pointers are properly clean
        attr_Position_read = NULL;
        phys_mot_pos = NULL;
        attr_Elements_read = NULL;
        attr_Motors_read = NULL;
        attr_MotorGroups_read = NULL;
        attr_PseudoMotors_read = NULL;
    }

    if(!is_ghost())
    {
        ind_elt_nb = phys_group_elt.size();
        usr_elt_nb = user_group_elt.size();
    }
    else
    {
        alias = "The_ghost";

//
// Init motor list for the ghost group
//
        Pool_ns::ElemIdVector tmp_phys_group_elt;
        pool_dev->get_physical_motors(tmp_phys_group_elt);
        Pool_ns::PoolTango::toTango(tmp_phys_group_elt, phys_group_elt);

        ind_elt_nb = usr_elt_nb = pool_dev->get_physical_motor_nb();

        assert((int32_t)phys_group_elt.size() == ind_elt_nb);

        state_array.clear();
        state_array.insert(state_array.begin(), usr_elt_nb, Tango::UNKNOWN);
    }

//
// We will push change event on State attribute
//

    Tango::Attribute &state_att = dev_attr->get_attr_by_name("state");
    state_att.set_change_event(true,false);

    Tango::Attribute &pos_att = dev_attr->get_attr_by_name("Position");
    pos_att.set_change_event(true);

    Tango::Attribute &elements_att = dev_attr->get_attr_by_name("Elements");
    elements_att.set_change_event(true,false);

    Tango::Attribute &motors_att = dev_attr->get_attr_by_name("Motors");
    motors_att.set_change_event(true,false);

    Tango::Attribute &motorgroups_att = dev_attr->get_attr_by_name("MotorGroups");
    motorgroups_att.set_change_event(true,false);

    Tango::Attribute &pseudomotors_att = dev_attr->get_attr_by_name("PseudoMotors");
    pseudomotors_att.set_change_event(true,false);

//
// Build the PoolBaseUtils class depending on the
// controller type
//

    set_utils(new MotorGroupUtil(pool_dev));

    Pool_ns::MotorGroupPool *motor_group_ptr = new Pool_ns::MotorGroupPool;
    init_pool_element(motor_group_ptr);

//
// Build group physical structure
//

    build_grp();
    motor_group_ptr->mot_ids.clear();
    for (int32_t i = 0;i < ind_elt_nb; i++)
        motor_group_ptr->mot_ids.push_back(ind_elts[i]->id);

//
// Convert sleep before last read property into the right unit
//

    if (sleep_bef_last_read != 0)
    {
        if (sleep_bef_last_read < 1000)
        {
            sbr_sec = 0;
            sbr_nsec = sleep_bef_last_read * 1000000;
        }
        else
        {
            sbr_sec = (time_t)(sleep_bef_last_read / 1000);
            sbr_nsec = (sleep_bef_last_read - (sbr_sec * 1000)) * 1000000;
        }
    }
    else
    {
        sbr_sec = 0;
        sbr_nsec = 0;
    }

//
// Insert motor group into pool except for ghost group
//

    if (!is_ghost())
    {
        Tango::AutoTangoMonitor atm(pool_dev);
        pool_dev->add_element(motor_group_ptr);
    }

    if(!init_cmd)
    {
        read_Elements(elements_att);
        elements_att.fire_change_event();

        read_Motors(motors_att);
        motors_att.fire_change_event();

        read_MotorGroups(motorgroups_att);
        motorgroups_att.fire_change_event();

        read_PseudoMotors(pseudomotors_att);
        pseudomotors_att.fire_change_event();
    }
}


void MotorGroup::init_pool_element(Pool_ns::PoolElement *pe)
{
    PoolGroupBaseDev::init_pool_element(pe);

    if(is_ghost())
        return;

    Pool_ns::MotorGroupPool *mgp = static_cast<Pool_ns::MotorGroupPool*>(pe);

    Pool_ns::PoolTango::toPool(user_group_elt, mgp->group_elts);
    Pool_ns::PoolTango::toPool(phys_group_elt, mgp->mot_ids);
    Pool_ns::PoolTango::toPool(motor_list, mgp->mot_elts);
    Pool_ns::PoolTango::toPool(pseudo_motor_list, mgp->pm_elts);
    Pool_ns::PoolTango::toPool(motor_group_list, mgp->mg_elts);

    mgp->update_info();
}

Pool_ns::MotorGroupPool &MotorGroup::get_motor_group_obj()
{
    return pool_dev->get_motor_group(get_id());
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::get_device_property()
//
// description : 	Read the device properties from database.
//
//-----------------------------------------------------------------------------
void MotorGroup::get_device_property()
{
    //	Initialize your default values here (if not done with  POGO).
    //------------------------------------------------------------------
    PoolGroupBaseDev::get_device_property();

    //	Read device properties from database.(Automatic code generation)
    //------------------------------------------------------------------
    Tango::DbData	dev_prop;
    dev_prop.push_back(Tango::DbDatum("Pool_device"));
    dev_prop.push_back(Tango::DbDatum("Motor_list"));
    dev_prop.push_back(Tango::DbDatum("Motor_group_list"));
    dev_prop.push_back(Tango::DbDatum("Pseudo_motor_list"));
    dev_prop.push_back(Tango::DbDatum("Sleep_bef_last_read"));
    dev_prop.push_back(Tango::DbDatum("User_group_elt"));
    dev_prop.push_back(Tango::DbDatum("Phys_group_elt"));
    dev_prop.push_back(Tango::DbDatum("Pos_spectrum_dim_x"));

    //	Call database and extract values
    //--------------------------------------------
    if (Tango::Util::instance()->_UseDb==true)
        get_db_device()->get_property(dev_prop);
    Tango::DbDatum	def_prop, cl_prop;
    MotorGroupClass	*ds_class =
        (static_cast<MotorGroupClass *>(get_device_class()));
    int	i = -1;

    //	Try to initialize Pool_device from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  pool_device;
    //	Try to initialize Pool_device from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  pool_device;
    //	And try to extract Pool_device value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  pool_device;

    //	Try to initialize Motor_list from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  motor_list;
    //	Try to initialize Motor_list from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  motor_list;
    //	And try to extract Motor_list value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  motor_list;

    //	Try to initialize Motor_group_list from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  motor_group_list;
    //	Try to initialize Motor_group_list from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  motor_group_list;
    //	And try to extract Motor_group_list value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  motor_group_list;

    //	Try to initialize Pseudo_motor_list from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  pseudo_motor_list;
    //	Try to initialize Pseudo_motor_list from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  pseudo_motor_list;
    //	And try to extract Pseudo_motor_list value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  pseudo_motor_list;

    //	Try to initialize Sleep_bef_last_read from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  sleep_bef_last_read;
    //	Try to initialize Sleep_bef_last_read from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  sleep_bef_last_read;
    //	And try to extract Sleep_bef_last_read value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  sleep_bef_last_read;

    //	Try to initialize User_group_elt from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  user_group_elt;
    //	Try to initialize User_group_elt from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  user_group_elt;
    //	And try to extract User_group_elt value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  user_group_elt;

    //	Try to initialize Phys_group_elt from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  phys_group_elt;
    //	Try to initialize Phys_group_elt from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  phys_group_elt;
    //	And try to extract Phys_group_elt value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  phys_group_elt;

    //	Try to initialize Pos_spectrum_dim_x from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  pos_spectrum_dim_x;
    //	Try to initialize Pos_spectrum_dim_x from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  pos_spectrum_dim_x;
    //	And try to extract Pos_spectrum_dim_x value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  pos_spectrum_dim_x;



    //	End of Automatic code generation
    //------------------------------------------------------------------

}
//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::always_executed_hook()
//
// description : 	method always executed before any command is executed
//
//-----------------------------------------------------------------------------
void MotorGroup::always_executed_hook()
{
    Pool_ns::PoolGroupBaseDev::always_executed_hook();

    //
// Check that the controllers implied in this group are correctly built
//

    vector<Pool_ns::CtrlGrp*>::iterator impl_ctrl_ite;
    Controller *ctrl = NULL;
    for (impl_ctrl_ite = implied_ctrls.begin();impl_ctrl_ite != implied_ctrls.end();++impl_ctrl_ite)
    {
        Pool_ns::ControllerPool *cp = (*impl_ctrl_ite)->ct;
        ctrl = cp->get_controller();
        if ((cp->ctrl_class_built == false) || (ctrl == NULL))
        {
            set_state(Tango::FAULT);
            break;
        }
    }
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::read_attr_hardware
//
// description : 	Hardware acquisition for attributes.
//
//-----------------------------------------------------------------------------
void MotorGroup::read_attr_hardware(vector<long> &attr_list)
{
    DEBUG_STREAM << "MotorGroup::read_attr_hardware(vector<long> &attr_list) entering... "<< endl;
    //	Add your own code here
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::read_Elements
//
// description : 	Extract real attribute values for Elements acquisition result.
//
//-----------------------------------------------------------------------------
void MotorGroup::read_Elements(Tango::Attribute &attr)
{
    uint32_t l = 0;
    for (std::vector<Tango::DevLong>::iterator ite = user_group_elt.begin();
         ite != user_group_elt.end(); ++ite, ++l)
    {
        Pool_ns::PoolElement *elem = pool_dev->get_element((Pool_ns::ElementId)*ite);
        attr_Elements_read[l] = const_cast<char *>(elem->get_name().c_str());
    }

    attr.set_value(attr_Elements_read, user_group_elt.size());
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::read_Motors
//
// description : 	Extract real attribute values for Motors acquisition result.
//
//-----------------------------------------------------------------------------
void MotorGroup::read_Motors(Tango::Attribute &attr)
{
    uint32_t l = 0;
    for (std::vector<Tango::DevLong>::iterator ite = motor_list.begin();
         ite != motor_list.end(); ++ite, ++l)
    {
        Pool_ns::MotorPool &motor = pool_dev->get_physical_motor((Pool_ns::ElementId)*ite);
        attr_Motors_read[l] = const_cast<char *>(motor.get_name().c_str());
    }
    attr.set_value(attr_Motors_read, motor_list.size());
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::read_MotorGroups
//
// description : 	Extract real attribute values for MotorGroupss acquisition result.
//
//-----------------------------------------------------------------------------
void MotorGroup::read_MotorGroups(Tango::Attribute &attr)
{
    uint32_t l = 0;
    for (std::vector<Tango::DevLong>::iterator ite = motor_group_list.begin();
         ite != motor_group_list.end(); ++ite, ++l)
    {
        Pool_ns::MotorGroupPool &mg = pool_dev->get_motor_group((Pool_ns::ElementId)*ite);
        attr_MotorGroups_read[l] = const_cast<char *>(mg.get_name().c_str());
    }

    attr.set_value(attr_MotorGroups_read, motor_group_list.size());
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::read_PseudoMotors
//
// description : 	Extract real attribute values for PseudoMotors acquisition result.
//
//-----------------------------------------------------------------------------
void MotorGroup::read_PseudoMotors(Tango::Attribute &attr)
{
    uint32_t l = 0;
    for (std::vector<Tango::DevLong>::iterator ite = pseudo_motor_list.begin();
         ite != pseudo_motor_list.end(); ++ite, ++l)
    {
        Pool_ns::PseudoMotorPool &pm = pool_dev->get_pseudo_motor(*ite);
        attr_PseudoMotors_read[l] = const_cast<char *>(pm.get_name().c_str());
    }

    attr.set_value(attr_PseudoMotors_read, pseudo_motor_list.size());
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::read_Position
//
// description : 	Extract real attribute values for Position acquisition result.
//
//-----------------------------------------------------------------------------
void MotorGroup::read_Position(Tango::Attribute &attr)
{
    DEBUG_STREAM << "MotorGroup::read_Position(Tango::Attribute &attr) entering... "<< endl;

    bool ctrl_locked = false;
    bool mot_locked = false;

//
// If we have some pseudo-motor in this group,
// check that they are correctly built
//

    if (nb_psm_in_grp != 0)
    {
        for (int32_t loop = 0;loop < nb_psm_in_grp;loop++)
        {
            if (!psm_in_grp[loop].dev->is_fica_built())
            {
                TangoSys_OMemStream o;
                o << "Impossible to read position of group " << get_name();
                o << "\nThe pseudo-motor " << psm_in_grp[loop].pool_psm.name;
                o << " is invalid" << ends;
                Tango::Except::throw_exception(
                        (const char *)"MotorGroup_InvalidPseudoMotor",
                        o.str(),
                        (const char *)"MotorGroup::read_Position");
            }
        }
    }

//
// Lock all the motors implied in this group
//

    int32_t loop = -1;

    mot_locked = true;
    for (loop = 0;loop < ind_elt_nb;loop++)
        ind_elts[loop]->Lock();

    DEBUG_STREAM << "All motors locked" << endl;

//
// Lock all the controllers implied in this group
//

    ctrl_locked = true;
    vector<Pool_ns::CtrlGrp*>::iterator impl_ctrl_ite;
    vector<Pool_ns::CtrlGrp*>::reverse_iterator impl_ctrl_rite;
    for (impl_ctrl_ite = implied_ctrls.begin();impl_ctrl_ite != implied_ctrls.end();++impl_ctrl_ite)
    {
        Pool_ns::ControllerPool *cp = (*impl_ctrl_ite)->ct;
        (*impl_ctrl_ite)->lock_ptr = new Pool_ns::AutoPoolLock(cp->get_ctrl_class_mon());
    }
    DEBUG_STREAM << "ALl ctrl locked" << endl;

    string except_func("PreReadAll");
    try
    {

//
// Send PreReadAll to all controller(s)
//

        for (impl_ctrl_ite = implied_ctrls.begin();impl_ctrl_ite != implied_ctrls.end();++impl_ctrl_ite)
        {
            Pool_ns::ControllerPool *cp = (*impl_ctrl_ite)->ct;
            MotorController *mc = static_cast<MotorController *>(cp->get_controller());
            try
            {
                mc->PreReadAll();
            }
            SAFE_CATCH(cp->get_class_name(),"PreReadAll()");
        }
        DEBUG_STREAM << "PreReadAll sent to ctrl(s)" << endl;

//
// Send PreReadOne to each implied motor
//

        except_func = "PreReadOne";
        for (loop = 0;loop < ind_elt_nb;loop++)
        {
            IndMov *ind_mov = static_cast<IndMov*>(ind_elts[loop]);
            Pool_ns::ControllerPool *cp = ind_mov->ctrl_grp->ct;
            MotorController *mc = static_cast<MotorController *>(cp->get_controller());
            try
            {
                mc->PreReadOne(ind_mov->idx_in_ctrl);
            }
            SAFE_CATCH(cp->get_class_name(),"PreReadOne()");
        }
        loop = -1;
        DEBUG_STREAM << "All PreReadOne sent" << endl;

//
// Send the ReadAll to all implied controller
//

        except_func = "ReadAll";
        for (impl_ctrl_ite = implied_ctrls.begin();impl_ctrl_ite != implied_ctrls.end();++impl_ctrl_ite)
        {
            Pool_ns::ControllerPool *cp = (*impl_ctrl_ite)->ct;
            MotorController *mc = static_cast<MotorController *>(cp->get_controller());
            try
            {
                mc->ReadAll();
            }
            SAFE_CATCH(cp->get_class_name(),"ReadAll()");
        }
        DEBUG_STREAM << "All ReadAll sent" << endl;

//
// Get each motor position
// The position returned by the controller is the dial position.
// We need to add motor offset
//

        except_func = "ReadOne";
        for (loop = 0;loop < ind_elt_nb;loop++)
        {
            IndMov *ind_mov = static_cast<IndMov*>(ind_elts[loop]);
            Pool_ns::ControllerPool *cp = ind_mov->ctrl_grp->ct;
            Motor_ns::Motor *m = ind_mov->get_motor_device();

            MotorController *mc = static_cast<MotorController *>(cp->get_controller());

            double mot_dial_pos = 0.0;
            try
            {
                mot_dial_pos = mc->ReadOne(ind_mov->idx_in_ctrl);
            }
            SAFE_CATCH(cp->get_class_name(), "ReadOne()");

            if (isnan(mot_dial_pos) != 0)
            {
                Tango::Except::throw_exception(
                    (const char *)"Motor_BadController",
                    (const char *)"The motor controller class has not re-defined method to read position (readOne(...))",
                    (const char *)"MotorGroup::read_Position");
            }

            double mot_offset = m->get_offset();
            int mot_sign = m->get_sign();
            double mot_pos = mot_sign*mot_dial_pos + mot_offset;

            DEBUG_STREAM << "Position for motor " << ind_mov->id << " is "
                         << mot_pos << endl;

            phys_mot_pos[ind_mov->idx_in_grp] = mot_pos;
        }
        loop = -1;

//
// Unlock all the controllers and all motor implied in this move
//

        for (impl_ctrl_rite = implied_ctrls.rbegin();
             impl_ctrl_rite != implied_ctrls.rend(); ++impl_ctrl_rite)
        {
            if ((*impl_ctrl_rite)->lock_ptr != NULL)
            {
                delete (*impl_ctrl_rite)->lock_ptr;
                (*impl_ctrl_rite)->lock_ptr = NULL;
            }
        }
        ctrl_locked = false;
        DEBUG_STREAM << "All ctrl unlocked" << endl;

        for (loop = 0;loop < ind_elt_nb;loop++)
        {
            ind_elts[loop]->Unlock();
        }
        mot_locked = false;
        DEBUG_STREAM << "All motors unlocked" << endl;

//
// Set attribute values
//

        from_phys_2_grp();
        attr.set_value(attr_Position_read,pos_spectrum_dim_x);

    }
    catch (Tango::DevFailed &e)
    {

//
// Unlock everything if needed
//

        if (ctrl_locked == true)
        {
            for (impl_ctrl_rite = implied_ctrls.rbegin();impl_ctrl_rite != implied_ctrls.rend();++impl_ctrl_rite)
            {
                if ((*impl_ctrl_rite)->lock_ptr != NULL)
                {
                    delete (*impl_ctrl_rite)->lock_ptr;
                    (*impl_ctrl_rite)->lock_ptr = NULL;
                }
            }
        }

        if (mot_locked == true)
        {
            for (int32_t ctr = 0;ctr < ind_elt_nb;ctr++)
            {
                ind_elts[ctr]->Unlock();
            }
        }

        TangoSys_OMemStream o;
        o << "Impossible to read position of group " << get_name();
        if (loop != -1)
        {
            o << "\nImpossible to read motor position for device " << ind_elts[loop]->get_alias() << " (";
            o << ind_elts[loop]->pe->get_full_name() << ")";
        }
        else
        {
            o << "\nController " ;
        }
        o << ". The " << except_func << "() controller method throws an exception" << ends;
        Tango::Except::re_throw_exception(e,(const char *)"Motor_ControllerFailed",
                                    o.str(),(const char *)"MotorGroup::read_Position");
    }

    Tango::DevState mot_sta = get_state();

    if (mot_sta == Tango::MOVING)
        attr.set_quality(Tango::ATTR_CHANGING);
    else if (mot_sta == Tango::ALARM)
        attr.set_quality(Tango::ATTR_ALARM);

}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::write_Position
//
// description : 	Write Position attribute values to hardware.
//
//-----------------------------------------------------------------------------
void MotorGroup::write_Position(Tango::WAttribute &attr)
{
    DEBUG_STREAM << "MotorGroup::write_Position(Tango::WAttribute &attr) entering... "<< endl;

//
// Check that we receive new position for all motors
//

    int32_t nb_received_pos = (int32_t) attr.get_write_value_length();
    if (nb_received_pos != pos_spectrum_dim_x)
    {
        TangoSys_OMemStream o;
        o << "This group is defined with " << pos_spectrum_dim_x << " motor(s) and you sent new position for ";
        o << nb_received_pos << " motor(s)" << ends;

        Tango::Except::throw_exception((const char *)"Motor_CantMoveGroup",o.str(),
                  (const char *)"MotorGroup::write_Position");
    }

//
// If we have some pseudo-motor in this group,
// check that they are correctly built
//

    if (nb_psm_in_grp != 0)
    {
        for (int32_t loop = 0;loop < nb_psm_in_grp;loop++)
        {
            if (!psm_in_grp[loop].dev->is_fica_built())
            {
                TangoSys_OMemStream o;
                o << "Impossible to write position of group " << get_name();
                o << "\nThe pseudo-motor " << psm_in_grp[loop].pool_psm.name;
                o << " is invalid" << ends;
                Tango::Except::throw_exception(
                        (const char *)"MotorGroup_InvalidPseudoMotor",
                        o.str(),
                        (const char *)"MotorGroup::write_Position");
            }
        }
    }

//
// Get written data
//

    const Tango::DevDouble *received_data;
    attr.get_write_value(received_data);

//
// Compute physical position
//

    from_grp_2_phys(received_data);

//
// Init vector to pass data to the movement thread
//

    vector<double> pos_vector;
    vector<Pool_ns::ElementId> mot_id_vector;

    vector<Pool_ns::IndEltGrp*>::iterator it;
    for(it = ind_elts.begin(); it != ind_elts.end(); ++it)
    {
        IndMov &ind_mov = *static_cast<IndMov*>(*it);
        mot_id_vector.push_back(ind_mov.id);
        pos_vector.push_back(phys_mot_pos[ind_mov.idx_in_grp]);
    }

//
// Start a movement thread
//

    th_failed = false;
    abort_cmd_executed = false;
    Pool_ns::PoolMonitor *mon = get_pool_element().get_notification_monitor();
    Pool_ns::MotorThread *pool_th = new Pool_ns::MotorThread(mot_id_vector,pos_vector,pool_dev,mon,get_id());

//
// Start it only while the pos_mon
// lock is taken. Otherwise, a dead-lock can happen, if the thread
// starts excuting its code just after the start() and before this code
// enters into the wait(). The movment thread will send the signal() but while
// this thread is not yet waiting for it and afterwards, we will have
// a dead-lock...
//

    {
        omni_mutex_lock lo(*mon);
        pool_th->start();
        mon->wait();
    }

    if (th_failed == true)
    {
        Tango::DevFailed ex(th_except);
        throw ex;
    }

}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::abort
 *
 *	description:	method to execute "Abort"
 *	Abort movement of all motors moving when the command is executed
 *
 *
 */
//+------------------------------------------------------------------
void MotorGroup::abort()
{
    DEBUG_STREAM << "MotorGroup::abort(): entering... !" << endl;

    //	Add your own code to control device here
    base_abort(true);
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::abort
 *
 *	description:	method to execute "Abort"
 *	Abort movement of all motors moving when the command is executed
 *
 *
 */
//+------------------------------------------------------------------
void MotorGroup::base_abort(bool send_evt)
{
//
// Send abort to all motors member of the group
//

    vector<Tango::DevFailed> v_except;

    abort_cmd_executed = true;

    vector<Pool_ns::IndEltGrp*>::iterator it;
    for(it = ind_elts.begin(); it != ind_elts.end(); ++it)
    {
        Pool_ns::IndEltGrp &ind_mov = *(*it);
        try
        {
            ind_mov.obj_proxy->command_inout("Abort");
        }
        catch (Tango::DevFailed &e)
        {
            v_except.push_back(e);
        }
    }
//
// Report exception to caller in case of
//

    if (v_except.size() != 0)
    {
        if (v_except.size() == 1)
        {
            Tango::Except::re_throw_exception(v_except[0],(const char *)"Motor_ExcepAbort",
                                            (const char *)"One motor throws exception during Abort command",
                                            (const char *)"MotorGroup::Abort");
        }
        else
        {
        }
    }
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::add_element
 *
 *	description:	method to execute "AddElement"
 *	Append a new experiment channel to the current list of channels in the measurement group.
 *
 * @param	argin	Experiment Channel name
 *
 */
//+------------------------------------------------------------------
void MotorGroup::add_element(Tango::DevString argin)
{
    DEBUG_STREAM << "MotorGroup::add_element(): entering... !" << endl;

    //	Add your own code to control device here

    Tango::AutoTangoMonitor atm(pool_dev);

    Pool_ns::MotorGroupPool &mgp = pool_dev->get_motor_group(get_id());

//
// Check that this group is not used by any pseudo motor
//
    vector<string> used_by_pm;
    if (pool_dev->get_pseudo_motors_that_use_mg(mgp.id,used_by_pm) == true)
    {
        TangoSys_OMemStream o;
        o << "Can't add group elements. ";
        o << "This motor group is used by pseudo motor(s): ";

        vector<string>::iterator ite = used_by_pm.begin();
        for(;ite != used_by_pm.end(); ite++)
            o << "'" << *ite << "', ";
        o << ends;

        Tango::Except::throw_exception((const char *)"MotorGroup_BadArgument",o.str(),
                             (const char *)"MotorGroup::add_element");
    }

    string elt_name(argin);

//
// Check that the element to be added is not already part of any motor group
// (including itself) in the hierarchy of motor groups to which this motor group
// belongs
//
    vector<string> used_by_mg;
    if(pool_dev->get_motor_groups_in_hierarchy_containing_elt(mgp,elt_name,used_by_mg) == true)
    {
        TangoSys_OMemStream o;
        o << "Can't add '" << elt_name << "'. ";

        if(mgp.name == used_by_mg[0])
        {
            o << "This motor group already contains (directly or indirectly) '" << elt_name << "'.";
        }
        else
        {
            o << "This motor group is member of motor group(s) (";
            vector<string>::iterator ite = used_by_mg.begin();
            for(;ite != used_by_mg.end(); ite++)
                o << "'" << *ite << "', ";
            o << ") that already contain (directly or indirectly) '" << elt_name << "'." << ends;
        }

        Tango::Except::throw_exception((const char *)"MotorGroup_BadArgument",o.str(),
                             (const char *)"MotorGroup::add_element");
    }

//
// Check if the element exists in the pool
//
    Pool_ns::GrpEltType type;
    Pool_ns::PoolElement *elt = NULL;

    bool elt_exists = true;

    try
    {
        elt = &pool_dev->get_physical_motor(elt_name);
        type = Pool_ns::MOTOR;
    }
    catch(Tango::DevFailed &e)
    {
        try
        {
            elt = &pool_dev->get_motor_group(elt_name);
            type = Pool_ns::GROUP;
        }
        catch(Tango::DevFailed &e)
        {
            try
            {
                elt = &pool_dev->get_pseudo_motor(elt_name);
                type = Pool_ns::PSEUDO_MOTOR;
            }
            catch(Tango::DevFailed &e)
            {
                elt_exists = false;
            }
        }
    }

    if(elt_exists == false)
    {
        TangoSys_OMemStream o;
        o << "No valid element (motor, pseudo motor or motor group) with name " << elt_name << " found in the Pool." << ends;

        Tango::Except::throw_exception((const char *)"MotorGroup_BadArgument",o.str(),
                                       (const char *)"MotorGroup::add_element");
    }

//
// If it is a motor group or a pseudo motor check that none of its ind elements
// already belongs to this motor group
// Also update the object members which are device properties values
// (motor_list, user_group_elt, pos_spectrum_dim_x)
//
    if(type == Pool_ns::GROUP)
    {
        Pool_ns::MotorGroupPool *grp = (Pool_ns::MotorGroupPool*)elt;
        MotorGroup *grp_dev = pool_dev->get_motor_group_device(*grp);

        IndMov *ind_elt = NULL;
        vector<Pool_ns::ElementId>::iterator ite = grp->mot_ids.begin();
        for(;ite != grp->mot_ids.end(); ite++)
        {
            try
            {
                ind_elt = &get_ind_mov_from_id(*ite);
                break;
            }
            catch(Tango::DevFailed &e) {}
        }

        if(ind_elt != NULL)
        {
            TangoSys_OMemStream o;
            o << "The motor group to be added contains an element (" << ind_elt->get_alias() << ") which is already part of the motor group" << ends;

            Tango::Except::throw_exception((const char *)"MotorGroup_BadArgument",o.str(),
                                           (const char *)"MotorGroup::add_element");
        }

        user_group_elt.push_back(grp->get_id());
        motor_group_list.push_back(grp->get_id());

        phys_group_elt.insert(phys_group_elt.end(),grp_dev->phys_group_elt.begin(), grp_dev->phys_group_elt.end());
        pos_spectrum_dim_x += grp_dev->pos_spectrum_dim_x;
    }
    else if(type == Pool_ns::PSEUDO_MOTOR)
    {
        Pool_ns::PseudoMotorPool *pm = (Pool_ns::PseudoMotorPool*)elt;
        PseudoMotor_ns::PseudoMotor *pm_dev = pool_dev->get_pseudo_motor_device(*pm);

        vector<PsmCtrlInGrp>::iterator pm_ctrl_ite = psm_ctrls_in_grp.begin();
        for(;pm_ctrl_ite != psm_ctrls_in_grp.end(); pm_ctrl_ite++)
        {
            if(pm_ctrl_ite->pool_psm_ctrl == pm_dev->get_controller())
                break;
        }

//
// If there isn't already a pseudo motor with the same controller in the group
// we have to check that none of the motors involved in the pseudo motor are
// already in the motor group.
//
        if(pm_ctrl_ite == psm_ctrls_in_grp.end())
        {
            IndMov *ind_elt = NULL;
            Pool_ns::ElemIdVectorIt ite = pm->mot_elts.begin();
            for(;ite != pm->mot_elts.end(); ite++)
            {
                try
                {
                    Pool_ns::PoolElement *elem = pool_dev->get_element(*ite);
                    ind_elt = &get_ind_mov_from_name(elem->name);
                    break;
                }
                catch(Tango::DevFailed &e) {}
            }

            if(ind_elt != NULL)
            {
                TangoSys_OMemStream o;
                o << "The pseudo motor to be added contains an element (" << ind_elt->get_alias() << ") which is already part of the motor group" << ends;

                Tango::Except::throw_exception((const char *)"MotorGroup_BadArgument",o.str(),
                                               (const char *)"MotorGroup::add_element");
            }

            Pool_ns::ElemIdVectorIt pm_m_ite = pm->mot_elts.begin();
            for(;pm_m_ite != pm->mot_elts.end(); pm_m_ite++)
            {
                phys_group_elt.push_back(*pm_m_ite);
            }
        }

        user_group_elt.push_back(pm->get_id());
        pseudo_motor_list.push_back(pm->get_id());
        pos_spectrum_dim_x++;
    }
    else if(type == Pool_ns::MOTOR)
    {
        Pool_ns::MotorPool *m = (Pool_ns::MotorPool*)elt;
        user_group_elt.push_back(m->get_id());
        phys_group_elt.push_back(m->get_id());
        motor_list.push_back(m->get_id());
        pos_spectrum_dim_x++;
    }

//
// Register for internal events on the new element
//
    elt->add_pool_elem_listener(&mgp);

    update_elements();

//
// Fire events on proper attributes
//
    if(type == Pool_ns::GROUP)
    {
        Tango::Attribute &mgs = dev_attr->get_attr_by_name("MotorGroups");
        read_MotorGroups(mgs);
        mgs.fire_change_event();
    }
    else if(type == Pool_ns::PSEUDO_MOTOR)
    {
        Tango::Attribute &pms = dev_attr->get_attr_by_name("PseudoMotors");
        read_PseudoMotors(pms);
        pms.fire_change_event();
    }
    else if(type == Pool_ns::MOTOR)
    {
        Tango::Attribute &mots = dev_attr->get_attr_by_name("Motors");
        read_Motors(mots);
        mots.fire_change_event();
    }

    Tango::Attribute &elts = dev_attr->get_attr_by_name("Elements");
    read_Elements(elts);
    elts.fire_change_event();

//
// Fire internal events to listeners
//
    Pool_ns::PoolElementEvent evt(Pool_ns::ElementListChange, &mgp);
    mgp.fire_pool_elem_change(&evt);

//
// Inform the pool so it can send a change event on the motor group list
//
    pool_dev->motor_group_elts_changed(get_id());
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::remove_element
 *
 *	description:	method to execute "RemoveElement"
 *	Removes the experiment channel from the list of experiment channels in the measurement group
 *
 * @param	argin	Experiment channel name
 *
 */
//+------------------------------------------------------------------
void MotorGroup::remove_element(Tango::DevString argin)
{
    DEBUG_STREAM << "MotorGroup::remove_element(): entering... !" << endl;

    //	Add your own code to control device here
    Tango::AutoTangoMonitor atm(pool_dev);

    Pool_ns::MotorGroupPool &mgp = pool_dev->get_motor_group(get_id());

//
// Check that this group is not used by any pseudo motor
//
    vector<string> used_by_pm;
    if (pool_dev->get_pseudo_motors_that_use_mg(mgp.id,used_by_pm))
    {
        TangoSys_OMemStream o;
        o << "Can't delete group with name " << argin;
        o << ". It is used by pseudo motor(s): ";

        vector<string>::iterator ite = used_by_pm.begin();
        for(;ite != used_by_pm.end(); ite++)
            o << *ite << ", " << ends;
        o << ends;

        Tango::Except::throw_exception((const char *)"MotorGroup_BadArgument",o.str(),
                             (const char *)"MotorGroup::add_element");
    }

    string elt_name(argin);

//
// Check which type of element it is
//
    Pool_ns::PoolElement *elt = NULL;
    Pool_ns::ElementType type = Pool_ns::UNDEF_ELEM;
    try
    {
        Pool_ns::PoolElement *pe = pool_dev->get_element(elt_name);
        type = pe->get_type();
    }
    catch(Tango::DevFailed &df)
    {
        TangoSys_OMemStream o;
        o << "There is no element named '"<< elt_name << "' in this pool" << ends;

        Tango::Except::re_throw_exception(df, "MotorGroup_UnknownElement", o.str(),
                                          "MotorGroup::remove_element");
    }

//
// Check that the element is in the group
//

    if(mgp.is_user_member(elt->get_id()) == false)
    {
        TangoSys_OMemStream o;
        o << "The element '" << elt_name << "' is not part of the motor group" << ends;

        Tango::Except::throw_exception("MotorGroup_BadArgument",o.str(),
                                       "MotorGroup::remove_element");
    }

//
// Update the object members which are device properties values
// (motor_list, user_group_elt, pos_spectrum_dim_x)
//
    if(type == Pool_ns::MOTOR_GROUP_ELEM)
    {
        Pool_ns::MotorGroupPool *grp = (Pool_ns::MotorGroupPool*)elt;
        MotorGroup *grp_dev = pool_dev->get_motor_group_device(*grp);

        // Remove the group
        Tango::DevLong mg_id = (Tango::DevLong) grp->get_id();
        std::vector<Tango::DevLong>::iterator v_ite = find(user_group_elt.begin(), user_group_elt.end(), mg_id);
        if (v_ite != user_group_elt.end())
            user_group_elt.erase(v_ite);

        v_ite = find(motor_group_list.begin(), motor_group_list.end(), mg_id);
        if (v_ite != motor_group_list.end())
            motor_group_list.erase(v_ite);

        // Remove the motors that are in the group
        for(v_ite = grp_dev->phys_group_elt.begin(); v_ite != grp_dev->phys_group_elt.end(); v_ite++)
        {
            Pool_ns::ElementId elem_id = (Pool_ns::ElementId)*v_ite;
            std::vector<Tango::DevLong>::iterator elt_ite = find(phys_group_elt.begin(), phys_group_elt.end(), elem_id);
            if (elt_ite != phys_group_elt.end())
                phys_group_elt.erase(elt_ite);
        }

        pos_spectrum_dim_x -= grp_dev->pos_spectrum_dim_x;

    }
    else if(type == Pool_ns::PSEUDO_MOTOR_ELEM)
    {
        Pool_ns::PseudoMotorPool *pm = (Pool_ns::PseudoMotorPool*)elt;
        PseudoMotor_ns::PseudoMotor *pm_dev = pool_dev->get_pseudo_motor_device(*pm);
        Tango::DevLong pm_id = (Tango::DevLong) pm->get_id();

        // Remove the pseudo motor
        std::vector<Tango::DevLong>::iterator v_ite = find(user_group_elt.begin(), user_group_elt.end(), pm_id);
        if (v_ite != user_group_elt.end())
            user_group_elt.erase(v_ite);

        v_ite = find(pseudo_motor_list.begin(), pseudo_motor_list.end(), pm_id);
        if (v_ite != pseudo_motor_list.end())
            pseudo_motor_list.erase(v_ite);
    //
    // If no other pseudo motor uses the motors of this pseudo motor (i.e. they have
    // the same controller), then remove the motors
    //
        vector<PsmInGrp>::iterator pm_ite = psm_in_grp.begin();
        for(;pm_ite != psm_in_grp.end(); pm_ite++)
        {
            if(pm_ite->pool_psm.get_id() == pm->get_id())
                continue;

            if(pm_ite->dev->get_ctrl_id() == pm_dev->get_ctrl_id())
                break;
        }

        if(pm_ite == psm_in_grp.end())
        {
            Pool_ns::ElemIdVectorIt pm_elt_ite = pm->mot_elts.begin();
            for(;pm_elt_ite != pm->mot_elts.end(); pm_elt_ite++)
            {
                std::vector<Tango::DevLong>::iterator elt_ite = find(phys_group_elt.begin(), phys_group_elt.end(), *pm_elt_ite);
                if (elt_ite != phys_group_elt.end())
                    phys_group_elt.erase(elt_ite);
            }
        }
        pos_spectrum_dim_x--;
    }
    else if(type == Pool_ns::MOTOR_ELEM)
    {
        Pool_ns::MotorPool *m = (Pool_ns::MotorPool*)elt;
        Tango::DevLong m_id = (Tango::DevLong) m->get_id();

        // Remove the motor
        std::vector<Tango::DevLong>::iterator v_ite = find(user_group_elt.begin(), user_group_elt.end(), m_id);
        if (v_ite != user_group_elt.end())
            user_group_elt.erase(v_ite);

        v_ite = find(motor_list.begin(), motor_list.end(), m_id);
        if (v_ite != motor_list.end())
            motor_list.erase(v_ite);

        v_ite = find(phys_group_elt.begin(), phys_group_elt.end(), m_id);
        if (v_ite != phys_group_elt.end())
            phys_group_elt.erase(v_ite);

        pos_spectrum_dim_x--;
    }
    else
    {
        TangoSys_OMemStream o;
        o << "Unexpected error. " << elt_name << " in the motor group should be"
          << "a motor, pseudo motor or motor group but it is a "
          << Pool_ns::ElementTypeStr[type] << " instead" << ends;

        Tango::Except::throw_exception(
            (const char *)"MotorGroup_Unexpected",o.str(),
            (const char *)"MotorGroup::remove_element");
    }

//
// Register for internal events on the new element
//
    elt->remove_pool_elem_listener(&mgp);

    update_elements();

//
// Fire events on proper attributes
//

    if(type == Pool_ns::MOTOR_GROUP_ELEM)
    {
        Tango::Attribute &mgs = dev_attr->get_attr_by_name("MotorGroups");
        read_MotorGroups(mgs);
        mgs.fire_change_event();
    }
    else if(type == Pool_ns::PSEUDO_MOTOR_ELEM)
    {
        Tango::Attribute &pms = dev_attr->get_attr_by_name("PseudoMotors");
        read_PseudoMotors(pms);
        pms.fire_change_event();
    }
    else if(type == Pool_ns::MOTOR_ELEM)
    {
        Tango::Attribute &mots = dev_attr->get_attr_by_name("Motors");
        read_Motors(mots);
        mots.fire_change_event();
    }

    Tango::Attribute &elts = dev_attr->get_attr_by_name("Elements");
    read_Elements(elts);
    elts.fire_change_event();

//
// Fire internal events to listeners
//
    Pool_ns::PoolElementEvent evt(Pool_ns::ElementListChange, &mgp);
    mgp.fire_pool_elem_change(&evt);

//
// Inform the pool so it can send a change event on the motor group list
//
    pool_dev->motor_group_elts_changed(get_id());

}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::update_elements
 *
 *	description: updates the motor group elements based on the values
 * of motor_list, user_group_elt, pos_spectrum_dim_x.
 *
 */
//+------------------------------------------------------------------
void MotorGroup::update_elements()
{

//
// Update some counters
//
    ind_elt_nb = phys_group_elt.size();
    usr_elt_nb = user_group_elt.size();

//
// Write the new values for the device properties
// (motor_list, user_group_elt, pos_spectrum_dim_x)
//
    Tango::DbData dev_prop;
    Tango::DbDatum
    mot_lst("Motor_list"),
    mg_lst("Motor_group_list"),
    pm_lst("Pseudo_motor_list"),
    usr_grp_lst("User_group_elt"),
    phy_grp_lst("Phys_group_elt"),
    pos_dim("Pos_spectrum_dim_x");
    mot_lst << motor_list;
    dev_prop.push_back(mot_lst);
    mg_lst << motor_group_list;
    dev_prop.push_back(mg_lst);
    pm_lst << pseudo_motor_list;
    dev_prop.push_back(pm_lst);
    usr_grp_lst << user_group_elt;
    dev_prop.push_back(usr_grp_lst);
    phy_grp_lst << phys_group_elt;
    dev_prop.push_back(phy_grp_lst);
    pos_dim << pos_spectrum_dim_x;
    dev_prop.push_back(pos_dim);
    get_db_device()->put_property(dev_prop);

//
// Clear the necessary structures
//
    vector<Pool_ns::IndEltGrp*>::iterator ind_it;
    for(ind_it = ind_elts.begin(); ind_it != ind_elts.end(); ++ind_it)
        delete(*ind_it);
    ind_elts.clear();

    vector<Pool_ns::CtrlGrp*>::iterator ctrl_it;
    for(ctrl_it = implied_ctrls.begin(); ctrl_it != implied_ctrls.end(); ++ctrl_it)
        delete(*ctrl_it);
    implied_ctrls.clear();

    user_group_elt_type.clear();
    grp_in_grp.clear();
    psm_in_grp.clear();
    psm_ctrls_in_grp.clear();

    state_array.clear();

//
// update Pool data structure
//
    Pool_ns::MotorGroupPool &mgp =
        pool_dev->get_motor_group(get_id());

    init_pool_element(&mgp);

    build_grp();

//
// Update missing pool data structure (only possible after a build_grp() )
//
    mgp.mot_ids.clear();
    for (long i = 0;i < ind_elt_nb; i++)
        mgp.mot_ids.push_back(ind_elts[i]->id);

    build_grp_struct();
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::pool_elem_changed
 *
 *	description: This method is called when the src object has changed
 *               and an event is generated
 *
 * arg(s) : - evt [in]: The event that has occured
 *          - forward_evt [out]: the new internal event data to be sent
 *                               to all listeners
 */
//+------------------------------------------------------------------

void MotorGroup::pool_elem_changed(Pool_ns::PoolElemEventList &evt_lst,
                                   Pool_ns::PoolElementEvent &forward_evt)
{
    Pool_ns::PoolElementEvent *evt = evt_lst.back();
    Pool_ns::PoolElement *src = evt->src;

    forward_evt.priority = evt->priority;

//
// State change from a motor
//

    switch(evt->type)
    {
        case Pool_ns::StateChange:
        {
//
// State events coming from underlying motor groups are discarted because the
// motor group already register for state changes on the underlying motors
//
            Tango::DevState old_state = get_state();

            // Warning: This method needs a lock on the Controller. Therefore, the element which
            // invoked the change should only do it after releasing its own lock.
            if(evt_lst.front()->src->get_type() == Pool_ns::MOTOR_GROUP_ELEM)
            {
                Tango::AutoTangoMonitor lo(this);
                update_state_from_ctrls();
            }
            else
            {
                IndMov &m = get_ind_mov_from_name(evt_lst.front()->src->name);
                {
                    Tango::AutoTangoMonitor lo(this);
                    update_state_from_ctrls(m.idx_in_grp,
                        (Tango::DevState)evt_lst.front()->curr.state);
                }
            }

            Tango::DevState new_state = get_state();

            if(old_state != new_state)
            {
                Tango::AutoTangoMonitor lo(this);
                Tango::MultiAttribute *dev_attrs = get_device_attr();
                Tango::Attribute &state_att = dev_attrs->get_attr_by_name("State");
                state_att.fire_change_event();
            }

            forward_evt.type = Pool_ns::StateChange;
            forward_evt.old.state = Pool_ns::PoolTango::toPool(old_state);
            forward_evt.curr.state = Pool_ns::PoolTango::toPool(new_state);
        }
        break;

//
// Position change event from a motor
//
        case Pool_ns::PositionChange:
        {
            //Find motor/pseudo motor that changed
            try
            {
                IndMov &m = get_ind_mov_from_name(src->name);

                // Confirm that the motor is directly seen by the user
                assert(m.idx_in_usr >=0);

                Tango::MultiAttribute *attr_list = get_device_attr();
                Tango::Attribute &attr           = attr_list->get_attr_by_name ("Position");

                Tango::DevState mg_state = get_state();


                // Make sure the event is sent to all clients
                if(true == evt->priority)
                    attr.set_change_event(true,false);

                {
                    // get the tango synchronization monitor
                    Tango::AutoTangoMonitor synch(this);

                    attr_Position_read[m.idx_in_usr] = evt->curr.position;

                    // set the attribute value
                    attr.set_value (attr_Position_read,pos_spectrum_dim_x);

                    if (mg_state == Tango::MOVING)
                        attr.set_quality(Tango::ATTR_CHANGING);
                    else if (mg_state == Tango::ALARM)
                        attr.set_quality(Tango::ATTR_ALARM);

                    // push the event
                    attr.fire_change_event();
                }

                if(true == evt->priority)
                    attr.set_change_event(true,true);
            }
            catch(Tango::DevFailed &e)
            {
                try
                {
                    PsmInGrp &psm = get_psm_from_name(src->name);

                    Tango::MultiAttribute *attr_list = get_device_attr();
                    Tango::Attribute &attr           = attr_list->get_attr_by_name ("Position");

                    Tango::DevState mg_state = get_state();

                    // Make sure the event is sent to all clients
                    if(true == evt->priority)
                        attr.set_change_event(true,false);

                    {
                        // get the tango synchronization monitor
                        Tango::AutoTangoMonitor synch(this);

                        attr_Position_read[psm.idx_in_usr] = evt->curr.position;

                        // set the attribute value
                        attr.set_value (attr_Position_read,pos_spectrum_dim_x);

                        if (mg_state == Tango::MOVING)
                            attr.set_quality(Tango::ATTR_CHANGING);
                        else if (mg_state == Tango::ALARM)
                            attr.set_quality(Tango::ATTR_ALARM);

                        // push the event
                        attr.fire_change_event();
                    }
                    if(true == evt->priority)
                        attr.set_change_event(true,true);
                }
                catch(Tango::DevFailed &e)
                {
                    TangoSys_OMemStream o;
                    o << "No element with name " << src->name << " found in Motor group element list" << ends;

                    Tango::Except::throw_exception((const char *)"Pool_BadArgument",o.str(),
                                                   (const char *)"MotorGroup::pool_elem_changed");
                }
            }

            forward_evt.type = Pool_ns::PositionArrayChange;
            forward_evt.dim = usr_elt_nb;
            forward_evt.old.position_array = NULL;
            forward_evt.curr.position_array = attr_Position_read;

//cout << get_alias() << "::pool_elem_changed (PositionChange, ";
//for(long l = 0; l < usr_elt_nb; l++) cout << attr_Position_read[l] << ",";
//cout << ")" << endl;
        }
        break;

//
// Position array change event from a motor group
//
        case Pool_ns::PositionArrayChange:
        {
            GrpInGrp &grp = get_grp_from_id(src->id);

            assert(evt->dim == grp.pos_len);

            Tango::MultiAttribute *attr_list = get_device_attr();
            Tango::Attribute &attr           = attr_list->get_attr_by_name ("Position");

            Tango::DevState mg_state = get_state();

            // Make sure the event is sent to all clients
            if(true == evt->priority)
                attr.set_change_event(true,false);

            {
                // get the tango synchronization monitor
                Tango::AutoTangoMonitor synch(this);

                memcpy(&(attr_Position_read[grp.idx_in_usr]),evt->curr.position_array,sizeof(double)*evt->dim);

                // set the attribute value
                attr.set_value (attr_Position_read,pos_spectrum_dim_x);

                if (mg_state == Tango::MOVING)
                    attr.set_quality(Tango::ATTR_CHANGING);
                else if (mg_state == Tango::ALARM)
                    attr.set_quality(Tango::ATTR_ALARM);

                // push the event
                attr.fire_change_event();
            }

            if(true == evt->priority)
                attr.set_change_event(true,true);

            forward_evt.type = Pool_ns::PositionArrayChange;
            forward_evt.dim = pos_spectrum_dim_x;
            forward_evt.old.position_array = NULL;
            forward_evt.curr.position_array = attr_Position_read;
        }
        break;

//
// Nothing to do. Just propagate the event.
//
        case Pool_ns::MotionEnded:
        {

        }
        break;

//
// One of the motor groups which are member of this motor group changed its list of
// elements.
//
        case Pool_ns::ElementListChange:
        {
            GrpInGrp &grp = get_grp_from_id(src->id);
            MotorGroup *grp_dev = pool_dev->get_motor_group_device(src->id);
            long diff_pos_len = grp_dev->pos_spectrum_dim_x - grp.pos_len;
            pos_spectrum_dim_x += diff_pos_len;

            // Rebuild the physical group list
            // This will not work in case the group has no elements!
            /*
            bool added = diff_pos_len > 0;
            vector<string>::iterator ite_start = find_in_phys_group_lst(grp.pool_grp->phy_group_elt[0]);
            vector<string>::iterator ite_end = ite_start;
            advance(ite_end,grp.mot_nb);
            phy_group_elt.erase(ite_start,ite_end);
            phy_group_elt.insert(ite_start,grp.pool_grp->phy_group_elt);
            */

            phys_group_elt.clear();
            for(unsigned long i = 0; i < user_group_elt.size(); i++)
            {
                Pool_ns::GrpEltType type = user_group_elt_type[i];

                if(type == Pool_ns::MOTOR)
                {
                    phys_group_elt.push_back(user_group_elt[i]);
                }
                else if(type == Pool_ns::GROUP)
                {
                    Pool_ns::MotorGroupPool &grp = pool_dev->get_motor_group(user_group_elt[i]);
                    for (unsigned long loop = 0;loop < grp.mot_ids.size();loop++)
                    {
                        Pool_ns::MotorPool &mot = pool_dev->get_physical_motor(grp.mot_ids[loop]);
                        phys_group_elt.push_back(mot.get_id());
                    }
                }
                else if(type == Pool_ns::PSEUDO_MOTOR)
                {
                    Pool_ns::PseudoMotorPool &pm = pool_dev->get_pseudo_motor(user_group_elt[i]);
                    for (unsigned long loop = 0;loop < pm.mot_elts.size();loop++)
                    {
                        Pool_ns::ElementId id = pm.mot_elts[loop];
                        if (find(phys_group_elt.begin(), phys_group_elt.end(), id) == phys_group_elt.end())
                            phys_group_elt.push_back(id);
                    }
                }
            }
            update_elements();
        }
        break;

//
// The structure of the motors/controlllers has changed.
//
        case Pool_ns::ElementStructureChange:
        {
            int32_t ctrl_grp_idx;
            Tango::AutoTangoMonitor atm(pool_dev);
            Pool_ns::ControllerPool &ctrl_ref = pool_dev->get_controller_from_element(src->id);
            Pool_ns::CtrlGrp &ctrl_grp = get_ctrl_grp_from_id(ctrl_ref.id, ctrl_grp_idx);
//
// Update controller data
//
            ctrl_grp.ct = &ctrl_ref;
//
// Update motor data
//
            IndMov &m = get_ind_mov_from_id(src->id);
            m.pe = src;

        }
        break;

        default:
        {
            assert(false);
        }
        break;
    }
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::update_state_from_ctrls
//
// description : 	Updates the state attribute
//
//-----------------------------------------------------------------------------

void MotorGroup::update_state_from_ctrls(Pool_ns::ElementId idx, Tango::DevState state)
{
    Tango::DevState old_state = get_state();

//
// Read all states
//

    vector<Tango::DevState> old_state_array(state_array);

    int32_t loop;

    if(idx == -1)
    {
        state_array = vector<Tango::DevState>(ind_elts.size(), Tango::UNKNOWN);
        read_state_from_ctrls();
    }
    else
    {
        if (state_array.size() == 0)
        {
            state_array = vector<Tango::DevState>(ind_elts.size(), Tango::UNKNOWN);
            read_state_from_ctrls();
        }
        state_array[idx] = state;
    }

    string &_status = get_status();
    _status.clear();

//
// If it is the ghost group and if the request comes from the polling
// thread, eventually forward state event on ind element devices
//

    int th_id = omni_thread::self()->id();

    if (is_ghost())
    {
//
// If it is the ghost group and if the request comes from the polling
// thread, eventually forward state event on ind element devices
//
        if(th_id == get_polling_thread_id())
        {
            send_state_event(old_state_array,state_array);
        }
//
// If it is the ghost group but the request comes from a motor for which there
// was a client state request, then inform the listeners that the state has changed
// thread, eventually forward state event on ind element devices.
// Note: the motor device is not locked in the code below because this code should
//       only be reached from a motor call from a client which already has the motor lock.
//
        else if (idx != -1)
        {
            Tango::DevState old_state = old_state_array[idx];
            Tango::DevState state = state_array[idx];
            if (old_state != state)
            {
                // Push event on the element device
                Tango::Device_4Impl *dev = ind_elts[idx]->get_device();
                Tango::Attribute &state_att = dev->get_device_attr()->get_attr_by_name("State");
                state_att.fire_change_event();

                // Notify listeners
                Pool_ns::MotorPool &pe = pool_dev->get_physical_motor(ind_elts[idx]->id);
                if(pe.has_listeners())
                {
                    Pool_ns::PoolElementEvent evt(Pool_ns::StateChange, &pe);
                    evt.old.state = Pool_ns::PoolTango::toPool(old_state);
                    evt.curr.state = Pool_ns::PoolTango::toPool(state);
                    pe.fire_pool_elem_change(&evt);
                }
            }
        }
    }


//
// Are there any elements in FAULT
//

    int32_t nb;
    vector<Tango::DevState>::iterator v_sta_start, v_sta_stop;
    vector<Pool_ns::IndEltGrp*>::iterator im_ite = ind_elts.begin();

    if ((nb = count(state_array.begin(),state_array.end(),Tango::FAULT)) != 0)
    {
        set_state(Tango::FAULT);
        v_sta_start = state_array.begin();
        for (loop = 0;loop < nb;loop++)
        {
            v_sta_stop = find(v_sta_start,state_array.end(),Tango::FAULT);
            int32_t dist = distance(state_array.begin(),v_sta_stop);
            vector<Pool_ns::IndEltGrp*>::iterator im_ite = ind_elts.begin();
            advance(im_ite,dist);
            Pool_ns::IndEltGrp *ind = *im_ite;
            if (loop != 0)
                _status = _status + '\n';
            _status = _status + ind->get_family() + " " + ind->get_alias() + " is in FAULT";
            v_sta_start = v_sta_stop;
            v_sta_start++;
        }
    }

//
// Is there any motor(s) in UNKNOWN
//

    else if ((nb = count(state_array.begin(),state_array.end(),Tango::UNKNOWN)) != 0)
    {
        set_state(Tango::UNKNOWN);
        v_sta_start = state_array.begin();
        for (loop = 0;loop < nb;loop++)
        {
            v_sta_stop = find(v_sta_start,state_array.end(),Tango::UNKNOWN);
            int32_t dist = distance(state_array.begin(),v_sta_stop);
            vector<Pool_ns::IndEltGrp*>::iterator im_ite = ind_elts.begin();
            advance(im_ite,dist);
            Pool_ns::IndEltGrp *ind = *im_ite;
            if (loop != 0)
                _status = _status + '\n';
            _status = _status + ind->get_family() + " " + ind->get_alias() + " is in UNKNOWN state";
            v_sta_start = v_sta_stop;
            v_sta_start++;
        }
    }

//
// Is there any motor(s) in ALARM
//

    else if ((nb = count(state_array.begin(),state_array.end(),Tango::ALARM)) != 0)
    {
        set_state(Tango::ALARM);
        v_sta_start = state_array.begin();
        for (loop = 0;loop < nb;loop++)
        {
            v_sta_stop = find(v_sta_start,state_array.end(),Tango::ALARM);
            int32_t dist = distance(state_array.begin(),v_sta_stop);
            vector<Pool_ns::IndEltGrp*>::iterator im_ite = ind_elts.begin();
            advance(im_ite,dist);
            Pool_ns::IndEltGrp *ind = *im_ite;
            if (loop != 0)
                _status = _status + '\n';
            _status = _status + ind->get_family() + " " + ind->get_alias() + " is in ALARM";
            v_sta_start = v_sta_stop;
            v_sta_start++;
        }
    }

//
// Is there any motor(s) moving
//

    else if ((nb = count(state_array.begin(),state_array.end(),Tango::MOVING)) != 0)
    {
        set_state(Tango::MOVING);
        v_sta_start = state_array.begin();
        for (loop = 0;loop < nb;loop++)
        {
            v_sta_stop = find(v_sta_start,state_array.end(),Tango::MOVING);
            int32_t dist = distance(state_array.begin(),v_sta_stop);
            vector<Pool_ns::IndEltGrp*>::iterator im_ite = ind_elts.begin();
            advance(im_ite,dist);
            Pool_ns::IndEltGrp *ind = *im_ite;
            if (loop != 0)
                _status = _status + '\n';
            _status = _status + ind->get_family() + " " + ind->get_alias() + " is MOVING";
            v_sta_start = v_sta_stop;
            v_sta_start++;
        }
    }

//
// All motor's ON
//

    else
    {
        set_state(Tango::ON);

//
// There is a trick here for client getting position with polling mode
// The movment thread stores motor position in the polling buffer and
// the client is getting position from this polling buffer
// When the movment thread detects that the movment is over
// (state != MOVING), it invalidates data from the polling buffer and
// therefore all clients will get data from hardware access.
// What could happens, is that a client thread detects first the
// end of the movment (before the movment thread). If this thread
// immediately reads the position after it detects the movment end, it will
// get the last value written in the polling buffer because the mov thread has not
// yet invalidate it.
// Therefore, if the thread executing this code is not the mov thread and if the state
// changed from MOVING to ON, delay the state changes that it will be detected by the
// movment thread. This movment thread is doing a motor call every 10 mS
//

        int th_id = omni_thread::self()->id();
        if (mov_th_id != 0)
        {
            if ((old_state == Tango::MOVING) && (th_id != mov_th_id) && (abort_cmd_executed == false))
                set_state(Tango::MOVING);
            else
                _status = StatusNotSet;
        }
        else
            _status = StatusNotSet;
    }
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::dev_state
 *
 *	description:	method to execute "State"
 *	This command gets the device state (stored in its <i>device_state</i> data member) and returns it to the caller.
 *
 * @return	State Code
 */
//+------------------------------------------------------------------
Tango::DevState MotorGroup::dev_state()
{
    Pool_ns::PoolGroupBaseDev::dev_state();
    DEBUG_STREAM << "MotorGroup::dev_state(): entering... !" << endl;

    if (pool_init_cmd == true)
        set_state(Tango::UNKNOWN);
    else
        update_state_from_ctrls();

    return get_state();
}

Pool_ns::CtrlGrp* MotorGroup::build_mot_ctrl(Pool_ns::ControllerPool &ctrl_ref)
{
    return new Pool_ns::CtrlGrp(ctrl_ref, this);
}

MotorGroup::IndMov* MotorGroup::build_motor(Pool_ns::MotorPool &m_ref)
{
    Pool_ns::ControllerPool &ctrl_ref = pool_dev->get_controller(m_ref.get_ctrl_id());

    int32_t ctrlgrp_idx;
    Pool_ns::CtrlGrp *ctrl_grp = NULL;
    try
    {
        ctrl_grp = &get_ctrl_grp_from_id(ctrl_ref.id, ctrlgrp_idx);
    }
    catch(Tango::DevFailed &e)
    {
        ctrl_grp = build_mot_ctrl(ctrl_ref);
        ctrlgrp_idx = implied_ctrls.size();
        implied_ctrls.push_back(ctrl_grp);
        implied_ctrls_sorted = implied_ctrls;
        sort(implied_ctrls_sorted.begin(), implied_ctrls_sorted.end(), Pool_ns::ictrl_id_cmp);
    }

    Motor_ns::Motor *mot_dev = pool_dev->get_motor_device(m_ref);
    IndMov *im = new IndMov(m_ref, ctrl_grp, mot_dev, get_id(), this);
    im->idx_in_grp = ind_elts.size();
    im->idx_in_ctrl = m_ref.get_axis();
    im->idx_in_ctrlgrp = ctrlgrp_idx; // not used (yet!)
    im->obj_proxy = new Tango::DeviceProxy(m_ref.get_full_name().c_str());
    im->obj_proxy->set_transparency_reconnection(true);

    return im;
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::build_grp
 *
 *	description:	Build from the user_group_elt property
 * 					value, information describing which motor
 * 					in the group belongs to group or to pseudo-motor
 */
//+------------------------------------------------------------------

void MotorGroup::build_grp()
{
    vector<Pool_ns::ElementId> mot_id_list;
    vector<Pool_ns::ElementId> mot_id_ctrl;

    mot_id_list.reserve(ind_elt_nb);
    mot_id_ctrl.reserve(ind_elt_nb);

    {
        Tango::AutoTangoMonitor atm(pool_dev);

        if(is_ghost())
        {
            Pool_ns::Pool::PoolElementTypeIt beg, end, it;
            pool_dev->get_all_physical_motor(beg, end);
            for(it = beg; it != end; ++it)
            {
                Pool_ns::MotorPool &motor = pool_dev->get_physical_motor(it->second);
                ind_elts.push_back(build_motor(motor));
                ind_elts_sorted = ind_elts;
                sort(ind_elts.begin(), ind_elts.end(), Pool_ns::ielt_id_cmp);
            }
            return;
        }
//
// Get all motor ID in a loop
//

        int32_t i;
        for (i = 0;i < ind_elt_nb;i++)
        {
            Pool_ns::MotorPool &motor = pool_dev->get_physical_motor(phys_group_elt[i]);
            mot_id_list.push_back(motor.get_id());
            mot_id_ctrl.push_back(motor.get_axis());
        }

//
// Get list of implied controller for this group
//
        for (i = 0;i < ind_elt_nb;i++)
        {
            Pool_ns::MotorPool &mot_ref = pool_dev->get_physical_motor(mot_id_list[i]);
            Motor_ns::Motor *mot_dev = pool_dev->get_motor_device(mot_ref);
            Pool_ns::ControllerPool &ctrl_ref = pool_dev->get_controller(mot_ref);
            Pool_ns::ElementId ct_id = ctrl_ref.id;

            Pool_ns::CtrlGrp *ctrl_ptr = NULL;
            if (implied_ctrls.empty() == true)
            {
                ctrl_ptr = new Pool_ns::CtrlGrp(ctrl_ref, this);
                implied_ctrls.push_back(ctrl_ptr);
                implied_ctrls_sorted = implied_ctrls;
                sort(implied_ctrls_sorted.begin(), implied_ctrls_sorted.end(), Pool_ns::ictrl_id_cmp);
            }
            else
            {
                vector<Pool_ns::CtrlGrp *>::iterator it;
                for (it = implied_ctrls.begin(); it != implied_ctrls.end(); ++it)
                {
                    Pool_ns::CtrlGrp *ctrl_grp = *it;
                    if (ctrl_grp->ctrl_id == ct_id)
                    {
                        ctrl_ptr = ctrl_grp;
                        break;
                    }
                }
                if (ctrl_ptr == NULL)
                {
                    ctrl_ptr = new Pool_ns::CtrlGrp(ctrl_ref, this);
                    implied_ctrls.push_back(ctrl_ptr);
                    implied_ctrls_sorted = implied_ctrls;
                    sort(implied_ctrls_sorted.begin(), implied_ctrls_sorted.end(), Pool_ns::ictrl_id_cmp);
                }
            }

//
// Build motor group info
//

            IndMov *im = new IndMov(mot_ref, ctrl_ptr, mot_dev, get_id(), this);
            im->idx_in_grp = i;
            im->idx_in_ctrl = mot_id_ctrl[i];
            im->idx_in_ctrlgrp = -1; // not used (yet!)
            Pool_ns::PoolElement *phys_elem = pool_dev->get_element(phys_group_elt[i]);
            im->obj_proxy = new Tango::DeviceProxy(phys_elem->get_name().c_str());
            im->obj_proxy->set_transparency_reconnection(true);

            std::vector<Tango::DevLong>::iterator ite = find(user_group_elt.begin(),user_group_elt.end(), im->id);

//
// If it is a motor directly used by the motor group, determine its index in the user array
//

            if(ite != user_group_elt.end())
                im->idx_in_usr = distance(user_group_elt.begin(),ite);
            else
                im->idx_in_usr = -1;

            ind_elts.push_back(im);
            ind_elts_sorted = ind_elts;
            sort(ind_elts.begin(), ind_elts.end(), Pool_ns::ielt_id_cmp);
        }
    }

//
// Allocate arrays to store motor pos.
//

    SAFE_DELETE_ARRAY(attr_Position_read);
    attr_Position_read = new double[pos_spectrum_dim_x];

    SAFE_DELETE_ARRAY(phys_mot_pos);
    phys_mot_pos = new double[ind_elt_nb];

    SAFE_DELETE_ARRAY(attr_Elements_read);
    attr_Elements_read = (usr_elt_nb > 0) ? new Tango::DevString[usr_elt_nb] : NULL;

    SAFE_DELETE_ARRAY(attr_Motors_read);
    attr_Motors_read = (motor_list.size() > 0) ? new Tango::DevString[motor_list.size()] : NULL;

    SAFE_DELETE_ARRAY(attr_MotorGroups_read);
    attr_MotorGroups_read = (motor_group_list.size() > 0) ? new Tango::DevString[motor_group_list.size()] : NULL;

    SAFE_DELETE_ARRAY(attr_PseudoMotors_read);
    attr_PseudoMotors_read = (pseudo_motor_list.size() > 0) ? new Tango::DevString[pseudo_motor_list.size()] : NULL;
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::build_grp_struct
 *
 *	description:	Build from the user_group_elt property
 * 					value, information describing which motor
 * 					in the group belongs to group or to pseudo-motor
 */
//+------------------------------------------------------------------

void MotorGroup::build_grp_struct()
{
    DEBUG_STREAM << "MotorGroup::build_grp_struct(): entering... for " << name() << endl;
    int32_t mot_idx = 0;
    int32_t idx_in_usr = 0;

    vector<string>::size_type nb_u_elt = user_group_elt.size();
    for (vector<string>::size_type loop = 0;loop < nb_u_elt;loop++)
    {
        if (find(motor_list.begin(),motor_list.end(),user_group_elt[loop]) != motor_list.end())
        {
            IndMov *ind_mov = static_cast<IndMov*>(ind_elts[mot_idx]);
            ind_mov->idx_in_usr = idx_in_usr;
            mot_idx++;
            idx_in_usr++;
            user_group_elt_type.push_back(Pool_ns::MOTOR);
            continue;
        }
        else if (find(motor_group_list.begin(),motor_group_list.end(),user_group_elt[loop]) != motor_group_list.end())
        {
            Pool_ns::MotorGroupPool &grp = pool_dev->get_motor_group(user_group_elt[loop]);
            MotorGroup_ns::MotorGroup *grp_dev = pool_dev->get_motor_group_device(grp);
            GrpInGrp tmp_grp(grp, grp_dev);
            tmp_grp.idx_in_usr = loop;
            tmp_grp.start_idx = mot_idx;
            mot_idx = mot_idx + tmp_grp.mot_nb;

            // Fix in the IndMov elements belonging to this motor group the idx_in_usr element
            for(int32_t i = 0; i < tmp_grp.mot_nb; i++)
            {
                IndMov *ind_mov = static_cast<IndMov*>(ind_elts[i + tmp_grp.start_idx]);
                ind_mov->idx_in_usr = idx_in_usr;
                idx_in_usr++;
            }

            grp_in_grp.push_back(tmp_grp);
            user_group_elt_type.push_back(Pool_ns::GROUP);

        }
        else
        {
            Pool_ns::PseudoMotorPool &psm = pool_dev->get_pseudo_motor(user_group_elt[loop]);
            PseudoMotor_ns::PseudoMotor *pm_dev = pool_dev->get_pseudo_motor_device(psm);
            PsmInGrp tmp_psm(psm, pm_dev);
            tmp_psm.mot_nb = psm.mot_elts.size();
            tmp_psm.idx_in_usr = idx_in_usr;
            idx_in_usr++;

            // Find the index of the first motor
            std::vector<Tango::DevLong>::iterator m_ite = find(phys_group_elt.begin(), phys_group_elt.end(), psm.mot_elts[0]);
            assert(m_ite != phys_group_elt.end());
            int32_t local_idx = distance(phys_group_elt.begin(), m_ite);
            tmp_psm.start_idx = local_idx;

 //
 // If this is the first pseudo motor which uses motors then the index can safely
 // increment. Otherwise, if it is using some motors that are already been used by
 // other pseudo motor in the same pseudo motor system, the index is not changed
 //
            if(local_idx == mot_idx)
                mot_idx = mot_idx + tmp_psm.mot_nb;

            psm_in_grp.push_back(tmp_psm);
            user_group_elt_type.push_back(Pool_ns::PSEUDO_MOTOR);
        }
    }

//
// Group pseudo motors by controller
//
    for(vector<PsmInGrp>::size_type psm_idx = 0; psm_idx < psm_in_grp.size(); psm_idx++)
    {
        PsmInGrp &psm = psm_in_grp[psm_idx];
        PseudoMotorController *curr_psm_ctrl = psm.dev->get_pm_ctrl();

        vector<PsmCtrlInGrp>::size_type ctrl_idx = 0;
        for(; ctrl_idx < psm_ctrls_in_grp.size(); ctrl_idx++)
        {
            if(psm_ctrls_in_grp[ctrl_idx].pool_psm_ctrl == curr_psm_ctrl)
                break;
        }

        // New pseudo motor controller
        if(ctrl_idx == psm_ctrls_in_grp.size())
        {
            PsmCtrlInGrp tmp_psm_ctrl(curr_psm_ctrl);
            Pool_ns::PseudoMotCtrlFiCa *fica =
                psm.dev->get_pm_fica_ptr();

            tmp_psm_ctrl.pm_count = fica->get_pseudo_motor_role_nb();
            tmp_psm_ctrl.mot_count = fica->get_motor_role_nb();
            // Fill the vector with -1
            tmp_psm_ctrl.psm_in_grp_idx.insert(tmp_psm_ctrl.psm_in_grp_idx.begin(),
                                               tmp_psm_ctrl.pm_count,-1);
            tmp_psm_ctrl.is_complete = true;
            tmp_psm_ctrl.mot_nb = psm.mot_nb;
            tmp_psm_ctrl.start_idx = psm.start_idx;

            psm_ctrls_in_grp.push_back(tmp_psm_ctrl);
        }

        int32_t role = psm.dev->get_axis();

        psm_ctrls_in_grp[ctrl_idx].psm_in_grp_idx[role-1] = psm_idx;

        if(psm_ctrls_in_grp[ctrl_idx].first_usr_psm == NULL)
        {
            psm_ctrls_in_grp[ctrl_idx].first_usr_psm = &psm;
        }

        psm.psm_ctrl_idx = ctrl_idx;
    }

//
// Determine which pseudo motor controllers have all pseudo motors included in this motor group.
// This is done for efficiency reasons
//
    vector<PsmCtrlInGrp>::iterator psm_ctrl_ite = psm_ctrls_in_grp.begin();
    for(;psm_ctrl_ite != psm_ctrls_in_grp.end(); psm_ctrl_ite++)
    {
        vector<int32_t> &psm_in_grp_idx = psm_ctrl_ite->psm_in_grp_idx;
        if( find(psm_in_grp_idx.begin(), psm_in_grp_idx.end(), -1) != psm_in_grp_idx.end() )
        {
            psm_ctrl_ite->is_complete = false;
        }
    }

    nb_psm_in_grp = psm_in_grp.size();
    nb_grp_in_grp = grp_in_grp.size();
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::from_phys_2_grp
 *
 *	description:	Build the array of motor position returned to user
 * 					If some pseudo-motor are involved in this group,
 * 					compute their positions from the motor physical
 * 					one.
 */
//+------------------------------------------------------------------

void MotorGroup::from_phys_2_grp()
{
    int32_t loop;

//
// If we don't have any pseudo-motor in this group,
// simply copy the motor position
//

    if (nb_psm_in_grp == 0)
    {
        for (loop = 0;loop < ind_elt_nb; ++loop)
            attr_Position_read[loop] = phys_mot_pos[loop];
    }
    else
    {
//
// Calculate all necessary pseudo motor positions
//
        for(vector<PsmCtrlInGrp>::size_type ctrl_idx = 0; ctrl_idx < psm_ctrls_in_grp.size(); ++ctrl_idx)
        {
            vector<double> phy_pos;
            PsmCtrlInGrp &psm_ctrl = psm_ctrls_in_grp[ctrl_idx];
            PseudoMotorController *ctrl = psm_ctrl.pool_psm_ctrl;
            int32_t start_idx = psm_ctrl.start_idx;
            int32_t mot_nb = psm_ctrl.mot_nb;

//
// For each controller build the list of involved physical motor positions
//
            for(int32_t mot_idx = start_idx; mot_idx < start_idx + mot_nb; mot_idx++)
            {
                phy_pos.push_back(phys_mot_pos[mot_idx]);
            }

//
// calculate the positions of all pseudo motors involved
//
            vector<double> pm_pos(psm_ctrl.pm_count);
            {
                AutoPythonGIL pl = AutoPythonGIL();
                ctrl->CalcAllPseudo(phy_pos, pm_pos);
            }

//
// store the calculated pseudo motor positions in the output buffer
//
            for(vector<int32_t>::size_type psm_idx = 0; psm_idx < psm_ctrl.psm_in_grp_idx.size(); psm_idx++)
            {
                int32_t psm_idx_in_grp = psm_ctrl.psm_in_grp_idx[psm_idx];

                if(psm_idx_in_grp == -1)
                    continue;

                PsmInGrp &psm = psm_in_grp[psm_idx_in_grp];
                int32_t psm_role = psm.dev->get_axis();
                attr_Position_read[psm.idx_in_usr] = pm_pos[psm_role-1];
                DEBUG_STREAM << "Storing in " << psm.pool_psm.name << "(idx = " << psm.idx_in_usr << ",role=" << psm_role << ") with value " << pm_pos[psm_role-1] << endl;
            }
        }

//
// store motor positions
//
        for (vector<Pool_ns::IndEltGrp*>::iterator ind_mov_it = ind_elts.begin();
             ind_mov_it != ind_elts.end(); ++ind_mov_it)
        {
            IndMov &m = *static_cast<IndMov*>(*ind_mov_it);
            if (m.idx_in_usr >= 0)
            {
                DEBUG_STREAM << "Storing usr_idx=" << m.idx_in_usr << " from idx in physical=" << m.idx_in_grp << endl;
                attr_Position_read[m.idx_in_usr] = phys_mot_pos[m.idx_in_grp];
            }
        }
    }
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::from_grp_2_phys
 *
 *	description:	Build the array of motor physical position from
 * 					the information sent by the caller
 */
//+------------------------------------------------------------------

void MotorGroup::from_grp_2_phys(const Tango::DevDouble *user_pos)
{
    int32_t loop;

//
// If we don't have any pseudo-motor in this group,
// simply copy the motor position
//

    if (nb_psm_in_grp == 0)
    {
        for (loop = 0;loop < ind_elt_nb;loop++)
            phys_mot_pos[loop] = user_pos[loop];

        if(nb_grp_in_grp > 0)
        {

//
// Get motor group positions
//

            for(unsigned long mg_idx = 0; mg_idx < grp_in_grp.size(); mg_idx++)
            {
                GrpInGrp &grp = grp_in_grp[mg_idx];
                for(long ll = 0;ll < grp.mot_nb;ll++)
                {
                    phys_mot_pos[grp.start_idx + ll] = user_pos[grp.idx_in_usr + ll];
                }
            }
        }
    }
    else
    {

//
// We are going to use the pseudo motor device proxy below so we check if the pool
// has already initialized all the proxy information
//

        pool_dev->create_proxies();

//
//
// For each pseudo motor simulate a write to check if limits are exceded
//

        DEBUG_STREAM << "checking pseudo motor limits" << endl;
        for(vector<PsmInGrp>::size_type psm_idx = 0; psm_idx < psm_in_grp.size(); psm_idx++)
        {
            PsmInGrp &psm = psm_in_grp[psm_idx];
            Pool_ns::PseudoMotorPool &psm_pool = psm.pool_psm;

            psm.dev->set_group_mov(true);
            double position = user_pos[psm.idx_in_usr];
            try
            {
                DEBUG_STREAM << "\tChecking psm " << psm_idx << " with pos=" << position << endl;
                Tango::DeviceAttribute attr("Position", position);
                pool_dev->get_element_proxy(psm_pool)->write_attribute(attr);
                psm.dev->set_group_mov(false);
            }
            catch(Tango::DevFailed e)
            {
                psm.dev->set_group_mov(false);
                throw e;
            }
        }

        DEBUG_STREAM << "from_grp_2_phys > starting to interate osm ctrls..." << endl;
        for (vector<PsmCtrlInGrp>::iterator ctrl_it = psm_ctrls_in_grp.begin();
             ctrl_it != psm_ctrls_in_grp.end(); ++ctrl_it)
        {
            PsmCtrlInGrp &psm_ctrl = *ctrl_it;
            PseudoMotorController *ctrl = psm_ctrl.pool_psm_ctrl;

            PsmInGrp *first_psm = psm_ctrl.first_usr_psm;
            assert(first_psm != NULL);

            vector<double> psm_pos(psm_ctrl.pm_count);

//
// For the pseudo controllers which we don't receive the pseudo motor positions from the user,
// they have to be calculated before, based on the current values of the motors which are involved
//

            if(psm_ctrl.is_complete == false)
            {
                DEBUG_STREAM << "psm ctrl in mg is not complete." << endl;

//
// Get the Motor group inside any of the pseudo motors in this controller and through it
// read the current physical motor positions of all motors involved
//

                DEBUG_STREAM << "read position for mg inside the psm" << endl;
                Tango::DeviceProxy *mg = first_psm->dev->get_motor_group_info().mg_proxy;

                vector<double> phy_pos;
                mg->read_attribute("Position") >> phy_pos;

//
// Calculate all pseudo positions
//

                DEBUG_STREAM << "calculate all old pseudo motor positions for psm ctrl" << endl;
                {
                    AutoPythonGIL pl = AutoPythonGIL();
                    ctrl->CalcAllPseudo(phy_pos,psm_pos);
                }
            }

//
// Fill the pseudo motor positions vector with the pseudo positions given by the user
//

            DEBUG_STREAM << "prepare psm position vector to send to psm ctrl" << endl;

            for(vector<int32_t>::size_type psm_ctrl_idx = 0; psm_ctrl_idx < psm_ctrl.psm_in_grp_idx.size(); psm_ctrl_idx++)
            {
                int32_t idx = psm_ctrl.psm_in_grp_idx[psm_ctrl_idx];

                if(idx == -1)
                    continue;

                PsmInGrp &psm = psm_in_grp[idx];
                int32_t role = psm.dev->get_axis();
                psm_pos[role-1] = user_pos[psm.idx_in_usr];
                DEBUG_STREAM << "\t user psm index=" << idx << ",role=" << role << " stored with value " << psm_pos[role-1] << endl;
            }

            DEBUG_STREAM << "calculate physical positions of motors that belong to the current psm controller" << endl;
            vector<double> phy_pos(psm_ctrl.mot_count);
            {
                AutoPythonGIL pl = AutoPythonGIL();
                ctrl->CalcAllPhysical(psm_pos,phy_pos);
            }

//
// Finally distribute the obtained motor positions in the output vector
//

            DEBUG_STREAM << "place the calculated physical positions in the correct place" << endl;
            for(int32_t idx = 0; idx < psm_ctrl.mot_nb; idx++)
            {
                phys_mot_pos[psm_ctrl.start_idx + idx] = phy_pos[idx];
            }
        }

//
// Get motor positions
//
        DEBUG_STREAM << "fill physical positions (if any)" << endl;
        for (vector<Pool_ns::IndEltGrp*>::iterator ind_mov_it = ind_elts.begin();
             ind_mov_it != ind_elts.end(); ++ind_mov_it)
        {
            IndMov &m = *static_cast<IndMov*>(*ind_mov_it);
            if(m.idx_in_usr >=0)
            {
                DEBUG_STREAM << "\tplacing physical motor from user index=" << m.idx_in_usr << "to physical=" << m.idx_in_grp << " with value=" << user_pos[m.idx_in_usr];
                phys_mot_pos[m.idx_in_grp] = user_pos[m.idx_in_usr];
            }
        }

//
// Get motor group positions
//
        DEBUG_STREAM << "fill motor group positions (if any)" << endl;
        for(vector<GrpInGrp>::size_type mg_idx = 0; mg_idx < grp_in_grp.size(); mg_idx++)
        {
            GrpInGrp &grp = grp_in_grp[mg_idx];
            for(int32_t ll = 0;ll < grp.mot_nb;ll++)
            {
                DEBUG_STREAM << "\tplacing physical motor (from mg) from user index=" << grp.idx_in_usr + ll << "to physical=" << grp.start_idx + ll << " with value=" << user_pos[grp.idx_in_usr + ll];
                phys_mot_pos[grp.start_idx + ll] = user_pos[grp.idx_in_usr + ll];
            }
        }
    }
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::add_motor_to_ghost_group
 *
 *	description:	Add a new motor to a group
 *
 *  arg(s) : In : mot_id : The motor identifier
 */
//+------------------------------------------------------------------

void MotorGroup::add_motor_to_ghost_group(Pool_ns::ElementId mot_id)
{
    DEBUG_STREAM << "MotorGroup::add_motor_to_group()"  << endl;

//
// Refuse to do anything if it is not for the ghost group
//

    if (!is_ghost())
    {
        Tango::Except::throw_exception((const char *)"Motor_ControllerFailed",
                                        (const char *)"This feature is available only for the ghost motor group",
                                        (const char *)"MotorGroup::add_motor_to_group");
    }

//
// Return if motor already in group
//

    std::vector<Tango::DevLong>::iterator ite;
    Pool_ns::MotorPool &mot_ref = pool_dev->get_physical_motor(mot_id);
    Motor_ns::Motor *mot_dev = pool_dev->get_motor_device(mot_ref);
    ite = find(phys_group_elt.begin(),phys_group_elt.end(),mot_id);
    if (ite != phys_group_elt.end())
        return;

    ind_elt_nb++;

    {
        Tango::AutoTangoMonitor atm(pool_dev);

//
// Get motor controller for this motor and eventually add it to
// the list of implied controller
//

        Pool_ns::ControllerPool &ctrl_ref = pool_dev->get_controller(mot_ref);

        Pool_ns::ElementId ct_id = ctrl_ref.id;

        Pool_ns::CtrlGrp *ctrl_ptr = NULL;
        if (implied_ctrls.empty() == true)
        {
            ctrl_ptr = new Pool_ns::CtrlGrp(ctrl_ref, this);
            implied_ctrls.push_back(ctrl_ptr);
            implied_ctrls_sorted = implied_ctrls;
            sort(implied_ctrls_sorted.begin(), implied_ctrls_sorted.end(), Pool_ns::ictrl_id_cmp);
        }
        else
        {
            for (vector<Pool_ns::CtrlGrp*>::size_type l = 0;l < implied_ctrls.size();l++)
            {
                if (implied_ctrls[l]->ctrl_id == ct_id)
                {
                    ctrl_ptr = implied_ctrls[l];
                    break;
                }
            }
            if (ctrl_ptr == NULL)
            {
                ctrl_ptr = new Pool_ns::CtrlGrp(ctrl_ref, this);
                implied_ctrls.push_back(ctrl_ptr);
                implied_ctrls_sorted = implied_ctrls;
                sort(implied_ctrls_sorted.begin(), implied_ctrls_sorted.end(), Pool_ns::ictrl_id_cmp);
            }
        }
//
// Build motor info for group
//
        IndMov *im = new IndMov(mot_ref, ctrl_ptr, mot_dev, get_id(), this);
        im->idx_in_grp = ind_elt_nb - 1;
        im->idx_in_ctrl = mot_ref.get_axis();
        im->obj_proxy = new Tango::DeviceProxy(mot_ref.name);
        im->obj_proxy->set_transparency_reconnection(true);

//
// Add motor to group in vector and its alias_name in phys_group_elt
//

        phys_group_elt.push_back(im->id);
        ind_elts.push_back(im);
        ind_elts_sorted = ind_elts;
        sort(ind_elts.begin(), ind_elts.end(), Pool_ns::ielt_id_cmp);
    }

//
// Add entry in the state array
//

    state_array.push_back(Tango::ON);

//
// Change arrays size to store motor pos.
//

    delete [] attr_Position_read;
    attr_Position_read = new double[pos_spectrum_dim_x];

    delete [] phys_mot_pos;
    phys_mot_pos = new double[ind_elt_nb];

}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::remove_motor_from_ghost_group
 *
 *	description:	Remove a motor from a group
 *
 *  arg(s) : In : mot_id : The motor identifier
 */
//+------------------------------------------------------------------

void MotorGroup::remove_motor_from_ghost_group(Pool_ns::ElementId del_mot_id)
{
    DEBUG_STREAM << "MotorGroup::remove_motor_from_group(), motor id = " << del_mot_id << endl;

//
// Refuse to do anything if it is not for the ghost group
//

    if (!is_ghost())
    {
        Tango::Except::throw_exception(
                (const char *)"Motor_CantRemoveMotor",
                (const char *)"This feature is available only for the ghost motor group",
                (const char *)"MotorGroup::remove_motor_from_group");
    }

    int32_t idx_in_array = 0;

    {
        Tango::AutoTangoMonitor atm(pool_dev);

//
// Find motor in group
//

        vector<Pool_ns::IndEltGrp*>::iterator ite;
        for (ite = ind_elts.begin();ite != ind_elts.end();++ite,++idx_in_array)
            if ((*ite)->id == del_mot_id)
                break;
        if (ite == ind_elts.end())
        {
            TangoSys_OMemStream o;
            o << "Motor with id " << del_mot_id << " is not a member of this group" << ends;

            Tango::Except::throw_exception(
                    (const char *)"Motor_CantRemoveMotor",
                    o.str(),
                    (const char *)"MotorGroup::remove_motor_from_group");
        }
        Pool_ns::IndEltGrp* elt = (*ite);
        Pool_ns::CtrlGrp *ctrl_grp = elt->ctrl_grp;
//
// Remove motor from group
//
        std::vector<Tango::DevLong>::iterator v_ite;
        assert(elt->id == phys_group_elt[idx_in_array]);
        v_ite = phys_group_elt.begin();
        advance(v_ite, idx_in_array);
        phys_group_elt.erase(v_ite);

        ind_elt_nb--;

//
// Remove from internal list
//
        ind_elts.erase(ite);
        SAFE_DELETE(elt);

//
// If the internal controller object no longer controls any element of this
// group then remove it
//
        if (ctrl_grp->channels.size() == 0)
        {
            vector<Pool_ns::CtrlGrp*>::iterator ctrl_ite =
                find(implied_ctrls.begin(), implied_ctrls.end(), ctrl_grp);
            implied_ctrls.erase(ctrl_ite);
            SAFE_DELETE(ctrl_grp);
        }
    }

//
// Remove entry in the state array
//

    if (state_array.size() != 0)
    {
        vector<Tango::DevState>::iterator state_ite = state_array.begin();
        advance(state_ite,idx_in_array);
        state_array.erase(state_ite);
    }

//
// Change arrays size to store motor pos.
//

    delete [] attr_Position_read;
    attr_Position_read = new double[pos_spectrum_dim_x];

    delete [] phys_mot_pos;
    phys_mot_pos = new double[ind_elt_nb];
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::update_motor_info
 *
 *	description:	Update motor info into the group
 *
 *  arg(s) : In : mot_id : The motor identifier
 */
//+------------------------------------------------------------------

void MotorGroup::update_motor_info(Pool_ns::ElementId upd_mot_id)
{
    DEBUG_STREAM << "MotorGroup::update_motor_info()"  << endl;

//
// Refuse to do anything if it is not for the ghost group
//

    if (!is_ghost())
    {
        Tango::Except::throw_exception((const char *)"Motor_CantUpdateMotor",
                                        (const char *)"This feature is available only for the ghost motor group",
                                        (const char *)"MotorGroup::update_motor_info");
    }

//
// Find motor in group
//

    vector<Pool_ns::IndEltGrp*>::iterator ite;
    for (ite = ind_elts.begin();ite != ind_elts.end();++ite)
    {
        Pool_ns::IndEltGrp *elt = *ite;
        if (elt->id == upd_mot_id)
            break;
    }
    if (ite == ind_elts.end())
    {
        TangoSys_OMemStream o;
        o << "Motor with id " << upd_mot_id << " is not a member of this group" << ends;

        Tango::Except::throw_exception((const char *)"Motor_CantUpdateMotor",
                                        o.str(),(const char *)"MotorGroup::update_motor_info");
    }

//
// Update its info
//
    unsigned long l;

    for(l = 0; l < ind_elts.size(); l++)
        delete ind_elts[l];
    ind_elts.clear();

    for(l = 0; l < implied_ctrls.size(); l++)
        delete implied_ctrls[l];
    implied_ctrls.clear();

    build_grp();
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::dev_status
 *
 *	description:	method to execute "Status"
 *	This command gets the device status (stored in its <i>device_status</i> data member) and returns it to the caller.
 *
 * @return	Status description
 *
 */
//+------------------------------------------------------------------
Tango::ConstDevString MotorGroup::dev_status()
{
    Tango::ConstDevString argout = Pool_ns::PoolGroupBaseDev::dev_status();
    DEBUG_STREAM << "MotorGroup::dev_status(): entering... !" << endl;

    //	Add your own code to control device here
    tmp_status = argout;
    Tango::DevState sta = get_state();

//
// If the motor is in FAULT, it could be because the ctrl is not OK.
// Otherwise, checks if the controller send an error string
//

    if (sta == Tango::FAULT)
    {
        vector<Pool_ns::CtrlGrp*>::iterator impl_ctrl_ite;
        MotorController *mc;
        for (impl_ctrl_ite = implied_ctrls.begin();impl_ctrl_ite != implied_ctrls.end();++impl_ctrl_ite)
        {
            Pool_ns::ControllerPool *cp = (*impl_ctrl_ite)->ct;
            mc = static_cast<MotorController *>(cp->get_controller());
            if ((cp->ctrl_class_built == false) || (mc == NULL))
            {
                tmp_status = tmp_status + "\nThe controller object (" + cp->name + ") used by some motor(s) in this group is not initialized";
            }
        }
    }

    argout = tmp_status.c_str();
    return argout;
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::State_all_ind
 *
 *	description:	Get each motor state
 */
//+------------------------------------------------------------------

void MotorGroup::State_all_ind(vector<Controller *> &failed_ctrls)
{
    vector<Controller *>::iterator pos;
    Controller *ctrl;

    for (long loop = 0;loop < ind_elt_nb;loop++)
    {
        IndMov *ind_mov = static_cast<IndMov*>(ind_elts[loop]);
        Motor_ns::Motor *mot_dev = ind_mov->get_motor_device();

        if(mot_dev->should_be_in_fault() == true)
        {
            mot_dev->set_state(Tango::FAULT);
        }
        else
        {
            try
            {
                MotorController::MotorState mi;
                Pool_ns::ControllerPool *cp = ind_mov->ctrl_grp->ct;
                ctrl = static_cast<MotorController *>(cp->get_controller());

                if (ctrl != NULL)
                {
                    if (failed_ctrls.empty() != true)
                    {
                        pos = find(failed_ctrls.begin(),failed_ctrls.end(),ctrl);
                        if (pos != failed_ctrls.end())
                        {
                            WARN_STREAM << "MotorGroup::State_all_ind: there are failed controllers for " << ind_mov->name << endl;
                            mot_dev->set_state(Tango::UNKNOWN);
                            state_array[loop] = Tango::UNKNOWN;
                            continue;
                        }
                    }

                    if (ind_mov->atm_ptr == NULL)
                    {
                        WARN_STREAM << "MotorGroup::State_all_ind: AutoTangoMonitor for " << ind_mov->name << " is NULL" << endl;
                        mot_dev->set_state(Tango::UNKNOWN);
                        state_array[loop] = Tango::UNKNOWN;
                        continue;
                    }
                    ctrl->StateOne(ind_mov->idx_in_ctrl,&mi);
                    mot_dev->set_motor_state_from_group(mi);
                }
                else
                    mot_dev->set_state(Tango::FAULT);
            }
            catch (Tango::DevFailed &e)
            {
                mot_dev->set_state(Tango::UNKNOWN);
            }
        }
        state_array[loop] =  mot_dev->get_state();
    }
}

void MotorGroup::State_ctrl_ind(Pool_ns::CtrlGrp *ctrl_grp, vector<Controller *> &failed_ctrls)
{
    std::map<Pool_ns::ElementId, Pool_ns::IndEltGrp *>::iterator
        elts_it  = ctrl_grp->channels.begin(),
        elts_end = ctrl_grp->channels.end();

    Pool_ns::ControllerPool &cp = *ctrl_grp->ct;
    Controller *ctrl = cp.get_controller();

    if(ctrl == NULL)
    {
        for(;elts_it != elts_end; ++elts_it)
        {
            Pool_ns::IndEltGrp &elt = *(elts_it->second);
            state_array[elt.idx_in_grp] = Tango::FAULT;
            elt.get_device()->set_state(Tango::FAULT);
        }
        return;
    }

    if (!failed_ctrls.empty() &&
        (find(failed_ctrls.begin(), failed_ctrls.end(), ctrl) != failed_ctrls.end()))
    {
        for(;elts_it != elts_end; ++elts_it)
        {
            Pool_ns::IndEltGrp &elt = *(elts_it->second);
            state_array[elt.idx_in_grp] = Tango::UNKNOWN;
            elt.get_device()->set_state(Tango::UNKNOWN);
        }
        return;
    }

    for(int32_t idx = 0; elts_it != elts_end; ++elts_it, ++idx)
    {
        IndMov &elt = *static_cast<IndMov*>(elts_it->second);
        Motor_ns::Motor *dev = elt.get_motor_device();
        int32_t elt_idx = elt.idx_in_grp;

        try
        {
            MotorController::MotorState mi;

            if (elt.atm_ptr == NULL)
            {
                dev->set_state(Tango::UNKNOWN);
                state_array[elt_idx] = Tango::UNKNOWN;
                continue;
            }

            ctrl->StateOne(elt.idx_in_ctrl, &mi);
            dev->set_motor_state_from_group(mi);

        }
        catch (Tango::DevFailed &e)
        {
            dev->set_state(Tango::UNKNOWN);
        }
        state_array[idx] = dev->get_state();
    }
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::get_ind_mov_from_id
 *
 *	description: Obtains the IndMov motor structure for the given
 *               motor id
 *
 * @return A reference to an IndMov motor data structure for the
 *         given motor id
 */
//+------------------------------------------------------------------

MotorGroup::IndMov &MotorGroup::get_ind_mov_from_id(Pool_ns::ElementId id)
{
    return static_cast<IndMov&>(get_ind_elt_from_id(id));
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::get_ind_mov_from_name
 *
 *	description: Obtains the IndMov motor structure for the given
 *               motor name
 *
 * @return A reference to an IndMov motor data structure for the
 *         given motor name
 */
//+------------------------------------------------------------------

MotorGroup::IndMov &MotorGroup::get_ind_mov_from_name(string &name)
{
    return static_cast<IndMov&>(get_ind_elt_from_name(name));
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::get_psm_from_name
 *
 *	description: Obtains the PsmInGrp pseudo motor structure for
 *               the given motor name
 *
 * @return A reference to an PsmInGrp pseudo motor data structure
 *         for the given pseudo motor name
 */
//+------------------------------------------------------------------

MotorGroup::PsmInGrp &MotorGroup::get_psm_from_name(string &name)
{
    vector<PsmInGrp>::iterator psm_ite = psm_in_grp.begin();
    for(; psm_ite != psm_in_grp.end(); psm_ite++)
    {
        if(psm_ite->psm_alias == name)
            break;
    }

    if (psm_ite == psm_in_grp.end())
    {
        TangoSys_OMemStream o;
        o << "No PsmInGrp with name " << name << " found in Motor group pseudo motor list" << ends;

        Tango::Except::throw_exception((const char *)"Pool_BadArgument",o.str(),
                                       (const char *)"MotorGroup::get_psm_from_name");
    }
    return *psm_ite;
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::get_grp_from_id
 *
 *	description: Obtains the GrpInGrp group structure for the given
 *               motor group id
 *
 * @return A reference to an GrpInGrp group data structure for the
 *         given motor group id
 */
//+------------------------------------------------------------------

MotorGroup::GrpInGrp &MotorGroup::get_grp_from_id(Pool_ns::ElementId id)
{
    vector<GrpInGrp>::iterator grp_ite = grp_in_grp.begin();
    for(; grp_ite != grp_in_grp.end(); grp_ite++)
    {
        if(grp_ite->grp_id == id)
            break;
    }

    if (grp_ite == grp_in_grp.end())
    {
        TangoSys_OMemStream o;
        o << "No GrpInGrp with ID " << id << " found in Motor group motor group list" << ends;

        Tango::Except::throw_exception((const char *)"Pool_BadArgument",o.str(),
                                       (const char *)"MotorGroup::get_grp_from_id");
    }
    return *grp_ite;
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::get_grp_from_name
 *
 *	description: Obtains the GrpInGrp group structure for the given
 *               group name
 *
 * @return A reference to an GrpInGrp group data structure for the
 *         given group name
 */
//+------------------------------------------------------------------

MotorGroup::GrpInGrp &MotorGroup::get_grp_from_name(string &name)
{
    vector<GrpInGrp>::iterator grp_ite = grp_in_grp.begin();
    for(; grp_ite != grp_in_grp.end(); grp_ite++)
    {
        if(grp_ite->pool_grp.name == name)
            break;
    }

    if (grp_ite == grp_in_grp.end())
    {
        TangoSys_OMemStream o;
        o << "No GrpInGrp with name " << name << " found in Motor group motor group list" << ends;

        Tango::Except::throw_exception((const char *)"Pool_BadArgument",o.str(),
                                       (const char *)"MotorGroup::get_grp_from_name");
    }
    return *grp_ite;
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::handle_temporary_siblings
//
// description : 	should be invoked by the ghost motor group periodically
//                  to manage the temporary siblings
//
//-----------------------------------------------------------------------------

void MotorGroup::handle_temporary_siblings()
{
    pool_dev->handle_tmp_motor_groups();
}


///////////////////////////////////////////////////
// E L E M E N T S
///////////////////////////////////////////////////

MotorGroup::IndMov::IndMov(Pool_ns::MotorPool &ref, Pool_ns::CtrlGrp *ctrl_ptr,
                           Tango::Device_4Impl *device, Pool_ns::ElementId grp,
                           Tango::Device_4Impl *logger /* = NULL*/):
    Pool_ns::IndEltGrp(ref, ctrl_ptr, device, grp, logger), idx_in_grp(-1),
    idx_in_usr(-1)
{}

Pool_ns::MotorPool *
MotorGroup::IndMov::get_motor()
{
    return static_cast<Pool_ns::MotorPool*>(pe);
}

Motor_ns::Motor *
MotorGroup::IndMov::get_motor_device()
{
    return static_cast<Motor_ns::Motor*>(dev);
}


MotorGroup::GrpInGrp::GrpInGrp(Pool_ns::MotorGroupPool &ref, MotorGroup *mg):
    grp_id(ref.id),pool_grp(ref),dev(mg)
{
    mot_nb=ref.mot_ids.size();
    usr_elts_nb = ref.group_elts.size();
    pos_len = mg->pos_spectrum_dim_x;
}

MotorGroup::GrpInGrp &
MotorGroup::GrpInGrp::operator=(const MotorGroup::GrpInGrp &rhs)
{
    grp_id=rhs.grp_id;
    pool_grp=rhs.pool_grp;
    mot_nb=rhs.mot_nb;
    usr_elts_nb = rhs.usr_elts_nb;
    pos_len = rhs.pos_len;
    start_idx=rhs.start_idx;
    idx_in_usr=rhs.idx_in_usr;
    return *this;
}

MotorGroup::PsmInGrp(Pool_ns::PseudoMotorPool &ref,
                     PseudoMotor_ns::PseudoMotor *pm_dev):
    pool_psm(ref),dev(pm_dev),psm_alias(ref.name)
{}

MotorGroup::PsmInGrp &
MotorGroup::PsmInGrp::operator=(const MotorGroup::PsmInGrp &rhs)
{
    mot_nb=rhs.mot_nb;
    start_idx=rhs.start_idx;
    idx_in_usr=rhs.idx_in_usr;
    psm_ctrl_idx=rhs.psm_ctrl_idx;
    pool_psm=rhs.pool_psm;
    psm_alias=rhs.psm_alias;
    return *this;
}
}	//	namespace
