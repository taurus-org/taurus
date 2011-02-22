//+=============================================================================
//
// file :         Pool.cpp
//
// description :  C++ source for the Pool and its commands.
//                The class is derived from Device. It represents the
//                CORBA servant object which will be accessed from the
//                network. All commands which can be executed on the
//                Pool are implemented in this file.
//
// project :      TANGO Device Server
//
// $Author$
//
// $Revision$
//
// $Log$
// Revision 1.120  2007/09/07 15:00:07  tcoutinho
// safety commit
//
// Revision 1.119  2007/08/30 12:40:39  tcoutinho
// - changes to support Pseudo counters.
//
// Revision 1.118  2007/08/24 15:55:26  tcoutinho
// safety weekend commit
//
// Revision 1.117  2007/08/23 10:32:43  tcoutinho
// - basic pseudo counter check
// - some fixes regarding pseudo motors
//
// Revision 1.116  2007/08/20 06:37:32  tcoutinho
// development commit
//
// Revision 1.115  2007/08/17 13:07:30  tcoutinho
// - pseudo motor restructure
// - pool base dev class restructure
// - initial commit for pseudo counters
//
// Revision 1.114  2007/08/08 08:47:55  tcoutinho
// Fix bug 18 : CreateController should be a one step operation
//
// Revision 1.113  2007/08/07 09:54:50  tcoutinho
// Small code changes
//
// Revision 1.112  2007/08/01 14:07:18  tcoutinho
// - bug fix returning null deviceproxy
// - prevent python errors by activating python lock
//
// Revision 1.111  2007/07/30 11:00:59  tcoutinho
// Fix bug 5 : Additional information for controllers
//
// Revision 1.110  2007/07/26 10:25:15  tcoutinho
// - Fix bug 1 :  Automatic temporary MotorGroup/MeasurementGroup deletion
//
// Revision 1.109  2007/07/17 11:41:57  tcoutinho
// replaced comunication with communication
//
// Revision 1.108  2007/07/16 11:00:24  tcoutinho
// - fix problem with communication controller information
// - fix problem reloading python modules
//
// Revision 1.107  2007/07/12 13:13:33  tcoutinho
// - added poolapi features
//
// Revision 1.106  2007/07/05 13:18:04  tcoutinho
// bug solve commit
//
// Revision 1.105  2007/07/05 13:13:17  tcoutinho
// development commit
//
// Revision 1.104  2007/07/04 15:06:38  tcoutinho
// first commit with stable Pool API
//
// Revision 1.103  2007/07/02 14:46:37  tcoutinho
// first stable comunication channel commit
//
// Revision 1.102  2007/06/28 16:22:37  tcoutinho
// safety commit during comunication channels development
//
// Revision 1.101  2007/06/28 07:15:34  tcoutinho
// safety commit during comunication channels development
//
// Revision 1.100  2007/06/27 10:24:45  tcoutinho
// scond commit for comuncation channels. Added command/attribute skeleton with pogo
//
// Revision 1.99  2007/06/13 15:18:58  etaurel
// - Fix memory leak
//
// Revision 1.98  2007/05/30 15:02:07  etaurel
// - Add init of the boolean used to inform ghost groups of an Init
// command being executed
// - Add init of a "language" data in the ReloadCtrl code command
//
// Revision 1.97  2007/05/17 07:06:37  etaurel
// - Use some new methods defined in Tango to create/delete device
//
// Revision 1.96  2007/05/15 15:02:41  tcoutinho
// - fix bugs
//
// Revision 1.95  2007/05/11 08:07:48  tcoutinho
// - added new propertie to allow different sleep time in CounterTimer
// - added new property to allow sleep time in 0D experiment channel
//
// Revision 1.94  2007/05/07 10:13:39  tcoutinho
// - small changes to 0D channel classes
// - fix bug in delete experiment channel
//
// Revision 1.93  2007/05/07 09:47:51  etaurel
// - Small changes for better 64 bits portability
//
// Revision 1.92  2007/04/30 15:47:05  tcoutinho
// - new attribute "Channels"
// - new device property "Channel_List"
// - when add/remove channel, pool sends a change event on the MeasurementGroupList
//
// Revision 1.91  2007/04/30 14:51:20  tcoutinho
// - make possible to Add/Remove elements on motorgroup that are part of other motor group(s)
//
// Revision 1.90  2007/04/26 08:24:57  tcoutinho
// - safe commit
//
// Revision 1.89  2007/04/23 15:23:06  tcoutinho
// - changes according to Sardana metting 26-03-2007: ActiveMeasurementGroup attribute became obsolete
//
// Revision 1.88  2007/03/02 16:34:27  tcoutinho
// - fix bugs with measurement group - event related, attribute quality, active measurement group management, etc
//
// Revision 1.87  2007/03/01 13:12:17  tcoutinho
// - measurement group event related fixes
//
// Revision 1.86  2007/02/28 16:21:52  tcoutinho
// - support for 0D channels
// - basic fixes after running first battery of tests on measurement group
//
// Revision 1.85  2007/02/26 09:53:00  tcoutinho
// - Introduction of properties for defult abs_change values in measurement group with fix
//
// Revision 1.84  2007/02/26 09:46:04  tcoutinho
// - Introduction of properties for defult abs_change values in measurement group
//
// Revision 1.83  2007/02/22 12:02:00  tcoutinho
// - added support for ghost measurement group
// - added support for measurement group in init/reload controller operations
// - added support of internal events on measurement group
//
// Revision 1.82  2007/02/16 09:59:57  tcoutinho
// - fix memory leak related with Active measurement group attribute
//
// Revision 1.81  2007/02/14 11:18:27  tcoutinho
// - fix bug on motorgroup when initcontroller is called
//
// Revision 1.80  2007/02/13 14:39:43  tcoutinho
// - fix bug in motor group when a motor or controller are recreated due to an InitController command
//
// Revision 1.79  2007/02/08 08:51:14  etaurel
// - Many changes. I don't remember the list
//
// Revision 1.78  2007/02/06 09:41:03  tcoutinho
// - added MeasurementGroup
//
// Revision 1.77  2007/01/26 08:36:47  etaurel
// - We now have a first release of ZeroDController
//
// Revision 1.76  2007/01/23 08:27:22  tcoutinho
// - fix some pm bugs found with the test procedure
// - added internal event for MotionEnded
//
// Revision 1.75  2007/01/17 09:38:14  tcoutinho
// - internal events bug fix.
//
// Revision 1.74  2007/01/16 14:32:21  etaurel
// - Coomit after a first release with CT
//
// Revision 1.73  2007/01/05 15:02:37  etaurel
// - First implementation of the Counter Timer class
//
// Revision 1.72  2007/01/05 13:03:37  tcoutinho
// -changes to internal event mechanism
// -support for gcc 4.1.1 compilation without errors
//
// Revision 1.71  2007/01/04 11:55:04  etaurel
// - Added the CounterTimer controller
//
// Revision 1.70  2006/12/28 15:36:58  etaurel
// - Fire events also on the motor limit_switches attribute
// - Throw events even in simulation mode
// - Mange motor position limit switches dependant of the offset attribute
//
// Revision 1.69  2006/12/20 10:23:47  tcoutinho
// - changes to support internal event propagation
// - bug fix in motor groups containing other motor groups or pseudo motors
//
// Revision 1.68  2006/12/18 11:37:09  etaurel
// - Features are only boolean values invisible from the external world
// - ExtraFeature becomes ExtraAttribute with data type of the old features
//
// Revision 1.67  2006/12/12 11:09:17  tcoutinho
// - support for pseudo motors and motor groups in a motor group
//
// Revision 1.66  2006/12/01 07:57:58  etaurel
// - Change a DEBUG message in the read_controllerClassList() method which was confusing
//
// Revision 1.65  2006/11/24 08:49:04  tcoutinho
// - changes to support pseudo motors in motor groups
//
// Revision 1.64  2006/11/23 11:46:37  tcoutinho
// - delete_pseudo_motor now additionally checks if it belongs to a motor group
//
// Revision 1.63  2006/11/21 14:39:55  tcoutinho
// bug fix
//
// Revision 1.62  2006/11/20 14:32:43  etaurel
// - Add ghost group and event on motor group position attribute
//
// Revision 1.61  2006/11/07 14:57:08  etaurel
// - Now, the pool really supports different kind of controllers (cpp and py)
//
// Revision 1.60  2006/11/06 13:23:16  tcoutinho
// - changed PseudoMotor interface. Now all methods require Python file name (with extension) as one parameter and a class name as a second paramenter
//
// Revision 1.59  2006/11/03 17:04:49  tcoutinho
// - read_PseudoMotorClassList now returns a format consistent with read_ControllerClassList
//
// Revision 1.58  2006/11/03 15:48:59  etaurel
// - Miscellaneous changes that I don't remember
//
// Revision 1.57  2006/10/30 11:37:18  etaurel
// - Some changes in the motor init sequence
//
// Revision 1.56  2006/10/27 14:43:02  etaurel
// - New management of the MaxDevice stuff
// - SendToCtrl cmd added
// - Some bug fixed in prop management
//
// Revision 1.55  2006/10/27 14:02:19  tcoutinho
// added support for class level properties in the Database
//
// Revision 1.54  2006/10/25 16:00:42  etaurel
// - The updated test suite is now running fine
//
// Revision 1.53  2006/10/25 10:04:30  etaurel
// - Complete implementation of the ReloadControllerCode command
// - Handle end of movment when reading position in polling mode
//
// Revision 1.52  2006/10/24 14:50:52  etaurel
// - The test suite is now back into full success
//
// Revision 1.51  2006/10/23 15:12:35  etaurel
// - Fix memory leak in several places
//
// Revision 1.50  2006/10/23 13:36:57  etaurel
// - First implementation of controller properties for CPP controller
//
// Revision 1.49  2006/10/20 15:37:30  etaurel
// - First release with GetControllerInfo command supported and with
// controller properties
//
// Revision 1.48  2006/10/17 14:28:09  tcoutinho
// bug fixes on properties
//
// Revision 1.47  2006/10/16 16:11:53  tcoutinho
// fix bug on pseudo motor creation
//
// Revision 1.46  2006/10/06 15:41:03  tcoutinho
// bug fixes: - error report in GetPseudoMotorInfo.
//                 - missed instatiation of pseudo_proxy in the PseudoMotorPool structure.
//
// Revision 1.45  2006/10/06 13:28:24  tcoutinho
// changed info command names, added properties functionality
//
// Revision 1.44  2006/10/05 14:53:32  etaurel
// - Test suite of motor controller features is now working
//
// Revision 1.43  2006/10/02 09:19:11  etaurel
// - Motor controller now supports extra features (both CPP and Python)
//
// Revision 1.42  2006/09/29 12:51:16  tcoutinho
// *** empty log message ***
//
// Revision 1.41  2006/09/28 09:22:24  etaurel
// - End of the ControllerClassList attribute implementation
//
// Revision 1.40  2006/09/27 15:15:49  etaurel
// - ExternalFile and CtrlFile has been splitted in several classes:
//   ExternalFile, CppCtrlFile, PyExternalFile and PyCtrlFile
//
// Revision 1.39  2006/09/25 15:27:30  tcoutinho
// python memory leak fix
//
// Revision 1.38  2006/09/22 15:31:01  etaurel
// - Miscellaneous changes
//
// Revision 1.37  2006/09/22 07:57:07  tcoutinho
// - Changes to the python in xxxFile classes
//
// Revision 1.36  2006/09/21 12:44:41  tcoutinho
// - python path changes
//
// Revision 1.35  2006/09/21 10:20:53  etaurel
// - The motor group do not ID any more
//
// Revision 1.34  2006/09/21 07:25:57  etaurel
// - Changes due to the removal of Motor ID in the Tango interface
//
// Revision 1.33  2006/09/20 15:59:21  tcoutinho
// pseudo motor API changed
//
// Revision 1.32  2006/09/20 13:11:11  etaurel
// - For the user point of view, the controller does not have ID any more.
// We are now using the controller instance name (uniq) to give them a name
//
// Revision 1.31  2006/09/19 15:57:03  tcoutinho
// get_pseudo_path fix
//
// Revision 1.30  2006/09/19 13:57:35  tcoutinho
// pseudo motor with test procedure clear.
//
// Revision 1.29  2006/09/19 09:57:12  etaurel
// - Commit after the controller, motor and motor_group test sequences works after the merge
//
// Revision 1.28  2006/09/19 07:24:32  tcoutinho
// - changes to make pseudo motor interface homogenous with the rest of the Pool
//
// Revision 1.27  2006/09/18 10:32:21  etaurel
// - Commit after merge with pseudo-motor branch
//
// Revision 1.11.2.9  2006/09/15 13:27:43  tcoutinho
// pseudo changes to reload pseudo code method
//
// Revision 1.11.2.8  2006/09/12 15:44:46  tcoutinho
// the pseudo motor at version 2.1
//
// Revision 1.11.2.7  2006/08/22 08:50:49  tcoutinho
// the pseudo motor at version 2.1
//
// Revision 1.11.2.6  2006/08/03 12:10:33  tcoutinho
// Pseudo Motor after first success in tests.
//
// Revision 1.11.2.5  2006/07/10 09:52:43  tcoutinho
// development
//
// Revision 1.11.2.4  2006/07/03 12:44:34  tcoutinho
// pseudo motor basic operations on the pool done as well as initial python support
//
// Revision 1.11.2.3  2006/06/27 09:26:28  tcoutinho
// commit before adding python pseudo function support to pseudo motors
//
// Revision 1.11.2.2  2006/05/23 14:29:56  tcoutinho
// minor changes
//
// Revision 1.11.2.1  2006/05/23 08:54:59  tcoutinho
// initial pseudo motor changes
//
// Revision 1.13  2006/05/23 07:31:29  tcoutinho
// Initial addons for Pseudo Motor.
//
// Revision 1.12  2006/05/22 09:46:17  tcoutinho
// Initial addons for Pseudo Motor.
//
// Revision 1.11  2006/04/27 07:29:42  etaurel
// - Many changes after the travel to Boston
//
// Revision 1.10  2006/03/29 07:08:59  etaurel
// - Added motor group features
//
// Revision 1.9  2006/03/27 12:52:32  etaurel
// - Commit before adding MotorGroup class
//
// Revision 1.8  2006/03/20 08:25:52  etaurel
// - Commit changes before changing the Motor interface
//
// Revision 1.7  2006/03/17 13:39:53  etaurel
// - Before modifying commands
//
// Revision 1.6  2006/03/16 08:05:45  etaurel
// - Added code for the ControllerCode load and unload commands
// - Test and debug InnitController cmd with motor attached to the controller
//
// Revision 1.5  2006/03/14 15:08:51  etaurel
// - Send a Init command to motor device after a successfull InitController command on a controller
//
// Revision 1.4  2006/03/14 14:54:09  etaurel
// - Again new changes in the internal structure
//
// Revision 1.3  2006/03/14 08:44:06  etaurel
// - Change the orders of the CreateController command arguments
//
// Revision 1.2  2006/03/14 08:25:10  etaurel
// - Change the way objects are aorganized within the pool device
//
// Revision 1.1.1.1  2006/03/10 13:40:57  etaurel
// Initial import
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
//  Command's name          |  Method's name
//	----------------------------------------
//  State                   |  dev_state()
//  Status                  |  dev_status()
//  CreateController        |  create_controller()
//  CreateExpChannel        |  create_exp_channel()
//  CreateMotor             |  create_motor()
//  CreateMotorGroup        |  create_motor_group()
//  DeleteController        |  delete_controller()
//  DeleteExpChannel        |  delete_exp_channel()
//  DeleteMotor             |  delete_motor()
//  DeleteMotorGroup        |  delete_motor_group()
//  DeletePseudoMotor       |  delete_pseudo_motor()
//  GetControllerInfo       |  get_controller_info()
//  InitController          |  init_controller()
//  ReloadControllerCode    |  reload_controller_code()
//  SendToController        |  send_to_controller()
//  CreateMeasurementGroup  |  create_measurement_group()
//  DeleteMeasurementGroup  |  delete_measurement_group()
//  CreateComChannel        |  create_com_channel()
//  DeleteComChannel        |  delete_com_channel()
//  GetControllerInfoEx     |  get_controller_info_ex()
//  DeletePseudoCounter     |  delete_pseudo_counter()
//  GetFile                 |  get_file()
//  PutFile                 |  put_file()
//  CreateIORegister        |  create_ioregister()
//  DeleteIORegister        |  delete_ioregister()
//  CreateElement           |  create_element()
//  DeleteElement           |  delete_element()
//  RenameElement           |  rename_element()
//
//===================================================================

#include "CtrlFiCa.h"
#include <tango.h>
#include <eventsupplier.h>
#include "Pool.h"
#include "PoolClass.h"
#include "PoolUtil.h"
#include "CppMotCtrlFile.h"

#include <algorithm>
#include <ltdl.h>
#include <functional>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

#include <pool/MotCtrl.h>

namespace Pool_ns
{

//+----------------------------------------------------------------------------
//
// method : 		Pool::Pool(string &s)
//
// description : 	constructor for simulated Pool
//
// in : - cl : Pointer to the DeviceClass object
//      - s : Device name
//
//-----------------------------------------------------------------------------
Pool::Pool(Tango::DeviceClass *cl,string &s)
:Tango::Device_4Impl(cl,s.c_str()), Pool_ns::DevicePool(new TangoThrower)
{
    init_cmd = false;
    init_device();
}

Pool::Pool(Tango::DeviceClass *cl,const char *s)
:Tango::Device_4Impl(cl,s), Pool_ns::DevicePool(new TangoThrower)
{
    init_cmd = false;
    init_device();
}

Pool::Pool(Tango::DeviceClass *cl,const char *s,const char *d)
:Tango::Device_4Impl(cl,s,d), Pool_ns::DevicePool(new TangoThrower)
{
    init_cmd = false;
    init_device();
}

Pool::~Pool()
{
    delete_device();
}

//+----------------------------------------------------------------------------
//
// method : 		Pool::delete_device()
//
// description : 	will be called at device destruction or at init command.
//
//-----------------------------------------------------------------------------
void Pool::delete_device()
{
    //	Delete device's allocated object

//
// Clear ctrl info vector
//
    ctrl_info.clear();

//
// Get ghost groups (motor and measurement) to inform them that we invalidate
// pool object in case a polling arrive while the Pool device init command
// is being executed
//

    MotorGroup_ns::MotorGroup *motor_ghost_ptr;
    MeasurementGroup_ns::MeasurementGroup *meas_ghost_ptr;

    try
    {
        motor_ghost_ptr = get_ghost_motor_group_ptr();
        motor_ghost_ptr->pool_init_cmd = true;
        meas_ghost_ptr = get_ghost_measurement_group_ptr();
        meas_ghost_ptr->pool_init_cmd = true;
    }
    catch (Tango::DevFailed &e) {}

//
// Mark all motors with controller code offline because
// we will delete all controllers objects
// But before, suicide them...
//

    DEBUG_STREAM << "Cleaning physical motor data (" << get_physical_motor_nb() << ")...";
    for (PoolElementTypeIt elem_it = element_types.lower_bound(MOTOR_ELEM);
         elem_it != element_types.upper_bound(MOTOR_ELEM); ++elem_it)
    {
        Motor_ns::Motor *mot = get_motor_device(elem_it->second);
        
        Tango::AutoTangoMonitor atm(mot);
        mot->suicide();
        mot->ctrl_offline();
    }
    remove_physical_motors();
    
//
// Mark all pseudo motors with controller code offline because
// we will delete all controllers objects
//

    DEBUG_STREAM << "Cleaning pseudo motor data (" << get_pseudo_motor_nb() << ")...";
    for (PoolElementTypeIt elem_it = element_types.lower_bound(PSEUDO_MOTOR_ELEM);
         elem_it != element_types.upper_bound(PSEUDO_MOTOR_ELEM); ++elem_it)
    {
        PseudoMotor_ns::PseudoMotor *pm = get_pseudo_motor_device(elem_it->second);

        Tango::AutoTangoMonitor atm(pm);
        pm->suicide();
        pm->ctrl_offline();
    }

//
// Mark all pseudo counters with controller code offline because
// we will delete all controllers objects
//

    DEBUG_STREAM << "Cleaning pseudo counter data (" << get_pseudo_counter_nb() << ")...";
    for (PoolElementTypeIt elem_it = element_types.lower_bound(PSEUDO_COUNTER_ELEM);
         elem_it != element_types.upper_bound(PSEUDO_COUNTER_ELEM); ++elem_it)
    {
        PseudoCounter_ns::PseudoCounter *pc = get_pseudo_counter_device(elem_it->second);

        Tango::AutoTangoMonitor atm(pc);
        pc->suicide();
        pc->ctrl_offline();
    }

//
// Mark all communication channels with controller code offline because
// we will delete all controllers objects
// But before, suicide them...
//

    DEBUG_STREAM << "Cleaning comm channel data ("
                 <<	get_communication_channel_nb() << ")...";
    for (PoolElementTypeIt elem_it = element_types.lower_bound(COM_ELEM);
         elem_it != element_types.upper_bound(COM_ELEM); ++elem_it)
    {
        CommunicationChannel_ns::CommunicationChannel *com = 
            get_communication_channel_device(elem_it->second);
            
        Tango::AutoTangoMonitor atm(com);
        com->suicide();
        com->ctrl_offline();
    }
//
// Mark all counter timer with controller code offline because
// we will delete all controllers objects
// But before, suicide them...
//

    DEBUG_STREAM << "Cleaning counter timer data (" << get_countertimer_nb() << ")...";
    
    for (PoolElementTypeIt elem_it = element_types.lower_bound(COTI_ELEM);
         elem_it != element_types.upper_bound(COTI_ELEM); ++elem_it)
    {    
        CTExpChannel_ns::CTExpChannel *ch = get_countertimer_device(elem_it->second);
        
        Tango::AutoTangoMonitor atm(ch);
        ch->suicide();
        ch->ctrl_offline();
    }
    
//
// Mark all Zero D with controller code offline because
// we will delete all controllers objects
// But before, suicide them...
//

    DEBUG_STREAM << "Cleaning 0D data (" << get_zerod_nb() << ")...";
    for (PoolElementTypeIt elem_it = element_types.lower_bound(ZEROD_ELEM);
         elem_it != element_types.upper_bound(ZEROD_ELEM); ++elem_it)
    {    
        ZeroDExpChannel_ns::ZeroDExpChannel *ch = get_zerod_device(elem_it->second);
        
        Tango::AutoTangoMonitor atm(ch);
        ch->suicide();
        ch->ctrl_offline();
    }

    DEBUG_STREAM << "Cleaning 1D data (" << get_oned_nb() << ")...";
    
    for (PoolElementTypeIt elem_it = element_types.lower_bound(ONED_ELEM);
         elem_it != element_types.upper_bound(ONED_ELEM); ++elem_it)
    {    
        OneDExpChannel_ns::OneDExpChannel *ch = get_oned_device(elem_it->second);
        
        Tango::AutoTangoMonitor atm(ch);
        ch->suicide();
        ch->ctrl_offline();
    }

    DEBUG_STREAM << "Cleaning 2D data (" << get_twod_nb() << ")...";
    
    for (PoolElementTypeIt elem_it = element_types.lower_bound(TWOD_ELEM);
         elem_it != element_types.upper_bound(TWOD_ELEM); ++elem_it)
    {    
        TwoDExpChannel_ns::TwoDExpChannel *ch = get_twod_device(elem_it->second);
        
        Tango::AutoTangoMonitor atm(ch);
        ch->suicide();
        ch->ctrl_offline();
    }
        
//
// Mark all io registers with controller code offline because
// we will delete all controllers objects
// But before, suicide them...
//

    DEBUG_STREAM << "Cleaning ioregister data (" <<	get_ioregister_nb() << ")...";
    for (PoolElementTypeIt elem_it = element_types.lower_bound(COM_ELEM);
         elem_it != element_types.upper_bound(COM_ELEM); ++elem_it)
    {
        IORegister_ns::IORegister *ioregister = get_ioregister_device(elem_it->second);
    
        Tango::AutoTangoMonitor atm(ioregister);
        ioregister->suicide();
        ioregister->ctrl_offline();
    }

//
// Clear the controller lists
//

    DEBUG_STREAM << "Cleaning controller data...";
    remove_controllers();

//
// Do not clear the controller vector in PoolClass
// object in case of several pool devices within the
// same DS
//

    init_cmd = true;

//
// A trick to inform client(s) listening on events that the pool device is down.
// Without this trick, the clients will have to wait for 3 seconds before being informed
// This is the Tango device time-out.
// To know that we are executing this code due to a pool shutdown and not due to a
// "Init" command, we are using the polling thread ptr which is cleared in the DS
// shutdown down sequence before the device destruction
//

    Tango::Util *tg = Tango::Util::instance();
    if (tg->get_polling_thread_object() == NULL)
    {
        //Also clear the API
        {
            AutoPythonGIL apl;
            Py_DECREF(pool_util);
            delete factory;
        }

        set_state(Tango::UNKNOWN);
        Tango::Attribute &state_att = dev_attr->get_attr_by_name("state");
        state_att.fire_change_event();
    }

    int nerr = lt_dlexit();

    if(nerr > 0)
    {
        TangoSys_OMemStream o;
        o << nerr << " occured in dynamic library shutdown";
        Tango::Except::throw_exception((const char *)"Pool_DLExitError",
                        o.str(), (const char *)"Pool::delete_device");
    }
    
    attr_read_method_map.clear();
}

//+----------------------------------------------------------------------------
//
// method : 		Pool::init_device()
//
// description : 	will be called at device initialization.
//
//-----------------------------------------------------------------------------
void Pool::init_device()
{
    INFO_STREAM << "Pool::Pool() create device " << device_name << endl;

    // Initialise variables to default values
    //--------------------------------------------

    const std::string &pool_version_str = get_version_str();
    
    if(!init_cmd) 
        cout << "Starting device pool " << pool_version_str << "..." << endl;

//
// Check that the process is using a correct release of Tango
//
    Tango::Util *tg = Tango::Util::instance();
    long tango_lib_vers = tg->get_tango_lib_release();
    if (tango_lib_vers < MIN_TANGO_VERSION)
    {
        TangoSys_OMemStream o;
        o << "You are using Tango release " << tango_lib_vers
          << "\nThe device pool needs Tango release " 
          << MIN_TANGO_VERSION << " or more"
          << "\nPlease update Tango" << ends;

        Tango::Except::throw_exception(
                        (const char *)"Pool_WrongTangoRelease", o.str(),
                        (const char *)"Pool::init_device");
    }

    poolPath.clear();
    poolPath.push_back("NotDefined");

    get_device_property();

    int32_t pool_tg_vers = DevicePool::to_version_nb(tg_version);
    int32_t pool_lib_vers = DevicePool::get_version_nb();
   
    if(pool_tg_vers > pool_lib_vers)
    {
        TangoSys_OMemStream o;
        o << "The Pool configuration version in the Database (" << tg_version
          << ") is more recent than the Pool executable (" << pool_version_str 
          << ").\nPlease update your Pool executable" << ends;

        Tango::Except::throw_exception(
                        (const char *)"Pool_WrongPoolRelease", o.str(),
                        (const char *)"Pool::init_device");
    }
    else if(pool_tg_vers < pool_lib_vers)
    {
        TangoSys_OMemStream o;
        o << "The Pool executable version (" << pool_version_str
          << ") is more recent than the Pool configuration version in the "
          << "Database (" << tg_version << ").\nPlease run:\n"
          << "% upgrade_sardana " << tg->get_ds_inst_name() << " " << tg_version
          << " " << pool_version_str << ends;

        Tango::Except::throw_exception(
                        (const char *)"Pool_WrongPoolRelease", o.str(),
                        (const char *)"Pool::init_device");
    }

    poolPath_splitted = false;
    last_id = 0;
    proxy_created = false;
    moving_state_requested = false;

    set_state(Tango::ON);
    int nerr = lt_dlinit();

    if(nerr > 0)
    {
        TangoSys_OMemStream o;
        o << nerr << " occured in dynamic library initialization";
        Tango::Except::throw_exception((const char *)"Pool_DLInitError",
                        o.str(), (const char *)"Pool::init_device");
    }
    if(!init_cmd)
    {
        // make sure python is initialized
        PythonUtils::instance()->initialize();
        
        {
            AutoPythonGIL apl;
            factory = new LoggingDeviceFactory();
            pool_util = (PyObject*)PoolUtil::init(factory);
        }
    }
    attr_SimulationMode_read = &attr_SimulationMode_write;

    Tango::WAttribute &att = get_device_attr()->get_w_attr_by_name("SimulationMode");
    attr_SimulationMode_write = false;
    att.set_write_value(attr_SimulationMode_write);
// We will push change event on several attributes
//

    Tango::Attribute &state_att = dev_attr->get_attr_by_name("state");
    state_att.set_change_event(true,false);

    Tango::Attribute &mgl = dev_attr->get_attr_by_name("MotorGroupList");
    mgl.set_change_event(true,false);
    attr_read_method_map[&mgl] = &Pool::read_MotorGroupList;
    
    Tango::Attribute &ml = dev_attr->get_attr_by_name("MotorList");
    ml.set_change_event(true,false);
    attr_read_method_map[&ml] = &Pool::read_MotorList;
    
    Tango::Attribute &pml = dev_attr->get_attr_by_name("PseudoMotorList");
    pml.set_change_event(true,false);
    attr_read_method_map[&pml] = &Pool::read_PseudoMotorList;

    Tango::Attribute &pcl = dev_attr->get_attr_by_name("PseudoCounterList");
    pcl.set_change_event(true,false);
    attr_read_method_map[&pcl] = &Pool::read_PseudoCounterList;

    Tango::Attribute &cl = dev_attr->get_attr_by_name("ControllerList");
    cl.set_change_event(true,false);
    attr_read_method_map[&cl] = &Pool::read_ControllerList;

    Tango::Attribute &ecl = dev_attr->get_attr_by_name("ExpChannelList");
    ecl.set_change_event(true,false);
    attr_read_method_map[&ecl] = &Pool::read_ExpChannelList;

    Tango::Attribute &mntgl = dev_attr->get_attr_by_name("MeasurementGroupList");
    mntgl.set_change_event(true,false);
    attr_read_method_map[&mntgl] = &Pool::read_MeasurementGroupList;

    Tango::Attribute &ccl = dev_attr->get_attr_by_name("ComChannelList");
    ccl.set_change_event(true,false);
    attr_read_method_map[&ccl] = &Pool::read_ComChannelList;

    Tango::Attribute &iorl = dev_attr->get_attr_by_name("IORegisterList");
    iorl.set_change_event(true,false);
    attr_read_method_map[&iorl] = &Pool::read_IORegisterList;

    Tango::Attribute &sm = dev_attr->get_attr_by_name("SimulationMode");
    sm.set_change_event(true,false);
    attr_read_method_map[&sm] = &Pool::read_SimulationMode;

    Tango::Attribute &il = dev_attr->get_attr_by_name("InstrumentList");
    il.set_change_event(true,false);
    attr_read_method_map[&il] = &Pool::read_InstrumentList;

//
// Create all the controller(s) we found in DB
//

    Tango::DbData db_data;
    db_data.push_back(Tango::DbDatum(INSTRUMENT_PROP));
    db_data.push_back(Tango::DbDatum(CTRL_PROP));
    get_db_device()->get_property(db_data);

//
// Create all the instrument(s) we found in DB
//
    Tango::DbDatum &instrument_prop = db_data[0];
    if (!instrument_prop.is_empty())
    {
        std::vector<std::string> instrument_vector;
        instrument_prop >> instrument_vector;
        
        assert (instrument_vector.size() % 3 == 0);
        
        std::vector<std::string>::iterator 
            instrument_beg = instrument_vector.begin(),
            instrument_end = instrument_vector.end(),
            instrument_it = instrument_beg;
        
        while(instrument_it != instrument_end)
        {   
            const std::string &instrument_type   = *instrument_it; ++instrument_it;
            const std::string &instrument_name   = *instrument_it; ++instrument_it;
            const std::string &instrument_id_str = *instrument_it; ++instrument_it;
            istringstream iss(instrument_id_str);
            ElementId instrument_id;
            iss >> instrument_id;
            add_instrument(instrument_type, instrument_name, instrument_id);
        }
    }
//
// Create all the controller(s) we found in DB
//
    Tango::DbDatum &ctrl_prop = db_data[1];
    if (!ctrl_prop.is_empty())
    {
        std::vector<std::string> ctrls;
        ctrl_prop >> ctrls;

        long nb_data = ctrls.size();
        if ((nb_data % PROP_BY_CTRL) != 0)
        {
            TangoSys_OMemStream o;
            o << "Can't create pool " << get_name();
            o << "\nWrong number of properties defining pool controller(s)";
            o << "\nCheck pool device property called Controller" << ends;

            Tango::Except::throw_exception((const char *)"Pool_ControllerAlreadyCreated",o.str(),
                            (const char *)"Pool::create_controller");
        }
        long nb_ctrl = nb_data / PROP_BY_CTRL;

        upd_db = false;
        for (long loop = 0;loop < nb_ctrl;loop++)
        {
            Tango::DevVarStringArray in;
            in.length(PROP_BY_CTRL);

            in[0] = ctrls[loop * PROP_BY_CTRL].c_str();
            in[1] = ctrls[(loop * PROP_BY_CTRL) + 1].c_str();
            in[2] = ctrls[(loop * PROP_BY_CTRL) + 2].c_str();
            in[3] = ctrls[(loop * PROP_BY_CTRL) + 3].c_str();
            in[4] = ctrls[(loop * PROP_BY_CTRL) + 4].c_str();

            string ctrl_status;

            try
            {
                add_ctrl(&in, true);
            }
            catch (Tango::DevFailed &e)
            {
                if (get_logger()->is_info_enabled())
                    Tango::Except::print_exception(e);

                string except_desc_0(e.errors[0].desc);
                string except_desc_1;
                long except_size = e.errors.length();
                if (except_size >= 2)
                    except_desc_1 = e.errors[1].desc;

                ctrl_status = "Error reported when trying to create controller ";
                ctrl_status = ctrl_status + ctrls[(loop * PROP_BY_CTRL) + 2].c_str() + " with instance ";
                ctrl_status = ctrl_status + ctrls[(loop * PROP_BY_CTRL) + 3].c_str() + " from file ";
                ctrl_status = ctrl_status + ctrls[loop * PROP_BY_CTRL + 1].c_str();
                ctrl_status = ctrl_status + ".\nThe reported error description is";
                ctrl_status = ctrl_status + "\n\t" + except_desc_0;
                if (except_size >= 2)
                    ctrl_status = ctrl_status + "\n\t" + except_desc_1;
            }
            string::size_type pos;
            string cp_name(in[1]);

            if ((pos = cp_name.find('.')) != string::npos)
                cp_name.erase(pos);
            cp_name = cp_name + '.' + in[2].in() + '/' + in[3].in();
            ControllerPool &cp = get_controller(cp_name, true);
            cp.error_status = ctrl_status;
        }

        //if (ctrl_list.size() >= 2)
        //	ctrl_list.sort(CtrlComp());

    }
    upd_db = true;

//
// If we are called due to a Init command, we need for each motor to
// force an Init command on each of them
// First, memorize motor names then, clear the pool motor list
// and finally send them an init command.
// The motor init command will register themself in the pool motor list
//
// WARNING: There is a trick here. At this point the pool controller list has been
// rebuilt. Therefore, the iterator stored in the motor objects on the controller list
// is invalid. The Motor class always_executed_hook() method uses this iterator....
// Setting the simulation flag to True will make the Motor always_executed_hook()
// method to not use this iterator. The Motor Init command will update the
// iterator to a new valid value and will reset the simulation flag to False
// (on top of other things).
//

/*	if (init_cmd == true)
    {*/
//
// Handle motors
//
        vector<string> tg_dev_name;

        for (PoolElementTypeIt elem_it = element_types.lower_bound(MOTOR_ELEM);
             elem_it != element_types.upper_bound(MOTOR_ELEM); ++elem_it)
        {
            MotorPool &motor_pool = get_physical_motor(elem_it->second);
            tg_dev_name.push_back(motor_pool.get_full_name());
            motor_pool.set_simulation_mode(true);
        }

        vector<string>::iterator name_ite;
        for (name_ite = tg_dev_name.begin();name_ite != tg_dev_name.end();++name_ite)
        {
            Tango::DeviceProxy mot_dev(*name_ite);
            mot_dev.command_inout("Init");
        }

//
// Handle pseudo motors
//

        vector<string> pm_tg_dev_name;
        for (PoolElementTypeIt elem_it = element_types.lower_bound(PSEUDO_MOTOR_ELEM);
             elem_it != element_types.upper_bound(PSEUDO_MOTOR_ELEM); ++elem_it)
        {
            PseudoMotorPool &pm_pool = get_pseudo_motor(elem_it->second);
            pm_tg_dev_name.push_back(pm_pool.get_full_name());
        }      

        vector<string>::iterator pm_name_ite;
        for (pm_name_ite = pm_tg_dev_name.begin();pm_name_ite != pm_tg_dev_name.end();++pm_name_ite)
        {
            Tango::DeviceProxy pm_dev(*pm_name_ite);
            pm_dev.command_inout("Init");
        }

//
// Handle pseudo counters
//
        vector<string> pc_tg_dev_name;
        for (PoolElementTypeIt elem_it = element_types.lower_bound(PSEUDO_COUNTER_ELEM);
             elem_it != element_types.upper_bound(PSEUDO_COUNTER_ELEM); ++elem_it)
        {
            PseudoCounterPool &pc_pool = get_pseudo_counter(elem_it->second);
            pc_tg_dev_name.push_back(pc_pool.get_full_name());
        }      

        vector<string>::iterator pc_name_ite;
        for (pc_name_ite = pc_tg_dev_name.begin();pc_name_ite != pc_tg_dev_name.end();++pc_name_ite)
        {
            Tango::DeviceProxy pc_dev(*pc_name_ite);
            pc_dev.command_inout("Init");
        }

//
// Handle CTExpChannel
//
        tg_dev_name.clear();
        for (PoolElementTypeIt elem_it = element_types.lower_bound(COTI_ELEM);
             elem_it != element_types.upper_bound(COTI_ELEM); ++elem_it)
        {
            CTExpChannelPool &ct_pool = get_countertimer(elem_it->second);
            tg_dev_name.push_back(ct_pool.get_full_name());
        }        

        for (name_ite = tg_dev_name.begin();name_ite != tg_dev_name.end();++name_ite)
        {
            Tango::DeviceProxy cte_dev(*name_ite);
            cte_dev.command_inout("Init");
        }

//
// Handle ZeroDExpChannel
//
        tg_dev_name.clear();
        for (PoolElementTypeIt elem_it = element_types.lower_bound(ZEROD_ELEM);
             elem_it != element_types.upper_bound(ZEROD_ELEM); ++elem_it)
        {
            ZeroDExpChannelPool &zerod_pool = get_zerod(elem_it->second);
            tg_dev_name.push_back(zerod_pool.get_full_name());
        }

        for (name_ite = tg_dev_name.begin();name_ite != tg_dev_name.end();++name_ite)
        {
            Tango::DeviceProxy cte_dev(*name_ite);
            cte_dev.command_inout("Init");
        }

//
// Handle OneDExpChannel
//
        tg_dev_name.clear();
        for (PoolElementTypeIt elem_it = element_types.lower_bound(ONED_ELEM);
             elem_it != element_types.upper_bound(ONED_ELEM); ++elem_it)
        {
            OneDExpChannelPool &oned_pool = get_oned(elem_it->second);
            tg_dev_name.push_back(oned_pool.get_full_name());
        }

        for (name_ite = tg_dev_name.begin();name_ite != tg_dev_name.end();++name_ite)
        {
            Tango::DeviceProxy cte_dev(*name_ite);
            cte_dev.command_inout("Init");
        }


//
// Handle TwoDExpChannel
//
        tg_dev_name.clear();
        for (PoolElementTypeIt elem_it = element_types.lower_bound(TWOD_ELEM);
             elem_it != element_types.upper_bound(TWOD_ELEM); ++elem_it)
        {
            TwoDExpChannelPool &twod_pool = get_twod(elem_it->second);
            tg_dev_name.push_back(twod_pool.get_full_name());
        }

        for (name_ite = tg_dev_name.begin();name_ite != tg_dev_name.end();++name_ite)
        {
            Tango::DeviceProxy cte_dev(*name_ite);
            cte_dev.command_inout("Init");
        }
        
//
// Handle measurement group
//
        tg_dev_name.clear();
        for (PoolElementTypeIt elem_it = element_types.lower_bound(MEASUREMENT_GROUP_ELEM);
             elem_it != element_types.upper_bound(MEASUREMENT_GROUP_ELEM); ++elem_it)
        {
            MeasurementGroupPool &mntgrp_pool = get_measurement_group(elem_it->second);
            tg_dev_name.push_back(mntgrp_pool.get_full_name());
        }

        for (name_ite = tg_dev_name.begin();name_ite != tg_dev_name.end();++name_ite)
        {
            Tango::DeviceProxy mg_dev(*name_ite);
            mg_dev.command_inout("Init");
        }

//
// Handle motor group
//
        tg_dev_name.clear();
        for (PoolElementTypeIt elem_it = element_types.lower_bound(MOTOR_GROUP_ELEM);
             elem_it != element_types.upper_bound(MOTOR_GROUP_ELEM); ++elem_it)
        {
            MotorGroupPool &motor_group_pool = get_motor_group(elem_it->second);
            tg_dev_name.push_back(motor_group_pool.get_full_name());
        }

        for (name_ite = tg_dev_name.begin();name_ite != tg_dev_name.end();++name_ite)
        {
            Tango::DeviceProxy gm_dev(*name_ite);
            gm_dev.command_inout("Init");
        }

//
// Handle CommunicationChannel
//
        tg_dev_name.clear();
        for (PoolElementTypeIt elem_it = element_types.lower_bound(COM_ELEM);
             elem_it != element_types.upper_bound(COM_ELEM); ++elem_it)
        {
            CommunicationChannelPool &cc_pool = get_communication_channel(elem_it->second);
            tg_dev_name.push_back(cc_pool.get_full_name());
        }

        for (name_ite = tg_dev_name.begin();name_ite != tg_dev_name.end();++name_ite)
        {
            Tango::DeviceProxy cce_dev(*name_ite);
            cce_dev.command_inout("Init");
        }

//
// Handle IORegister
//
        tg_dev_name.clear();
        for (PoolElementTypeIt elem_it = element_types.lower_bound(IOREGISTER_ELEM);
             elem_it != element_types.upper_bound(IOREGISTER_ELEM); ++elem_it)
        {
            IORegisterPool &ior_pool = get_ioregister(elem_it->second);
            tg_dev_name.push_back(ior_pool.get_full_name());
        }

        for (name_ite = tg_dev_name.begin();name_ite != tg_dev_name.end();++name_ite)
        {
            Tango::DeviceProxy ior_dev(*name_ite);
            ior_dev.command_inout("Init");
        }

//
// Handle the ghost group
//

        try
        {
            MotorGroup_ns::MotorGroup *ghost_ptr = get_ghost_motor_group_ptr();

            Tango::AutoTangoMonitor atm(ghost_ptr);
            ghost_ptr->delete_device();
            ghost_ptr->init_device();
        }
        catch (Tango::DevFailed &e) {}

//
// Handle the ghost measurement group
//

        try
        {
            MeasurementGroup_ns::MeasurementGroup *ghost_ptr =
                get_ghost_measurement_group_ptr();

            Tango::AutoTangoMonitor atm(ghost_ptr);
            ghost_ptr->delete_device();
            ghost_ptr->init_device();
        }
        catch (Tango::DevFailed &e) {}

/*		init_cmd = false;
    }*/

//
// Push change_event to inform client listenning on events
//
    read_MotorGroupList(mgl);
    mgl.fire_change_event();

    read_MotorList(ml);
    ml.fire_change_event();

    read_ControllerList(cl);
    cl.fire_change_event();

    read_ControllerClassList(cl);

    read_ExpChannelList(ecl);
    ecl.fire_change_event();

    read_PseudoMotorList(pml);
    pml.fire_change_event();

    read_PseudoCounterList(pcl);
    pcl.fire_change_event();

    read_MeasurementGroupList(mntgl);
    mntgl.fire_change_event();

    read_ComChannelList(ccl);
    ccl.fire_change_event();

    read_IORegisterList(iorl);
    iorl.fire_change_event();

    read_SimulationMode(sm);
    sm.fire_change_event();  
}


//+----------------------------------------------------------------------------
//
// method : 		Pool::get_device_property()
//
// description : 	Read the device properties from database.
//
//-----------------------------------------------------------------------------
void Pool::get_device_property()
{
    //	Initialize your default values here (if not done with  POGO).
    //------------------------------------------------------------------

    //	Read device properties from database.(Automatic code generation)
    //------------------------------------------------------------------
    Tango::DbData	dev_prop;
    dev_prop.push_back(Tango::DbDatum("PoolPath"));
    dev_prop.push_back(Tango::DbDatum("DefaultMotPos_AbsChange"));
    dev_prop.push_back(Tango::DbDatum("DefaultMotGrpPos_AbsChange"));
    dev_prop.push_back(Tango::DbDatum("GhostGroup_PollingPeriod"));
    dev_prop.push_back(Tango::DbDatum("MotThreadLoop_SleepTime"));
    dev_prop.push_back(Tango::DbDatum("NbStatePerRead"));
    dev_prop.push_back(Tango::DbDatum("DefaultCtVal_AbsChange"));
    dev_prop.push_back(Tango::DbDatum("ZeroDNbReadPerEvent"));
    dev_prop.push_back(Tango::DbDatum("DefaultZeroDVal_AbsChange"));
    dev_prop.push_back(Tango::DbDatum("DefaultCtGrpVal_AbsChange"));
    dev_prop.push_back(Tango::DbDatum("DefaultZeroDGrpVal_AbsChange"));
    dev_prop.push_back(Tango::DbDatum("CTThreadLoop_SleepTime"));
    dev_prop.push_back(Tango::DbDatum("ZeroDThreadLoop_SleepTime"));
    dev_prop.push_back(Tango::DbDatum("TmpElement_MaxInactTime"));
    dev_prop.push_back(Tango::DbDatum("OneDNbReadPerEvent"));
    dev_prop.push_back(Tango::DbDatum("OneDThreadLoop_SleepTime"));
    dev_prop.push_back(Tango::DbDatum("DefaultOneDVal_AbsChange"));
    dev_prop.push_back(Tango::DbDatum("DefaultOneDGrpVal_AbsChange"));
    dev_prop.push_back(Tango::DbDatum("TwoDNbReadPerEvent"));
    dev_prop.push_back(Tango::DbDatum("TwoDThreadLoop_SleepTime"));
    dev_prop.push_back(Tango::DbDatum("Version"));

    //	Call database and extract values
    //--------------------------------------------
    if (Tango::Util::instance()->_UseDb==true)
        get_db_device()->get_property(dev_prop);
    Tango::DbDatum	def_prop, cl_prop;
    PoolClass	*ds_class =
        (static_cast<PoolClass *>(get_device_class()));
    int	i = -1;

    //	Try to initialize PoolPath from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  poolPath;
    //	Try to initialize PoolPath from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  poolPath;
    //	And try to extract PoolPath value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  poolPath;

    //	Try to initialize DefaultMotPos_AbsChange from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  defaultMotPos_AbsChange;
    //	Try to initialize DefaultMotPos_AbsChange from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  defaultMotPos_AbsChange;
    //	And try to extract DefaultMotPos_AbsChange value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  defaultMotPos_AbsChange;

    //	Try to initialize DefaultMotGrpPos_AbsChange from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  defaultMotGrpPos_AbsChange;
    //	Try to initialize DefaultMotGrpPos_AbsChange from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  defaultMotGrpPos_AbsChange;
    //	And try to extract DefaultMotGrpPos_AbsChange value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  defaultMotGrpPos_AbsChange;

    //	Try to initialize GhostGroup_PollingPeriod from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  ghostGroup_PollingPeriod;
    //	Try to initialize GhostGroup_PollingPeriod from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  ghostGroup_PollingPeriod;
    //	And try to extract GhostGroup_PollingPeriod value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  ghostGroup_PollingPeriod;

    //	Try to initialize MotThreadLoop_SleepTime from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  motThreadLoop_SleepTime;
    //	Try to initialize MotThreadLoop_SleepTime from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  motThreadLoop_SleepTime;
    //	And try to extract MotThreadLoop_SleepTime value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  motThreadLoop_SleepTime;

    //	Try to initialize NbStatePerRead from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  nbStatePerRead;
    //	Try to initialize NbStatePerRead from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  nbStatePerRead;
    //	And try to extract NbStatePerRead value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  nbStatePerRead;

    //	Try to initialize DefaultCtVal_AbsChange from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  defaultCtVal_AbsChange;
    //	Try to initialize DefaultCtVal_AbsChange from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  defaultCtVal_AbsChange;
    //	And try to extract DefaultCtVal_AbsChange value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  defaultCtVal_AbsChange;

    //	Try to initialize ZeroDNbReadPerEvent from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  zeroDNbReadPerEvent;
    //	Try to initialize ZeroDNbReadPerEvent from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  zeroDNbReadPerEvent;
    //	And try to extract ZeroDNbReadPerEvent value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  zeroDNbReadPerEvent;

    //	Try to initialize DefaultZeroDVal_AbsChange from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  defaultZeroDVal_AbsChange;
    //	Try to initialize DefaultZeroDVal_AbsChange from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  defaultZeroDVal_AbsChange;
    //	And try to extract DefaultZeroDVal_AbsChange value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  defaultZeroDVal_AbsChange;

    //	Try to initialize DefaultCtGrpVal_AbsChange from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  defaultCtGrpVal_AbsChange;
    //	Try to initialize DefaultCtGrpVal_AbsChange from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  defaultCtGrpVal_AbsChange;
    //	And try to extract DefaultCtGrpVal_AbsChange value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  defaultCtGrpVal_AbsChange;

    //	Try to initialize DefaultZeroDGrpVal_AbsChange from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  defaultZeroDGrpVal_AbsChange;
    //	Try to initialize DefaultZeroDGrpVal_AbsChange from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  defaultZeroDGrpVal_AbsChange;
    //	And try to extract DefaultZeroDGrpVal_AbsChange value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  defaultZeroDGrpVal_AbsChange;

    //	Try to initialize CTThreadLoop_SleepTime from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  cTThreadLoop_SleepTime;
    //	Try to initialize CTThreadLoop_SleepTime from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  cTThreadLoop_SleepTime;
    //	And try to extract CTThreadLoop_SleepTime value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  cTThreadLoop_SleepTime;

    //	Try to initialize ZeroDThreadLoop_SleepTime from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  zeroDThreadLoop_SleepTime;
    //	Try to initialize ZeroDThreadLoop_SleepTime from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  zeroDThreadLoop_SleepTime;
    //	And try to extract ZeroDThreadLoop_SleepTime value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  zeroDThreadLoop_SleepTime;

    //	Try to initialize TmpElement_MaxInactTime from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  tmpElement_MaxInactTime;
    //	Try to initialize TmpElement_MaxInactTime from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  tmpElement_MaxInactTime;
    //	And try to extract TmpElement_MaxInactTime value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  tmpElement_MaxInactTime;

    //	Try to initialize OneDNbReadPerEvent from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  oneDNbReadPerEvent;
    //	Try to initialize OneDNbReadPerEvent from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  oneDNbReadPerEvent;
    //	And try to extract OneDNbReadPerEvent value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  oneDNbReadPerEvent;

    //	Try to initialize OneDThreadLoop_SleepTime from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  oneDThreadLoop_SleepTime;
    //	Try to initialize OneDThreadLoop_SleepTime from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  oneDThreadLoop_SleepTime;
    //	And try to extract OneDThreadLoop_SleepTime value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  oneDThreadLoop_SleepTime;

    //	Try to initialize DefaultOneDVal_AbsChange from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  defaultOneDVal_AbsChange;
    //	Try to initialize DefaultOneDVal_AbsChange from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  defaultOneDVal_AbsChange;
    //	And try to extract DefaultOneDVal_AbsChange value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  defaultOneDVal_AbsChange;

    //	Try to initialize DefaultOneDGrpVal_AbsChange from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  defaultOneDGrpVal_AbsChange;
    //	Try to initialize DefaultOneDGrpVal_AbsChange from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  defaultOneDGrpVal_AbsChange;
    //	And try to extract DefaultOneDGrpVal_AbsChange value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  defaultOneDGrpVal_AbsChange;

    //  Try to initialize TwoDNbReadPerEvent from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)  cl_prop  >>  twoDNbReadPerEvent;
    //  Try to initialize TwoDNbReadPerEvent from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false) def_prop  >>  twoDNbReadPerEvent;
    //  And try to extract TwoDNbReadPerEvent value from database
    if (dev_prop[i].is_empty()==false)      dev_prop[i]  >>  twoDNbReadPerEvent;

    //      Try to initialize TwoDThreadLoop_SleepTime from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)  cl_prop  >>  twoDThreadLoop_SleepTime;
    //      Try to initialize TwoDThreadLoop_SleepTime from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false) def_prop  >>  twoDThreadLoop_SleepTime;
    //      And try to extract TwoDThreadLoop_SleepTime value from database
    if (dev_prop[i].is_empty()==false)      dev_prop[i]  >>  twoDThreadLoop_SleepTime;
    
    //  Try to initialize Version from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)  cl_prop  >>  tg_version;
    //  Try to initialize Version from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false) def_prop  >>  tg_version;
    //  And try to extract Version value from database
    if (dev_prop[i].is_empty()==false)      dev_prop[i]  >>  tg_version;

    //	End of Automatic code generation
    //------------------------------------------------------------------

}
//+----------------------------------------------------------------------------
//
// method : 		Pool::always_executed_hook()
//
// description : 	method always executed before any command is executed
//
//-----------------------------------------------------------------------------
void Pool::always_executed_hook()
{
    if (proxy_created == false)
    {
        create_proxies();
        proxy_created = true;
    }
}

//+----------------------------------------------------------------------------
//
// method : 		Pool::read_attr_hardware
//
// description : 	Hardware acquisition for attributes.
//
//-----------------------------------------------------------------------------
void Pool::read_attr_hardware(vector<long> &attr_list)
{
    DEBUG_STREAM << "Pool::read_attr_hardware(vector<long> &attr_list) entering... "<< endl;
    //	Add your own code here
}
//+----------------------------------------------------------------------------
//
// method : 		Pool::read_IORegisterList
//
// description : 	Extract real attribute values for IORegisterList acquisition result.
//
//-----------------------------------------------------------------------------
void Pool::read_IORegisterList(Tango::Attribute &attr)
{
    DEBUG_STREAM << "Pool::read_IORegisterList(Tango::Attribute &attr) entering... "<< endl;

    int32_t l = 0;
    PoolElementTypeIt elem_it, elem_end;
    for(get_all_ioregister(elem_it, elem_end); elem_it != elem_end; ++elem_it, ++l)
    {
        IORegisterPool &ior_pool = get_ioregister(elem_it->second);
        ioregister_name_list[l] = const_cast<char *>(ior_pool.user_full_name.c_str());
    }

    attr.set_value(ioregister_name_list, get_ioregister_nb());
}

void Pool::read_InstrumentList(Tango::Attribute &attr)
{
    DEBUG_STREAM << "Pool::read_InstrumentList(Tango::Attribute &attr) entering... "<< endl;

    int32_t l = 0;
    PoolElementTypeIt elem_it, elem_end;
    for(get_all_instrument(elem_it, elem_end); elem_it != elem_end; ++elem_it, ++l)
    {
        InstrumentPool &instrument_pool = get_instrument(elem_it->second);
        instrument_name_list[l] = const_cast<char *>(instrument_pool.user_full_name.c_str());
    }

    attr.set_value(instrument_name_list, get_instrument_nb());
}

//+----------------------------------------------------------------------------
//
// method : 		Pool::read_PseudoCounterList
//
// description : 	Extract real attribute values for PseudoCounterList acquisition result.
//
//-----------------------------------------------------------------------------
void Pool::read_PseudoCounterList(Tango::Attribute &attr)
{
    DEBUG_STREAM << "Pool::read_PseudoCounterList(Tango::Attribute &attr) entering... "<< endl;
    
    int32_t l = 0;
    PoolElementTypeIt elem_it, elem_end;
    for(get_all_pseudo_counter(elem_it, elem_end); elem_it != elem_end; ++elem_it, ++l)
    {
        PseudoCounterPool &pc_pool = get_pseudo_counter(elem_it->second);
        pseudo_counter_name_list[l] = const_cast<char *>(pc_pool.user_full_name_extra.c_str());
    }

    attr.set_value(pseudo_counter_name_list, get_pseudo_counter_nb());
}

//+----------------------------------------------------------------------------
//
// method : 		Pool::read_ComChannelList
//
// description : 	Extract real attribute values for ComChannelList acquisition result.
//
//-----------------------------------------------------------------------------
void Pool::read_ComChannelList(Tango::Attribute &attr)
{
    DEBUG_STREAM << "Pool::read_ComChannelList(Tango::Attribute &attr) entering... "<< endl;
    
    int32_t l = 0;
    PoolElementTypeIt elem_it, elem_end;
    for(get_all_communication_channel(elem_it, elem_end); elem_it != elem_end; ++elem_it, ++l)
    {	
        CommunicationChannelPool &cc_pool = get_communication_channel(elem_it->second);
        com_channel_name_list[l] = const_cast<char *>(cc_pool.user_full_name.c_str());
    }

    attr.set_value(com_channel_name_list, get_communication_channel_nb());
}

//+----------------------------------------------------------------------------
//
// method : 		Pool::read_MeasurementGroupList
//
// description : 	Extract real attribute values for MeasurementGroupList acquisition result.
//
//-----------------------------------------------------------------------------
void Pool::read_MeasurementGroupList(Tango::Attribute &attr)
{
    DEBUG_STREAM << "Pool::read_MeasurementGroupList(Tango::Attribute &attr) entering... "<< endl;

    int32_t l = 0;
    PoolElementTypeIt elem_it, elem_end;
    for(get_all_measurement_group(elem_it, elem_end); elem_it != elem_end; ++elem_it, ++l)
    {
        MeasurementGroupPool &mntgrp_pool = get_measurement_group(elem_it->second);
        measurement_group_name_list[l] = const_cast<char *>(mntgrp_pool.user_full_name.c_str());
    }

    attr.set_value(measurement_group_name_list, get_measurement_group_nb());
}


//+----------------------------------------------------------------------------
//
// method : 		Pool::read_ExpChannelList
//
// description : 	Extract real attribute values for ExpChannelList acquisition result.
//
//-----------------------------------------------------------------------------
void Pool::read_ExpChannelList(Tango::Attribute &attr)
{
    DEBUG_STREAM << "Pool::read_ExpChannelList(Tango::Attribute &attr) entering... "<< endl;
    
    int32_t l = 0;
    PoolElementTypeIt elem_it, elem_end;

    for(get_all_countertimer(elem_it, elem_end); elem_it != elem_end; ++elem_it, ++l)
    {
        CTExpChannelPool &ct_pool = get_countertimer(elem_it->second);
        expch_name_list[l] = const_cast<char *>(ct_pool.user_full_name.c_str());
    }
    
    for(get_all_zerod(elem_it, elem_end); elem_it != elem_end; ++elem_it, ++l)
    {
        ZeroDExpChannelPool &zerod_pool = get_zerod(elem_it->second);
        expch_name_list[l] = const_cast<char *>(zerod_pool.user_full_name.c_str());
    }    

    for(get_all_oned(elem_it, elem_end); elem_it != elem_end; ++elem_it, ++l)
    {
        OneDExpChannelPool &oned_pool = get_oned(elem_it->second);
        expch_name_list[l] = const_cast<char *>(oned_pool.user_full_name.c_str());
    }
    
    for(get_all_twod(elem_it, elem_end); elem_it != elem_end; ++elem_it, ++l)
    {
        TwoDExpChannelPool &twod_pool = get_twod(elem_it->second);
        expch_name_list[l] = const_cast<char *>(twod_pool.user_full_name.c_str());
    }    

    for(get_all_pseudo_counter(elem_it, elem_end); elem_it != elem_end; ++elem_it, ++l)
    {
        PseudoCounterPool &pc_pool = get_pseudo_counter(elem_it->second);
        expch_name_list[l] = const_cast<char *>(pc_pool.user_full_name.c_str());
    }    

    attr.set_value(expch_name_list,l);
}

//+----------------------------------------------------------------------------
//
// method : 		Pool::read_ControllerClassList
//
// description : 	Extract real attribute values for ControllerClassList acquisition result.
//
//-----------------------------------------------------------------------------
void Pool::read_ControllerClassList(Tango::Attribute &attr)
{
    DEBUG_STREAM << "Pool::read_ControllerClassList(Tango::Attribute &attr) entering... "<< endl;

    cpp_ctrl_classes.clear();
    py_ctrl_classes.clear();

//
// First add to the list all the possible Controller class(es) for the
// controller we already have in memory
//

    vector<string> tmp_ctrl_list;
    vector<string> ctrl_type_list;
    
    for (PoolElementTypeIt ctrl_it = element_types.lower_bound(CTRL_ELEM);
         ctrl_it !=element_types.upper_bound(CTRL_ELEM); ++ctrl_it)
    {
        ControllerPool &ctrl = get_controller(ctrl_it->second);
        tmp_ctrl_list.clear();
        ctrl_type_list.clear();
        if (ctrl.ctrl_class_built == true)
        {
            string ctrl_full_f_name = ctrl.get_path() + '/' + ctrl.get_f_name();
            long nb_class = ctrl.get_ctrl_file().get_classes(tmp_ctrl_list,ctrl_type_list);
            Language lang = ctrl.get_language();

            for (long loop = 0;loop < nb_class;loop++)
            {
                // <class name> '('<full file name>')' <type>
                string &tmp_ctrl = tmp_ctrl_list[loop];
                string tmp_str = tmp_ctrl.substr(tmp_ctrl.find('.') + 1);
                tmp_str += " (" + ctrl_full_f_name + ") ";
                tmp_str += ctrl_type_list[loop];

//
// If it a file and a class that that we already have, forget it
//

                bool leave_loop = false;
                if (lang == CPP)
                {
                    unsigned long nb = cpp_ctrl_classes.size();
                    for (unsigned long ll = 0;ll < nb;ll++)
                    {
                        if (tmp_str == cpp_ctrl_classes[ll])
                        {
                            leave_loop = true;
                            break;
                        }
                    }

                    if (leave_loop == true)
                        continue;
                    else
                        cpp_ctrl_classes.push_back(tmp_str);
                }
                else
                {

//
// If it a file that we already have, forget it
//
                    unsigned long nb = py_ctrl_classes.size();
                    for (unsigned long ll = 0;ll < nb;ll++)
                    {
                        if (tmp_str == py_ctrl_classes[ll])
                        {
                            leave_loop = true;
                            break;
                        }
                    }

                    if (leave_loop == true)
                        continue;
                    else
                        py_ctrl_classes.push_back(tmp_str);
                }
            }
        }
    }

    vector<string> py_files;
    vector<string> cpp_files;
    vector<string>::iterator path_ite;

//
// Get all the directories in the PoolPath
//

    vector<string> &paths = get_pool_path();

//
// Get list of python files in each directories
//

    for(path_ite = paths.begin(); path_ite != paths.end(); path_ite++)
        get_files_with_extension(*path_ite,".py",py_files);

//
// Get list of .la files in each directories
//

    for (path_ite = paths.begin();path_ite != paths.end(); path_ite++)
        get_files_with_extension(*path_ite,".la",cpp_files);

//
// Check which of the .la files are valid controllers
//

    vector<string>::iterator ite;

    for (ite = cpp_files.begin();ite != cpp_files.end();ite++)
    {
        try
        {

//
// Is it a file we already have in the list ?
// If yes, forget it
//

            bool leave_loop = false;
            unsigned long nb = cpp_ctrl_classes.size();
            for (unsigned long ll = 0;ll < nb;ll++)
            {
                string &ctrl_class = cpp_ctrl_classes[ll];
                string::size_type start = ctrl_class.find('(');
                string::size_type end   = ctrl_class.find(')');
                string tmp_file_name = ctrl_class.substr(start + 1, end - start -1);
                if (tmp_file_name == *ite)
                {
                    leave_loop = true;
                    break;
                }
            }

            if (leave_loop == true)
                continue;

//
// Build the ctrl as an undefined type ctrl
//
            CppUndefCtrlFile tmp_undef_ctrl(*ite);

            tmp_ctrl_list.clear();
            ctrl_type_list.clear();
            bool exit_search = false;
            long class_count;

//
// Is it a motor controller?
//

            try
            {
                class_count = 0;
                CppMotCtrlFile tmp_mot_ctrl(tmp_undef_ctrl);
                class_count = tmp_mot_ctrl.get_classes(tmp_ctrl_list,ctrl_type_list);
                DEBUG_STREAM << "Found " << class_count << " Motor Controller Classes in " << *ite << endl;
                if (class_count != 0)
                    exit_search = true;
            }
            catch (Tango::DevFailed &e)
            {
                DEBUG_STREAM << "Cpp file " << *ite << " is not a valid motor controller" << endl;
            }

//
// Is it a pseudo motor controller?
//
            if (exit_search == false)
            {
                try
                {
                    class_count = 0;
                    CppPseudoMotCtrlFile tmp_mot_ctrl(tmp_undef_ctrl);
                    class_count = tmp_mot_ctrl.get_classes(tmp_ctrl_list,ctrl_type_list);
                    DEBUG_STREAM << "Found " << class_count << " Pseudo Motor Controller Classes in " << *ite << endl;
                    if (class_count != 0)
                        exit_search = true;
                }
                catch (Tango::DevFailed &e)
                {
                    DEBUG_STREAM << "Cpp file " << *ite << " is not a valid pseudo motor controller" << endl;
                }
            }

//
// Is it a pseudo counter controller?
//
            if (exit_search == false)
            {
                try
                {
                    class_count = 0;
                    CppPseudoCoCtrlFile tmp_counter_ctrl(tmp_undef_ctrl);
                    class_count = tmp_counter_ctrl.get_classes(tmp_ctrl_list,ctrl_type_list);
                    DEBUG_STREAM << "Found " << class_count << " Pseudo Counter Controller Classes in " << *ite << endl;
                    if (class_count != 0)
                        exit_search = true;
                }
                catch (Tango::DevFailed &e)
                {
                    DEBUG_STREAM << "Cpp file " << *ite << " is not a valid pseudo counter controller" << endl;
                }
            }

//
// Is it a Counter Timer ctrl?
//

            if (exit_search == false)
            {
                try
                {
                    class_count = 0;
                    CppCoTiCtrlFile tmp_ctrl_file(tmp_undef_ctrl);
                    class_count = tmp_ctrl_file.get_classes(tmp_ctrl_list,ctrl_type_list);
                    DEBUG_STREAM << "Found " << class_count << " CounterTimer Controller Classes in " << *ite << endl;
                    if (class_count != 0)
                        exit_search = true;
                }
                catch (Tango::DevFailed &e)
                {
                    DEBUG_STREAM << "Cpp file " << *ite << " is not a valid CounterTimer controller" << endl;
                }
            }

//
// Is it a Zero D Exp Channel ctrl?
//

            if (exit_search == false)
            {
                try
                {
                    class_count = 0;
                    CppZeroDCtrlFile tmp_ctrl_file(tmp_undef_ctrl);
                    class_count = tmp_ctrl_file.get_classes(tmp_ctrl_list,ctrl_type_list);
                    DEBUG_STREAM << "Found " << class_count << " ZeroDExpChannel Controller Classes in " << *ite << endl;
                    if (class_count != 0)
                        exit_search = true;
                }
                catch (Tango::DevFailed &e)
                {
                    DEBUG_STREAM << "Cpp file " << *ite << " is not a valid ZeroDExpChannel controller" << endl;
                }
            }


//
// Is it a One D Exp Channel ctrl?
//

            if (exit_search == false)
            {			
                try
                {
                    class_count = 0;
                    CppOneDCtrlFile tmp_ctrl_file(tmp_undef_ctrl);
                    class_count = tmp_ctrl_file.get_classes(tmp_ctrl_list,ctrl_type_list);
                    DEBUG_STREAM << "Found " << class_count << " OneDExpChannel Controller Classes in " << *ite << endl;
                    if (class_count != 0)
                        exit_search = true;
                }
                catch (Tango::DevFailed &e)
                {
                    DEBUG_STREAM << "Cpp file " << *ite << " is not a valid OneDExpChannel controller" << endl;
                }
            }
            
//
// Is it a Two D Exp Channel ctrl?
//

            if (exit_search == false)
            {			
                try
                {
                    class_count = 0;
                    CppTwoDCtrlFile tmp_ctrl_file(tmp_undef_ctrl);
                    class_count = tmp_ctrl_file.get_classes(tmp_ctrl_list,ctrl_type_list);
                    DEBUG_STREAM << "Found " << class_count << " TwoDExpChannel Controller Classes in " << *ite << endl;
                    if (class_count != 0)
                        exit_search = true;
                }
                catch (Tango::DevFailed &e)
                {
                    DEBUG_STREAM << "Cpp file " << *ite << " is not a valid TwoDExpChannel controller" << endl;
                }
            }
            
//
// Is it a Communication Channel ctrl?
//

            if (exit_search == false)
            {
                try
                {
                    class_count = 0;
                    CppComCtrlFile tmp_ctrl_file(tmp_undef_ctrl);
                    class_count = tmp_ctrl_file.get_classes(tmp_ctrl_list,ctrl_type_list);
                    DEBUG_STREAM << "Found " << class_count << " Communication Controller Classes in " << *ite << endl;
                    if (class_count != 0)
                        exit_search = true;
                }
                catch (Tango::DevFailed &e)
                {
                    DEBUG_STREAM << "Cpp file " << *ite << " is not a valid Communication controller" << endl;
                }
            }
//
// Is it a IORegister ctrl?
//

            if (exit_search == false)
            {
                try
                {
                    class_count = 0;
                    CppIORegisterCtrlFile tmp_ctrl_file(tmp_undef_ctrl);
                    class_count = tmp_ctrl_file.get_classes(tmp_ctrl_list,ctrl_type_list);
                    DEBUG_STREAM << "Found " << class_count << " IORegister Classes in " << *ite << endl;
                    if (class_count != 0)
                        exit_search = true;
                }
                catch (Tango::DevFailed &e)
                {
                    DEBUG_STREAM << "Cpp file " << *ite << " is not a valid IORegister controller" << endl;
                    throw;
                }
            }

            for (long loop = 0;loop < class_count;loop++)
            {
                // <class name> '('<full file name>')' <type>
                string &tmp_ctrl = tmp_ctrl_list[loop];
                string tmp_str = tmp_ctrl.substr(tmp_ctrl.find('.') + 1);
                tmp_str += " (" + *ite + ") ";
                tmp_str += ctrl_type_list[loop];
                cpp_ctrl_classes.push_back(tmp_str);
            }

        }
        catch (Tango::DevFailed &e)
        {
            string reason = e.errors[0].reason.in();
            if (reason == "Pool_ControllerNotFound")
            {
                WARN_STREAM << "\tReason: " << e.errors[0].reason << endl;
                WARN_STREAM << "\tDescription: " << e.errors[0].desc << endl;
            }
            else
            {
                DEBUG_STREAM << "\tReason: " << e.errors[0].reason << endl;
                DEBUG_STREAM << "\tDescription: " << e.errors[0].desc << endl;
            }

        }

    }

//
// Check which of the .py files are valid controller
//

    for(ite = py_files.begin(); ite != py_files.end(); ite++)
    {
        try
        {

//
// Is it a file we already have in the list ?
// If yes, forget it
//

            bool leave_loop = false;
            unsigned long nb = py_ctrl_classes.size();
            for (unsigned long ll = 0;ll < nb;ll++)
            {
                string &ctrl_class = py_ctrl_classes[ll];
                string::size_type start = ctrl_class.find('(');
                string::size_type end   = ctrl_class.find(')');
                string tmp_file_name = ctrl_class.substr(start + 1, end - start -1);
                if (tmp_file_name == *ite)
                {
                    leave_loop = true;
                    break;
                }
            }

            if (leave_loop == true)
                continue;

//
// Build the ctrl as an undefined type ctrl
//

            PyUndefCtrlFile tmp_undef_ctrl(*ite);

            tmp_ctrl_list.clear();
            ctrl_type_list.clear();
            long class_count;
            bool exit_search = false;

//
// Is it a motor controller?
//

            try
            {
                class_count = 0;
                PyMotCtrlFile tmp_ctrl_file(tmp_undef_ctrl);
                class_count = tmp_ctrl_file.get_classes(tmp_ctrl_list,ctrl_type_list);
                DEBUG_STREAM << "Found " << class_count << " Motor Controller Classes in " << *ite << endl;
                if (class_count != 0)
                    exit_search = true;
            }
            catch (Tango::DevFailed &e)
            {
                DEBUG_STREAM << "Python file " << *ite << " is not a valid motor controller" << endl;
            }

//
// Is it a pseudo motor controller?
//

            if (exit_search == false)
            {
                try
                {
                    class_count = 0;
                    PyPseudoMotCtrlFile tmp_ctrl_file(tmp_undef_ctrl);
                    class_count = tmp_ctrl_file.get_classes(tmp_ctrl_list,ctrl_type_list);
                    DEBUG_STREAM << "Found " << class_count << " Pseudo Motor Controller Classes in " << *ite << endl;
                    if (class_count != 0)
                        exit_search = true;
                }
                catch (Tango::DevFailed &e)
                {
                    DEBUG_STREAM << "Python file " << *ite << " is not a valid pseudo motor controller" << endl;
                }
            }

//
// Is it a pseudo counter controller?
//

            if (exit_search == false)
            {
                try
                {
                    class_count = 0;
                    PyPseudoCoCtrlFile tmp_ctrl_file(tmp_undef_ctrl);
                    class_count = tmp_ctrl_file.get_classes(tmp_ctrl_list,ctrl_type_list);
                    DEBUG_STREAM << "Found " << class_count << " Pseudo Counter Controller Classes in " << *ite << endl;
                    if (class_count != 0)
                        exit_search = true;
                }
                catch (Tango::DevFailed &e)
                {
                    DEBUG_STREAM << "Python file " << *ite << " is not a valid pseudo counter controller" << endl;
                }
            }

//
// Is it a Counter Timer ctrl?
//

            if (exit_search == false)
            {
                try
                {
                    class_count = 0;
                    PyCoTiCtrlFile tmp_ctrl_file(tmp_undef_ctrl);
                    class_count = tmp_ctrl_file.get_classes(tmp_ctrl_list,ctrl_type_list);
                    DEBUG_STREAM << "Found " << class_count << " CounterTimer Controller Classes in " << *ite << endl;
                    if (class_count != 0)
                        exit_search = true;
                }
                catch (Tango::DevFailed &e)
                {
                    DEBUG_STREAM << "Python file " << *ite << " is not a valid CounterTimer controller" << endl;
                }
            }

//
// Is it a Zero D Exp Channel ctrl?
//

            if (exit_search == false)
            {
                try
                {
                    class_count = 0;
                    PyZeroDCtrlFile tmp_ctrl_file(tmp_undef_ctrl);
                    class_count = tmp_ctrl_file.get_classes(tmp_ctrl_list,ctrl_type_list);
                    DEBUG_STREAM << "Found " << class_count << " ZeroDExpChannel Controller Classes in " << *ite << endl;
                    if (class_count != 0)
                        exit_search = true;
                }
                catch (Tango::DevFailed &e)
                {
                    DEBUG_STREAM << "Python file " << *ite << " is not a valid ZeroDExpChannel controller" << endl;
                }
            }
//
// Is it a One D Exp Channel ctrl?
//

            if (exit_search == false)
            {			
                try
                {
                    class_count = 0;
                    PyOneDCtrlFile tmp_ctrl_file(tmp_undef_ctrl);
                    class_count = tmp_ctrl_file.get_classes(tmp_ctrl_list,ctrl_type_list);
                    DEBUG_STREAM << "Found " << class_count << " OneDExpChannel Controller Classes in " << *ite << endl;
                    if (class_count != 0)
                        exit_search = true;
                }
                catch (Tango::DevFailed &e)
                {
                    DEBUG_STREAM << "Python file " << *ite << " is not a valid OneDExpChannel controller" << endl;
                }
            }
//
// Is it a Two D Exp Channel ctrl?
//

            if (exit_search == false)
            {			
                try
                {
                    class_count = 0;
                    PyTwoDCtrlFile tmp_ctrl_file(tmp_undef_ctrl);
                    class_count = tmp_ctrl_file.get_classes(tmp_ctrl_list,ctrl_type_list);
                    DEBUG_STREAM << "Found " << class_count << " TwoDExpChannel Controller Classes in " << *ite << endl;
                    if (class_count != 0)
                        exit_search = true;
                }
                catch (Tango::DevFailed &e)
                {
                    DEBUG_STREAM << "Python file " << *ite << " is not a valid TwoDExpChannel controller" << endl;
                }
            }
            
//
// Is it a Communication Channel ctrl?
//

            if (exit_search == false)
            {
                try
                {
                    class_count = 0;
                    PyComCtrlFile tmp_ctrl_file(tmp_undef_ctrl);
                    class_count = tmp_ctrl_file.get_classes(tmp_ctrl_list,ctrl_type_list);
                    DEBUG_STREAM << "Found " << class_count << " Communication Controller Classes in " << *ite << endl;
                    if (class_count != 0)
                        exit_search = true;
                }
                catch (Tango::DevFailed &e)
                {
                    DEBUG_STREAM << "Python file " << *ite << " is not a valid Communication controller" << endl;
                }
            }
//
// Is it a IORegister ctrl?
//

            if (exit_search == false)
            {
                try
                {
                    class_count = 0;
                    PyIORegisterCtrlFile tmp_ctrl_file(tmp_undef_ctrl);
                    class_count = tmp_ctrl_file.get_classes(tmp_ctrl_list,ctrl_type_list);
                    DEBUG_STREAM << "Found " << class_count << " IORegister Controller Classes in " << *ite << endl;
                    if (class_count != 0)
                        exit_search = true;
                }
                catch (Tango::DevFailed &e)
                {
                    DEBUG_STREAM << "Python file " << *ite << " is not a valid IORegister controller" << endl;
                    throw;
                }
            }

            for (long loop = 0;loop < class_count;loop++)
            {
                // <class name> '('<full file name>')' <type>
                string &tmp_ctrl = tmp_ctrl_list[loop];
                string tmp_str = tmp_ctrl.substr(tmp_ctrl.find('.') + 1);
                tmp_str += " (" + *ite + ") ";
                tmp_str += ctrl_type_list[loop];
                py_ctrl_classes.push_back(tmp_str);
            }
        }
        catch (Tango::DevFailed &e)
        {
            DEBUG_STREAM << "Python file " << *ite << " is not a valid controller" << endl;
        }
    }

//
// Fill in the array used to return attribute value
// after merging the 2 classes et in the Cpp vector
//

    cpp_ctrl_classes.insert(cpp_ctrl_classes.end(),py_ctrl_classes.begin(),py_ctrl_classes.end());
    sort(cpp_ctrl_classes.begin(),cpp_ctrl_classes.end());

    unsigned long nb_classes = cpp_ctrl_classes.size();
    for(unsigned long i = 0; i < nb_classes; i++)
    {
        ctrl_class_list[i] = const_cast<char *>(cpp_ctrl_classes[i].c_str());
        DEBUG_STREAM << "Adding class " << ctrl_class_list[i] << endl;
    }

    attr.set_value(ctrl_class_list, nb_classes);
}

//+----------------------------------------------------------------------------
//
// method : 		Pool::read_PseudoMotorList
//
// description : 	Extract real attribute values for PseudoMotorList acquisition result.
//
//-----------------------------------------------------------------------------
void Pool::read_PseudoMotorList(Tango::Attribute &attr)
{
    DEBUG_STREAM << "Pool::read_PseudoMotorList(Tango::Attribute &attr) entering... "<< endl;

    int32_t l = 0;
    PoolElementTypeIt elem_it, elem_end;
    
    for(get_all_pseudo_motor(elem_it, elem_end); elem_it != elem_end; ++elem_it, ++l)
    {
        PseudoMotorPool &pm_pool = get_pseudo_motor(elem_it->second);
        pseudo_motor_name_list[l] = const_cast<char *>(pm_pool.user_full_name_extra.c_str());
    }

    attr.set_value(pseudo_motor_name_list, get_pseudo_motor_nb());
}

//+----------------------------------------------------------------------------
//
// method : 		Pool::read_MotorGroupList
//
// description : 	Extract real attribute values for MotorGroupList acquisition result.
//
//-----------------------------------------------------------------------------
void Pool::read_MotorGroupList(Tango::Attribute &attr)
{
    DEBUG_STREAM << "Pool::read_MotorGroupList(Tango::Attribute &attr) entering... "<< endl;

    int32_t l = 0;
    PoolElementTypeIt elem_it, elem_end;
    
    for(get_all_motor_group(elem_it, elem_end); elem_it != elem_end; ++elem_it, ++l)
    {
        MotorGroupPool &motor_group_pool = get_motor_group(elem_it->second);
        motor_group_name_list[l] = const_cast<char *>(motor_group_pool.user_full_name.c_str());
    }

    attr.set_value(motor_group_name_list, get_motor_group_nb());
}

//+----------------------------------------------------------------------------
//
// method : 		Pool::read_SimulationMode
//
// description : 	Extract real attribute values for SimulationMode acquisition result.
//
//-----------------------------------------------------------------------------
void Pool::read_SimulationMode(Tango::Attribute &attr)
{
    DEBUG_STREAM << "Pool::read_SimulationMode(Tango::Attribute &attr) entering... "<< endl;

    attr.set_value(attr_SimulationMode_read);
}

//+----------------------------------------------------------------------------
//
// method : 		Pool::write_SimulationMode
//
// description : 	Write SimulationMode attribute values to hardware.
//
//-----------------------------------------------------------------------------
void Pool::write_SimulationMode(Tango::WAttribute &attr)
{
    DEBUG_STREAM << "Pool::write_SimulationMode(Tango::WAttribute &attr) entering... "<< endl;
    bool old_simu = attr_SimulationMode_write;
    attr.get_write_value(attr_SimulationMode_write);
    DEBUG_STREAM << "Wanted simulationMode = " << attr_SimulationMode_write << endl;

//
// Do nothing if the new value is the same one than the other
//

    if (old_simu == attr_SimulationMode_write)
        return;

//
// Send this new value to all Motors devices
//

    for (PoolElementTypeIt elem_it = element_types.lower_bound(MOTOR_ELEM);
         elem_it != element_types.upper_bound(MOTOR_ELEM); ++elem_it)
    {
        MotorPool &motor_pool = get_physical_motor(elem_it->second);
        Motor_ns::Motor *mot = get_motor_device(motor_pool);
        
        Tango::AutoTangoMonitor sync(mot);
        bool allo = mot->is_SimulationMode_allowed(Tango::WRITE_REQ);
        if (allo == true)
        {
            motor_pool.set_simulation_mode(attr_SimulationMode_write);
            if ((attr_SimulationMode_write == false) && (old_simu == true))
                mot->restore_att_values();
            else
                mot->save_att_values();
        }
        else
        {
            attr_SimulationMode_write = old_simu;
            
            for (PoolElementTypeIt ite_except = element_types.lower_bound(MOTOR_ELEM);
                 ite_except != elem_it; ++ite_except)
            {
                MotorPool &motor_pool_except = get_physical_motor(ite_except->second);
                Motor_ns::Motor *mot_except = get_motor_device(motor_pool_except);
                
                Tango::AutoTangoMonitor sy(mot_except);
                motor_pool_except.set_simulation_mode(attr_SimulationMode_write);
            }

            TangoSys_OMemStream o;
            o << "It is actually not allowed to switch motor ";
            o << motor_pool.name << " (" << motor_pool.get_full_name() << ") ";
            o << "to simulation mode (Motor moving)" << ends;

            Tango::Except::throw_exception((const char *)"Pool_MotorMoving",o.str(),
                            (const char *)"Pool::write_SimulationMode");
        }
    }

//
// Send the new value also to CT
//
    for (PoolElementTypeIt elem_it = element_types.lower_bound(COTI_ELEM);
         elem_it != element_types.upper_bound(COTI_ELEM); ++elem_it)
    {
        CTExpChannelPool &ct_pool = get_countertimer(elem_it->second);
        CTExpChannel_ns::CTExpChannel *ct = get_countertimer_device(elem_it->second);
        
        Tango::AutoTangoMonitor sync(ct);
        bool allow = ct->is_SimulationMode_allowed(Tango::WRITE_REQ);
        if (allow == true)
        {
            ct_pool.set_simulation_mode(attr_SimulationMode_write);
        }
        else
        {
            attr_SimulationMode_write = old_simu;
            for (PoolElementTypeIt elem_it_except = element_types.lower_bound(COTI_ELEM);
                 elem_it_except != elem_it ; ++elem_it_except)
            {
                CTExpChannelPool &ct_pool_except = get_countertimer(elem_it_except->second);
                CTExpChannel_ns::CTExpChannel *ct_except = 
                    get_countertimer_device(ct_pool_except);
                
                Tango::AutoTangoMonitor sy(ct_except);
                ct_pool_except.set_simulation_mode(attr_SimulationMode_write);
            }

            TangoSys_OMemStream o;
            o << "It is actually not allowed to switch Counter/Timer ";
            o << ct_pool.name << " (" << ct_pool.get_full_name() << ") ";
            o << "to simulation mode" << ends;

            Tango::Except::throw_exception((const char *)"Pool_CTMoving",o.str(),
                            (const char *)"Pool::write_SimulationMode");
        }
    }

//
// Send the new value also to ZeroDExpChannel
//
    for (PoolElementTypeIt elem_it = element_types.lower_bound(ZEROD_ELEM);
         elem_it != element_types.upper_bound(ZEROD_ELEM); ++elem_it)
    {
        ZeroDExpChannelPool &zerod_pool = get_zerod(elem_it->second);
        ZeroDExpChannel_ns::ZeroDExpChannel *zerod = get_zerod_device(elem_it->second);
    
        Tango::AutoTangoMonitor sync(zerod);
        bool allo = zerod->is_SimulationMode_allowed(Tango::WRITE_REQ);
        if (allo == true)
        {
            zerod_pool.set_simulation_mode(attr_SimulationMode_write);
            if ((attr_SimulationMode_write == false) && (old_simu == true))
                zerod->restore_att_values();
            else
                zerod->save_att_values();
        }
        else
        {
            attr_SimulationMode_write = old_simu;
            
            for (PoolElementTypeIt elem_it_except = element_types.lower_bound(ZEROD_ELEM);
                 elem_it_except != elem_it ; ++elem_it_except)
            {
                ZeroDExpChannelPool &zerod_pool_except = get_zerod(elem_it_except->second);
                ZeroDExpChannel_ns::ZeroDExpChannel *zerod_except = 
                    get_zerod_device(zerod_pool_except);
                
                Tango::AutoTangoMonitor sy(zerod_except);
                zerod_pool_except.set_simulation_mode(attr_SimulationMode_write);
            }

            TangoSys_OMemStream o;
            o << "It is actually not allowed to switch ZeroDExpChannel ";
            o << zerod_pool.name << " (" << zerod_pool.get_full_name() << ") ";
            o << "to simulation mode" << ends;

            Tango::Except::throw_exception((const char *)"Pool_0DMoving",o.str(),
                            (const char *)"Pool::write_SimulationMode");
        }
    }
    
//
// Send the new value also to OneDExpChannel
//
    
    for (PoolElementTypeIt elem_it = element_types.lower_bound(ONED_ELEM);
         elem_it != element_types.upper_bound(ONED_ELEM); ++elem_it)
    {
        OneDExpChannelPool &oned_pool = get_oned(elem_it->second);
        OneDExpChannel_ns::OneDExpChannel *oned = get_oned_device(oned_pool);
    
        Tango::AutoTangoMonitor sync(oned);
        bool allo = oned->is_SimulationMode_allowed(Tango::WRITE_REQ);
        if (allo == true)
        {
            oned_pool.set_simulation_mode(attr_SimulationMode_write);
            if ((attr_SimulationMode_write == false) && (old_simu == true))
                oned->restore_att_values();
            else
                oned->save_att_values();
        }
        else
        {
            attr_SimulationMode_write = old_simu;
            for (PoolElementTypeIt elem_it_except = element_types.lower_bound(ONED_ELEM);
                 elem_it_except != elem_it ; ++elem_it_except)
            {
                OneDExpChannelPool &oned_pool_except = get_oned(elem_it_except->second);
                OneDExpChannel_ns::OneDExpChannel *oned_except =
                    get_oned_device(oned_pool_except);

                Tango::AutoTangoMonitor sy(oned_except);
                oned_pool_except.set_simulation_mode(attr_SimulationMode_write);
            }
            
            TangoSys_OMemStream o;
            o << "It is actually not allowed to switch OneDExpChannel ";
            o << oned_pool.name << " (" << oned_pool.get_full_name() << ") ";
            o << "to simulation mode" << ends;
    
            Tango::Except::throw_exception(
                                (const char *)"Pool_1DMoving",o.str(),
                                (const char *)"Pool::write_SimulationMode");
        }
    }

//
// Send the new value also to TwoDExpChannel
//
    
    for (PoolElementTypeIt elem_it = element_types.lower_bound(TWOD_ELEM);
         elem_it != element_types.upper_bound(TWOD_ELEM); ++elem_it)
    {
        TwoDExpChannelPool &twod_pool = get_twod(elem_it->second);
        TwoDExpChannel_ns::TwoDExpChannel *twod = get_twod_device(twod_pool);
    
        Tango::AutoTangoMonitor sync(twod);
        bool allo = twod->is_SimulationMode_allowed(Tango::WRITE_REQ);
        if (allo == true)
        {
            twod_pool.set_simulation_mode(attr_SimulationMode_write);
            if ((attr_SimulationMode_write == false) && (old_simu == true))
                twod->restore_att_values();
            else
                twod->save_att_values();
        }
        else
        {
            attr_SimulationMode_write = old_simu;
            for (PoolElementTypeIt elem_it_except = element_types.lower_bound(TWOD_ELEM);
                 elem_it_except != elem_it ; ++elem_it_except)
            {
                TwoDExpChannelPool &twod_pool_except = get_twod(elem_it_except->second);
                TwoDExpChannel_ns::TwoDExpChannel *twod_except =
                    get_twod_device(twod_pool_except);

                Tango::AutoTangoMonitor sy(twod_except);
               twod_pool_except.set_simulation_mode(attr_SimulationMode_write);
            }
            
            TangoSys_OMemStream o;
            o << "It is actually not allowed to switch TwoDExpChannel ";
            o << twod_pool.name << " (" << twod_pool.get_full_name() << ") ";
            o << "to simulation mode" << ends;
    
            Tango::Except::throw_exception(
                                (const char *)"Pool_2DMoving",o.str(),
                                (const char *)"Pool::write_SimulationMode");
        }
    }
    
//
// Send the new value also to Communication channels
//
    for (PoolElementTypeIt elem_it = element_types.lower_bound(COM_ELEM);
         elem_it != element_types.upper_bound(COM_ELEM); ++elem_it)
    {
        CommunicationChannelPool &comch_pool = 
                            get_communication_channel(elem_it->second);
        CommunicationChannel_ns::CommunicationChannel *comch = 
                            get_communication_channel_device(comch_pool);
    
        Tango::AutoTangoMonitor sync(comch);
        bool allo =comch->is_SimulationMode_allowed(Tango::WRITE_REQ);
        if (allo == true)
        {
            comch_pool.set_simulation_mode(attr_SimulationMode_write);
        }
        else
        {
            attr_SimulationMode_write = old_simu;
            for (PoolElementTypeIt elem_it_except = element_types.lower_bound(COM_ELEM);
                 elem_it_except != elem_it ; ++elem_it_except)
            {            
                CommunicationChannelPool &comch_pool_except = 
                            get_communication_channel(elem_it_except->second);
                CommunicationChannel_ns::CommunicationChannel *comch_except = 
                    get_communication_channel_device(comch_pool_except);
                Tango::AutoTangoMonitor sy(comch_except);
                comch_pool_except.set_simulation_mode(attr_SimulationMode_write);
            }

            TangoSys_OMemStream o;
            o << "It is actually not allowed to switch CommunicationChannel ";
            o << comch_pool.name << " (" << comch_pool.get_full_name() << ") ";
            o << "to simulation mode" << ends;

            Tango::Except::throw_exception(
                            (const char *)"Pool_ComChMoving", o.str(),
                            (const char *)"Pool::write_SimulationMode");
        }
    }

//
// Send the new value also to IORegisters
//
    for (PoolElementTypeIt elem_it = element_types.lower_bound(IOREGISTER_ELEM);
         elem_it != element_types.upper_bound(IOREGISTER_ELEM); ++elem_it)
    {
        IORegisterPool &ior_pool = get_ioregister(elem_it->second);
        IORegister_ns::IORegister *ioregister = get_ioregister_device(ior_pool);
    
        Tango::AutoTangoMonitor sync(ioregister);
        bool allo = ioregister->is_SimulationMode_allowed(Tango::WRITE_REQ);
        if (allo == true)
        {
            ior_pool.set_simulation_mode(attr_SimulationMode_write);
        }
        else
        {
            attr_SimulationMode_write = old_simu;
            for (PoolElementTypeIt elem_it_except = element_types.lower_bound(IOREGISTER_ELEM);
                 elem_it_except != elem_it ; ++elem_it_except)
            {
                IORegisterPool &ior_pool_except = get_ioregister(elem_it_except->second);
                IORegister_ns::IORegister *ioregister_except = 
                    get_ioregister_device(elem_it_except->second);
                    
                Tango::AutoTangoMonitor sy(ioregister_except);
                ior_pool_except.set_simulation_mode(attr_SimulationMode_write);
            }

            TangoSys_OMemStream o;
            o << "It is actually not allowed to switch CommunicationChannel ";
            o << ior_pool.name << " (" << ior_pool.get_full_name() << ") ";
            o << "to simulation mode" << ends;

            Tango::Except::throw_exception(
                            (const char *)"Pool_ComChMoving", o.str(),
                            (const char *)"Pool::write_SimulationMode");
        }
    }

//
// Push a change_event to inform client listenning on event
//

    read_SimulationMode(attr);
    attr.fire_change_event();
}

//+----------------------------------------------------------------------------
//
// method : 		Pool::read_MotorList
//
// description : 	Extract real attribute values for MotorList acquisition result.
//
//-----------------------------------------------------------------------------
void Pool::read_MotorList(Tango::Attribute &attr)
{
    DEBUG_STREAM << "Pool::read_MotorList(Tango::Attribute &attr) entering... "<< endl;

    int32_t l = 0;
    PoolElementTypeIt elem_it, elem_end;
    
    for(get_all_physical_motor(elem_it, elem_end); elem_it != elem_end; ++elem_it, ++l)
    {
        MotorPool &motor_pool = get_physical_motor(elem_it->second);
        motor_name_list[l] = const_cast<char *>(motor_pool.user_full_name.c_str());
    }

    for(get_all_pseudo_motor(elem_it, elem_end); elem_it != elem_end; ++elem_it, ++l)
    {
        PseudoMotorPool &pm_pool = get_pseudo_motor(elem_it->second);
        motor_name_list[l] = const_cast<char *>(pm_pool.user_full_name_extra.c_str());
    }

    attr.set_value(motor_name_list, l);
}

//+----------------------------------------------------------------------------
//
// method : 		Pool::read_ControllerList
//
// description : 	Extract real attribute values for ControllerList acquisition result.
//
//-----------------------------------------------------------------------------
void Pool::read_ControllerList(Tango::Attribute &attr)
{
    DEBUG_STREAM << "Pool::read_ControllerList(Tango::Attribute &attr) entering... "<< endl;

    int32_t l = 0;
    PoolElementTypeIt elem_it, elem_end;
    
    for(get_all_controller(elem_it, elem_end); elem_it != elem_end; ++elem_it, ++l)
    {
        ControllerPool &ctrl = get_controller(elem_it->second);
        ctrl_name_list[l] = const_cast<char *>(ctrl.user_full_name.c_str());
    }

    attr.set_value(ctrl_name_list, l);
}

//+------------------------------------------------------------------
/**
 *	method:	Pool::create_controller
 *
 *	description:	method to execute "CreateController"
 *	This command creates a controller object in the pool. Each controller code has to be defined as a shared library
 *	and the user LD_LIBRARY_PATH environment variable has to be correctly set to find the controller shared library.
 *	Each controller shared library has to have a C function called "_create_<Controller name>" to create a controller object.
 *	This command has four arguments which are :
 *
 *	1 - The controller device type (Motor, Ccd,....)
 *	2 - The controller shared library name (Cpp or Python)
 *	3 - The controller name
 *	4 - The controller instance name
 *
 *	Each controller is represented in the pool device by a separate object. If you have several instance of the same controller
 *	within a pool, the instance name is used to retrieve the correct instance.
 *
 * @param	argin	in[0] = Controller dev type, in[1] = Controller lib, in[2] = Controller name, in[3] = Instance name
 *
 */
//+------------------------------------------------------------------
void Pool::create_controller(const Tango::DevVarStringArray *argin)
{
    DEBUG_STREAM << "Pool::create_controller(): entering... !" << endl;
    //	Add your own code to control device here
    add_ctrl(argin);
}

//------------------------------------------------------------------------------
// Pool::delete_element
//
void Pool::delete_element(const Tango::DevString argin)
{
    DEBUG_STREAM << "Pool::delete_element(): entering... !" << endl;
    
    //	Add your own code to control device here
    Tango::Except::throw_exception(
        (const char *)"Pool_FeatureNotImplemented",
        (const char *)"This feature has not been implemented yet",
        (const char *)"Pool::delete_element");	    
}

//------------------------------------------------------------------------------
// Pool::rename_element
//
void Pool::rename_element(const Tango::DevVarStringArray *argin)
{
    DEBUG_STREAM << "Pool::rename_element(): entering... !" << endl;
    
    int32_t len = argin->length();
    if(len < 2)
    {
        Tango::Except::throw_exception(
            (const char *)"Pool_WrongArgumentNumber",
            (const char *)"Wrong number of argument for command RenameElement. Needs at least 2 strings",
            (const char *)"Pool::rename_element");
    }
    
    string old_alias((*argin)[0]);
    string new_alias((*argin)[1]);
    
    ElemSet deps;
    rename_element(old_alias, new_alias, deps);
}

void Pool::create_element(const Tango::DevVarStringArray *argin)
{
    DEBUG_STREAM << "Pool::create_element(): entering... !" << endl;
    
    //	Add your own code to control device here
    Tango::Except::throw_exception(
        (const char *)"Pool_FeatureNotImplemented",
        (const char *)"This feature has not been implemented yet",
        (const char *)"Pool::create_element");	

    
}

//+------------------------------------------------------------------
/**
 *	method:	Pool::create_motor
 *
 *	description:	method to execute "CreateMotor"
 *	This command creates a new motor in the pool. It has three arguments which are
 *	1 - The controller name (its instance name)
 *	2 - The motor number within the controller
 *	3 - The motor name. The motor name is a Tango alias and does not have any '/' characters.
 *	4 - The motor tango device name (optional default is: motor/<controller instance name>/<axis>)
 *	This command creates a Tango device with a Tango name set to
 *	"motor/controller_instance_name/motor_number"
 *	and with an alias as given by the user in the command parameter.
 *	All the created motors are automatically re-created at pool device startup time.
 *
 * @param	argin	long[0] = Motor number in Ctrl, string[0] = Motor name, string[1] = Controller instance name
 *
 */
//+------------------------------------------------------------------
void Pool::create_motor(const Tango::DevVarLongStringArray *argin)
{
    DEBUG_STREAM << "Pool::create_motor(): entering... !" << endl;

    //	Add your own code to control device here

    int32_t l_len = argin->lvalue.length();
    int32_t str_len = argin->svalue.length();

    if ((l_len != 1) || (str_len < 2))
    {
        Tango::Except::throw_exception(
            (const char *)"Pool_WrongArgumentNumber",
            (const char *)"Wrong number of argument for command CreateMotor. Needs 1 long and at least 2 strings",
            (const char *)"Pool::create_controller");
    }

    Tango::DevLong motor_idx = argin->lvalue[0];
    string ctrl_inst_name(argin->svalue[1]);
    string mot_name(argin->svalue[0]);
    ControllerPool &mot_ctrl = get_controller(ctrl_inst_name, true);
    
    ElementId ctrl_id = mot_ctrl.id;

    DEBUG_STREAM << "Controller ID = " << ctrl_id << endl;
    DEBUG_STREAM << "Motor index = " << motor_idx << endl;
    DEBUG_STREAM << "Motor name = " << mot_name << endl;

//
// Check if the controller has been successfully constructed
//

    if (!mot_ctrl.get_controller())
    {
        Tango::Except::throw_exception(
            (const char *)"Pool_WrongControllerId",
            (const char *)"Can't create a motor on a non-responding controller",
            (const char *)"Pool::create_motor");
    }

//
// Check if we don't have already enough motors
//

    DEBUG_STREAM << "Checking motor number" << endl;

    if (get_physical_motor_nb() == MAX_MOTOR)
    {
        Tango::Except::throw_exception(
            (const char *)"Pool_TooManyMotor",
            (const char *)"Too many motor in your pool",
            (const char *)"Pool::create_motor");
    }

//
// Check that the controller still have some motors available
//

    if (mot_ctrl.nb_dev == mot_ctrl.MaxDevice)
    {
        TangoSys_OMemStream o;
        o << "Max number of motor reached (" << mot_ctrl.MaxDevice << ")"
          << ends;

        Tango::Except::throw_exception(
                (const char *)"Pool_MaxNbMotorInCtrl",o.str(),
                (const char *)"Pool::create_motor()");
    }

//
// Build Tango device name
//
    string tg_dev_name = "";
    if (str_len >= 3)
    {
        tg_dev_name = argin->svalue[2];
    }
    else
    {
        stringstream s;
        s << motor_idx;

        tg_dev_name = "motor/" + mot_ctrl.name + '/' + s.str();
    }

    DEBUG_STREAM << "Tango device name = " << tg_dev_name << endl;

//
// Check if this device is already defined in database
// Check by device alias and by Tango device name
//

    Tango::Util *tg = Tango::Util::instance();
    Tango::Database *db = tg->get_database();

    Tango::DbDevImportInfo my_device_import;
    bool device_exist = false;
    bool by_alias = false;

    try
    {
        my_device_import = db->import_device(mot_name);
        device_exist = true;
        by_alias = true;
    }
    catch (Tango::DevFailed &e)
    {
        if (::strcmp(e.errors[0].reason.in(),"DB_DeviceNotDefined") != 0)
        {
            device_exist = true;
        }
    }

    if (device_exist == false)
    {
        try
        {
            my_device_import = db->import_device(tg_dev_name);
            device_exist = true;
        }
        catch (Tango::DevFailed &e)
        {
            if (::strcmp(e.errors[0].reason.in(),"DB_DeviceNotDefined") != 0)
            {
                device_exist = true;
            }
        }
    }

    if (device_exist == true)
    {
        TangoSys_OMemStream o;
        o << "Motor ";
        if (by_alias == false)
            o << "device name " << tg_dev_name;
        else
            o << "name " << mot_name;
        o << " is already defined" << ends;
        
        Tango::Except::throw_exception(
                (const char *)"Pool_WrongMotorName",o.str(),
                (const char *)"Pool::create_motor");
    }

//
// If the device is not defined in database, create it in database, set its
// alias, define the property used to store its ID (called motor_id) and create
// the default abs_change property for the Position attribute
//

    if (device_exist == false)
    {
        DEBUG_STREAM << "Trying to create device entry in database" << endl;

        try
        {
            Tango::DbDevInfo my_device_info;
            my_device_info.name = tg_dev_name.c_str();
            my_device_info._class = "Motor";
            my_device_info.server = tg->get_ds_name().c_str();

            db->add_device(my_device_info);

            db->put_device_alias(tg_dev_name, mot_name);

            Tango::DbDatum db_id(ID_PROP);
            Tango::DbData db_data;
            ElementId mot_id = get_new_id();
            db_id << (Tango::DevLong)mot_id;
            
            Tango::DbDatum db_ctrl_id(CTRL_ID_PROP);
            db_ctrl_id << (Tango::DevLong)ctrl_id;

            Tango::DbDatum db_axis(AXIS_PROP);
            db_axis << motor_idx;
            
            db_data.push_back(db_id);
            db_data.push_back(db_ctrl_id);
            db_data.push_back(db_axis);
            
            if (str_len > 2)
            {
                string desc_str(argin->svalue[2]);
                Tango::DbDatum desc("Description");
                desc << desc_str;
                db_data.push_back(desc);
            }
            db->put_device_property(tg_dev_name.c_str(),db_data);

            Tango::DbDatum pos("Position"),abs_ch("abs_change");
            db_data.clear();
            pos << (long)1;
            abs_ch << defaultMotPos_AbsChange;
            db_data.push_back(pos);
            db_data.push_back(abs_ch);
            db->put_device_attribute_property(tg_dev_name.c_str(),db_data);

            DEBUG_STREAM << "Device created in database (with alias)" << endl;
        }
        catch (Tango::DevFailed &e)
        {
            DEBUG_STREAM << "Gasp an exception........" << endl;
            TangoSys_OMemStream o;
            o << "Can't create motor " << mot_name << " in database" << ends;

            Tango::Except::re_throw_exception(e,
                    (const char *)"Pool_CantCreateMotor",o.str(),
                    (const char *)"Pool::create_motor");
        }

//
// Find the Tango Motor class and create the motor
//

        const vector<Tango::DeviceClass *> *cl_list = tg->get_class_list();
        for (unsigned long i = 0;i < cl_list->size();i++)
        {
            if ((*cl_list)[i]->get_name() == "Motor")
            {
                try
                {
                    Tango::DevVarStringArray na;
                    na.length(1);
                    na[0] = tg_dev_name.c_str();
                    (*cl_list)[i]->device_factory(&na);
                    break;
                }
                catch (Tango::DevFailed &e)
                {
                    DEBUG_STREAM << "Exception while trying to create Motor device" << endl;

//
// Check if this motor has already been added into pool structures
// If yes, remove it from pool structures
//

                    try
                    {   
                        DevicePool::remove_element(mot_name, false);
                    }
                    catch (...) {}

//
// The delete_device will also delete device property(ies)
//

                    db->delete_device(tg_dev_name);

                    TangoSys_OMemStream o;
                    o << "Can't create motor device " << mot_name << ends;

                    Tango::Except::re_throw_exception(e,
                            (const char *)"Pool_CantCreateMotor",o.str(),
                            (const char *)"Pool::create_motor");
                }
            }
        }

//
// Create a Tango device proxy on the newly created motor
// and set its connection to automatic re-connection
//
        MotorPool &motor_pool = get_physical_motor(mot_name);
        Tango::DeviceProxy *tmp_dev =
            new Tango::DeviceProxy(motor_pool.get_full_name().c_str());
        tmp_dev->set_transparency_reconnection(true);
        
        Motor_ns::Motor *dev = static_cast<Motor_ns::Motor*>
            (tg->get_device_by_name(motor_pool.get_full_name()));

        set_tango_element(motor_pool, tmp_dev, dev);
    }

//
// Inform ghost group that there is a new motor
//

    MotorGroup_ns::MotorGroup *ghost_ptr = get_ghost_motor_group_ptr();
    {
        Tango::AutoTangoMonitor atm(ghost_ptr);
        MotorPool &motor_pool = get_physical_motor(mot_name);
        ghost_ptr->add_motor_to_ghost_group(motor_pool.id);
    }

//
// Push a change event for client listening on event
//

    Tango::Attribute &ml = dev_attr->get_attr_by_name("MotorList");
    read_MotorList(ml);
    ml.fire_change_event();
}

//+------------------------------------------------------------------
/**
 *	method:	Pool::delete_motor
 *
 *	description:	method to execute "DeleteMotor"
 *	Delete a motor from its name
 *	Once a motor is deleted, it is not available any more. All its information have been
 *	removed from the database
 *
 * @param	argin	Motor name
 *
 */
//+------------------------------------------------------------------
void Pool::delete_motor(Tango::DevString argin)
{
    DEBUG_STREAM << "Pool::delete_motor(): entering... with argin = " << argin << endl;
    //	Add your own code to control device here

//
// Find motor in motor list
//

    string user_name(argin);
    MotorPool &mot_to_del = get_physical_motor(user_name, true);

    DEBUG_STREAM << "Motor found" << endl;
//
// Check that the motor is not moving
//

    if (get_element_proxy(mot_to_del)->state() == Tango::MOVING)
    {
        TangoSys_OMemStream o;
        o << "Can't delete motor with name " << argin;
        o << ". It is actually moving." << ends;

        Tango::Except::throw_exception((const char *)"Pool_CantDeleteMotor",o.str(),
                                 (const char *)"Pool::delete_motor");
    }

//
// Check that the motor is not member of a motor group
//
    
    for (PoolElementTypeIt elem_it = element_types.lower_bound(MOTOR_GROUP_ELEM);
         elem_it != element_types.upper_bound(MOTOR_GROUP_ELEM); ++elem_it)
    {
        MotorGroupPool &mgp = get_motor_group(elem_it->second);

        if (find(mgp.mot_ids.begin(), mgp.mot_ids.end(), mot_to_del.id) != mgp.mot_ids.end())
        {
            TangoSys_OMemStream o;
            o << "Can't delete motor with name " << argin;
            o << ". It is actually member of group " << mgp.name << ends;

            Tango::Except::throw_exception((const char *)"Pool_CantDeleteMotor",o.str(),
                                     (const char *)"Pool::delete_motor");
        }
    }

//
// If this command is used after a Abort command, check that the pool
// internal thread has finished its job
//

    long wait_ctr = 0;
    struct timespec wait,rem;

    wait.tv_sec = 0;
    wait.tv_nsec = 10000000;

    Motor_ns::Motor *mot_dev = get_motor_device(mot_to_del);
    while (mot_dev->get_mov_th_id() != 0)
    {
        nanosleep(&wait, &rem);
        wait_ctr++;

        if (wait_ctr == 3)
        {
            TangoSys_OMemStream o;
            o << "Can't delete motor with name " << argin;
            o << ". The pool internal thread still uses it" << ends;

            Tango::Except::throw_exception((const char *)"Pool_CantDeleteMotor",o.str(),
                                            (const char *)"Pool::delete_motor");
        }
    }

//
// Remove its entry in database. This will also delete any device
// properties and device attribute properties
//
    Tango::Util *tg = Tango::Util::instance();
    try
    {
        tg->get_database()->delete_device(mot_to_del.get_full_name());

//
// Delete motor device from server but first find its Tango xxxClass instance
//
        Motor_ns::Motor *mot_dev = get_motor_device(mot_to_del);
        Tango::DeviceClass *dc = mot_dev->get_device_class();
        dc->device_destroyer(mot_to_del.get_full_name());
    }
    catch (Tango::DevFailed &e)
    {
        TangoSys_OMemStream o;
        o << "Can't delete motor with name " << argin << ends;

        Tango::Except::re_throw_exception(e,(const char *)"Pool_CantDeleteMotor",o.str(),
                                 (const char *)"Pool::delete_motor");
    }

//
// Before returning, send a change event for client listenning
// on event
//

    Tango::Attribute &ml = dev_attr->get_attr_by_name("MotorList");
    read_MotorList(ml);
    ml.fire_change_event();
}

//+------------------------------------------------------------------
/**
 *	method:	Pool::dev_state
 *
 *	description:	method to execute "State"
 *	This command gets the device state (stored in its <i>device_state</i> data member) and returns it to the caller.
 *
 * @return	State Code
 *
 */
//+------------------------------------------------------------------
Tango::DevState Pool::dev_state()
{
//	Tango::DevState	argout = DeviceImpl::dev_state();
    DEBUG_STREAM << "Pool::dev_state(): entering... !" << endl;

    //	Add your own code to control device here

//
// If the moving_state_requested is set to true, this means that we have received
// an order to die while a motar was moving. In this case, set state to Moving
//

    if (moving_state_requested == true)
        set_state(Tango::MOVING);
    else
    {

//
// Check each controller state
//

        bool all_ok = true;

        string &_status = get_status();
        _status.clear();

        for (PoolElementTypeIt ctrl_it = element_types.lower_bound(CTRL_ELEM);
             ctrl_it !=element_types.upper_bound(CTRL_ELEM); ++ctrl_it)
        {
            ControllerPool &ctrlpool = get_controller(ctrl_it->second);
            if(!ctrlpool.get_controller())
            {
                set_state(Tango::ALARM);
                all_ok = false;
            }
        }
        
//
// If all controller are OK, set state to ON
// and status to default one
//

        if (all_ok == true)
        {
            set_state(Tango::ON);
            _status = StatusNotSet;
        }
    }

    Tango::DevState argout = DeviceImpl::dev_state();
    return argout;
}

//+------------------------------------------------------------------
/**
 *	method:	Pool::reload_controller_code
 *
 *	description:	method to execute "ReloadControllerCode"
 *	This command reloads controller code in the device server process. For C++ controller, it will
 *	unload and load the controller shared library and for Python controller, it will re-load the controller module.
 *
 * @param	argin	Controller file name
 *
 */
//+------------------------------------------------------------------
void Pool::reload_controller_code(Tango::DevString argin)
{
    DEBUG_STREAM << "Pool::reload_controller_code(): entering... !" << endl;
    //	Add your own code to control device here

//
//Check that we receive only a file name and not a path
//

    string in_file(argin);
    if (in_file.find('/') != string::npos)
    {
        TangoSys_OMemStream o;
        o << in_file << " is not a valid file. Only file name is valid ";
        o << "not path" << ends;

        Tango::Except::throw_exception(
                (const char *)"Pool_FileUnsupportedType",o.str(),
                (const char *)"Pool::unload_controller_code");
    }



//
// Check which controller we have with this file name
//

    vector<Pool::CtrlBkp> ctrls;
    CtrlType ctrl_dev_type = UNDEF_CTRL;

    PoolElementTypeIt ctrl_it;
    PoolElementTypeIt ctrl_beg, ctrl_end;
    get_all_controller(ctrl_beg, ctrl_end);
    for (ctrl_it = ctrl_beg; ctrl_it != ctrl_end; ++ctrl_it)
    {
        ControllerPool &ctrl = get_controller(ctrl_it->second);

        const std::string &f_name = f_name_from_db_prop(ctrl.get_name());
        if (f_name == in_file)
        {
            Pool::CtrlBkp cb;
            cb.dist = distance(ctrl_beg, ctrl_it);
            cb.idx = ctrl.get_id();
            cb.good_old_ctrl = ctrl.get_controller();
            cb.wrong_fica = false;
            cb.fica_ite = ctrl.ite_ctrl_class;
            cb.old_fica_built = ctrl.ctrl_class_built;
            cb.fica_already_reloaded = false;
            ctrls.push_back(cb);
            string con_name = ctrl.name.substr(ctrl.name.find('.') + 1);
            ctrl_dev_type = dev_type_from_db_prop(con_name);
        }
    }

    if (ctrls.empty() == true)
    {
        TangoSys_OMemStream o;
        o << "No controller defined with file named " << argin << ends;

        Tango::Except::throw_exception(
                (const char *)"Pool_ControllerNotFound",o.str(),
                (const char *)"Pool::reload_controller_code");
    }

//
// Get Pool Class ptr
//

    PoolClass *po_class = static_cast<PoolClass *>(get_device_class());

//
// Check device. If their controller ID is the concerned controller,
// check that the controller code can be unloaded
// For motor, this means checking that the motor is not moving
//

    vector<Pool::ObjBkp> mots;

    switch (ctrl_dev_type)
    {
        case MOTOR_CTRL:
        find_and_invalidate_motor(ctrls,mots);
        break;

        case PSEUDO_MOTOR_CTRL:
        find_and_invalidate_pseudo_motor(ctrls,mots);
        break;

        case PSEUDO_COUNTER_CTRL:
        find_and_invalidate_pseudo_counter(ctrls,mots);
        break;

        case COTI_CTRL:
        find_and_invalidate_ct(ctrls,mots);
        break;

        case ZEROD_CTRL:
        find_and_invalidate_zerod(ctrls,mots);
        break;

        case ONED_CTRL:
        find_and_invalidate_oned(ctrls,mots);
        break;
        
        case TWOD_CTRL:
        find_and_invalidate_twod(ctrls,mots);
        break;        

        case COM_CTRL:
        find_and_invalidate_comch(ctrls,mots);
        break;

        case IOREGISTER_CTRL:
        find_and_invalidate_ioregister(ctrls,mots);
        break;

        case CONSTRAINT_CTRL:
        // constraint does not have any devices so there is no need to invalidate
        break;

        default:
        Tango::Except::throw_exception(
                (const char *)"Pool_BadCtrlType",
                (const char *)"Undefined controller type !!!",
                (const char *)"Pool::reload_controller_code");
        break;
    }

//
// Starting from this point, we might change the device state
//

    PoolStateEvent pse(this);

//
// Mark all concerned controller as unusable
//

    get_all_controller(ctrl_beg, ctrl_end);
    vector<Pool::CtrlBkp>::iterator ite;
    for (ite = ctrls.begin();ite != ctrls.end();++ite)
    {   
        ctrl_it = ctrl_beg;
        advance(ctrl_it, ite->dist);
        ControllerPool &ctrlpool = get_controller(ctrl_it->second);
        if (ctrlpool.ctrl_class_built == true)
        {
            AutoPoolLock lo(ctrlpool.get_ctrl_class_mon());
            Controller *ctrl = ctrlpool.get_controller();
            SAFE_DELETE(ctrl);
        }
        ctrlpool.set_controller(NULL);
    }

//
// Reload controller code
//

    Language ctrl_lang = UNDEF_LANG;
    bool reloaded = false;

    try
    {
        get_all_controller(ctrl_beg, ctrl_end);
        for (ite = ctrls.begin();ite != ctrls.end();++ite)
        {
            ctrl_it = ctrl_beg;
            advance(ctrl_it, ite->dist);
            ControllerPool &ctrlpool = get_controller(ctrl_it->second);

            if ((ite->wrong_fica == true) || (ite->fica_already_reloaded == true))
                continue;


            if (ctrlpool.ctrl_class_built == true)
            {
                ctrl_lang = ctrlpool.get_language();
                if (ctrl_lang == CPP)
                {
                    if (reloaded == false)
                    {
                        ctrlpool.reload();
                        reloaded = true;
                    }
                    (*(ctrlpool.ite_ctrl_class))->check_features(ctrl_lang,&ctrlpool.get_ctrl_file(),ctrlpool.ctrl_class_name);
                }
                else
                {

//
// Reload the new code and check that it is correct
//

                    AutoPoolLock lo(ctrlpool.get_ctrl_class_mon());
                    if (reloaded == false)
                    {
                        ctrlpool.reload();
                        reloaded = true;
                    }

                    (*(ctrlpool.ite_ctrl_class))->check_python(ctrlpool.ctrl_class_name);
                    (*(ctrlpool.ite_ctrl_class))->check_features(ctrl_lang,&ctrlpool.get_ctrl_file(),ctrlpool.ctrl_class_name);

//
// Reload a possible new list of properties
//

                    vector<PropertyData *> &prop_list = (*(ctrlpool.ite_ctrl_class))->get_ctrl_prop_list();
                    for (unsigned long loop = 0;loop < prop_list.size();loop++)
                        delete prop_list[loop];
                    prop_list.clear();

                    ctrlpool.get_ctrl_file().get_prop_info(ctrlpool.ctrl_class_name,prop_list);
                }
            }
            else
            {

//
// We need to try to re-create the FiCa
// Retrieve ctrl info in the entry coming from database.
//

                int32_t nb_ctrl = get_controller_nb();
                string::size_type pos;

                pos = ctrlpool.name.find('/');
                string ctrl = ctrlpool.name.substr(0,pos);
                string inst = ctrlpool.name.substr(pos + 1);
                int32_t ind_array = 0;

                for (int32_t l = 0;l < nb_ctrl;l++)
                {
                    string file_db = ctrl_info[(l * PROP_BY_CTRL) + 1];
                    string::size_type pos;
                    if ((pos = file_db.find('.')) != string::npos)
                        file_db.erase(pos);
                    string ctrl_db(file_db);
                    ctrl_db = ctrl_db + '.' + ctrl_info[(l * PROP_BY_CTRL) + 2];
                    string inst_db = ctrl_info[(l * PROP_BY_CTRL) + 3];
                    transform(ctrl_db.begin(),ctrl_db.end(),ctrl_db.begin(),::tolower);
                    transform(inst_db.begin(),inst_db.end(),inst_db.begin(),::tolower);
                    if ((ctrl_db == ctrl) && (inst_db == inst))
                    {
                        ind_array = l * PROP_BY_CTRL;
                        break;
                    }
                }

//
// Try to re-create FiCa entry from info stored in DB
//

                vector<string>::iterator v_ite = ctrl_info.begin();
                v_ite += ind_array;

//
// We here have 2 cases
//  1 - The FiCa has been correctly created but the properties are wrong.
//		We know that we are in this case because the FiCa is in the FiCa list
//		Then, we do not need to re-create it but we need to re-create the
//		property list because it could have changed
//  2 - The FiCa has not been built at all and then we need to build it
//

                PoolClass *cl_ptr = static_cast<PoolClass *>(this->get_device_class());
                bool re_create = true;
                try
                {
                    CtrlType ctrl_type = str_2_CtrlType(*v_ite);
                    vct_ite tmp_ite = cl_ptr->get_ctrl_fica_by_name(ctrlpool.ctrl_class_name,ctrl_type);
                    re_create = false;

                    vector<PropertyData *> &prop_list = (*tmp_ite)->get_ctrl_prop_list();
                    for (unsigned long loop = 0;loop < prop_list.size();loop++)
                        delete prop_list[loop];
                    prop_list.clear();

                    {
                        AutoPoolLock lo = AutoPoolLock(ctrlpool.get_ctrl_class_mon());
                        if (reloaded == false)
                        {
                            ctrlpool.reload();
                            reloaded = true;
                        }

                        ctrl_lang = PYTHON;
                        CtrlFiCa &ctrl_fica = *(*(ctrlpool.ite_ctrl_class));

                        ctrl_fica.check_python(ctrlpool.ctrl_class_name);

                        ctrl_fica.check_features(ctrl_lang,
                                        &ctrlpool.get_ctrl_file(),
                                        ctrlpool.ctrl_class_name);

                        (*tmp_ite)->get_ctrl_file()->get_prop_info(ctrlpool.ctrl_class_name,prop_list);
                    }
                }
                catch (Tango::DevFailed &e)
                {
                    if (re_create == true)
                    {
                        CtrlType ctrl_type = str_2_CtrlType(*v_ite);
                        ctrlpool.ite_ctrl_class = cl_ptr->add_ctrl_fica(ctrlpool.ctrl_class_name,*(v_ite + 1),ctrlpool.ctrl_class_name,ctrl_type,this);
                    }
                    else
                    {
                        throw;
                    }
                }
                ctrl_lang = ctrlpool.get_language();
            }

//
// Mark all controllers with this FiCa as FiCa already re-loaded
//

            vector<Pool::CtrlBkp>::iterator ite_2;
            for (ite_2 = ctrls.begin();ite_2 != ctrls.end();++ite_2)
            {
                if (ite_2->fica_ite == ite->fica_ite)
                    ite_2->fica_already_reloaded = true;
            }

        }
    }
    catch (Tango::DevFailed &e)
    {

//
// Memorize error for pool status, mark the FiCa as not built and
// remove the File entry in the CtrlFile vector before re-throwing the exception
//

        bool first_loop = true;
        string ct_stat;
        int32_t nb_ctrl = get_controller_nb();
        int32_t loop = 0;

        if (reloaded == false)
        {

//
// We have a major error at file level
// Mark all controllers using this file as bad
// and re-throw the exception
//
            get_all_controller(ctrl_beg, ctrl_end);
            for (ite = ctrls.begin();ite != ctrls.end();++ite)
            {
                loop++;
                ctrl_it = ctrl_beg;
                advance(ctrl_it, ite->dist);
                ControllerPool &ctrlpool = get_controller(ctrl_it->second);

                ctrlpool.error_status.clear();
                ctrlpool.error_status = "Error reported when trying to create controller ";
                ctrlpool.error_status += ctrlpool.name;
                ctrlpool.error_status += ".";
                if (first_loop == true)
                {
                    except_2_ctrl_status(e, ct_stat);
                    first_loop = false;
                }
                ctrlpool.error_status += ct_stat;
                ctrlpool.ctrl_class_built = false;

                if (loop == nb_ctrl)
                    po_class->remove_fica_by_name(ctrlpool.ctrl_class_name);
            }

            po_class->remove_ctrl_file_by_name(in_file);
            throw;
        }
        else
        {

//
// The error is now at the class level
// Mark only the controllers using this class as bad
//
            get_all_controller(ctrl_beg, ctrl_end);
            vector<Pool::CtrlBkp>::iterator ite_2;
            for (ite_2 = ctrls.begin();ite_2 != ctrls.end();++ite_2)
            {
                if (ite_2->fica_ite == ite->fica_ite)
                {
                    ctrl_it = ctrl_beg;
                    advance(ctrl_it, ite_2->dist);
                    ControllerPool &ctrlpool = get_controller(ctrl_it->second);

                    ctrlpool.error_status.clear();
                    ctrlpool.error_status = "Error reported when trying to create controller ";
                    ctrlpool.error_status = ctrlpool.error_status + ctrlpool.name;
                    if (first_loop == true)
                    {
                        except_2_ctrl_status(e,ct_stat);
                        first_loop = false;
                    }
                    ctrlpool.error_status += ct_stat;
                    ctrlpool.ctrl_class_built = false;
                    ite_2->wrong_fica = true;
                }
            }
        }
    }

//
// Re-create controller objects and mark all concerned controller as usable
//

    vector<Tango::DevFailed> save_exceptions;
    get_all_controller(ctrl_beg, ctrl_end);
    for (ite = ctrls.begin();ite != ctrls.end();++ite)
    {
        ctrl_it = ctrl_beg;
        advance(ctrl_it, ite->dist);
        ControllerPool &ctrlpool = get_controller(ctrl_it->second);

        if (ite->wrong_fica == true)
        {

//
// Add exception catched in previous loop in the save_exceptions vector
//

            Tango::DevErrorList errors;
            errors.length(1);
            errors[0].desc = CORBA::string_dup(ctrlpool.error_status.c_str());
            errors[0].severity = Tango::ERR;
            errors[0].origin = CORBA::string_dup("Pool::reload_controller_code()");
            errors[0].reason = CORBA::string_dup("Pool_BadController");

            Tango::DevFailed tmp_except(errors);
            save_exceptions.push_back(tmp_except);
            continue;
        }
        else
        {
            string::size_type pos = ctrlpool.name.find('/');
            pos++;
            string inst_name = ctrlpool.name.substr(pos);

            Controller *ct;
            if (ctrl_lang == CPP)
            {

//
// Retrieve the controller object creator C function
//

                lt_ptr sym;

                string sym_name("_create_");
                sym_name = sym_name + ctrlpool.ctrl_class_name;

                DEBUG_STREAM << "Symbol name = " << sym_name << endl;

                sym = lt_dlsym(ctrlpool.get_lib_ptr(),sym_name.c_str());
                if (sym == NULL)
                {
                    TangoSys_OMemStream o;
                    o << "Controller library " << in_file;
                    o << " does not have the C creator function "
                         "(_create_<Controller name>)" << ends;

                    Tango::Except::throw_exception(
                        (const char *)"Pool_CCreatorFunctionNotFound",o.str(),
                        (const char *)"Pool::reload_controller_code");
                }

                DEBUG_STREAM << "lt_dlsym is a success" << endl;

//
// Create the controller
//

                Ctrl_creator_ptr ct_ptr = (Ctrl_creator_ptr)sym;
                vector<Controller::Properties> *prop = NULL;

                try
                {
                    AutoPoolLock lo(ctrlpool.get_ctrl_class_mon());
                    vct_ite	tmp_ite = ctrlpool.ite_ctrl_class;

                    vector<pair<string,string> > prop_pairs;

                    build_property_data(inst_name,ctrlpool.ctrl_class_name,
                                        prop_pairs,
                                        (*tmp_ite)->get_ctrl_prop_list());
                    check_property_data((*tmp_ite)->get_ctrl_prop_list());
                    prop = properties_2_cpp_vect(
                            (*tmp_ite)->get_ctrl_prop_list());

                    ct = (*ct_ptr)(inst_name.c_str(),*prop);
                    ctrlpool.ctrl_class_built = true;

                    delete ctrlpool.cpp_ctrl_prop;
                    ctrlpool.cpp_ctrl_prop = prop;
                }
                catch (Tango::DevFailed &e)
                {
                    if (prop != NULL)
                        delete prop;

                    ct = NULL;
                    save_exceptions.push_back(e);

                    string ct_stat;
                    ctrlpool.error_status.clear();
                    ctrlpool.error_status = "Error reported when trying to create "
                                        "controller ";
                    ctrlpool.error_status = ctrlpool.error_status + ctrlpool.name;
                    except_2_ctrl_status(e,ct_stat);
                    ctrlpool.error_status = ctrlpool.error_status + ct_stat;
                }
            }
            else
            {

//
// Retrieve the controller object creator C function
//

                lt_ptr sym;
                string dev_type_str = CtrlTypeStr[ctrl_dev_type];

                string sym_name = "_create_Py" + dev_type_str + "Controller";
                DEBUG_STREAM << "Symbol name = " << sym_name << endl;

                sym = lt_dlsym(ctrlpool.get_py_inter_lib_ptr(),sym_name.c_str());
                if (sym == NULL)
                {
                    TangoSys_OMemStream o;
                    o << "Controller library " << in_file;
                    o << " does not have the C creator function "
                         "(_create_<Controller name>)" << ends;

                    Tango::Except::throw_exception(
                        (const char *)"Pool_CCreatorFunctionNotFound",o.str(),
                        (const char *)"Pool::reload_controller_code");
                }

                DEBUG_STREAM << "lt_dlsym is a success" << endl;

//
// Create the Python controller object after building and checking
// its properties set
//

                PyCtrl_creator_ptr ct_ptr = (PyCtrl_creator_ptr)sym;
                try
                {
                    AutoPoolLock lo(ctrlpool.get_ctrl_class_mon());
                    vct_ite	tmp_ite = ctrlpool.ite_ctrl_class;

                    vector<pair<string,string> > prop_pairs;

                    build_property_data(inst_name,ctrlpool.ctrl_class_name,
                                        prop_pairs,
                                        (*tmp_ite)->get_ctrl_prop_list());
                    check_property_data((*tmp_ite)->get_ctrl_prop_list());
                    PyObject *prop_dict =
                        properties_2_py_dict((*tmp_ite)->get_ctrl_prop_list());

                    ct = (*ct_ptr)(inst_name.c_str(),
                                   ctrlpool.ctrl_class_name.c_str(),
                                   ctrlpool.get_py_module(),prop_dict);
                    ctrlpool.ctrl_class_built = true;
                }
                catch (Tango::DevFailed &e)
                {
                    ct = NULL;
                    save_exceptions.push_back(e);

                    string ct_stat;
                    ctrlpool.error_status.clear();
                    ctrlpool.error_status = "Error reported when trying to create "
                                        "controller ";
                    ctrlpool.error_status = ctrlpool.error_status + ctrlpool.name;
                    except_2_ctrl_status(e,ct_stat);
                    ctrlpool.error_status = ctrlpool.error_status + ct_stat;
                }
            }

//
// Retrieve the possibly changed MaxDevice property
//
            vct_ite	tmp_ite = ctrlpool.ite_ctrl_class;
            long MaxDevice = (*tmp_ite)->get_MaxDevice();

//
// Update info in pool list
//

            ctrlpool.set_controller(ct);
            ctrlpool.MaxDevice = MaxDevice;

//
// Mark all devices using this controller as usable
// and restart them using an Init
// command. It is not enough to send them the Init command
// because there are some cases where the device interface
// could have changed and dynamic attributes have to be created
// This is the case where the ctrl FiCa was not built
// and is built by this command.
// Do this only if the controller creation was a success
//

            if (ct != NULL)
            {
                ctrlpool.error_status.clear();

                switch (ctrl_dev_type)
                {
                    case MOTOR_CTRL:
                    restore_motor(mots,ctrlpool,ite);
                    break;

                    case PSEUDO_MOTOR_CTRL:
                    restore_pseudo_motor(mots,ctrlpool,ite);
                    break;

                    case PSEUDO_COUNTER_CTRL:
                    restore_pseudo_counter(mots,ctrlpool,ite);
                    break;

                    case COTI_CTRL:
                    restore_ct(mots,ctrlpool,ite);
                    break;

                    case ZEROD_CTRL:
                    restore_zerod(mots,ctrlpool,ite);
                    break;

                    case ONED_CTRL:
                    restore_oned(mots,ctrlpool,ite);
                    break;

                    case TWOD_CTRL:
                    restore_twod(mots,ctrlpool,ite);
                    break;

                    case COM_CTRL:
                    restore_comch(mots,ctrlpool,ite);
                    break;

                    case IOREGISTER_CTRL:
                    restore_ioregister(mots,ctrlpool,ite);
                    break;

                    case CONSTRAINT_CTRL:
                    // No devices on constraint so no need to invalidate
                    break;

                    default:
                    Tango::Except::throw_exception(
                            (const char *)"Pool_BadCtrlType",
                            (const char *)"Undefined controller type !!!",
                            (const char *)"Pool::reload_controller_code");
                    break;
                }

//
// The motor Init command clears the Motor proxy. Mark the
// proxy created flag as false to recreate the proxy
//

                proxy_created = false;
            }
        }
    }

//
// If it was not possible to create controller object(s),
// send exception to caller to inform him(her)
//

    if (save_exceptions.size() != 0)
    {
        TangoSys_OMemStream o;
        o << "Not possible to create " << save_exceptions.size() << " controller(s)";
        o << "\nError messages are: ";
        for (unsigned long loo = 0;loo < save_exceptions.size();loo++)
            o << "\n" << save_exceptions[loo].errors[0].desc;
        o << ends;

        Tango::Except::throw_exception((const char *)"Pool_CantCreateController",o.str(),
                      (const char *)"Pool::reload_controller_code");
    }
}

//+------------------------------------------------------------------
/**
 *	method:	Pool::create_motor_group
 *
 *	description:	method to execute "CreateMotorGroup"
 *	This command creates a motor group. The name of the group is the first element in the input
 *	argument followed by the group element name.
 *
 * @param	argin	Group name followed by motor's name
 *
 */
//+------------------------------------------------------------------
void Pool::create_motor_group(const Tango::DevVarStringArray *argin)
{
    DEBUG_STREAM << "Pool::create_motor_group(): entering... !" << endl;

    //	Add your own code to control device here

//
// Basic check on input parameters
//

    string group_name((*argin)[0]);
    long input_nb = argin->length() - 1;

    if (input_nb <= 0)
    {
        TangoSys_OMemStream o;
        o << "Cant create motor group " << group_name << ". You haven't defined any element as group member" << ends;

        Tango::Except::throw_exception((const char *)"Pool_BadArgument",o.str(),
                        (const char *)"Pool::create_motor_group");
    }

    string second_arg((*argin)[1]);
    bool manual_tg_dev_name = second_arg.find('/') != std::string::npos;
    
    long input_start = manual_tg_dev_name ? 2 : 1;

    if(manual_tg_dev_name) input_nb--;
    
    if (input_nb <= 0)
    {
        TangoSys_OMemStream o;
        o << "Cant create motor group " << group_name << ". You haven't defined any element as group member" << ends;

        Tango::Except::throw_exception((const char *)"Pool_BadArgument",o.str(),
                        (const char *)"Pool::create_motor_group");
    }    
    
    DEBUG_STREAM << "Group name = " << group_name;
    vector<GrpEltType> in_type;
    long i;
    for (i = input_start;i < input_nb + input_start;i++)
        DEBUG_STREAM << "Input elt name = " << (*argin)[i];

//
// Check if each element are member of this pool
// as motor, pseudo-motor or group
//

    for (i = input_start;i < input_nb + input_start;i++)
    {
        string elt_name((*argin)[i]);
        if (physical_motor_exists(elt_name) == false)
        {
            if (pseudo_motor_exists(elt_name) == false)
            {
                if (motor_group_exists(elt_name) == false)
                {
                    TangoSys_OMemStream o;
                    o << "Element " << elt_name << " is neither a motor, pseudo-motor or group defined in this pool. Can't create the group." << ends;

                    Tango::Except::throw_exception((const char *)"Pool_BadArgument",o.str(),
                                            (const char *)"Pool::create_motor_group");
                }
                else
                    in_type.push_back(GROUP);
            }
            else
                in_type.push_back(PSEUDO_MOTOR);
        }
        else
            in_type.push_back(MOTOR);
    }

//
// Check if we don't have already enough motor groups
//

    DEBUG_STREAM << "Checking motor group number" << endl;

    if (get_motor_group_nb() == MAX_MOTOR_GROUP)
    {
        Tango::Except::throw_exception((const char *)"Pool_TooManyMotorGroup",
                           (const char *)"Too many motor groups in your pool",
                           (const char *)"Pool::create_motor_group");
    }

    Tango::Util *tg = Tango::Util::instance();
    
//
// Build Tango device name
//
    string tg_dev_name = "";
    if (manual_tg_dev_name)
    {
        tg_dev_name = second_arg;
    }
    else
    {
        tg_dev_name = "mg/" + tg->get_ds_inst_name() + '/' + group_name;
    }

    DEBUG_STREAM << "Tango motor group device name = " << tg_dev_name << endl;

//
// Check if this device is already defined in database
// Check by device alias and by Tango device name
//

    Tango::Database *db = tg->get_database();

    Tango::DbDevImportInfo my_device_import;
    bool device_exist = false;
    bool by_alias = false;

    try
    {
        my_device_import = db->import_device(group_name);
        device_exist = true;
        by_alias = true;
    }
    catch (Tango::DevFailed &e)
    {
        if (::strcmp(e.errors[0].reason.in(),"DB_DeviceNotDefined") != 0)
        {
            device_exist = true;
        }
    }

    if (device_exist == false)
    {
        try
        {
            my_device_import = db->import_device(tg_dev_name);
            device_exist = true;
        }
        catch (Tango::DevFailed &e)
        {
            if (::strcmp(e.errors[0].reason.in(),"DB_DeviceNotDefined") != 0)
            {
                device_exist = true;
            }
        }
    }

    if (device_exist == true)
    {
        TangoSys_OMemStream o;
        o << "Motor group ";
        if (by_alias == false)
            o << tg_dev_name;
        else
            o << group_name;
        o << " already defined" << ends;

        Tango::Except::throw_exception("Pool_WrongMotorGroupName",o.str(),
                                       "Pool::create_motor_group");
    }

//
// Build group physical structure
// (replace group by its motor and
// pseudo-motor by its physical motors)
//

    int32_t wanted_in_nb = 0;
    std::vector<Tango::DevLong> grp_mot_id;

    vector<pair<ElementId, Controller *> > m_to_pmctrl;

    for (i = input_start;i < input_nb + input_start;i++)
    {
        string in_elt((*argin)[i]);
        GrpEltType type = in_type[i - input_start];
        if (type == MOTOR)
        {
            //transform(in_elt.begin(),in_elt.end(),in_elt.begin(),::tolower);
            //grp_mot_name.push_back(in_elt);
            grp_mot_id.push_back((Tango::DevLong)get_element_id(in_elt));
            wanted_in_nb++;
        }
        else if (type == PSEUDO_MOTOR)
        {
            PseudoMotorPool &pm = get_pseudo_motor(in_elt);
            PseudoMotor_ns::PseudoMotor *pm_dev = get_pseudo_motor_device(pm);
            wanted_in_nb++;
            for (unsigned long loop = 0;loop < pm.mot_elts.size();loop++)
            {
                ElementId tmp_mot_id = pm.mot_elts[loop];
                //string tmp_mot_name(pm.mot_elts[loop]->name);
                //transform(tmp_mot_name.begin(),tmp_mot_name.end(),tmp_mot_name.begin(),::tolower);
                
                pair<ElementId,Controller*> m_ctrl(tmp_mot_id, pm_dev->get_controller());

//
// if we find a motor that has not yet been used by the current pseudo motor controller we
// had it to the list.
// This is done to allow the same motors to be used by different pseudo motors that belong
// to the same pseudo motor controller
//
                if(find(m_to_pmctrl.begin(), m_to_pmctrl.end(), m_ctrl) == m_to_pmctrl.end())
                {
                    m_to_pmctrl.push_back(m_ctrl);
                    grp_mot_id.push_back((Tango::DevLong)tmp_mot_id);
                }
            }
        }
        else
        {
            MotorGroupPool &grp = get_motor_group(in_elt, true);
            for (unsigned long loop = 0;loop < grp.mot_ids.size();loop++)
            {
                //MotorPool &mot = get_physical_motor(grp.mot_ids[loop]);
                //grp_mot_name.push_back(mot.get_name());
                grp_mot_id.push_back((Tango::DevLong)grp.mot_ids[loop]);
                wanted_in_nb++;
            }
        }
    }

//
// Check that each motor is not used several times within the group
//

    for (unsigned long hh = 0;hh < grp_mot_id.size();hh++)
    {
        int num;
        if ((num = count(grp_mot_id.begin(),grp_mot_id.end(),grp_mot_id[hh])) > 1)
        {
            TangoSys_OMemStream o;
            PoolElement *elem = get_element(grp_mot_id[hh]);
            o << "Motor " << elem->get_name() << " is used " << num
              << " times in this group\nEach motor should be used only once in a group"
              << ends;

            Tango::Except::throw_exception("Pool_WrongMotorGroup", o.str(),
                                           "Pool::create_motor_group");
        }
    }

//
// If the device is not defined in database, create it in database, set its alias
// and define its properties used to store its ID, its device pool and its motor list
//

    if (device_exist == false)
    {
        DEBUG_STREAM << "Trying to create device entry in database" << endl;

        try
        {
            Tango::DbDevInfo my_device_info;
            my_device_info.name = tg_dev_name.c_str();
            my_device_info._class = "MotorGroup";
            my_device_info.server = tg->get_ds_name().c_str();

            db->add_device(my_device_info);
            db->put_device_alias(tg_dev_name, group_name);

            Tango::DbDatum id(ID_PROP);
            Tango::DbDatum phy_list(PHYS_GROUP_ELT);
            Tango::DbDatum usr_list(USER_GROUP_ELT);
            Tango::DbDatum mot_list(MOTOR_GROUP_LIST);
            Tango::DbDatum mot_grp_list(MOTOR_GROUP_GROUP_LIST);
            Tango::DbDatum pm_list(PSEUDO_MOTOR_GROUP_LIST);
            Tango::DbDatum want_in(POS_SPECTRUM_DIM_X);
            Tango::DbData db_data;

            ElementId mot_group_id = get_new_id();
            id << (Tango::DevLong)mot_group_id;
            db_data.push_back(id);

            phy_list << grp_mot_id;
            db_data.push_back(phy_list);

            std::vector<Tango::DevLong> user_ids, mot_ids, mg_ids, pm_ids;
            for (long loop = input_start;loop < input_nb + input_start; ++loop)
            {
                Tango::DevLong elem_id = (Tango::DevLong) get_element_id((*argin)[loop].in());
                if (in_type[loop - input_start] == MOTOR)
                {
                    mot_ids.push_back(elem_id);
                }
                else if (in_type[loop - input_start] == GROUP)
                {
                    mg_ids.push_back(elem_id);
                }
                else
                {
                    pm_ids.push_back(elem_id);
                }
                user_ids.push_back(elem_id);
            }

            usr_list << user_ids;
            db_data.push_back(usr_list);

            mot_list << mot_ids;
            db_data.push_back(mot_list);

            mot_grp_list << mg_ids;
            db_data.push_back(mot_grp_list);

            pm_list << pm_ids;
            db_data.push_back(pm_list);

            want_in << (Tango::DevLong)wanted_in_nb;
            db_data.push_back(want_in);

            db->put_device_property(tg_dev_name.c_str(), db_data);

            Tango::DbDatum pos("Position"),abs_ch("abs_change");
            db_data.clear();
            pos << (long)1;
            abs_ch << defaultMotGrpPos_AbsChange;
            db_data.push_back(pos);
            db_data.push_back(abs_ch);
            db->put_device_attribute_property(tg_dev_name.c_str(),db_data);

            DEBUG_STREAM << "Device created in database (with alias)" << endl;
        }
        catch (Tango::DevFailed &e)
        {
            DEBUG_STREAM << "Gasp an exception........" << endl;
            TangoSys_OMemStream o;
            o << "Can't create motor group " << group_name << " in database" << ends;

            Tango::Except::re_throw_exception(e,(const char *)"Pool_CantCreateMotorGroup",o.str(),
                              (const char *)"Pool::create_motor_group");
        }

//
// Find the Tango MotorGroup class and create the motor group
//

        const vector<Tango::DeviceClass *> *cl_list = tg->get_class_list();
        for (unsigned long i = 0;i < cl_list->size();i++)
        {
            if ((*cl_list)[i]->get_name() == "MotorGroup")
            {
                try
                {
                    Tango::DevVarStringArray na;
                    na.length(1);
                    na[0] = tg_dev_name.c_str();
                    (*cl_list)[i]->device_factory(&na);
                    break;
                }
                catch (Tango::DevFailed &e)
                {
                    DEBUG_STREAM << "Exception while trying to create MotorGroup device" << endl;

    //
    // The delete_device will also delete device property(ies)
    //

                    db->delete_device(tg_dev_name);

                    TangoSys_OMemStream o;
                    o << "Can't create motor group device " << group_name << ends;

                    Tango::Except::re_throw_exception(e,(const char *)"Pool_CantCreateMotorGroup",o.str(),
                              (const char *)"Pool::create_motor_group");
                }
            }
        }

    //
    // Create a Tango device proxy on the newly created motor
    // and set its connection to automatic re-connection
    //
        MotorGroupPool &mgp = get_motor_group(group_name);

        Tango::DeviceProxy *tmp_dev = new Tango::DeviceProxy(mgp.get_full_name().c_str());
        tmp_dev->set_transparency_reconnection(true);
       
        MotorGroup_ns::MotorGroup *dev = static_cast<MotorGroup_ns::MotorGroup*>
            (tg->get_device_by_name(mgp.get_full_name()));
        
        set_tango_element(mgp, tmp_dev, dev);
    }

//
// subscribe to the internal events coming from each element of the motor group
//
    MotorGroupPool &mgp = get_motor_group(group_name);

    ElemIdVectorIt ite = mgp.group_elts.begin();
    for(; ite != mgp.group_elts.end(); ite++)
    {
        get_element(*ite)->add_pool_elem_listener(&mgp);
    }

//
// Push a change event for clients listenning on events
//

    Tango::Attribute &mgl = dev_attr->get_attr_by_name("MotorGroupList");
    read_MotorGroupList(mgl);
    mgl.fire_change_event();
}



//+------------------------------------------------------------------
/**
 *	method:	Pool::delete_motor_group
 *
 *	description:	method to execute "DeleteMotorGroup"
 *	This command delete a motor group from its name
 *
 * @param	argin	The motor group name
 *
 */
//+------------------------------------------------------------------
void Pool::delete_motor_group(Tango::DevString argin)
{
    DEBUG_STREAM << "Pool::delete_motor_group(): entering... !" << endl;

    //	Add your own code to control device here

//
// Find motor group in motor group list
//

    string user_name(argin);

    MotorGroupPool &mg_to_del = get_motor_group(user_name);

    DEBUG_STREAM << "Motor group found" << endl;

//
// Check that the group is not moving
//

    if (get_element_proxy(mg_to_del)->state() == Tango::MOVING)
    {
        TangoSys_OMemStream o;
        o << "Can't delete group with name " << argin;
        o << ". It is actually moving." << ends;

        Tango::Except::throw_exception(
                            (const char *)"Pool_CantDeleteGroup", o.str(),
                            (const char *)"Pool::delete_motor_group");
    }

//
// Check that this group is not member of any other group
//

    vector<string> used_by_mg;
    if (get_motor_groups_containing_elt(mg_to_del.get_id(), used_by_mg) == true)
    {
        TangoSys_OMemStream o;
        o << "Can't delete group with name " << argin;
        o << ". It is used in group(s): ";

        vector<string>::iterator ite = used_by_mg.begin();
        for(;ite != used_by_mg.end(); ite++)
            o << *ite << ", " << ends;
        o << ends;

        Tango::Except::throw_exception(
                            (const char *)"Pool_CantDeleteGroup", o.str(),
                            (const char *)"Pool::delete_motor_group");
    }

//
// Check that this group is not used by any pseudo motor
//

    vector<string> used_by_pm;
    if (get_pseudo_motors_that_use_mg(mg_to_del.get_id(), used_by_pm) == true)
    {
        TangoSys_OMemStream o;
        o << "Can't delete group with name " << argin;
        o << ". It is used by pseudo motor(s): ";

        vector<string>::iterator ite = used_by_pm.begin();
        for(;ite != used_by_pm.end(); ite++)
            o << *ite << ", " << ends;
        o << ends;

        Tango::Except::throw_exception(
                            (const char *)"Pool_CantDeleteGroup", o.str(),
                            (const char *)"Pool::delete_motor_group");
    }

//
// Unsubscribe to the internal events for each element of the motor group
//

    ElemIdVectorIt it = mg_to_del.group_elts.begin();
    for(; it != mg_to_del.group_elts.end();++it)
    {
        get_element(*it)->remove_pool_elem_listener(&mg_to_del);
    }

//
// Remove its entry in database. This will also delete any device
// properties and device attribute properties
//

    Tango::Util *tg = Tango::Util::instance();
    try
    {
        tg->get_database()->delete_device(mg_to_del.get_full_name());

//
// Delete motor group device from server but first find its Tango xxxClass instance
//
        MotorGroup_ns::MotorGroup *mg_dev = get_motor_group_device(mg_to_del);
        Tango::DeviceClass *dc = mg_dev->get_device_class();
        dc->device_destroyer(mg_to_del.get_full_name());
    }
    catch (Tango::DevFailed &e)
    {
        TangoSys_OMemStream o;
        o << "Can't delete motor group with name " << argin << ends;

        Tango::Except::re_throw_exception(e,(const char *)"Pool_CantDeleteMotorGroup",o.str(),
                                 (const char *)"Pool::delete_motor_group");
    }

//
// Push a change event for clients listenning on events
//

    Tango::Attribute &mgl = dev_attr->get_attr_by_name("MotorGroupList");
    read_MotorGroupList(mgl);
    mgl.fire_change_event();

}


//+------------------------------------------------------------------
/**
 *	method:	Pool::dev_status
 *
 *	description:	method to execute "Status"
 *	This command gets the device status (stored in its <i>device_status</i> data member) and returns it to the caller.
 *
 * @return	Status descrition
 *
 */
//+------------------------------------------------------------------
Tango::ConstDevString Pool::dev_status()
{
    Tango::ConstDevString	argout = DeviceImpl::dev_status();
    DEBUG_STREAM << "Pool::dev_status(): entering... !" << endl;

    //	Add your own code to control device here

    tmp_status = argout;

    if (get_state() == Tango::MOVING)
    {
        tmp_status = tmp_status + '\n';
        tmp_status = tmp_status + "The pool device is shuting down but is waiting for the end of motor(s) movement";
    }
    else
    {
        bool first_ctrl_in_error = true;

        for (PoolElementTypeIt ctrl_it = element_types.lower_bound(CTRL_ELEM);
             ctrl_it !=element_types.upper_bound(CTRL_ELEM); ++ctrl_it)
        {
            ControllerPool &ctrlpool = get_controller(ctrl_it->second);
            
            if (!ctrlpool.get_controller())
            {
                if (first_ctrl_in_error == false)
                    tmp_status = tmp_status + '\n';

                tmp_status = tmp_status + ctrlpool.error_status;
                first_ctrl_in_error = false;
            }
        }
    }

    argout = tmp_status.c_str();
    return argout;
}

//+------------------------------------------------------------------
/**
 *	method:	Pool::delete_pseudo_motor
 *
 *	description:	method to execute "DeletePseudoMotor"
 *	This command deletes a pseudo motor
 *
 * @param	argin	Pseudo Motor name
 *
 */
//+------------------------------------------------------------------
void Pool::delete_pseudo_motor(Tango::DevString argin)
{
    DEBUG_STREAM << "Pool::delete_pseudo_motor(): entering... !" << endl;

    //	Add your own code to control device here

//
// Find pseudo motor in pseudo motor list
//
    string user_name(argin);
    PseudoMotorPool &pm_to_del =  get_pseudo_motor(user_name);
    MotorGroupPool &pm_to_del_mg = get_motor_group(pm_to_del.motor_group_id);
    
    DEBUG_STREAM << "Pseudo Motor found" << endl;

//
// Check that the pseudo motor is not moving
//
    if (get_element_proxy(pm_to_del)->state() == Tango::MOVING)
    {
        TangoSys_OMemStream o;
        o << "Can't delete pseudo motor with name " << argin;
        o << ". It is actually moving." << ends;

        Tango::Except::throw_exception(
                    (const char *)"Pool_CantDeletePseudoMotor",o.str(),
                    (const char *)"Pool::delete_pseudo_motor");
    }

//
// Check that the pseudo motor is not member of a motor group
// Also check if the underlying motor group used by this pseudo motor is not
// used by another motor group
//
    bool mg_shared_by_other_mg = false;
    for (PoolElementTypeIt elem_it = element_types.lower_bound(MOTOR_GROUP_ELEM);
         elem_it != element_types.upper_bound(MOTOR_GROUP_ELEM); ++elem_it)
    {
        MotorGroupPool &mgp = get_motor_group(elem_it->second);
        if(mgp.is_user_member(pm_to_del.get_id()))
        {
            TangoSys_OMemStream o;
            o << "Can't delete pseudo motor with name " << argin;
            o << ". It is actually member of group " << mgp.name << ends;

            Tango::Except::throw_exception(
                    (const char *)"Pool_CantDeletePseudoMotor",o.str(),
                    (const char *)"Pool::delete_pseudo_motor");
        }
        
        if(mgp.is_user_member(pm_to_del_mg.get_id()))
        {
            mg_shared_by_other_mg = true;
        }
    }

//
// Check if the underlying motor group used by this pseudo motor should be
// deleted. It should be deleted if and only if:
// - there is no other pseudo motor using it and
// - there is no other motor group using it (this condition was checked in the
//   code above)
//
    bool mg_shared_by_other_pm = false;
    for (PoolElementTypeIt elem_it = element_types.lower_bound(PSEUDO_MOTOR_ELEM);
         elem_it != element_types.upper_bound(PSEUDO_MOTOR_ELEM); ++elem_it)
    {
        PseudoMotorPool &pmp = get_pseudo_motor(elem_it->second);
        if((pmp.motor_group_id == pm_to_del.motor_group_id) &&
           (pmp.name != pm_to_del.name))
        {
            mg_shared_by_other_pm = true;
            break;
        }
    }
    
//
// Delete the motor group attached to this pseudo motor if it is not shared by
// other element
//
    if(!mg_shared_by_other_pm && !mg_shared_by_other_mg)
    {
        Tango::DeviceProxy tg_pool(this->get_name());
        Tango::DeviceData din,dout;

        din << pm_to_del_mg.name;

//
// A little trick here: The DeleteMotorGroup command checks if there is any
// pseudo motor using the motor groups before it deletes the motor group. It
// does this by checking the mg_id in each pseudo motor with its own id. To skip
// this test for the pseudo motor being deleted we set mg_id value temporarily
// to -1
//
        pm_to_del.motor_group_id = InvalidId;
        try
        {
            dout = tg_pool.command_inout("DeleteMotorGroup", din);
        }
        catch(Tango::DevFailed &ex)
        {
            WARN_STREAM << "Delete of Motor Group for Pseudo Motor " << pm_to_del.name << " failed" << endl;
        }
        pm_to_del.motor_group_id = pm_to_del_mg.get_id();
    }

    Tango::Util *util = Tango::Util::instance();
    Tango::Database *db = util->get_database();

//
// Inform siblings that a sibling will die
//
    //Set the siblings for each pseudo motor
    for (PoolElementTypeIt elem_it = element_types.lower_bound(PSEUDO_MOTOR_ELEM);
         elem_it != element_types.upper_bound(PSEUDO_MOTOR_ELEM); ++elem_it)
    {
        PseudoMotorPool &pmp = get_pseudo_motor(elem_it->second);
        if(pmp.get_ctrl_id() == pm_to_del.get_ctrl_id())
        {
            PseudoMotor_ns::PseudoMotor *pm_dev = get_pseudo_motor_device(pmp);
            pm_dev->sibling_died(pm_to_del.get_axis());
        }
    }
    
//
// Remove its entry in database. This will also delete any device
// properties and device attribute properties
//
    try
    {
        db->delete_device(pm_to_del.get_full_name());

//
// Delete pseudo motor device from server but first find its Tango xxxClass instance
//
        PseudoMotor_ns::PseudoMotor *pm_dev = get_pseudo_motor_device(pm_to_del);
        Tango::DeviceClass *dc = pm_dev->get_device_class();
        dc->device_destroyer(pm_to_del.get_full_name());
    }
    catch (Tango::DevFailed &e)
    {
        TangoSys_OMemStream o;
        o << "Can't delete pseudo motor '" << argin << "'" << ends;

        Tango::Except::re_throw_exception(e,
                (const char *)"Pool_CantDeletePseudoMotor",o.str(),
                (const char *)"Pool::delete_pseudo_motor");
    }

//
// Push a change event for clients listenning on events
//

    Tango::Attribute &pml = dev_attr->get_attr_by_name("PseudoMotorList");
    read_PseudoMotorList(pml);
    pml.fire_change_event();
}

//+------------------------------------------------------------------
/**
 *	method:	Pool::delete_controller
 *
 *	description:	method to execute "DeleteController"
 *	Delete controller from its name.
 *	Before executing this command, you must first delete all the elements associated
 *	with this controller
 *
 * @param	argin	The controller name
 *
 */
//+------------------------------------------------------------------
void Pool::delete_controller(Tango::DevString argin)
{
    DEBUG_STREAM << "Pool::delete_controller(): entering... !" << endl;

    //	Add your own code to control device here

//
// Find controller in controller list
//

    string user_ctrl(argin);

    ControllerPool &ctrl_to_del = get_controller(user_ctrl, true);

//
// Get controller object type and check that we don't have any object
// still using the controller
//

    if (ctrl_to_del.ctrl_class_built == true)
    {
        CtrlType type = ctrl_to_del.get_ctrl_obj_type();

        switch(type)
        {
            case MOTOR_CTRL:
            {

//
// Check that we don't have any motor left on this controller
//
                int32_t nb_remain_motor = 0;
                TangoSys_OMemStream o;

                for (PoolElementTypeIt elem_it = element_types.lower_bound(MOTOR_ELEM);
                     elem_it != element_types.upper_bound(MOTOR_ELEM); ++elem_it)
                {
                    MotorPool &motor_pool = get_physical_motor(elem_it->second);
                    if (motor_pool.get_ctrl_id() == ctrl_to_del.id)
                    {
                        if (nb_remain_motor == 0)
                        {
                            o << "Can't delete controller, motor(s) ";
                            o << motor_pool.name;
                        }
                        else
                        {
                            o << ", " << motor_pool.name;
                        }
                        nb_remain_motor++;
                    }
                }
                if (nb_remain_motor != 0)
                {
                    o << " are still defined using this controller" << ends;

                    Tango::Except::throw_exception(
                            (const char *)"Pool_CantDeleteController",o.str(),
                            (const char *)"Pool::delete_controller");
                }
            }
            break;

            case PSEUDO_MOTOR_CTRL:
            {

//
// Check that we don't have any pseudo motor left on this controller
//
                int32_t nb_remain_pseudo_motor = 0;
                TangoSys_OMemStream o;

                for (PoolElementTypeIt elem_it = element_types.lower_bound(PSEUDO_MOTOR_ELEM);
                     elem_it != element_types.upper_bound(PSEUDO_MOTOR_ELEM); ++elem_it)
                {
                    PseudoMotorPool &pmp = get_pseudo_motor(elem_it->second);

                    if (pmp.get_ctrl_id() == ctrl_to_del.id)
                    {
                        if (nb_remain_pseudo_motor == 0)
                        {
                            o << "Can't delete controller, pseudo motor(s) ";
                            o << pmp.name;
                        }
                        else
                        {
                            o << ", " << pmp.name;
                        }
                        nb_remain_pseudo_motor++;
                    }
                }

                if (nb_remain_pseudo_motor != 0)
                {
                    o << " are still defined using this controller" << ends;

                    Tango::Except::throw_exception(
                            (const char *)"Pool_CantDeleteController",o.str(),
                            (const char *)"Pool::delete_controller");
                }
            }
            break;

            case PSEUDO_COUNTER_CTRL:
            {
//
// Check that we don't have any pseudo counter left on this controller
// In principle there can be only one but...we check
//
                for (PoolElementTypeIt elem_it = element_types.lower_bound(PSEUDO_COUNTER_ELEM);
                     elem_it != element_types.upper_bound(PSEUDO_COUNTER_ELEM); ++elem_it)
                {
                    PseudoCounterPool &pcp = get_pseudo_counter(elem_it->second);
                    if (pcp.get_ctrl_id() == ctrl_to_del.id)
                    {
                        TangoSys_OMemStream o;
                        o << "Can't delete controller, pseudo counter ";
                        o << pcp.name;
                        o << " is still defined using this controller" << ends;
                        Tango::Except::throw_exception(
                            (const char *)"Pool_CantDeleteController",o.str(),
                            (const char *)"Pool::delete_controller");
                    }
                }
            }
            break;

            case COTI_CTRL:
            {
//
// Check that we don't have any counter timer left on this controller
//
                int32_t nb_remain_channel = 0;
                TangoSys_OMemStream o;

                for (PoolElementTypeIt elem_it = element_types.lower_bound(COTI_ELEM);
                     elem_it != element_types.upper_bound(COTI_ELEM); ++elem_it)
                {
                    CTExpChannelPool &ct_pool = get_countertimer(elem_it->second);

                    if (ct_pool.get_ctrl_id() == ctrl_to_del.id)
                    {
                        if (nb_remain_channel == 0)
                        {
                            o << "Can't delete controller, channel(s) ";
                            o << ct_pool.name;
                        }
                        else
                        {
                            o << ", " << ct_pool.name;
                        }
                        nb_remain_channel++;
                    }
                }

                if (nb_remain_channel != 0)
                {
                    o << " are still defined using this controller" << ends;

                    Tango::Except::throw_exception(
                            (const char *)"Pool_CantDeleteController",o.str(),
                            (const char *)"Pool::delete_controller");
                }
            }
            break;

            case ZEROD_CTRL:
            {
//
// Check that we don't have any channel left on this controller
//
                int32_t nb_remain_channel = 0;
                TangoSys_OMemStream o;

                for (PoolElementTypeIt elem_it = element_types.lower_bound(ZEROD_ELEM);
                     elem_it != element_types.upper_bound(ZEROD_ELEM); ++elem_it)
                {
                    ZeroDExpChannelPool &zerod_pool = get_zerod(elem_it->second);

                    if (zerod_pool.get_ctrl_id() == ctrl_to_del.id)
                    {
                        if (nb_remain_channel == 0)
                        {
                            o << "Can't delete controller, channel(s) ";
                            o << zerod_pool.name;
                        }
                        else
                        {
                            o << ", " << zerod_pool.name;
                        }
                        nb_remain_channel++;
                    }
                }

                if (nb_remain_channel != 0)
                {
                    o << " are still defined using this controller" << ends;

                    Tango::Except::throw_exception(
                            (const char *)"Pool_CantDeleteController",o.str(),
                            (const char *)"Pool::delete_controller");
                }
            }
            break;


            case ONED_CTRL:
            {
//
// Check that we don't have any channel left on this controller
//
                int32_t nb_remain_channel = 0;
                TangoSys_OMemStream o;
                    
                for (PoolElementTypeIt elem_it = element_types.lower_bound(ONED_ELEM);
                     elem_it != element_types.upper_bound(ONED_ELEM); ++elem_it)
                {
                    OneDExpChannelPool &oned_pool = get_oned(elem_it->second);
                    if (oned_pool.get_ctrl_id() == ctrl_to_del.id)
                    {
                        if (nb_remain_channel == 0)
                        {
                            o << "Can't delete controller, channel(s) ";
                            o << oned_pool.name;
                        }
                        else
                        {
                            o << ", " << oned_pool.name;
                        }
                        nb_remain_channel++;
                    }	
                }
          
                if (nb_remain_channel != 0)
                {
                    o << " are still defined using this controller" << ends;
                          
                    Tango::Except::throw_exception(
                            (const char *)"Pool_CantDeleteController",o.str(),
                            (const char *)"Pool::delete_controller");
                }
            }
            break;
                        
            case TWOD_CTRL:
            {
//
// Check that we don't have any channel left on this controller
//
                int32_t nb_remain_channel = 0;
                TangoSys_OMemStream o;
                    
                for (PoolElementTypeIt elem_it = element_types.lower_bound(TWOD_ELEM);
                     elem_it != element_types.upper_bound(TWOD_ELEM); ++elem_it)
                {
                    TwoDExpChannelPool &twod_pool = get_twod(elem_it->second);
                    if (twod_pool.get_ctrl_id() == ctrl_to_del.id)
                    {
                        if (nb_remain_channel == 0)
                        {
                            o << "Can't delete controller, channel(s) ";
                            o << twod_pool.name;
                        }
                        else
                        {
                            o << ", " << twod_pool.name;
                        }
                        nb_remain_channel++;
                    }	
                }
          
                if (nb_remain_channel != 0)
                {
                    o << " are still defined using this controller" << ends;
                          
                    Tango::Except::throw_exception(
                            (const char *)"Pool_CantDeleteController",o.str(),
                            (const char *)"Pool::delete_controller");
                }
            }
            break;
            
            case COM_CTRL:
            {
//
// Check that we don't have any communication channel left on this controller
//
                int32_t nb_remain_channel = 0;
                TangoSys_OMemStream o;

                for (PoolElementTypeIt elem_it = element_types.lower_bound(COM_ELEM);
                     elem_it != element_types.upper_bound(COM_ELEM); ++elem_it)
                {
                    CommunicationChannelPool &cc_pool = get_communication_channel(elem_it->second);
                    if (cc_pool.get_ctrl_id() == ctrl_to_del.id)
                    {
                        if (nb_remain_channel == 0)
                        {
                            o << "Can't delete controller, channel(s) ";
                            o << cc_pool.name;
                        }
                        else
                        {
                            o << ", " << cc_pool.name;
                        }
                        nb_remain_channel++;
                    }
                }

                if (nb_remain_channel != 0)
                {
                    o << " are still defined using this controller" << ends;

                    Tango::Except::throw_exception(
                            (const char *)"Pool_CantDeleteController", o.str(),
                            (const char *)"Pool::delete_controller");
                }
            }
            break;

            case IOREGISTER_CTRL:
            {
//
// Check that we don't have any ioregister left on this controller
//
                int32_t nb_remain_channel = 0;
                TangoSys_OMemStream o;
                
                for (PoolElementTypeIt elem_it = element_types.lower_bound(IOREGISTER_ELEM);
                     elem_it != element_types.upper_bound(IOREGISTER_ELEM); ++elem_it)
                {
                    IORegisterPool &ior_pool = get_ioregister(elem_it->second);

                    if (ior_pool.get_ctrl_id() == ctrl_to_del.id)
                    {
                    
                        if (nb_remain_channel == 0)
                        {
                            o << "Can't delete controller, channel(s) ";
                            o << ior_pool.name;
                        }
                        else
                        {
                            o << ", " << ior_pool.name;
                        }
                        nb_remain_channel++;
                    }
                }

                if (nb_remain_channel != 0)
                {
                    o << " are still defined using this controller" << ends;

                    Tango::Except::throw_exception(
                            (const char *)"Pool_CantDeleteController", o.str(),
                            (const char *)"Pool::delete_controller");
                }
            }
            break;

            case CONSTRAINT_CTRL:
            {
                // no devices in constraint controller so nothing to be done.
            }
            break;

            default:
            Tango::Except::throw_exception((const char *)"Pool_BadCtrlType",
                                           (const char *)"Undefined controller type !!!",
                                           (const char *)"Pool::delete_controller");
            break;
        }
    }

//
// Starting from this point, we might change the device state
//

    PoolStateEvent pse(this);

//
// Remove its entry in database. First find our infos in the ctrl_info
// vector
//
    int32_t nb_ctrl = get_controller_nb();
    string::size_type pos;

    const string &ctrl_full_name = ctrl_to_del.get_full_name();
    pos = ctrl_full_name.find('/');
    string ctrl_class = ctrl_full_name.substr(0,pos);
    string ctrl_inst = ctrl_full_name.substr(pos + 1);
    int32_t ind_array = 0;

    for (int32_t l = 0;l < nb_ctrl;l++)
    {
        string f_name_db = ctrl_info[(l * PROP_BY_CTRL) + 1];
        if ((pos = f_name_db.find('.')) != string::npos)
            f_name_db.erase(pos);
        f_name_db = f_name_db + '.';
        string ctrl_class_db = ctrl_info[(l * PROP_BY_CTRL) + 2];
        ctrl_class_db.insert(0,f_name_db);
        string inst_db = ctrl_info[(l * PROP_BY_CTRL) + 3];

        transform(ctrl_class_db.begin(),ctrl_class_db.end(),ctrl_class_db.begin(),::tolower);
        transform(inst_db.begin(),inst_db.end(),inst_db.begin(),::tolower);

        if ((ctrl_class_db == ctrl_class) && (inst_db == ctrl_inst))
        {
            ind_array = l * PROP_BY_CTRL;
            break;
        }
    }

//
// Remove controller infos in vector
//

    vector<string>::iterator v_ite = ctrl_info.begin();
    v_ite += ind_array;
    ctrl_info.erase(v_ite,v_ite+PROP_BY_CTRL);

//
// Update database
//

    Tango::DbDatum ctrl_prop(CTRL_PROP);
    Tango::DbData db_data;

    ctrl_prop << ctrl_info;
    db_data.push_back(ctrl_prop);

    try
    {
        get_db_device()->put_property(db_data);
    }
    catch (Tango::DevFailed &e)
    {
        TangoSys_OMemStream o;
        o << "Can't update Db for controller with ID " << argin << ends;

        Tango::Except::re_throw_exception(e,
                (const char *)"Pool_CantUpdateDb",o.str(),
                (const char *)"Pool::delete_controller");
    }

//
// Remove all properties of this controller in the database
//
    if (ctrl_to_del.ctrl_class_built == true)
    {
        vector<PropertyData *> &props =
            (*ctrl_to_del.ite_ctrl_class)->get_ctrl_prop_list();

        Tango::DbData ctrl_db_data;

        for(unsigned long l = 0; l < props.size(); l++)
        {
            string final_prop_name = ctrl_to_del.get_controller()->get_name() + "/" +
                                     props[l]->name;
            ctrl_db_data.push_back(Tango::DbDatum(final_prop_name));
        }

        get_db_device()->delete_property(ctrl_db_data);
    }


//
// Is there any other FiCa using the controller file ?
// If we are the last one, mark the FiCa and the File
// as unused. This will force a reload of the controller
// code next time a controller using this file is created
//
    PoolClass *cl_ptr = static_cast<PoolClass *>(this->get_device_class());
    int32_t fica_nb = 0;
    int32_t fica_f_nb = 0;
    int32_t ctrl_fica_nb = 0;
    std::string f_name;
    std::string fica_name_safe;

    if (ctrl_to_del.ctrl_class_built == true)
    {
        std::string &fica_name = ctrl_to_del.get_class_name();
        fica_name_safe = fica_name;
        f_name = fica_name.substr(0,fica_name.find('/'));
        ctrl_fica_nb = get_controller_nb_by_class_name(fica_name);
        if (ctrl_fica_nb == 1)
        {
            fica_f_nb = cl_ptr->get_fica_nb_by_f_name(f_name);
            fica_nb = cl_ptr->get_fica_nb_by_name(fica_name);
        }
    }
//
// Delete controller object and erase controller entry in pool
//

    if (ctrl_to_del.get_controller())
    {
        AutoPoolLock lo(ctrl_to_del.get_ctrl_class_mon());
        PoolUtil::instance()->clean_ctrl_elems(ctrl_to_del.get_controller()->get_name());
    }
    
    remove_controller(ctrl_to_del.id);
    
//
// Remove entry in FiCa and File vectors if needed
//

    if (ctrl_fica_nb == 1)
    {
        if (fica_f_nb == 1)
        {
            cl_ptr->remove_fica_by_name(fica_name_safe);

            if (fica_nb == 1)
                cl_ptr->remove_ctrl_file_by_name(f_name);
        }
    }

//
// Before returning, push a change_event to client(s) listening
// on event
//
    Tango::Attribute &cl = dev_attr->get_attr_by_name("ControllerList");
    read_ControllerList(cl);
    cl.fire_change_event();

}

//+------------------------------------------------------------------
/**
 *	method:	Pool::init_controller
 *
 *	description:	method to execute "InitController"
 *	Initialiaze a controller. Needed if the pool has been started when a controller was down in order to
 *	connect the controller to the pool without needs to restart the complete pool once it has
 *	been switched up.
 *
 * @param	argin	Controller name
 *
 */
//+------------------------------------------------------------------
void Pool::init_controller(Tango::DevString argin)
{
    DEBUG_STREAM << "Pool::init_controller(): entering... !" << endl;

    //	Add your own code to control device here


//
// Find controller in controller list
//

    string user_ctrl(argin);

    ControllerPool &ctrl_to_init = get_controller(user_ctrl, true);

//
// If the controller is marked as OK, do nothing
//

    if (ctrl_to_init.get_controller())
    {
        DEBUG_STREAM << "init_ctrl: ctrl was null. Exiting!" << endl;
        return;
    }
//
// If the controller FiCa is not created, throw exception
//

    if (ctrl_to_init.ctrl_class_built == false)
    {
        TangoSys_OMemStream o;
        o << "Controller code from file " << f_name_from_db_prop(ctrl_to_init.name) << " is not loaded in memory";
        o << "\nTry the ReloadControllerCode command first" << ends;

        Tango::Except::throw_exception((const char *)"Pool_ControllerNotLoaded",o.str(),
                           (const char *)"Pool::init_controller");
    }

//
// Starting from this point, we might change the device state
//

    PoolStateEvent pse(this);
    DEBUG_STREAM << "init_ctrl: after poolstateevent" << endl;
//
// Try to re-create controller object
//

    Controller *ct = NULL;
    vector<CtrlFiCa *>::iterator ctrl_fica_ite = ctrl_to_init.ite_ctrl_class;
    Language lang = (*ctrl_fica_ite)->get_language();

    string::size_type pos = ctrl_to_init.name.find('/');
    pos++;
    string inst_name_lower = ctrl_to_init.name.substr(pos);

    CtrlType obj_type = ctrl_to_init.get_ctrl_obj_type();

    if (lang == CPP)
    {

//
// Retrieve the controller object creator C function
//

        lt_ptr sym;

        string sym_name("_create_");
        sym_name = sym_name + ctrl_to_init.ctrl_class_name;

        DEBUG_STREAM << "Symbol name = " << sym_name << endl;

        sym = lt_dlsym((*ctrl_fica_ite)->get_lib_ptr(),sym_name.c_str());
        if (sym == NULL)
        {
            TangoSys_OMemStream o;
            o << "Controller library " << f_name_from_db_prop(ctrl_to_init.name) << " does not have the C creator function (_create_<Controller name>)" << ends;

            Tango::Except::throw_exception((const char *)"Pool_CCreatorFunctionNotFound",o.str(),
                               (const char *)"Pool::create_controller");
        }

        DEBUG_STREAM << "lt_dlsym is a success" << endl;

//
// Create the controller
//

        Ctrl_creator_ptr ct_ptr = (Ctrl_creator_ptr)sym;
        vector<Controller::Properties> *prop = NULL;

        try
        {
            vector<pair<string,string> > prop_pairs;
            AutoPoolLock lo((*ctrl_fica_ite)->get_mon());
            build_property_data(inst_name_lower,ctrl_to_init.ctrl_class_name,
                                prop_pairs,
                                (*ctrl_fica_ite)->get_ctrl_prop_list());
            check_property_data((*ctrl_fica_ite)->get_ctrl_prop_list());
            prop =
                properties_2_cpp_vect((*ctrl_fica_ite)->get_ctrl_prop_list());
            ct = (*ct_ptr)(inst_name_lower.c_str(),*prop);
            ctrl_to_init.cpp_ctrl_prop = prop;
        }
        catch (Tango::DevFailed &e)
        {
            if (prop != NULL)
                delete prop;

            Tango::Except::re_throw_exception(e,
                    (const char *)"Pool_CantCreateController",
                    (const char *)"Can't create controller!!!",
                    (const char *)"Pool::create_controller");
        }
    }
    else
    {

//
// Retrieve the controller object creator C function
//

        lt_ptr sym;

        string sym_name = "_create_Py";

        CtrlType type = (*ctrl_fica_ite)->get_obj_type();
        string type_str = CtrlTypeStr[type];

        sym_name += type_str;

        if(obj_type != CONSTRAINT_CTRL)
            sym_name += "Controller";

        DEBUG_STREAM << "Symbol name = " << sym_name << endl;

        sym = lt_dlsym((*ctrl_fica_ite)->get_py_inter_lib_ptr(),sym_name.c_str());
        if (sym == NULL)
        {
            TangoSys_OMemStream o;
            o << "Controller library " << f_name_from_db_prop(ctrl_to_init.name);
            o << " does not have the C creator function "
                 "(_create_<Controller name>)" << ends;

            Tango::Except::throw_exception(
                    (const char *)"Pool_CCreatorFunctionNotFound",o.str(),
                    (const char *)"Pool::create_controller");
        }

        DEBUG_STREAM << "lt_dlsym is a success" << endl;

//
// Create the Python controller object but before re-read the property
//

        PyCtrl_creator_ptr ct_ptr = (PyCtrl_creator_ptr)sym;
        try
        {
            vector<pair<string,string> > prop_pairs;
            AutoPoolLock lo((*ctrl_fica_ite)->get_mon());
            build_property_data(inst_name_lower,ctrl_to_init.ctrl_class_name,
                                prop_pairs,
                                (*ctrl_fica_ite)->get_ctrl_prop_list());
            check_property_data((*ctrl_fica_ite)->get_ctrl_prop_list());
            PyObject *prop_dict =
                properties_2_py_dict((*ctrl_fica_ite)->get_ctrl_prop_list());
            ct = (*ct_ptr)(inst_name_lower.c_str(),
                           ctrl_to_init.ctrl_class_name.c_str(),
                           (*ctrl_fica_ite)->get_py_module(),prop_dict);
        }
        catch (Tango::DevFailed &e)
        {
            Tango::Except::re_throw_exception(e,
                    (const char *)"Pool_CantCreateController",
                    (const char *)"Can't create controller!!!",
                    (const char *)"Pool::create_controller");
        }
    }

//
// Update controller object ptr and the possibly changed MaxDevice prop
//

    ctrl_to_init.set_controller(ct);

    vct_ite	tmp_ite = ctrl_to_init.ite_ctrl_class;

//
// Send a Init command to all objects belonging to this controller
// Warning: The object init command delete and re-insert entry
// in the object list. Take care of this in iterator management
//


    if (obj_type == MOTOR_CTRL)
    {
        for (PoolElementTypeIt elem_it = element_types.lower_bound(MOTOR_ELEM);
             elem_it != element_types.upper_bound(MOTOR_ELEM); ++elem_it)
        {
            MotorPool &motor_pool = get_physical_motor(elem_it->second);

            if (motor_pool.get_ctrl_id() == ctrl_to_init.id)
            {
                int32_t dist = distance(element_types.lower_bound(MOTOR_ELEM), elem_it);
//
// Get the listeners
//
                list<IPoolElementListener*> listeners = motor_pool.get_pool_elem_listeners();
                get_element_proxy(motor_pool)->command_inout("Init");
                elem_it = element_types.lower_bound(MOTOR_ELEM);
                advance(elem_it, dist);
//
// Restore the listeners to the new MotorPool object
//
                MotorPool &new_motor_pool = get_physical_motor(elem_it->second);
                new_motor_pool.set_pool_elem_listeners(listeners);

//
// Inform the listeners that the motor changed structure
//
                if(new_motor_pool.has_listeners())
                {
                    PoolElementEvent evt(ElementStructureChange, &new_motor_pool);
                    new_motor_pool.fire_pool_elem_change(&evt);
                }
            }
        }
    }
    else if (obj_type == COTI_CTRL)
    {
        PoolElementTypeIt elem_beg = element_types.lower_bound(COTI_ELEM);
        for (PoolElementTypeIt elem_it = elem_beg;
             elem_it != element_types.upper_bound(COTI_ELEM); ++elem_it)
        {
            CTExpChannelPool &ct_pool = get_countertimer(elem_it->second);
            if (ct_pool.get_ctrl_id() == ctrl_to_init.id)
            {
                int32_t dist = distance(elem_beg, elem_it);
//
// Get the listeners
//
                list<IPoolElementListener*> listeners = ct_pool.get_pool_elem_listeners();
                get_element_proxy(ct_pool)->command_inout("Init");
                elem_it = elem_beg;
                advance(elem_it, dist);
//
// Restore the listeners to the new CTPool object
//              
                CTExpChannelPool &new_ct_pool = get_countertimer(elem_it->second);
                new_ct_pool.set_pool_elem_listeners(listeners);

//
// Inform the listeners that the channel changed structure
//
                if(new_ct_pool.has_listeners())
                {
                    PoolElementEvent evt(ElementStructureChange, &new_ct_pool);
                    new_ct_pool.fire_pool_elem_change(&evt);
                }
            }
        }
    }
    else if (obj_type == ZEROD_CTRL)
    {
        PoolElementTypeIt elem_beg = element_types.lower_bound(ZEROD_ELEM);
        for (PoolElementTypeIt elem_it = elem_beg;
             elem_it != element_types.upper_bound(ZEROD_ELEM); ++elem_it)
        {
            ZeroDExpChannelPool &zerod_pool = get_zerod(elem_it->second);

            if (zerod_pool.get_ctrl_id() == ctrl_to_init.id)
            {
                int32_t dist = distance(elem_beg, elem_it);
//
// Get the listeners
//
                list<IPoolElementListener*> listeners = zerod_pool.get_pool_elem_listeners();
                get_element_proxy(zerod_pool)->command_inout("Init");
                elem_it = elem_beg;
                advance(elem_it, dist);
//
// Restore the listeners to the new 0D Pool object
//
                ZeroDExpChannelPool &new_zerod_pool = get_zerod(elem_it->second);
                new_zerod_pool.set_pool_elem_listeners(listeners);

//
// Inform the listeners that the channel changed structure
//
                if(new_zerod_pool.has_listeners())
                {
                    PoolElementEvent evt(ElementStructureChange, &new_zerod_pool);
                    new_zerod_pool.fire_pool_elem_change(&evt);
                }
            }
        }
    }

    else if (obj_type == ONED_CTRL)
    {
        PoolElementTypeIt elem_beg = element_types.lower_bound(ONED_ELEM);
        for (PoolElementTypeIt elem_it = elem_beg;
             elem_it != element_types.upper_bound(ONED_ELEM); ++elem_it)
        {
            OneDExpChannelPool &oned_pool = get_oned(elem_it->second);
            if (oned_pool.get_ctrl_id() == ctrl_to_init.id)
            {
                int32_t dist = distance(elem_beg, elem_it);
//
// Get the listeners
//	  			
                list<IPoolElementListener*> listeners = oned_pool.get_pool_elem_listeners();
                get_element_proxy(oned_pool)->command_inout("Init");  					
                elem_it = elem_beg;
                advance(elem_it, dist);
//
// Restore the listeners to the new 1D Pool object
//	  			
                OneDExpChannelPool &new_oned_pool = get_oned(elem_it->second);
                new_oned_pool.set_pool_elem_listeners(listeners);

                
//
// Inform the listeners that the channel changed structure
//	
                if(new_oned_pool.has_listeners())
                {
                    PoolElementEvent evt(ElementStructureChange, &new_oned_pool);
                    new_oned_pool.fire_pool_elem_change(&evt);
                }	  		  			
            }
        }
    }

    else if (obj_type == TWOD_CTRL)
    {
        PoolElementTypeIt elem_beg = element_types.lower_bound(TWOD_ELEM);
        for (PoolElementTypeIt elem_it = elem_beg;
             elem_it != element_types.upper_bound(TWOD_ELEM); ++elem_it)
        {
            TwoDExpChannelPool &twod_pool = get_twod(elem_it->second);
            if (twod_pool.get_ctrl_id() == ctrl_to_init.id)
            {
                int32_t dist = distance(elem_beg, elem_it);
//
// Get the listeners
//	  			
                list<IPoolElementListener*> listeners = twod_pool.get_pool_elem_listeners();
                get_element_proxy(twod_pool)->command_inout("Init");  					
                elem_it = elem_beg;
                advance(elem_it, dist);
//
// Restore the listeners to the new 2D Pool object
//	  			
                TwoDExpChannelPool &new_twod_pool = get_twod(elem_it->second);
                new_twod_pool.set_pool_elem_listeners(listeners);

                
//
// Inform the listeners that the channel changed structure
//	
                if(new_twod_pool.has_listeners())
                {
                    PoolElementEvent evt(ElementStructureChange, &new_twod_pool);
                    new_twod_pool.fire_pool_elem_change(&evt);
                }	  		  			
            }
        }
    }  

//
// The object Init command clears the object proxy. Mark the
// proxy created flag as false to recreate the proxy
//

    proxy_created = false;
}

//+------------------------------------------------------------------
/**
 *	method:	Pool::send_to_controller
 *
 *	description:	method to execute "SendToController"
 *	This commands sends an uninterpreted string to a controller. The first input argument is the controller
 *	name. The second input argument is the string to be sent to the controller.
 *	It returns the controller answer without any interpretation.
 *
 * @param	argin	In[0] = Controller name, In[1] = String to send
 * @return	The controller answer
 *
 */
//+------------------------------------------------------------------
Tango::DevString Pool::send_to_controller(const Tango::DevVarStringArray *argin)
{
    //	POGO has generated a method core with argout allocation.
    //	If you would like to use a static reference without copying,
    //	See "TANGO Device Server Programmer's Manual"
    //		(chapter : Writing a TANGO DS / Exchanging data)
    //------------------------------------------------------------
    Tango::DevString	argout;
    DEBUG_STREAM << "Pool::send_to_controller(): entering... !" << endl;

    //	Add your own code to control device here

//
// Check input args
//

    if (argin->length() != 2)
    {
        Tango::Except::throw_exception((const char *)"Pool_WrongArgument",
                        (const char *)"Wrong number of arguments. Two arguments required",
                        (const char *)"Pool::send_to_controller()");
    }

    string ctrl_name((*argin)[0]);

//
// Check that we have this controller
//

    ControllerPool &ctl = get_controller(ctrl_name, true);

//
// Check that ctrl is OK
//

    if (!ctl.get_controller())
    {
        TangoSys_OMemStream o;
        o << "Controller " << ctrl_name << " is not valid" << ends;

        Tango::Except::throw_exception((const char *)"Pool_WrongArgument",o.str(),
                    (const char *)"Pool::send_to_controller()");
    }

//
// Send string to ctrl
//

    string sent((*argin)[1]);
    string received;

    {
        AutoPoolLock lo(ctl.get_ctrl_class_mon());
        received = ctl.get_controller()->SendToCtrl(sent);
    }

    argout = new char[received.size() + 1];
    strcpy(argout,received.c_str());

    return argout;
}

//+------------------------------------------------------------------
/**
 *	method:	Pool::get_controller_info
 *
 *	description:	method to execute "GetControllerInfo"
 *	Get controller class data like parameters description from the controller class name
 *
 * @param	argin	in[0] - Controller type, in[1] - Controller file name, in[2] - Controller class name, in[3] - Controller instance name (optional)
 * @return	Controller class data
 *
 */
//+------------------------------------------------------------------
Tango::DevVarStringArray* Pool::get_controller_info(const Tango::DevVarStringArray *argin)
{
    //	Add your own code to control device here

//
// Get info from controller
//
    vector<string> info;
    get_ctrl_info(argin, info);

//
// Return info to caller
//
    Tango::DevVarStringArray *argout = new Tango::DevVarStringArray();
    argout->length(info.size());

    for(unsigned int i = 0;i < info.size();i++)
        (*argout)[i] = CORBA::string_dup(const_cast<char *>(info[i].c_str()));

    return argout;
}

//+------------------------------------------------------------------
/**
 *	method:	Pool::get_controller_info_ex
 *
 *	description:	method to execute "GetControllerInfoEx"
 *	Get controller class extra data like parameters description from the controller class name
 *
 * @param	argin	in[0] - Controller type, in[1] - Controller file name, in[2] - Controller class name
 * @return	Controller class data
 *
 */
//+------------------------------------------------------------------
Tango::DevVarCharArray* Pool::get_controller_info_ex(const Tango::DevVarStringArray *argin)
{
    DEBUG_STREAM << "Pool::get_controller_info_ex(): entering... !" << endl;

    //	Add your own code to control device here

//
// Get info from controller
//
    vector<string> info;
    Tango::DevVarCharArray *info_ex = new Tango::DevVarCharArray();
    get_ctrl_info(argin, info, info_ex);

//
// Return info to caller
//
    return info_ex;
}

//+------------------------------------------------------------------
/**
 *	method:	Pool::get_controller_info
 *
 *	description:	method to execute "GetControllerInfo"/"GetControllerInfoEx"
 *	Get controller class data like parameters description from the controller class name
 *
 * @param	argin	in[0] - Controller type,
 * 					in[1] - Controller file name,
 * 					in[2] - Controller class name,
 * 					in[3] - Controller instance name (optional)
 * @return	Controller class data
 *
 */
//+------------------------------------------------------------------
void Pool::get_ctrl_info(const Tango::DevVarStringArray *argin,
                         vector<string> &info, Tango::DevVarCharArray *info_ex)
{

//
// Check if the user request for instance info or class info
//

    string instance_name;
    bool instance_info = false;

    long nb_args = argin->length();

    if (nb_args == 4)
    {
        instance_name = (*argin)[3];
        instance_info = true;
    }
    else if ((nb_args < 3) || (nb_args > 4))
    {
        Tango::Except::throw_exception(
            (const char *)"Pool_WrongArgumentNumber",
            (const char *)"Wrong number of argument for command GetControllerInfo."
                          " Needs 3 or 4 strings",
            (const char *)"Pool::get_controller_info");
    }

    string ctrl_type = (*argin)[0].in();
    string module_name = (*argin)[1].in();
    string class_name = (*argin)[2].in();
    string f_name;

//
// Check the module (file) name
//

    string::size_type pos;

    if ((pos = module_name.find('.')) == string::npos)
    {
        TangoSys_OMemStream o;
        o << module_name << " does not have file type extension.";
        o << "Please define one (.py or .la)" << ends;

        Tango::Except::throw_exception(
            (const char *)"Pool_FileUnsupportedType",o.str(),
            (const char *)"Pool::get_controller_info");
    }
    else
    {
        string file_ext = module_name.substr(pos);

        if ((file_ext == ".la") || (file_ext == ".py")) ;
        else
        {
            TangoSys_OMemStream o;
            o << "File " << module_name << " is from one unsupported type";
            o << ends;

            Tango::Except::throw_exception(
                (const char *)"Pool_FileUnsupportedType",o.str(),
                (const char *)"Pool::get_controller_info");
        }
    }

    PoolClass *cl_ptr = static_cast<PoolClass *>(this->get_device_class());

//
// Check the controller type
//

    transform(ctrl_type.begin(),ctrl_type.end(),ctrl_type.begin(),::tolower);
    ctrl_type[0] = ::toupper(ctrl_type[0]);
    CtrlType type = str_2_CtrlType(ctrl_type);

//
// Check that we know this class
//

    Language lang = UNDEF_LANG;
    if(find_file_in_pool_path(module_name,f_name,PYTHON) == false)
    {
        if(find_file_in_pool_path(module_name,f_name,CPP) == false)
        {
            TangoSys_OMemStream o;
            o << "The " << module_name << " module or file could not be found.";
            o << " Please check that PoolPath property contains the correct "
                 "path." << ends;

            Tango::Except::throw_exception(
                (const char *)"Pool_CantLocateControllerFile",
                o.str(),
                (const char *)"Pool::get_controller_class_info");
        }
        else
            lang = CPP;
    }
    else
        lang = PYTHON;

//
// First check if the Pool device contains the controller file
//

    bool local_ctrl_file_found = false;
    vcf_ite ctrl_f;

    try
    {
        string::size_type pos = f_name.rfind('/');
        string tmp_name = f_name.substr(pos + 1);
        ctrl_f = cl_ptr->get_ctrl_file_by_name(tmp_name);
        local_ctrl_file_found = true;
    }
    catch (Tango::DevFailed &e)
    {
    }

//
// Trying to get instance information for a controller file that has not even
// been loaded yet is an error
//
    if(local_ctrl_file_found == false && instance_info == true)
    {
        TangoSys_OMemStream o;
        o << "The controller instance " << (*argin)[3].in();
        o << " does not exist" << ends;
        Tango::Except::throw_exception(
            (const char *)"Pool_CantLocateController",o.str(),
            (const char *)"Pool::get_controller_info");
    }

    if(instance_info == false)
    {
//
// Build a temporary xxxCtrlFile object even if the controller already exists.
// This is done because the file may have been changed and we want to return
// always the latest information.
//
        CtrlFile *tmp_ctrl_file = NULL;

        if (lang == PYTHON)
        {
            switch(type)
            {
                case MOTOR_CTRL:
                tmp_ctrl_file = new PyMotCtrlFile(f_name);
                break;

                case PSEUDO_MOTOR_CTRL:
                tmp_ctrl_file = new PyPseudoMotCtrlFile(f_name);
                break;

                case PSEUDO_COUNTER_CTRL:
                tmp_ctrl_file = new PyPseudoCoCtrlFile(f_name);
                break;

                case COTI_CTRL:
                tmp_ctrl_file = new PyCoTiCtrlFile(f_name);
                break;

                case ZEROD_CTRL:
                tmp_ctrl_file = new PyZeroDCtrlFile(f_name);
                break;

                case ONED_CTRL:
                tmp_ctrl_file = new PyOneDCtrlFile(f_name);
                break;
                
                case TWOD_CTRL:
                tmp_ctrl_file = new PyTwoDCtrlFile(f_name);
                break;                
                
                case COM_CTRL:
                tmp_ctrl_file = new PyComCtrlFile(f_name);
                break;

                case IOREGISTER_CTRL:
                tmp_ctrl_file = new PyIORegisterCtrlFile(f_name);
                break;


                case CONSTRAINT_CTRL:
                tmp_ctrl_file = new PyConstraintFile(f_name);
                break;

                default:
                Tango::Except::throw_exception(
                        (const char *)"Pool_BadCtrlType",
                        (const char *)"Undefined controller type !!!",
                        (const char *)"Pool::get_controller_info");
                break;
            }
        }
        else
        {
            switch(type)
            {
                case MOTOR_CTRL:
                tmp_ctrl_file = new CppMotCtrlFile(f_name);
                break;

                case PSEUDO_MOTOR_CTRL:
                tmp_ctrl_file = new CppPseudoMotCtrlFile(f_name);
                break;

                case PSEUDO_COUNTER_CTRL:
                tmp_ctrl_file = new CppPseudoCoCtrlFile(f_name);
                break;

                case COTI_CTRL:
                tmp_ctrl_file = new CppCoTiCtrlFile(f_name);
                break;

                case ZEROD_CTRL:
                tmp_ctrl_file = new CppZeroDCtrlFile(f_name);
                break;

                case ONED_CTRL:
                tmp_ctrl_file = new CppOneDCtrlFile(f_name);
                break;
            
                case TWOD_CTRL:
                tmp_ctrl_file = new CppTwoDCtrlFile(f_name);
                break;	

                case COM_CTRL:
                tmp_ctrl_file = new CppComCtrlFile(f_name);
                break;

                case IOREGISTER_CTRL:
                tmp_ctrl_file = new CppIORegisterCtrlFile(f_name);
                break;

                case CONSTRAINT_CTRL:
                tmp_ctrl_file = new CppConstraintFile(f_name);
                break;

                default:
                Tango::Except::throw_exception(
                        (const char *)"Pool_BadCtrlType",
                        (const char *)"Undefined controller type !!!",
                        (const char *)"Pool::get_controller_info");
                break;
            }
        }

//
// Get the number of controller class defined in this file
//

        int32_t nb_class = 0;
        std::vector<std::string> tmp_ctrl_list;
        std::vector<std::string> ctrl_type_list;
        try
        {
            nb_class = tmp_ctrl_file->get_classes(tmp_ctrl_list, ctrl_type_list);
        }
        catch (Tango::DevFailed &e)
        {
            TangoSys_OMemStream o;
            o << "The class " << class_name << " does not exist ";
            o << "(or is not a valid controller) in file " << f_name << ends;
            Tango::Except::throw_exception(
                (const char *)"Pool_BadArgument", o.str(),
                (const char *)"Pool::get_controller_info");
        }

//
// Check that the user class is one of the class found in the file
//

        if (nb_class == 0)
        {
            TangoSys_OMemStream o;
            o << "The class " << class_name << " does not exist ";
            o << "(or is not a valid controller) in file " << f_name << ends;
            Tango::Except::throw_exception(
                (const char *)"Pool_BadArgument", o.str(),
                (const char *)"Pool::get_controller_info");
        }
        long cl_ind;
        for (cl_ind = 0;cl_ind < nb_class;cl_ind++)
        {
            std::string::size_type pos = tmp_ctrl_list[cl_ind].find('.');
            std::string class_wo_mod;
            if (pos != string::npos)
                class_wo_mod = tmp_ctrl_list[cl_ind].substr(pos + 1);
            else
                class_wo_mod = tmp_ctrl_list[cl_ind];
            if (class_wo_mod == class_name)
                break;
        }
        if (cl_ind == nb_class)
        {
            TangoSys_OMemStream o;
            o << "The class " << class_name << " does not exist ";
            o << "(or is not a valid controller) in file " << f_name << ends;
            Tango::Except::throw_exception(
                (const char *)"Pool_BadArgument",o.str(),
                (const char *)"Pool::get_controller_info");
        }
//
// Get class info
//
        if(info_ex == NULL)
            tmp_ctrl_file->get_info(class_name,info);
        else
            tmp_ctrl_file->get_info_ex(class_name,info_ex);

        delete tmp_ctrl_file;
    }
//
// In case the information about an instance is requested and
// the controller is already loaded
//
    else
    {
        ControllerPool *ctrl_in_pool = NULL;
        try
        {
            ctrl_in_pool = &get_controller(instance_name, true);
        }
        catch (Tango::DevFailed &e)
        {
            TangoSys_OMemStream o;
            o << "The controller instance " << instance_name;
            o << " does not exist" << ends;
            Tango::Except::throw_exception(
                    (const char *)"Pool_CantLocateControllerInstance",o.str(),
                    (const char *)"Pool::get_controller_info");
        }

        if(ctrl_in_pool->ctrl_class_name != class_name)
        {
            TangoSys_OMemStream o;
            o << "The controller instance " << instance_name;
            o << " does not exist for the class " << module_name << ends;
            Tango::Except::throw_exception(
                    (const char *)"Pool_CantLocateControllerInstance",o.str(),
                    (const char *)"Pool::get_controller_info");
        }
        vct_ite ite = ctrl_in_pool->ite_ctrl_class;

        if(info_ex == NULL)
            (*ite)->get_ctrl_file()->get_info(class_name,instance_name,info);
        else
            (*ite)->get_ctrl_file()->get_info_ex(class_name,instance_name,info_ex);
    }
}

//+------------------------------------------------------------------
/**
 *	method:	Pool::create_exp_channel
 *
 *	description:	method to execute "CreateExpChannel"
 *	This command creates a new experiment channel in the pool. It has three arguments which are
 *	1 - The controller name (its instance name)
 *	2 - The experiment channel number within the controller
 *	3 - The experiment channel name. The experiment channel name is a Tango alias and does not have any '/' characters.
 *	This command creates a Tango device with a Tango name set to
 *	"ctexp/controller_instance_name/ctrl_number"
 *	and with an alias as given by the user in the command parameter.
 *	All the created experiment channels are automatically re-created at pool device startup time.
 *
 * @param	argin	long[0] = Exp Channel number in Ctrl, string[0] = Exp Channel name, string[1] = Controller instance name
 *
 */
//+------------------------------------------------------------------
void Pool::create_exp_channel(const Tango::DevVarLongStringArray *argin)
{
    DEBUG_STREAM << "Pool::create_exp_channel(): entering... !" << endl;

    //	Add your own code to control device here

    int32_t l_len = argin->lvalue.length();
    int32_t str_len = argin->svalue.length();
    
    if ((l_len != 1) || (str_len < 2))
    {
        Tango::Except::throw_exception((const char *)"Pool_WrongArgumentNumber",
                        (const char *)"Wrong number of argument for command CreateExpChannel. Needs 1 long and at least 2 strings",
                        (const char *)"Pool::create_exp_channel");
    }

    Tango::DevLong channel_idx = argin->lvalue[0];
    string ctrl_inst_name(argin->svalue[1]);
    string channel_name(argin->svalue[0]);
    ControllerPool &channel_ctrl = get_controller(ctrl_inst_name, true);
    int32_t ctrl_id = channel_ctrl.id;

    DEBUG_STREAM << "Controller ID = " << ctrl_id << endl;
    DEBUG_STREAM << "Motor index = " << channel_idx << endl;
    DEBUG_STREAM << "Motor name = " << channel_name << endl;

//
// Check if the controller has been successfully constructed
//

    if (!channel_ctrl.get_controller())
    {
        Tango::Except::throw_exception((const char *)"Pool_WrongControllerId",
                        (const char *)"Can't create an experiment channel on a non-responding controller",
                        (const char *)"Pool::create_exp_channel");
    }

    CtrlType channel_type = channel_ctrl.get_ctrl_obj_type();

//
// Check if we don't have already  enough experiment channel
//

    DEBUG_STREAM << "Checking exp channel number" << endl;

    switch (channel_type)
    {
        case COTI_CTRL:
        if (get_countertimer_nb() == MAX_CT)
        {
            Tango::Except::throw_exception((const char *)"Pool_TooManyCounterTimer",
                               (const char *)"Too many CounterTimer in your pool",
                               (const char *)"Pool::create_exp_channel");
        }
        break;

        case ZEROD_CTRL:
        if (get_zerod_nb() == MAX_ZEROD)
        {
            Tango::Except::throw_exception((const char *)"Pool_TooManyZeroDExpChannel",
                               (const char *)"Too many Zero D Experiment Channel in your pool",
                               (const char *)"Pool::create_exp_channel");
        }
        break;

        case ONED_CTRL:
        if (get_oned_nb() == MAX_ONED)
        {
            Tango::Except::throw_exception((const char *)"Pool_TooManyOneDExpChannel",
                               (const char *)"Too many One D Experiment Channel in your pool",
                               (const char *)"Pool::create_exp_channel");
        }
        break;

        case TWOD_CTRL:
        if (get_twod_nb() == MAX_TWOD)
        {
            Tango::Except::throw_exception((const char *)"Pool_TooManyTwoDExpChannel",
                               (const char *)"Too many Two D Experiment Channel in your pool",
                               (const char *)"Pool::create_exp_channel");
        }
        break;
        
        case UNDEF_CTRL:
        Tango::Except::throw_exception((const char *)"Pool_BadCtrlType",
                                       (const char *)"Undefined controller type !!!",
                                       (const char *)"Pool::create_exp_channel");
        break;

        case MOTOR_CTRL:
        Tango::Except::throw_exception((const char *)"Pool_BadCtrlType",
                                       (const char *)"Cannot create an experiment channel from a motor controller !!!",
                                       (const char *)"Pool::create_exp_channel");
        break;

        case CONSTRAINT_CTRL:
        Tango::Except::throw_exception((const char *)"Pool_BadCtrlType",
                                       (const char *)"Cannot create an experiment channel from a constraint !!!",
                                       (const char *)"Pool::create_exp_channel");
        break;

        default:
        Tango::Except::throw_exception((const char *)"Pool_BadCtrlType",
                                       (const char *)"Unhandled controller type!!!",
                                       (const char *)"Pool::create_exp_channel");
        break;        
    }

//
// Check that the controller still have some experiment channel available
//

    if (channel_ctrl.nb_dev == channel_ctrl.MaxDevice)
    {
        TangoSys_OMemStream o;
        o << "Max number of experiment channel reached (" << channel_ctrl.MaxDevice << ")" << ends;

        Tango::Except::throw_exception((const char *)"Pool_MaxNbExpChannelInCtrl",o.str(),
                                       (const char *)"Pool::create_exp_channel()");
    }

//
// Build Tango device name
//

    string tg_dev_name = "";
    if (str_len >= 3)
    {
        tg_dev_name = argin->svalue[2];
    }
    else
    {
        stringstream s;
        s << channel_idx;

        tg_dev_name = "expchan/" + channel_ctrl.name + '/' + s.str();
    }

    DEBUG_STREAM << "Tango device name = " << tg_dev_name << endl;

//
// Check if this device is already defined in database
// Check by device alias and by Tango device name
//

    Tango::Util *tg = Tango::Util::instance();
    Tango::Database *db = tg->get_database();

    Tango::DbDevImportInfo my_device_import;
    bool device_exist = false;
    bool by_alias = false;

    try
    {
        my_device_import = db->import_device(channel_name);
        device_exist = true;
        by_alias = true;
    }
    catch (Tango::DevFailed &e)
    {
        if (::strcmp(e.errors[0].reason.in(),"DB_DeviceNotDefined") != 0)
        {
            device_exist = true;
        }
    }

    if (device_exist == false)
    {
        try
        {
            my_device_import = db->import_device(tg_dev_name);
            device_exist = true;
        }
        catch (Tango::DevFailed &e)
        {
            if (::strcmp(e.errors[0].reason.in(),"DB_DeviceNotDefined") != 0)
            {
                device_exist = true;
            }
        }
    }

    if (device_exist == true)
    {
        TangoSys_OMemStream o;
        o << "Experiment channel ";
        if (by_alias == false)
            o << "device name " << tg_dev_name;
        else
            o << "name " << channel_name;
        o << " is already defined" << ends;
        
        Tango::Except::throw_exception("Pool_WrongExpChannelName", o.str(),
                                       "Pool::create_exp_channel");
    }

//
// If the device is not defined in database, create it in database, set its alias,
// define the property used to store its ID (called motor_id) and create the default
// abs_change property for the Position attribute
//

    if (device_exist == false)
    {
        DEBUG_STREAM << "Trying to create device entry in database" << endl;

        try
        {
            Tango::DbDevInfo my_device_info;
            my_device_info.name = tg_dev_name.c_str();
            if (channel_type == COTI_CTRL)
            {
                my_device_info._class = "CTExpChannel";
            }
            else if (channel_type == ZEROD_CTRL)
            {
                my_device_info._class = "ZeroDExpChannel";
            }
            else if (channel_type == ONED_CTRL)
            {      			
                my_device_info._class = "OneDExpChannel";
            }
            else if (channel_type == TWOD_CTRL)
            {      			
                my_device_info._class = "TwoDExpChannel";
            }			

            my_device_info.server = tg->get_ds_name().c_str();

            db->add_device(my_device_info);
            db->put_device_alias(tg_dev_name,channel_name);

            Tango::DbDatum db_id(ID_PROP);
            Tango::DbData db_data;
            ElementId exp_channel_id = get_new_id();
            db_id << (Tango::DevLong)exp_channel_id;
            
            Tango::DbDatum db_ctrl_id(CTRL_ID_PROP);
            db_ctrl_id << (Tango::DevLong)ctrl_id;

            Tango::DbDatum db_axis(AXIS_PROP);
            db_axis << channel_idx;
            
            db_data.push_back(db_id);
            db_data.push_back(db_ctrl_id);
            db_data.push_back(db_axis);

            db->put_device_property(tg_dev_name.c_str(),db_data);

            if (channel_type == COTI_CTRL)
            {
                Tango::DbDatum pos("Value"),abs_ch("abs_change");
                db_data.clear();
                pos << (long)1;
                abs_ch << defaultCtVal_AbsChange;
                db_data.push_back(pos);
                db_data.push_back(abs_ch);
            }
            else if (channel_type == ZEROD_CTRL)
            {
                Tango::DbDatum pos("CumulatedValue"),abs_ch("abs_change");
                db_data.clear();
                pos << (long)1;
                abs_ch << defaultZeroDVal_AbsChange;
                db_data.push_back(pos);
                db_data.push_back(abs_ch);
            }
            else if (channel_type == ONED_CTRL)
            {
                Tango::DbDatum pos("Value"),abs_ch("abs_change");
                db_data.clear();
                pos << (long)1;
                abs_ch << defaultOneDVal_AbsChange;
                db_data.push_back(pos);
                db_data.push_back(abs_ch);
            }
            

                    if(channel_type != TWOD_CTRL){
                        db->put_device_attribute_property(tg_dev_name.c_str(),db_data);
                    }

            DEBUG_STREAM << "Device created in database (with alias)" << endl;
        }
        catch (Tango::DevFailed &e)
        {
            DEBUG_STREAM << "Gasp an exception........" << endl;
            TangoSys_OMemStream o;
            o << "Can't create experiment channel " << channel_name << " in database" << ends;

            Tango::Except::re_throw_exception(e,(const char *)"Pool_CantCreateExpChannel",o.str(),
                              (const char *)"Pool::create_exp_channel");
        }

//
// Find the Tango Experiment channel class and create the device
//

        string cl_name;
        if (channel_type == COTI_CTRL)
        {
            cl_name = "CTExpChannel";
        }
        else if (channel_type == ZEROD_CTRL)
        {
            cl_name = "ZeroDExpChannel";
        }

        else if (channel_type == ONED_CTRL)
        {
            cl_name = "OneDExpChannel";
        }
        else if (channel_type == TWOD_CTRL)
        {
            cl_name = "TwoDExpChannel";
        }

        const vector<Tango::DeviceClass *> *cl_list = tg->get_class_list();
        for (unsigned long i = 0;i < cl_list->size();i++)
        {
            if ((*cl_list)[i]->get_name() == cl_name)
            {
                try
                {
                    Tango::DevVarStringArray na;
                    na.length(1);
                    na[0] = tg_dev_name.c_str();
                    (*cl_list)[i]->device_factory(&na);
                    break;
                }
                catch (Tango::DevFailed &e)
                {
                    DEBUG_STREAM << "Exception while trying to create Experiment Channel device" << endl;

//
// Check if this experiment channel has already been added into pool structures
// If yes, remove it from pool structures
//

                    try
                    {
                        DevicePool::remove_element(channel_name);
                    }
                    catch (...) {}

//
// The delete_device will also delete device property(ies)
//

                    db->delete_device(tg_dev_name);

                    TangoSys_OMemStream o;
                    o << "Can't create experiment channel device " << channel_name << ends;

                    Tango::Except::re_throw_exception(e,(const char *)"Pool_CantCreateExpChannel",o.str(),
                              (const char *)"Pool::create_exp_channel");
                }
            }
        }

//
// Create a Tango device proxy on the newly created experiment channel
// and set its connection to automatic re-connection
//
        PoolElement *pe_ptr = get_element(channel_name);
        Tango::DeviceProxy *tmp_dev = new Tango::DeviceProxy(pe_ptr->get_full_name().c_str());
        tmp_dev->set_transparency_reconnection(true);
        
        Tango::Device_4Impl *dev = static_cast<Tango::Device_4Impl *>
            (tg->get_device_by_name(pe_ptr->get_full_name()));
        
        set_tango_element(*pe_ptr, tmp_dev, dev);
    }

//
// Inform ghost group that there is a new channel
//
    MeasurementGroup_ns::MeasurementGroup *ghost_ptr = get_ghost_measurement_group_ptr();
    {
        Tango::AutoTangoMonitor atm(ghost_ptr);
        if (channel_type == COTI_CTRL)
            ghost_ptr->add_ct_to_ghost_group(get_last_assigned_id());
        else if (channel_type == ZEROD_CTRL)
            ghost_ptr->add_zerod_to_ghost_group(get_last_assigned_id());
        else if (channel_type == ONED_CTRL)
            ghost_ptr->add_oned_to_ghost_group(get_last_assigned_id());
        else if (channel_type == TWOD_CTRL)
            ghost_ptr->add_twod_to_ghost_group(get_last_assigned_id());
    }

//
// Push a change event for client listenning on event
//

    Tango::Attribute &ecl = dev_attr->get_attr_by_name("ExpChannelList");
    read_ExpChannelList(ecl);
    ecl.fire_change_event();

}

//+------------------------------------------------------------------
/**
 *	method:	Pool::delete_exp_channel
 *
 *	description:	method to execute "DeleteExpChannel"
 *	Delete a experiment channel from its name
 *	Once an experiment channel is deleted, it is not available any more. All its information have been
 *	removed from the database
 *
 * @param	argin	Exp Channel name
 *
 */
//+------------------------------------------------------------------
void Pool::delete_exp_channel(Tango::DevString argin)
{
    DEBUG_STREAM << "Pool::delete_exp_channel(): entering... !" << endl;

    //	Add your own code to control device here

//
// Find experiment channel in exp channel list
//

    string user_name(argin);
    PoolElement &channel_to_del =  get_experiment_channel(user_name);
    ElementId id = channel_to_del.get_id();
    ElementType type = channel_to_del.get_type();
    
    if(type == PSEUDO_COUNTER_ELEM)
    {
        TangoSys_OMemStream o;
        o << "'" << user_name << "' is a pseudo counter. Please delete it by "
             "using the 'DeletePseudoCounter' commnad" << ends;

        Tango::Except::throw_exception(
                            (const char *)"Pool_BadArgument", o.str(),
                            (const char *)"Pool::delete_exp_channel");
    }

    DEBUG_STREAM << "Experiment Channel found" << endl;

//
// Check that the exp channel is not actually used
//

    if (get_element_proxy(channel_to_del)->state() == Tango::MOVING)
    {
        TangoSys_OMemStream o;
        o << "Can't delete experiment channel with name " << argin;
        o << ". It is actually used (counting/acquiring)." << ends;

        Tango::Except::throw_exception(
                            (const char *)"Pool_CantDeleteExpChannel", o.str(),
                            (const char *)"Pool::delete_exp_channel");
    }

//
// Get experiment channel type
//

    ControllerPool &cp = get_controller(channel_to_del.get_ctrl_id());
    CtrlType channel_type = cp.get_ctrl_obj_type();

//
// If this command is used after a Stop (Abort) command, check that the pool
// internal thread has finished its job
//

    if (channel_type == COTI_CTRL)
    {
        CTExpChannelPool &ct = static_cast<CTExpChannelPool &>(channel_to_del);

        long wait_ctr = 0;
        struct timespec wait,rem;

        wait.tv_sec = 0;
        wait.tv_nsec = 10000000;
        
        CTExpChannel_ns::CTExpChannel *ct_dev = get_countertimer_device(ct);
        while (ct_dev->get_mov_th_id() != 0)
        {
            nanosleep(&wait,&rem);
            wait_ctr++;

            if (wait_ctr == 3)
            {
                TangoSys_OMemStream o;
                o << "Can't delete experiment channel with name " << argin;
                o << ". The pool internal thread still uses it" << ends;

                Tango::Except::throw_exception((const char *)"Pool_CantDeleteExpChannel",o.str(),
                                                (const char *)"Pool::delete_exp_channel");
            }
        }
    }

//
// Check that the experiment channel is not member of a measurement group
//
    for (PoolElementTypeIt elem_it = element_types.lower_bound(MEASUREMENT_GROUP_ELEM);
         elem_it != element_types.upper_bound(MEASUREMENT_GROUP_ELEM); ++elem_it)
    {
        MeasurementGroupPool &mntgrp_pool = get_measurement_group(elem_it->second);
            
        if (find(mntgrp_pool.ch_ids.begin(), mntgrp_pool.ch_ids.end(), channel_to_del.id) != mntgrp_pool.ch_ids.end())
        {
            TangoSys_OMemStream o;
            o << "Can't delete channel with name " << argin;
            o << ". It is actually member of measurement group " << mntgrp_pool.name << ends;

            Tango::Except::throw_exception(
                                (const char *)"Pool_CantDeleteChannel", o.str(),
                                (const char *)"Pool::delete_channel");
        }
    }

//
// Remove its entry in database. This will also delete any device
// properties and device attribute properties
//

    Tango::Util *tg = Tango::Util::instance();
    try
    {
        tg->get_database()->delete_device(channel_to_del.get_full_name());

//
// Delete experiment channel device from server but first find its Tango xxxClass instance
//

        Tango::DeviceClass *dc = get_element_device(id)->get_device_class();

        dc->device_destroyer(channel_to_del.get_full_name());
    }
    catch (Tango::DevFailed &e)
    {
        TangoSys_OMemStream o;
        o << "Can't delete experiment channel with name " << argin << ends;

        Tango::Except::re_throw_exception(e,(const char *)"Pool_CantDeleteExpChannel",o.str(),
                                 (const char *)"Pool::delete_exp_channel");
    }

//
// Before returning, send a change event for client listenning
// on event
//

    Tango::Attribute &ecl = dev_attr->get_attr_by_name("ExpChannelList");
    read_ExpChannelList(ecl);
    ecl.fire_change_event();

}

//+------------------------------------------------------------------
/**
 *	method:	Pool::create_measurement_group
 *
 *	description:	method to execute "CreateMeasurementGroup"
 *	This command creates a measurement group. The name of the measurement group is the first element in the input
 *	argument followed by the group element names.
 *
 * @param	argin	Measurement Group name followed by names of the elements
 *
 */
//+------------------------------------------------------------------
void Pool::create_measurement_group(const Tango::DevVarStringArray *argin)
{
    DEBUG_STREAM << "Pool::create_measurement_group(): entering... !" << endl;

    //	Add your own code to control device here

//
// Basic check on input parameters
//
    string group_name((*argin)[0]);
    long input_nb = argin->length() - 1;

    if (input_nb <= 0)
    {
        TangoSys_OMemStream o;
        o << "Cant create measurement group " << group_name << ". ";
        o << "You haven't defined any data aquisition member" << ends;

        Tango::Except::throw_exception(
                (const char *)"Pool_BadArgument",o.str(),
                (const char *)"Pool::create_measurement_group");
    }

    string second_arg((*argin)[1]);
    bool manual_tg_dev_name = second_arg.find('/') != std::string::npos;
    
    long input_start = manual_tg_dev_name ? 2 : 1;

    if(manual_tg_dev_name) input_nb--;
    
    if (input_nb <= 0)
    {
        TangoSys_OMemStream o;
        o << "Cant create measurement group " << group_name << ". ";
        o << "You haven't defined any data aquisition member" << ends;

        Tango::Except::throw_exception(
                (const char *)"Pool_BadArgument",o.str(),
                (const char *)"Pool::create_measurement_group");
    }

    DEBUG_STREAM << "Measurement Group name = " << group_name;

//
// Check if we don't have already enough measurement groups
//

    DEBUG_STREAM << "Checking measurement group number" << endl;

    if (get_measurement_group_nb() == MAX_MEASUREMENT_GROUP)
    {
        Tango::Except::throw_exception((const char *)"Pool_TooManyMeasurementGroup",
                           (const char *)"Too many measurement groups in your pool",
                           (const char *)"Pool::create_measurement_group");
    }

    
    ElemIdVector group_usr_elt_ids, group_phy_elt_ids, group_ct_elt_ids,
                 group_0D_elt_ids, group_1D_elt_ids, group_2D_elt_ids,
                 group_pseudo_elt_ids, group_motor_elt_ids;
    
    long i;
    for (i = input_start;i < input_nb + input_start;i++)
    {
        string elem_name((*argin)[i]);
        
        PoolElement *elem = get_element(elem_name);
        ElementType elem_type = elem->get_type();
        ElementId elem_id = elem->get_id();
        
        if (!IS_EXPERIMENT_CHANNEL(elem_type) && !IS_MOTOR(elem_type))
        {
            TangoSys_OMemStream o;
            o << "Element " << elem_name << " is neither a counter/timer, 0D, ";
            o << "1D or 2D experiment channel, pseudo counter or motor defined ";
            o << "in this pool. Can't create the measurement group." << ends;

            Tango::Except::throw_exception("Pool_BadArgument", o.str(),
                                           "Pool::create_measurement_group");
        }
        group_usr_elt_ids.push_back(elem_id);

//
// Check if each element is member of this pool
// as CounterTimer, 0DExpChannel, 1DExpChannel or 2DExpChannel or a pseudo counter
//
        ElemIdVector *id_vec = NULL;
        switch(elem_type)
        {
            case COTI_ELEM:           id_vec = &group_ct_elt_ids; break;
            case ZEROD_ELEM:          id_vec = &group_0D_elt_ids; break;
            case ONED_ELEM:           id_vec = &group_1D_elt_ids; break;
            case TWOD_ELEM:           id_vec = &group_2D_elt_ids; break;
            case PSEUDO_COUNTER_ELEM: id_vec = &group_pseudo_elt_ids; break;
            case MOTOR_ELEM:          id_vec = &group_motor_elt_ids; break;
            default:                  id_vec = NULL;
        }
        
        if (id_vec) id_vec->push_back(elem_id);
    }
    
    // Consider pseudo motors as physical elements since we get the values
    // directly from them
    vector<ElementType> filter;
    filter.push_back(PSEUDO_MOTOR_ELEM);
    
    user_elems_to_phy_elems(group_usr_elt_ids, group_phy_elt_ids, filter, true);

    Tango::Util *tg = Tango::Util::instance();
//
// Build Tango device name
//
    string tg_dev_name = "";
    if (manual_tg_dev_name)
    {
        tg_dev_name = second_arg;
    }
    else
    {
        tg_dev_name = "mntgrp/" + tg->get_ds_inst_name() + '/' + group_name;
    }
    
    DEBUG_STREAM << "Tango measurement group device name = " << tg_dev_name << endl;

//
// Check if this device is already defined in database
// Check by device alias and by Tango device name
//

    Tango::Database *db = tg->get_database();

    Tango::DbDevImportInfo my_device_import;
    bool device_exist = false;
    bool by_alias = false;

    try
    {
        my_device_import = db->import_device(group_name);
        device_exist = true;
        by_alias = true;
    }
    catch (Tango::DevFailed &e)
    {
        if (::strcmp(e.errors[0].reason.in(),"DB_DeviceNotDefined") != 0)
        {
            device_exist = true;
        }
    }

    if (device_exist == false)
    {
        try
        {
            my_device_import = db->import_device(tg_dev_name);
            device_exist = true;
        }
        catch (Tango::DevFailed &e)
        {
            if (::strcmp(e.errors[0].reason.in(),"DB_DeviceNotDefined") != 0)
            {
                device_exist = true;
            }
        }
    }

    if (device_exist == true)
    {
        TangoSys_OMemStream o;
        o << "Measurement group ";
        if (by_alias == false)
            o << tg_dev_name;
        else
            o << group_name;
        o << " already defined" << ends;

        Tango::Except::throw_exception((const char *)"Pool_WrongMeasurementGroupName",o.str(),
                        (const char *)"Pool::create_measurement_group");
    }



//
// If the device is not defined in database, create it in database, set its alias
// and define its properties used to store its ID, its device pool and its element list
//

    if (device_exist == false)
    {
        DEBUG_STREAM << "Trying to create device entry in database" << endl;

        std::vector<Tango::DevLong>
                    tg_group_usr_elt_ids, tg_group_phy_elt_ids, tg_group_ct_elt_ids,
                    tg_group_0D_elt_ids, tg_group_1D_elt_ids, tg_group_2D_elt_ids,
                    tg_group_pseudo_elt_ids, tg_group_motor_elt_ids;
        
        PoolTango::toTango(group_usr_elt_ids, tg_group_usr_elt_ids);
        PoolTango::toTango(group_phy_elt_ids, tg_group_phy_elt_ids);
        PoolTango::toTango(group_ct_elt_ids, tg_group_ct_elt_ids);
        PoolTango::toTango(group_0D_elt_ids, tg_group_0D_elt_ids);
        PoolTango::toTango(group_1D_elt_ids, tg_group_1D_elt_ids);
        PoolTango::toTango(group_2D_elt_ids, tg_group_2D_elt_ids);
        PoolTango::toTango(group_pseudo_elt_ids, tg_group_pseudo_elt_ids);
        PoolTango::toTango(group_motor_elt_ids, tg_group_motor_elt_ids);
        
        try
        {
            Tango::DbDevInfo my_device_info;
            my_device_info.name = tg_dev_name.c_str();
            my_device_info._class = "MeasurementGroup";
            my_device_info.server = tg->get_ds_name().c_str();

            db->add_device(my_device_info);
            db->put_device_alias(tg_dev_name,group_name);

            Tango::DbDatum id(ID_PROP);
            Tango::DbDatum elt_ct_list(MMNT_GRP_CT_LIST);
            Tango::DbDatum elt_0D_list(MMNT_GRP_0D_LIST);
            Tango::DbDatum elt_1D_list(MMNT_GRP_1D_LIST);
            Tango::DbDatum elt_2D_list(MMNT_GRP_2D_LIST);
            Tango::DbDatum elt_pc_list(MMNT_GRP_PC_LIST);
            Tango::DbDatum elt_mt_list(MMNT_GRP_MT_LIST);
            Tango::DbDatum user_group_elt(USER_GROUP_ELT);
            Tango::DbDatum phys_group_elt(PHYS_GROUP_ELT);
            Tango::DbData db_data;

            ElementId measurement_group_id = get_new_id();
            id << (Tango::DevLong)measurement_group_id;
            db_data.push_back(id);

            elt_ct_list << tg_group_ct_elt_ids;
            db_data.push_back(elt_ct_list);

            elt_0D_list << tg_group_0D_elt_ids;
            db_data.push_back(elt_0D_list);

            elt_1D_list << tg_group_1D_elt_ids;
            db_data.push_back(elt_1D_list);

            elt_2D_list << tg_group_2D_elt_ids;
            db_data.push_back(elt_2D_list);

            elt_pc_list << tg_group_pseudo_elt_ids;
            db_data.push_back(elt_pc_list);

            elt_mt_list << tg_group_motor_elt_ids;
            db_data.push_back(elt_mt_list);

            user_group_elt << tg_group_usr_elt_ids;
            db_data.push_back(user_group_elt);

            phys_group_elt << tg_group_phy_elt_ids;
            db_data.push_back(phys_group_elt);

            db->put_device_property(tg_dev_name.c_str(),db_data);

//
// Put default values for memorized attributes
//
            db_data.clear();
            Tango::DbDatum it("Integration_time"),it_value("__value");
            Tango::DbDatum ic("Integration_count"),ic_value("__value");
            Tango::DbDatum timer("Timer"),timer_value("__value");
            Tango::DbDatum monitor("Monitor"),monitor_value("__value");

            it << 1L;
            it_value << 0.0;
            db_data.push_back(it);
            db_data.push_back(it_value);

            ic << 1L;
            ic_value << 0L;
            db_data.push_back(ic);
            db_data.push_back(ic_value);

            timer << 1L;
            timer_value << "Not Initialized";
            db_data.push_back(timer);
            db_data.push_back(timer_value);

            monitor << 1L;
            monitor_value << "Not Initialized";
            db_data.push_back(monitor);
            db_data.push_back(monitor_value);

//
// Register abs_change for change events on CT, 0D and pseudo attributes
//
            for(unsigned long idx = 0 ; idx < group_ct_elt_ids.size(); idx++)
            {
                std::string attr_name = get_element(group_ct_elt_ids[idx])->get_name();
                attr_name += "_value";
                Tango::DbDatum value(attr_name),abs_ch("abs_change");
                value << 1L;
                abs_ch << defaultCtGrpVal_AbsChange;
                db_data.push_back(value);
                db_data.push_back(abs_ch);
            }
            for(unsigned long idx = 0 ; idx < group_0D_elt_ids.size(); idx++)
            {
                std::string attr_name = get_element(group_0D_elt_ids[idx])->get_name();
                attr_name += "_value";
                Tango::DbDatum value(attr_name),abs_ch("abs_change");
                value << 1L;
                abs_ch << defaultZeroDGrpVal_AbsChange;
                db_data.push_back(value);
                db_data.push_back(abs_ch);
            }
            for(unsigned long idx = 0 ; idx < group_1D_elt_ids.size(); idx++)
            {
                std::string attr_name = get_element(group_1D_elt_ids[idx])->get_name();
                attr_name += "_value";
                Tango::DbDatum value(attr_name),abs_ch("abs_change");
                value << 1L;
                abs_ch << defaultOneDGrpVal_AbsChange;
                db_data.push_back(value);
                db_data.push_back(abs_ch);
            }
            for(unsigned long idx = 0 ; idx < group_pseudo_elt_ids.size(); idx++)
            {
                std::string attr_name = get_element(group_pseudo_elt_ids[idx])->get_name();
                attr_name += "_value";
                Tango::DbDatum value(attr_name),abs_ch("abs_change");
                value << 1L;
                abs_ch << defaultCtGrpVal_AbsChange;
                db_data.push_back(value);
                db_data.push_back(abs_ch);
            }
            for(unsigned long idx = 0 ; idx < group_motor_elt_ids.size(); idx++)
            {
                std::string attr_name = get_element(group_motor_elt_ids[idx])->get_name();
                attr_name += "_value";
                Tango::DbDatum value(attr_name),abs_ch("abs_change");
                value << 1L;
                abs_ch << defaultMotPos_AbsChange;
                db_data.push_back(value);
                db_data.push_back(abs_ch);
            }            
            db->put_device_attribute_property(tg_dev_name.c_str(),db_data);

            DEBUG_STREAM << "Device created in database (with alias)" << endl;
        }
        catch (Tango::DevFailed &e)
        {
            DEBUG_STREAM << "Gasp an exception........" << endl;
            TangoSys_OMemStream o;
            o << "Can't create measurement group " << group_name << " in database" << ends;

            Tango::Except::re_throw_exception(e,
                    (const char *)"Pool_CantCreateMeasurementGroup", o.str(),
                    (const char *)"Pool::create_measurement_group");
        }

//
// Find the Tango MeasurementGroup class and create the measurement group
//

        const vector<Tango::DeviceClass *> *cl_list = tg->get_class_list();
        for (vector<Tango::DeviceClass *>::size_type i = 0; 
             i < cl_list->size(); i++)
        {
            if ((*cl_list)[i]->get_name() == "MeasurementGroup")
            {
                try
                {
                    Tango::DevVarStringArray na;
                    na.length(1);
                    na[0] = tg_dev_name.c_str();
                    (*cl_list)[i]->device_factory(&na);
                    break;
                }
                catch (Tango::DevFailed &e)
                {
                    DEBUG_STREAM << "Exception while trying to create MeasurementGroup device" << endl;

//
// The delete_device will also delete device property(ies)
//

                    db->delete_device(tg_dev_name);

                    TangoSys_OMemStream o;
                    o << "Can't create measurement group device " << group_name << ends;

                    Tango::Except::re_throw_exception(e,(const char *)"Pool_CantCreateMeasurementGroup",o.str(),
                              (const char *)"Pool::create_measurement_group");
                }
            }
        }

//
// Create a Tango device proxy on the newly created measurement group
// and set its connection to automatic re-connection
//
        MeasurementGroupPool &mgp = get_measurement_group(group_name);
        Tango::DeviceProxy *tmp_dev = new Tango::DeviceProxy(mgp.get_full_name().c_str());
        tmp_dev->set_transparency_reconnection(true);
        
        MeasurementGroup_ns::MeasurementGroup *dev = static_cast<MeasurementGroup_ns::MeasurementGroup*>
            (tg->get_device_by_name(mgp.get_full_name()));

        set_tango_element(mgp.get_id(), tmp_dev, dev);
    }

    MeasurementGroupPool &mgp = get_measurement_group(get_last_assigned_id());

//
// By default, if possible set the first Counter/timer given by the user to be the timer channel
//
    if(!group_ct_elt_ids.empty())
    {
        std::string timer = get_element(group_ct_elt_ids[0])->get_name();
        Tango::DeviceAttribute attr("Timer", timer);
        get_element_proxy(mgp)->write_attribute(attr);
    }

//
// subscribe to the internal events coming from each channel of the measurement group
//
    ElemIdVectorIt ite = mgp.group_elts.begin();
    for(; ite != mgp.group_elts.end(); ite++)
    {
        get_element(*ite)->add_pool_elem_listener(&mgp);
    }

//
// Push a change event for clients listenning on events
//
    Tango::Attribute &mgl = dev_attr->get_attr_by_name("MeasurementGroupList");
    read_MeasurementGroupList(mgl);
    mgl.fire_change_event();
}

//+------------------------------------------------------------------
/**
 *	method:	Pool::delete_measurement_group
 *
 *	description:	method to execute "DeleteMeasurementGroup"
 *	This command deletes a measurement group from its name
 *
 * @param	argin	The motor group name
 *
 */
//+------------------------------------------------------------------
void Pool::delete_measurement_group(Tango::DevString argin)
{
    DEBUG_STREAM << "Pool::delete_measurement_group(): entering... !" << endl;

    //	Add your own code to control device here

//
// Find measurement group in measurement group list
//

    string user_name(argin);

    MeasurementGroupPool &mg_to_del = get_measurement_group(user_name);

    Tango::DevState mg_state = get_element_proxy(mg_to_del)->state();
//
// Check that the group is not moving
//

    if(mg_state == Tango::MOVING)
    {
        TangoSys_OMemStream o;
        o << "Can't delete measurement group with name " << argin;
        o << ". It is actually taking data." << ends;

        Tango::Except::throw_exception(
                    (const char *)"Pool_CantDeleteMeasurementGroup", o.str(),
                    (const char *)"Pool::delete_measurement_group");
    }

//
// Unsubscribe to the internal events for each element of the motor group
//

    ElemIdVectorIt it = mg_to_del.group_elts.begin();
    for(; it != mg_to_del.group_elts.end();++it)
    {
        get_element(*it)->remove_pool_elem_listener(&mg_to_del);
    }

//
// Remove its entry in database. This will also delete any device
// properties and device attribute properties
//

    Tango::Util *tg = Tango::Util::instance();
    try
    {
        tg->get_database()->delete_device(mg_to_del.get_full_name());

//
// Delete measurement group device from server but first find its 
// Tango xxxClass instance
//
        MeasurementGroup_ns::MeasurementGroup *mg_dev = 
            get_measurement_group_device(mg_to_del);
        Tango::DeviceClass *dc = mg_dev->get_device_class();
        dc->device_destroyer(mg_to_del.get_full_name());
    }
    catch (Tango::DevFailed &e)
    {
        TangoSys_OMemStream o;
        o << "Can't delete measurement group with name " << argin << ends;

        Tango::Except::re_throw_exception(e,
                    (const char *)"Pool_CantDeleteMeasurementGroup", o.str(),
                    (const char *)"Pool::delete_measurement_group");
    }

//
// Push a change event for clients listenning on events
//

    Tango::Attribute &mgl = dev_attr->get_attr_by_name("MeasurementGroupList");
    read_MeasurementGroupList(mgl);
    mgl.fire_change_event();

}

//+------------------------------------------------------------------
/**
 *	method:	Pool::create_com_channel
 *
 *	description:	method to execute "CreateComChannel"
 *	This command creates a new communication channel in the pool. It has three arguments which are
 *	1 - The controller name (its instance name)
 *	2 - The communication channel number within the controller
 *	3 - The communication channel name. The communication channel name is a Tango alias and does not have any '/' characters.
 *	This command creates a Tango device with a Tango name set to
 *	"comchan/controller_instance_name/ctrl_number"
 *	and with an alias as given by the user in the command parameter.
 *	All the created communication channels are automatically re-created at pool device startup time.
 *
 * @param	argin	long[0] = Communication Channel number in Ctrl, string[0] = communication Channel name, string[1] = Controller instance name
 *
 */
//+------------------------------------------------------------------
void Pool::create_com_channel(const Tango::DevVarLongStringArray *argin)
{
    DEBUG_STREAM << "Pool::create_com_channel(): entering... !" << endl;

    //	Add your own code to control device here

    int32_t l_len = argin->lvalue.length();
    int32_t str_len = argin->svalue.length();
    
    if ((l_len != 1) || (str_len < 2))
    {
        Tango::Except::throw_exception(
            (const char *)"Pool_WrongArgumentNumber",
            (const char *)"Wrong number of argument for command CreateComChannel. Needs 1 long and at least 2 strings",
            (const char *)"Pool::create_com_channel");
    }

    Tango::DevLong channel_idx = argin->lvalue[0];
    string ctrl_inst_name(argin->svalue[1]);
    string channel_name(argin->svalue[0]);
    ControllerPool &com_ch_ctrl = get_controller(ctrl_inst_name, true);
    int32_t ctrl_id = com_ch_ctrl.id;

    DEBUG_STREAM << "Controller ID = " << ctrl_id << endl;
    DEBUG_STREAM << "Communication channel index = " << channel_idx << endl;
    DEBUG_STREAM << "Communication channel name = " << channel_name << endl;

//
// Check if the controller has been successfully constructed
//

    if (!com_ch_ctrl.get_controller())
    {
        Tango::Except::throw_exception((const char *)"Pool_WrongControllerId",
            (const char *)"Can't create a communication channel on a non-responding controller",
            (const char *)"Pool::create_com_channel");
    }

//
// Check if we don't have already  enough motor
//

    DEBUG_STREAM << "Checking communication channel number" << endl;

    if (get_communication_channel_nb() == MAX_COM_CHANNEL)
    {
        Tango::Except::throw_exception(
            (const char *)"Pool_TooManyCommunicationChannel",
            (const char *)"Too many Communication Channel in your pool",
            (const char *)"Pool::create_com_channel");
    }

//
// Check that the controller still have some communication channels available
//

    if (com_ch_ctrl.nb_dev == com_ch_ctrl.MaxDevice)
    {
        TangoSys_OMemStream o;
        o << "Max number of communication channel reached (" 
          << com_ch_ctrl.MaxDevice << ")" << ends;

        Tango::Except::throw_exception(
            (const char *)"Pool_MaxNbComChannelInCtrl", o.str(),
            (const char *)"Pool::create_com_channel()");
    }

//
// Build Tango device name
//
    string tg_dev_name = "";
    if (str_len >= 3)
    {
        tg_dev_name = argin->svalue[2];
    }
    else
    {
        stringstream s;
        s << channel_idx;

        tg_dev_name = "comchan/" + com_ch_ctrl.name + '/' + s.str();
    }

    DEBUG_STREAM << "Tango device name = " << tg_dev_name << endl;

//
// Check if this device is already defined in database
// Check by device alias and by Tango device name
//

    Tango::Util *tg = Tango::Util::instance();
    Tango::Database *db = tg->get_database();

    Tango::DbDevImportInfo my_device_import;
    bool device_exist = false;
    bool by_alias = false;

    try
    {
        my_device_import = db->import_device(channel_name);
        device_exist = true;
        by_alias = true;
    }
    catch (Tango::DevFailed &e)
    {
        if (::strcmp(e.errors[0].reason.in(),"DB_DeviceNotDefined") != 0)
        {
            device_exist = true;
        }
    }

    if (device_exist == false)
    {
        try
        {
            my_device_import = db->import_device(tg_dev_name);
            device_exist = true;
        }
        catch (Tango::DevFailed &e)
        {
            if (::strcmp(e.errors[0].reason.in(),"DB_DeviceNotDefined") != 0)
            {
                device_exist = true;
            }
        }
    }

    if (device_exist == true)
    {
        TangoSys_OMemStream o;
        o << "Communication channel ";
        if (by_alias == false)
            o << "device name " << tg_dev_name;
        else
            o << "name " << channel_name;
        o << " is already defined" << ends;
        
        Tango::Except::throw_exception("Pool_WrongComChannelName", o.str(),
                                       "Pool::create_com_channel");
    }

//
// If the device is not defined in database, create it in database, set its alias,
// define the property used to store its ID (called channel_id)
//

    if (device_exist == false)
    {
        DEBUG_STREAM << "Trying to create device entry in database" << endl;

        try
        {
            Tango::DbDevInfo my_device_info;
            my_device_info.name = tg_dev_name.c_str();
            my_device_info._class = "CommunicationChannel";
            my_device_info.server = tg->get_ds_name().c_str();

            db->add_device(my_device_info);

            db->put_device_alias(tg_dev_name,channel_name);

            Tango::DbDatum db_id(ID_PROP);
            Tango::DbData db_data;
            ElementId com_channel_id = get_new_id();
            db_id << (Tango::DevLong)com_channel_id;
            
            Tango::DbDatum db_ctrl_id(CTRL_ID_PROP);
            db_ctrl_id << (Tango::DevLong)ctrl_id;

            Tango::DbDatum db_axis(AXIS_PROP);
            db_axis << channel_idx;
            
            db_data.push_back(db_id);
            db_data.push_back(db_ctrl_id);
            db_data.push_back(db_axis);
            
            db->put_device_property(tg_dev_name.c_str(),db_data);

            DEBUG_STREAM << "Device created in database (with alias)" << endl;
        }
        catch (Tango::DevFailed &e)
        {
            DEBUG_STREAM << "Gasp an exception........" << endl;
            TangoSys_OMemStream o;
            o << "Can't create communication channel " << channel_name << " in database" << ends;

            Tango::Except::re_throw_exception(e,(const char *)"Pool_CantCreateComChannel",o.str(),
                              (const char *)"Pool::create_com_channel");
        }

//
// Find the Tango CommunicationChannel class and create the communication channel
//

        const vector<Tango::DeviceClass *> *cl_list = tg->get_class_list();
        for (unsigned long i = 0;i < cl_list->size();i++)
        {
            if ((*cl_list)[i]->get_name() == "CommunicationChannel")
            {
                try
                {
                    DEBUG_STREAM << "Found DeviceClass CommunicationChannel. Will create the device" << endl;
                    Tango::DevVarStringArray na;
                    na.length(1);
                    na[0] = tg_dev_name.c_str();
                    (*cl_list)[i]->device_factory(&na);
                    break;
                }
                catch (Tango::DevFailed &e)
                {
                    DEBUG_STREAM << "Exception while trying to create CommunicationChannel device" << endl;

//
// Check if this communication channel has already been added into pool structures
// If yes, remove it from pool structures
//

                    try
                    {
                        DevicePool::remove_element(channel_name);
                    }
                    catch (...) {}

//
// The delete_device will also delete device property(ies)
//

                    db->delete_device(tg_dev_name);

                    TangoSys_OMemStream o;
                    o << "Can't create communication channel device " 
                      << channel_name << ends;

                    Tango::Except::re_throw_exception(e,
                            (const char *)"Pool_CantCreateComChannel", o.str(),
                            (const char *)"Pool::create_com_channel");
                }
            }
        }

//
// Create a Tango device proxy on the newly created communication channel
// and set its connection to automatic re-connection
//
        CommunicationChannelPool &ccp = get_communication_channel(channel_name);
        Tango::DeviceProxy *tmp_dev = new Tango::DeviceProxy(ccp.get_full_name().c_str());
        tmp_dev->set_transparency_reconnection(true);
        
        CommunicationChannel_ns::CommunicationChannel *dev = 
            static_cast<CommunicationChannel_ns::CommunicationChannel*>
            (tg->get_device_by_name(ccp.get_full_name()));
        
        set_tango_element(ccp.get_id(), tmp_dev, dev);
    }

//
// Inform ghost group that there is a new communication channel
//
    //TODO: Inform ghost group that there is a new communication channel
    /*
    MotorGroup_ns::MotorGroup *ghost_ptr = get_ghost_motor_group_ptr();
    {
        Tango::AutoTangoMonitor atm(ghost_ptr);
        ghost_ptr->add_motor_to_group(mot_list.back().id);
    }
    */

//
// Push a change event for client listening on event
//

    Tango::Attribute &ccl = dev_attr->get_attr_by_name("ComChannelList");
    read_ComChannelList(ccl);
    ccl.fire_change_event();
}

//+------------------------------------------------------------------
/**
 *	method:	Pool::delete_com_channel
 *
 *	description:	method to execute "DeleteComChannel"
 *	Delete a communication channel from its name
 *	Once an communication channel is deleted, it is not available any more. All its information have been
 *	removed from the database
 *
 * @param	argin	Communication Channel name
 *
 */
//+------------------------------------------------------------------
void Pool::delete_com_channel(Tango::DevString argin)
{
    DEBUG_STREAM << "Pool::delete_com_channel(): entering... !" << endl;

    //	Add your own code to control device here

//
// Find communication channel in exp channel list
//

    string user_name(argin);
    CommunicationChannelPool &channel_to_del =  get_communication_channel(user_name);

    DEBUG_STREAM << "Communication Channel found" << endl;

//
// Check that the com channel is not actually used
//
    if (get_element_proxy(channel_to_del)->state() == Tango::MOVING)
    {
        TangoSys_OMemStream o;
        o << "Can't delete communication channel with name " << argin;
        o << ". It is actually used (reading/writing)." << ends;

        Tango::Except::throw_exception((const char *)"Pool_CantDeleteComChannel",o.str(),
                                 (const char *)"Pool::delete_com_channel");
    }

//
// Remove its entry in database. This will also delete any device
// properties and device attribute properties
//

    Tango::Util *tg = Tango::Util::instance();
    try
    {
        tg->get_database()->delete_device(channel_to_del.get_full_name());

//
// Delete communication channel device from server but first find its Tango xxxClass instance
//
        CommunicationChannel_ns::CommunicationChannel *comch_dev = 
            get_communication_channel_device(channel_to_del);
        Tango::DeviceClass *dc = comch_dev->get_device_class();

        dc->device_destroyer(channel_to_del.get_full_name());
    }
    catch (Tango::DevFailed &e)
    {
        TangoSys_OMemStream o;
        o << "Can't delete communication channel with name " << argin << ends;

        Tango::Except::re_throw_exception(e,(const char *)"Pool_CantDeleteComChannel",o.str(),
                                 (const char *)"Pool::delete_com_channel");
    }

//
// Before returning, send a change event for client listenning
// on event
//

    Tango::Attribute &ccl = dev_attr->get_attr_by_name("ComChannelList");
    read_ComChannelList(ccl);
    ccl.fire_change_event();
}

//+------------------------------------------------------------------
/**
 *	method:	Pool::delete_pseudo_counter
 *
 *	description:	method to execute "DeletePseudoCounter"
 *	This command deletes a pseudo counter
 *
 * @param	argin	Pseudo Motor name
 *
 */
//+------------------------------------------------------------------
void Pool::delete_pseudo_counter(Tango::DevString argin)
{
    DEBUG_STREAM << "Pool::delete_pseudo_counter(): entering... !" << endl;

    //	Add your own code to control device here
//
// Find pseudo counter in pseudo counter list
//
    string user_name(argin);
    PseudoCounterPool &pc_to_del =  get_pseudo_counter(user_name);

    DEBUG_STREAM << "Pseudo Counter found" << endl;

//
// Check that the pseudo counter is not member of a measurement group
//
    for (PoolElementTypeIt elem_it = element_types.lower_bound(MEASUREMENT_GROUP_ELEM);
         elem_it != element_types.upper_bound(MEASUREMENT_GROUP_ELEM); ++elem_it)
    {
        MeasurementGroupPool &mntgrp_pool = get_measurement_group(elem_it->second);
        try
        {
            MeasurementGroup_ns::MeasurementGroup *mg_dev = 
                get_measurement_group_device(mntgrp_pool);
            mg_dev->get_pc_from_id(pc_to_del.id);
        }
        catch (Tango::DevFailed &e)
        {
            continue;
        }

        TangoSys_OMemStream o;
        o << "Can't delete pseudo counter with name " << argin;
        o << ". It is actually member of measurement group " << mntgrp_pool.name << ends;

        Tango::Except::throw_exception(
                (const char *)"Pool_CantDeletePseudoCounter",o.str(),
                (const char *)"Pool::delete_pseudo_counter");
    }

    Tango::Util *util = Tango::Util::instance();
    Tango::Database *db = util->get_database();

//
// Remove its entry in database. This will also delete any device
// properties and device attribute properties
//
    try
    {
        db->delete_device(pc_to_del.get_full_name());

//
// Delete pseudo motor device from server but first find its Tango xxxClass instance
//
        PseudoCounter_ns::PseudoCounter *pc_dev = get_pseudo_counter_device(pc_to_del);
        Tango::DeviceClass *dc = pc_dev->get_device_class();
        dc->device_destroyer(pc_to_del.get_full_name());
    }
    catch (Tango::DevFailed &e)
    {
        TangoSys_OMemStream o;
        o << "Can't delete pseudo counter '" << argin << "'" << ends;

        Tango::Except::re_throw_exception(e,
                (const char *)"Pool_CantDeletePseudoCounter",o.str(),
                (const char *)"Pool::delete_pseudo_counter");
    }

//
// Push a change event for clients listenning on events
//

    Tango::Attribute &pcl = dev_attr->get_attr_by_name("PseudoCounterList");
    read_PseudoCounterList(pcl);
    pcl.fire_change_event();
}

//+------------------------------------------------------------------
/**
 *	method:	Pool::get_file
 *
 *	description:	method to execute "GetFile"
 *	Returns the contents of the given file as a stream of bytes
 *
 * @param	argin	complete(with absolute path) file name
 * @return	File data
 *
 */
//+------------------------------------------------------------------
Tango::DevVarCharArray* Pool::get_file(Tango::DevString argin)
{
    //	POGO has generated a method core with argout allocation.
    //	If you would like to use a static reference without copying,
    //	See "TANGO Device Server Programmer's Manual"
    //		(chapter : Writing a TANGO DS / Exchanging data)
    //------------------------------------------------------------
    DEBUG_STREAM << "Pool::get_file(): entering... !" << endl;

    //	Add your own code to control device here
    string f_name(argin);

    // Relative path
    if(f_name.find('/') == string::npos)
    {
        string f_path;
        if(find_file_in_pool_path(f_name,f_path) == false)
        {
            TangoSys_OMemStream o;
            o << "The " << f_name << " file could not be found. Please check ";
            o << "that PoolPath property contains the correct path." << ends;

            Tango::Except::throw_exception(
                (const char *)"Pool_CantLocateFile", o.str(),
                (const char *)"Pool::get_file");
        }
        f_name = f_path;
    }
    else
    {
        if(f_name[0] != '/')
        {
            Tango::Except::throw_exception(
                (const char *)"Pool_CantLocateFile",
                (const char *)"The given path must be absolute",
                (const char *)"Pool::get_file");
        }
        string usr_f_path = f_name.substr(0,f_name.rfind('/'));
        string usr_f_name = f_name.substr(f_name.rfind('/')+1);

        vector<string> &pp = get_pool_path();

        if( find(pp.begin(),pp.end(),usr_f_path) == pp.end())
        {
            TangoSys_OMemStream o;
            o << "The '" << usr_f_path << "' path is not part of the PoolPath " << ends;

            Tango::Except::throw_exception(
                (const char *)"Pool_CantLocateFile", o.str(),
                (const char *)"Pool::get_file");
        }

        vector<string> files;
        get_files_with_extension(usr_f_path,".*",files);

        bool file_found = false;
        for(vector<string>::iterator ite = files.begin(); ite != files.end(); ite++)
        {
            string curr_file = (*ite).substr((*ite).rfind("/")+1);
            if(curr_file == usr_f_name)
            {
                file_found = true;
                break;
            }
        }

        if( file_found == false )
        {
            TangoSys_OMemStream o;
            o << "The '" << usr_f_name << "' file could not be found in '";
            o << usr_f_path << "'" << ends;

            Tango::Except::throw_exception(
                (const char *)"Pool_CantLocateFile", o.str(),
                (const char *)"Pool::get_file");
        }
    }

    ifstream infile(f_name.c_str(), ios::in | ios::binary);

    // Checks that the file is ok for reading
    if(infile.fail())
    {
        infile.close();
        TangoSys_OMemStream o;
        o << "Error trying to read '" << f_name << "'" << ends;

        Tango::Except::throw_exception(
            (const char *)"Pool_CantReadFile", o.str(),
            (const char *)"Pool::get_file");
    }

    // Determine the size of the file
    infile.seekg (0, ios::end);
    unsigned long file_size = infile.tellg();
    infile.seekg (0, ios::beg);

    Tango::DevVarCharArray *ret = new Tango::DevVarCharArray();
    ret->length(file_size);

    // Read the data into the buffer
    if(file_size > 0)
    {
        char *dest = (char*)(&(*ret)[0]);
        infile.read(dest,file_size);
    }
    infile.close();
    return ret;
}

//+------------------------------------------------------------------
/**
 *	method:	Pool::put_file
 *
 *	description:	method to execute "PutFile"
 *	Adds/updates a new file into the Pool.
 *	Files can only be placed in directories which are in the PoolPath property.
 *
 * @param	argin	complete filename (inc. absolute path)+'\0'+\nusername+'\0'+\ndescription of the change+'\0'+\nfile data
 *
 */
//+------------------------------------------------------------------
void Pool::put_file(const Tango::DevVarCharArray *argin)
{
    DEBUG_STREAM << "Pool::put_file(): entering... !" << endl;

    //	Add your own code to control device here
    unsigned long idx = 0;
    unsigned long len = argin->length();

//
// Determine Filename
//
    string f_name;
    while(idx < len && (*argin)[idx] != '\0')
        f_name += (*argin)[idx++];

    TangoSys_OMemStream gen_desc;
    gen_desc << "Invalid format: Argument must contain:\n";
    gen_desc << " - complete filename (inc. absolute path) + '\0' +\n";
    gen_desc << " - username + '\0' +\n";
    gen_desc << " - description of the change + '\0' +\n";
    gen_desc << " - file data";

    DEBUG_STREAM << "Filename is " << f_name << endl;

    if(idx == len)
    {
        Tango::Except::throw_exception(
            (const char *)"Pool_CantDetermineFilename", gen_desc.str(),
            (const char *)"Pool::put_file");
    }

    // Make sure it is an absolute path
    if(f_name.size() == 0 || f_name[0] != '/')
    {
        Tango::Except::throw_exception(
            (const char *)"Pool_CantDetermineFilename",
            (const char *)"The filename must contain an absolute path",
            (const char *)"Pool::put_file");
    }

    string usr_f_path = f_name.substr(0,f_name.rfind('/'));
    string usr_f_name = f_name.substr(f_name.rfind('/')+1);

    // Don't check against PoolPath.
    // It should be possible to add files first to a new directory and only
    // after add this new directory to the PoolPath.
    /*
    vector<string> &pp = get_pool_path();
    if( find(pp.begin(),pp.end(),usr_f_path) == pp.end() )
    {
        TangoSys_OMemStream o;
        o << "The '" << usr_f_path << "' path is not part of the PoolPath.\n"
             "New files can only be inserted in directories inside the "
             "PoolPath" << ends;

        Tango::Except::throw_exception(
            (const char *)"Pool_CantDetermineFilename", o.str(),
            (const char *)"Pool::put_file");
    }
    */


    // No need to check if the file already exists
    /*
    vector<string> files;
    get_files_with_extension(usr_f_path,".*",files);

    bool file_found = false;
    for(vector<string>::iterator ite = files.begin(); ite != files.end(); ite++)
    {
        string curr_file = (*ite).substr((*ite).rfind("/")+1);
        if(curr_file == usr_f_name)
        {
            file_found = true;
            break;
        }
    }
    */

//
// Determine username
//

    // skip the NULL character
    idx++;

    string user_name;
    while(idx < len && (*argin)[idx] != '\0')
        user_name += (*argin)[idx++];

    if(idx == len)
    {
        Tango::Except::throw_exception(
            (const char *)"Pool_CantDetermineUsername", gen_desc.str(),
            (const char *)"Pool::put_file");
    }

//
// Determine commit description
//

    // skip the NULL character
    idx++;

    string descr;
    while(idx < len && (*argin)[idx] != '\0')
        descr += (*argin)[idx++];

    if(idx == len)
    {
        Tango::Except::throw_exception(
            (const char *)"Pool_CantDetermineDescription", gen_desc.str(),
            (const char *)"Pool::put_file");
    }


//
// Determine file data
//

    // skip the NULL character
    idx++;
    stringstream strm_data;

//
// Determine if the file should contain the metadata. For now this is only
// enabled for files with extension: .py, .h and .cpp and Makefile
//
    string f_ext = usr_f_name.substr(usr_f_name.rfind('.'));
    if(f_ext == ".py" || f_ext == ".h" || f_ext == ".cpp" || usr_f_name == "Makefile")
    {
        DEBUG_STREAM << "File is writable." << endl;

        bool has_meta = false;
        string meta;

        string cmt = "// ";

        if(usr_f_name == "Makefile")
            cmt = "# ";
        else if(f_ext == ".py")
        {
            cmt = "# ";
            // Avoid writing before the '#!' line if it exists
            if(idx+2<len)
            {
                unsigned char c1 = (*argin)[idx], c2 = (*argin)[idx+1];
                if(c1 == '#' && c2 == '!')
                {
                    has_meta = true;
                    while(idx < len && (*argin)[idx] != '\n')
                        meta += (*argin)[idx++];

                    // Skip the new line
                    idx++;
                }
            }
        }

        time_t rawtime;
        struct tm * timeinfo;
        char buffer [80];

        time ( &rawtime );
        timeinfo = localtime ( &rawtime );
        strftime (buffer,80,"%c",timeinfo);
        if (has_meta)
            strm_data << meta << endl;
        strm_data << cmt << buffer << " by " << user_name << endl;
        strm_data << cmt << descr << endl;
    }


    while(idx < len)
    {
        strm_data << (*argin)[idx++];
    }

    ofstream outfile(f_name.c_str(), ios::out | ios::binary);

    // Checks that the file is ok for reading
    if(outfile.fail())
    {
        outfile.close();
        TangoSys_OMemStream o;
        o << "Error trying to create '" << f_name << "'" << ends;

        Tango::Except::throw_exception(
            (const char *)"Pool_CantCreateFile", o.str(),
            (const char *)"Pool::put_file");
    }

    outfile << strm_data.str();
    outfile.close();
}

//+------------------------------------------------------------------
/**
 *	method:	Pool::create_ioregister
 *
 *	description:	method to execute "CreateIORegister"
 *	This command creates a new ioregister in the pool. It has three arguments which are
 *	1 - The controller name (its instance name)
 *	2 - The ioregister number within the controller
 *	3 - The ioregister name. The ioregister name is a Tango alias and does not have any '/' characters.
 *	This command creates a Tango device with a Tango name set to
 *	"ioregister/controller_instance_name/ctrl_number"
 *	and with an alias as given by the user in the command parameter.
 *	All the created ioregisters are automatically re-created at pool device startup time.
 *
 * @param	argin	long[0] = IORegister number in Ctrl, string[0] = IORegister name, string[1] = Controller instance name
 *
 */
//+------------------------------------------------------------------
void Pool::create_ioregister(const Tango::DevVarLongStringArray *argin)
{
    DEBUG_STREAM << "Pool::create_ioregister(): entering... !" << endl;

    //	Add your own code to control device here

    int32_t l_len = argin->lvalue.length();
    int32_t str_len = argin->svalue.length();
    
    if ((l_len != 1) || (str_len < 2))
    {
        Tango::Except::throw_exception(
            (const char *)"Pool_WrongArgumentNumber",
            (const char *)"Wrong number of argument for command CreateIORegister. Needs 1 long and at least 2 strings",
            (const char *)"Pool::create_ioregister");
    }


    Tango::DevLong channel_idx = argin->lvalue[0];
    string ctrl_inst_name(argin->svalue[1]);
    string channel_name(argin->svalue[0]);


    ControllerPool &ioregister_ctrl = get_controller(ctrl_inst_name, true);
    int32_t ctrl_id = ioregister_ctrl.id;

    DEBUG_STREAM << "Controller ID = " << ctrl_id << endl;
    DEBUG_STREAM << "IORegister index = " << channel_idx << endl;
    DEBUG_STREAM << "IORegister name = " << channel_name << endl;


//
// Check if the controller has been successfully constructed
//

    if (!ioregister_ctrl.get_controller())
    {
        Tango::Except::throw_exception((const char *)"Pool_WrongControllerId",
            (const char *)"Can't create a ioregister on a non-responding controller",
            (const char *)"Pool::create_ioregister");
    }

//
// Check if we don't have already  enough ioregister
//
    DEBUG_STREAM << "Checking ioregister number" << endl;

    if (get_ioregister_nb() == MAX_IOREGISTER)
    {
        Tango::Except::throw_exception((const char *)"Pool_TooManyIORegister",
                           (const char *)"Too many IORegisters in your pool",
                           (const char *)"Pool::create_ioregister");
    }

//
// Check that the controller still have some ioregisters available
//
    if (ioregister_ctrl.nb_dev == ioregister_ctrl.MaxDevice)
    {
        TangoSys_OMemStream o;
        o << "Max number of ioregisters reached (" 
          << ioregister_ctrl.MaxDevice << ")" << ends;

        Tango::Except::throw_exception(
            (const char *)"Pool_MaxNbIORegisterInCtrl", o.str(),
            (const char *)"Pool::create_ioregister()");
    }

//
// Build Tango device name
//
    string tg_dev_name = "";
    if (str_len >= 3)
    {
        tg_dev_name = argin->svalue[2];
    }
    else
    {
        stringstream s;
        s << channel_idx;

        tg_dev_name = "ioregister/" + ioregister_ctrl.name + '/' + s.str();
    }

    DEBUG_STREAM << "Tango device name = " << tg_dev_name << endl;

//
// Check if this device is already defined in database
// Check by device alias and by Tango device name
//
    Tango::Util *tg = Tango::Util::instance();
    Tango::Database *db = tg->get_database();

    Tango::DbDevImportInfo my_device_import;
    bool device_exist = false;
    bool by_alias = false;

    try
    {
        my_device_import = db->import_device(channel_name);
        device_exist = true;
        by_alias = true;
    }
    catch (Tango::DevFailed &e)
    {
        if (::strcmp(e.errors[0].reason.in(),"DB_DeviceNotDefined") != 0)
        {
            device_exist = true;
        }
    }

    if (device_exist == false)
    {
        try
        {
            my_device_import = db->import_device(tg_dev_name);
            device_exist = true;
        }
        catch (Tango::DevFailed &e)
        {
            if (::strcmp(e.errors[0].reason.in(),"DB_DeviceNotDefined") != 0)
            {
                device_exist = true;
            }
        }
    }

    if (device_exist == true)
    {
        TangoSys_OMemStream o;
        o << "IORegister ";
        if (by_alias == false)
            o << "device name " << tg_dev_name;
        else
            o << "name " << channel_name;
        o << " is already defined" << ends;
        
        Tango::Except::throw_exception("Pool_WrongIORegisterName", o.str(),
                                       "Pool::create_ioregister");
    }


//
// If the device is not defined in database, create it in database, set its alias,
// define the property used to store its ID (called channel_id)
//
    if (device_exist == false)
    {
        DEBUG_STREAM << "Trying to create device entry in database" << endl;

        try
        {
            Tango::DbDevInfo my_device_info;
            my_device_info.name = tg_dev_name.c_str();
            my_device_info._class = "IORegister";
            my_device_info.server = tg->get_ds_name().c_str();

            db->add_device(my_device_info);

            db->put_device_alias(tg_dev_name,channel_name);

            Tango::DbDatum db_id(ID_PROP);
            Tango::DbData db_data;
            ElementId ioregister_id = get_new_id();
            db_id << (Tango::DevLong)ioregister_id;
            
            Tango::DbDatum db_ctrl_id(CTRL_ID_PROP);
            db_ctrl_id << (Tango::DevLong)ctrl_id;

            Tango::DbDatum db_axis(AXIS_PROP);
            db_axis << channel_idx;
            
            db_data.push_back(db_id);
            db_data.push_back(db_ctrl_id);
            db_data.push_back(db_axis);
            
            db->put_device_property(tg_dev_name.c_str(),db_data);

            DEBUG_STREAM << "Device created in database (with alias)" << endl;
        }
        catch (Tango::DevFailed &e)
        {
            DEBUG_STREAM << "Gasp an exception........" << endl;
            TangoSys_OMemStream o;
            o << "Can't create ioregister " << channel_name << " in database" << ends;

            Tango::Except::re_throw_exception(e,(const char *)"Pool_CantCreateIORegister",o.str(),
                              (const char *)"Pool::create_ioregister");
        }

//
// Find the Tango IORegister class and create the ioregister
//
        const vector<Tango::DeviceClass *> *cl_list = tg->get_class_list();
        for (unsigned long i = 0;i < cl_list->size();i++)
        {
            if ((*cl_list)[i]->get_name() == "IORegister")
            {
                try
                {
                    DEBUG_STREAM << "Found DeviceClass IORegister. Will create the device" << endl;
                    Tango::DevVarStringArray na;
                    na.length(1);
                    na[0] = tg_dev_name.c_str();
                    (*cl_list)[i]->device_factory(&na);
                    break;
                }
                catch (Tango::DevFailed &e)
                {
                    DEBUG_STREAM << "Exception while trying to create IORegister device" << endl;

//
// Check if this ioregister has already been added into pool structures
// If yes, remove it from pool structures
//
                    try
                    {
                        DevicePool::remove_element(channel_name);
                    }
                    catch (...) {}

//
// The delete_device will also delete device property(ies)
//
                    db->delete_device(tg_dev_name);

                    TangoSys_OMemStream o;
                    o << "Can't create ioregister device " << channel_name << ends;

                    Tango::Except::re_throw_exception(e,(const char *)"Pool_CantCreateIORegister",o.str(),
                              (const char *)"Pool::create_ioregister");
                }
            }
        }

//
// Create a Tango device proxy on the newly created ioregister
// and set its connection to automatic re-connection
//
        IORegisterPool &iorp = get_ioregister(channel_name);
        Tango::DeviceProxy *tmp_dev = new Tango::DeviceProxy(iorp.get_full_name().c_str());
        tmp_dev->set_transparency_reconnection(true);
        
        IORegister_ns::IORegister *dev = static_cast<IORegister_ns::IORegister*>
            (tg->get_device_by_name(iorp.get_full_name()));

        set_tango_element(iorp, tmp_dev, dev);
    }

//
// Inform ghost group that there is a new communication channel
//
    //TODO: Inform ghost group that there is a new communication channel
    /*
    MotorGroup_ns::MotorGroup *ghost_ptr = get_ghost_motor_group_ptr();
    {
        Tango::AutoTangoMonitor atm(ghost_ptr);
        ghost_ptr->add_motor_to_group(mot_list.back().id);
    }
    */

//
// Push a change event for client listening on event
//

    Tango::Attribute &iorl = dev_attr->get_attr_by_name("IORegisterList");
    read_IORegisterList(iorl);
    iorl.fire_change_event();

}

//+------------------------------------------------------------------
/**
 *	method:	Pool::delete_ioregister
 *
 *	description:	method to execute "DeleteIORegister"
 *	Delete a ioregister from its name
 *	Once an ioregister is deleted, it is not available any more. All its information have been
 *	removed from the database
 *
 * @param	argin	IORegister name
 *
 */
//+------------------------------------------------------------------
void Pool::delete_ioregister(Tango::DevString argin)
{
    DEBUG_STREAM << "Pool::delete_ioregister(): entering... !" << endl;

    //	Add your own code to control device here
//
// Find ioregister in ioregister list
//

    string user_name(argin);
    IORegisterPool &channel_to_del =  get_ioregister(user_name);

    DEBUG_STREAM << "IORegister found" << endl;

//
// Check that the ioregister is not actually used
//
    if (get_element_proxy(channel_to_del)->state() == Tango::MOVING)
    {
        TangoSys_OMemStream o;
        o << "Can't delete ioregister with name " << argin;
        o << ". It is actually used (reading/writing)." << ends;

        Tango::Except::throw_exception((const char *)"Pool_CantDeleteIORegister",o.str(),
                                 (const char *)"Pool::delete_ioregister");
    }

//
// Remove its entry in database. This will also delete any device
// properties and device attribute properties
//

    Tango::Util *tg = Tango::Util::instance();
    try
    {
        tg->get_database()->delete_device(channel_to_del.get_full_name());

//
// Delete ioregister device from server but first find its Tango xxxClass instance
//
        IORegister_ns::IORegister *ioregister_dev =  get_ioregister_device(channel_to_del);
        Tango::DeviceClass *dc = ioregister_dev->get_device_class();

        dc->device_destroyer(channel_to_del.get_full_name());
    }
    catch (Tango::DevFailed &e)
    {
        TangoSys_OMemStream o;
        o << "Can't delete ioregister with name " << argin << ends;

        Tango::Except::re_throw_exception(e,(const char *)"Pool_CantDeleteIORegister",o.str(),
                                 (const char *)"Pool::delete_ioregister");
    }

//
// Before returning, send a change event for client listenning
// on event
//

    Tango::Attribute &iorl = dev_attr->get_attr_by_name("IORegisterList");
    read_IORegisterList(iorl);
    iorl.fire_change_event();
}

}	//	namespace
