//+=============================================================================
//
// file :         PoolUtil.cpp
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
// Revision 1.62  2007/09/07 15:00:06  tcoutinho
// safety commit
//
// Revision 1.61  2007/08/30 12:40:39  tcoutinho
// - changes to support Pseudo counters.
//
// Revision 1.60  2007/08/24 15:55:26  tcoutinho
// safety weekend commit
//
// Revision 1.59  2007/08/23 10:32:44  tcoutinho
// - basic pseudo counter check
// - some fixes regarding pseudo motors
//
// Revision 1.58  2007/08/20 06:37:32  tcoutinho
// development commit
//
// Revision 1.57  2007/08/17 15:37:29  tcoutinho
// - fix bug: in case pseudo motor controller is in error
//
// Revision 1.56  2007/08/17 13:07:30  tcoutinho
// - pseudo motor restructure
// - pool base dev class restructure
// - initial commit for pseudo counters
//
// Revision 1.55  2007/08/08 10:46:35  tcoutinho
// Fix bug 17 : Controller properties should be Pool properties and not global properties
//
// Revision 1.54  2007/08/08 09:10:36  tcoutinho
// - dropped feature : controller class properties are no longer supported. This is a preliminary step towards moving controller properties from global properties in the database to properties in the pool device were the controller belongs (resolution of bug 17)
//
// Revision 1.53  2007/08/08 08:47:55  tcoutinho
// Fix bug 18 : CreateController should be a one step operation
//
// Revision 1.52  2007/07/30 11:01:00  tcoutinho
// Fix bug 5 : Additional information for controllers
//
// Revision 1.51  2007/07/26 10:25:15  tcoutinho
// - Fix bug 1 :  Automatic temporary MotorGroup/MeasurementGroup deletion
//
// Revision 1.50  2007/07/17 11:41:57  tcoutinho
// replaced comunication with communication
//
// Revision 1.49  2007/07/02 14:46:37  tcoutinho
// first stable comunication channel commit
//
// Revision 1.48  2007/06/28 16:22:38  tcoutinho
// safety commit during comunication channels development
//
// Revision 1.47  2007/06/28 07:15:34  tcoutinho
// safety commit during comunication channels development
//
// Revision 1.46  2007/06/27 08:56:28  tcoutinho
// first commit for comuncation channels
//
// Revision 1.45  2007/04/30 15:47:05  tcoutinho
// - new attribute "Channels"
// - new device property "Channel_List"
// - when add/remove channel, pool sends a change event on the MeasurementGroupList
//
// Revision 1.44  2007/04/30 14:51:20  tcoutinho
// - make possible to Add/Remove elements on motorgroup that are part of other motor group(s)
//
// Revision 1.43  2007/04/23 15:23:06  tcoutinho
// - changes according to Sardana metting 26-03-2007: ActiveMeasurementGroup attribute became obsolete
//
// Revision 1.42  2007/02/28 16:21:52  tcoutinho
// - support for 0D channels
// - basic fixes after running first battery of tests on measurement group
//
// Revision 1.41  2007/02/22 12:02:00  tcoutinho
// - added support for ghost measurement group
// - added support for measurement group in init/reload controller operations
// - added support of internal events on measurement group
//
// Revision 1.40  2007/02/14 11:20:12  tcoutinho
// - fix valgrind error by splitting a string concatenation operation in two operations (a little strange this valgrind error...)
//
// Revision 1.39  2007/02/13 14:39:43  tcoutinho
// - fix bug in motor group when a motor or controller are recreated due to an InitController command
//
// Revision 1.38  2007/02/08 10:49:29  etaurel
// - Some small changes after the merge
//
// Revision 1.37  2007/02/08 08:51:16  etaurel
// - Many changes. I don't remember the list
//
// Revision 1.36  2007/02/06 09:41:03  tcoutinho
// - added MeasurementGroup
//
// Revision 1.35  2007/01/30 16:00:47  etaurel
// - The CT Value attribute is now a Double
// WARNING, this change has made us discouvering the GCC BUG  2834...
// Some code is now between ifdef/endif statement to compile using gcc 3.3
//
// Revision 1.34  2007/01/26 08:36:48  etaurel
// - We now have a first release of ZeroDController
//
// Revision 1.33  2007/01/23 08:27:22  tcoutinho
// - fix some pm bugs found with the test procedure
// - added internal event for MotionEnded
//
// Revision 1.32  2007/01/17 09:38:14  tcoutinho
// - internal events bug fix.
//
// Revision 1.31  2007/01/16 14:32:22  etaurel
// - Coomit after a first release with CT
//
// Revision 1.30  2007/01/09 07:52:10  tcoutinho
// - changes to make it gcc 4.1 compatible
//
// Revision 1.29  2007/01/05 15:02:38  etaurel
// - First implementation of the Counter Timer class
//
// Revision 1.28  2007/01/05 13:02:05  tcoutinho
// - changes to support internal event propagation
//
// Revision 1.27  2006/12/28 15:36:58  etaurel
// - Fire events also on the motor limit_switches attribute
// - Throw events even in simulation mode
// - Mange motor position limit switches dependant of the offset attribute
//
// Revision 1.26  2006/12/20 10:25:35  tcoutinho
// - changes to support internal event propagation
// - bug fix in motor groups containing other motor groups or pseudo motors
//
// Revision 1.25  2006/12/12 11:09:16  tcoutinho
// - support for pseudo motors and motor groups in a motor group
//
// Revision 1.24  2006/11/24 08:48:45  tcoutinho
// - minor changes
//
// Revision 1.23  2006/11/21 14:40:40  tcoutinho
// bug fix on group_exit method
//
// Revision 1.22  2006/11/20 14:32:43  etaurel
// - Add ghost group and event on motor group position attribute
//
// Revision 1.21  2006/11/07 14:57:09  etaurel
// - Now, the pool really supports different kind of controllers (cpp and py)
//
// Revision 1.20  2006/11/03 15:48:59  etaurel
// - Miscellaneous changes that I don't remember
//
// Revision 1.19  2006/10/27 14:43:02  etaurel
// - New management of the MaxDevice stuff
// - SendToCtrl cmd added
// - Some bug fixed in prop management
//
// Revision 1.18  2006/10/27 14:02:19  tcoutinho
// added support for class level properties in the Database
//
// Revision 1.17  2006/10/23 15:12:36  etaurel
// - Fix memory leak in several places
//
// Revision 1.16  2006/10/23 13:36:57  etaurel
// - First implementation of controller properties for CPP controller
//
// Revision 1.15  2006/10/20 15:37:30  etaurel
// - First release with GetControllerInfo command supported and with
// controller properties
//
// Revision 1.14  2006/10/17 14:28:10  tcoutinho
// bug fixes on properties
//
// Revision 1.13  2006/10/06 15:41:03  tcoutinho
// bug fixes: - error report in GetPseudoMotorInfo.
//                 - missed instatiation of pseudo_proxy in the PseudoMotorPool structure.
//
// Revision 1.12  2006/10/06 13:36:39  tcoutinho
// changed info command names, added properties functionality
//
// Revision 1.11  2006/10/02 09:19:12  etaurel
// - Motor controller now supports extra features (both CPP and Python)
//
// Revision 1.10  2006/09/29 12:53:22  tcoutinho
// *** empty log message ***
//
// Revision 1.9  2006/09/27 15:15:50  etaurel
// - ExternalFile and CtrlFile has been splitted in several classes:
//   ExternalFile, CppCtrlFile, PyExternalFile and PyCtrlFile
//
// Revision 1.8  2006/09/22 15:31:01  etaurel
// - Miscellaneous changes
//
// Revision 1.7  2006/09/21 10:20:54  etaurel
// - The motor group do not ID any more
//
// Revision 1.6  2006/09/21 08:01:31  etaurel
// - Now all test suite is OK withou ID on motor interface
//
// Revision 1.5  2006/09/21 07:25:58  etaurel
// - Changes due to the removal of Motor ID in the Tango interface
//
// Revision 1.4  2006/09/20 16:00:36  tcoutinho
// pseudo motor API changed
//
// Revision 1.3  2006/09/20 13:11:12  etaurel
// - For the user point of view, the controller does not have ID any more.
// We are now using the controller instance name (uniq) to give them a name
//
// Revision 1.2  2006/09/18 10:32:22  etaurel
// - Commit after merge with pseudo-motor branch
//
// Revision 1.1  2006/07/07 13:39:14  etaurel
// - A new file
//
// Revision 1.4  2006/06/28 15:56:46  etaurel
// - Commit after first series of tests
//
// Revision 1.3  2006/06/22 14:49:24  etaurel
// - Some more changes
//
// Revision 1.2  2006/06/21 14:48:12  etaurel
// - Don't remember the changes I did..
//
// Revision 1.1  2006/06/19 12:31:50  etaurel
// -Split Pool.cpp file in two
//
//
// copyleft :     CELLS/ALBA
//				  Edifici Ciències Nord. Mòdul C-3 central.
//  			  Campus Universitari de Bellaterra. Universitat Autònoma de Barcelona
//  			  08193 Bellaterra, Barcelona
//  			  Spain
//
//+=============================================================================

#include "CtrlFiCa.h"
#include "PoolUtil.h"
#include "PoolClass.h"
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
#include "pool/Ctrl.h"
#include "pool/ComCtrl.h"
#include "pool/MotCtrl.h"
#include "pool/CoTiCtrl.h"
#include "pool/ZeroDCtrl.h"
#include "pool/OneDCtrl.h"
#include "pool/TwoDCtrl.h"
#include "pool/PseudoCoCtrl.h"
#include "pool/IORegisterCtrl.h"
#include <sys/types.h>
#include <sys/stat.h>
#include <dirent.h>

namespace Pool_ns
{

inline std::ostream & printToStream(std::ostream & flux, PoolElemEventList &lst, int indent = 0)
{
    indent++;
    for(PoolElemEventList::iterator it = lst.begin(); it != lst.end(); ++it)
        (*it)->printToStream(flux, indent);
    return flux;
}

//------------------------------------------------------------------------------
// Pool::f_name_from_db_prop
//
const std::string &Pool::f_name_from_db_prop(const std::string &ctrl_name)
{
    int32_t nb_ctrl = get_controller_nb();

    string::size_type pos;
    pos = ctrl_name.find('/');
    string ctrl = ctrl_name.substr(0,pos);
    string inst = ctrl_name.substr(pos + 1);
    int32_t ind_array = 0;

    for (int32_t l = 0;l < nb_ctrl; l++)
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

        if ((ctrl_class_db == ctrl) && (inst_db == inst))
        {
            ind_array = l * PROP_BY_CTRL;
            break;
        }
    }

    vector<string>::iterator v_ite = ctrl_info.begin();
    v_ite += ind_array;

    return *(v_ite + 1);
}

//------------------------------------------------------------------------------
// Pool::dev_type_from_db_prop
//
CtrlType Pool::dev_type_from_db_prop(string &ctrl_name)
{
    int32_t nb_ctrl = get_controller_nb();
    string::size_type pos;

    pos = ctrl_name.find('/');
    string ctrl = ctrl_name.substr(0,pos);
    string inst = ctrl_name.substr(pos + 1);
    int32_t ind_array = 0;

    for (int32_t l = 0;l < nb_ctrl;l++)
    {
        string ctrl_db = ctrl_info[(l * PROP_BY_CTRL) + 2];
        string inst_db = ctrl_info[(l * PROP_BY_CTRL) + 3];
        transform(ctrl_db.begin(),ctrl_db.end(),ctrl_db.begin(),::tolower);
        transform(inst_db.begin(),inst_db.end(),inst_db.begin(),::tolower);
        if ((ctrl_db == ctrl) && (inst_db == inst))
        {
            ind_array = l * PROP_BY_CTRL;
            break;
        }
    }

    vector<string>::iterator v_ite = ctrl_info.begin();
    v_ite += ind_array;

    return str_2_CtrlType(*v_ite);
}

//------------------------------------------------------------------------------
// Pool::restore_ctrl_obj
//
void Pool::restore_ctrl_obj(vector<Pool::CtrlBkp> *ctrls,vector<Pool::ObjBkp> *objs)
{
//
// First, restore controllers
//
    if (ctrls != NULL)
    {
        PoolElementTypeIt ctrl_it, ctrl_beg, ctrl_end;
        get_all_controller(ctrl_beg, ctrl_end);

        vector<Pool::CtrlBkp>::iterator ite;
        for (ite = ctrls->begin();ite != ctrls->end();++ite)
        {
            ctrl_it = ctrl_beg;
            advance(ctrl_it, ite->dist);
            
            ControllerPool &ctrlpool = get_controller(ctrl_it->second);
            ctrlpool.set_controller(ite->good_old_ctrl);
        }
    }

//
// Now, restore objects
//

    if (objs != NULL)
    {
        vector<Pool::ObjBkp>::iterator obj_ite;
        for (obj_ite = objs->begin();obj_ite != objs->end();++obj_ite)
        {

//
// Is it a motor ?
//

            if (obj_ite->type == MOTOR_CTRL)
            {
                PoolElementTypeIt elem_it = element_types.lower_bound(MOTOR_ELEM);
                
                advance(elem_it, obj_ite->dist);
                
                MotorPool &motor_pool = get_physical_motor(elem_it->second);
                Motor_ns::Motor *mot_dev = get_motor_device(motor_pool);
                
                ControllerPool &ct = get_controller(motor_pool);
                vct_ite ct_fica = ct.ite_ctrl_class;
                {
                    AutoPoolLock lo((*ct_fica)->get_mon());
                    MotorController *tmp_mc =
                        static_cast<MotorController *>(obj_ite->old_ctrl);
                    mot_dev->set_ctrl(tmp_mc);
                    mot_dev->ctrl_online();
                }
            }

//
// Is it a pseudo motor ?
//

            if (obj_ite->type == PSEUDO_MOTOR_CTRL)
            {
                PoolElementTypeIt elem_it = element_types.lower_bound(PSEUDO_MOTOR_ELEM);
                advance(elem_it, obj_ite->dist);
                    
                PseudoMotorPool &pm_pool = get_pseudo_motor(elem_it->second);
                PseudoMotor_ns::PseudoMotor *pm_dev = get_pseudo_motor_device(pm_pool);
                
                ControllerPool &ct = get_controller(pm_pool);
                vct_ite ct_fica = ct.ite_ctrl_class;
                {
                    AutoPoolLock lo((*ct_fica)->get_mon());
                    PseudoMotorController *tmp_mc =
                        static_cast<PseudoMotorController *>(obj_ite->old_ctrl);
                    pm_dev->set_ctrl(tmp_mc);
                    pm_dev->ctrl_online();
                }
            }

//
// Is it a pseudo counter ?
//

            if (obj_ite->type == PSEUDO_COUNTER_CTRL)
            {
                PoolElementTypeIt ite_co_rest = element_types.lower_bound(PSEUDO_COUNTER_ELEM);
                advance(ite_co_rest, obj_ite->dist);
                    
                PseudoCounterPool &pc_pool = get_pseudo_counter(ite_co_rest->second);
                PseudoCounter_ns::PseudoCounter *pc_dev = get_pseudo_counter_device(pc_pool);
                
                ControllerPool &ct = get_controller(pc_pool);
                vct_ite ct_fica = ct.ite_ctrl_class;
                {
                    AutoPoolLock lo((*ct_fica)->get_mon());
                    PseudoCounterController *tmp_mc =
                        static_cast<PseudoCounterController *>(obj_ite->old_ctrl);
                    pc_dev->set_ctrl(tmp_mc);
                    pc_dev->ctrl_online();
                }
            }
//
// Is it a Counter Timer ?
//

            else if (obj_ite->type == COTI_CTRL)
            {
                PoolElementTypeIt ite_ct_rest = element_types.lower_bound(COTI_ELEM);
                advance(ite_ct_rest, obj_ite->dist);
                
                CTExpChannelPool &ct_pool = get_countertimer(ite_ct_rest->second);
                CTExpChannel_ns::CTExpChannel *ct_dev = get_countertimer_device(ct_pool);
                
                ControllerPool &ct = get_controller(ct_pool);
                
                vct_ite ct_fica = ct.ite_ctrl_class;
                {
                    AutoPoolLock lo((*ct_fica)->get_mon());
                    CoTiController *tmp_ctc =
                        static_cast<CoTiController *>(obj_ite->old_ctrl);
                    ct_dev->set_ctrl(tmp_ctc);
                    ct_dev->ctrl_online();
                }
            }

//
// Is it a Zero D Exp Channel ?
//

            else if (obj_ite->type == ZEROD_CTRL)
            {
                PoolElementTypeIt ite_zerod_rest = element_types.lower_bound(ZEROD_ELEM);
                advance(ite_zerod_rest, obj_ite->dist);
                
                ZeroDExpChannelPool &zerod_pool = get_zerod(ite_zerod_rest->second);
                ZeroDExpChannel_ns::ZeroDExpChannel *zerod_dev = get_zerod_device(zerod_pool);

                ControllerPool &ct = get_controller(zerod_pool);
                vct_ite ct_fica = ct.ite_ctrl_class;
                {
                    AutoPoolLock lo((*ct_fica)->get_mon());
                    ZeroDController *tmp_zdc =
                        static_cast<ZeroDController *>(obj_ite->old_ctrl);
                    zerod_dev->set_ctrl(tmp_zdc);
                    zerod_dev->ctrl_online();
                }
            }
//
// Is it a One D Exp Channel ?
//

            else if (obj_ite->type == ONED_CTRL)
            {
                PoolElementTypeIt ite_oned_rest = element_types.lower_bound(ONED_ELEM);
                advance(ite_oned_rest, obj_ite->dist);
                
                OneDExpChannelPool &oned_pool = get_oned(ite_oned_rest->second);
                OneDExpChannel_ns::OneDExpChannel *oned_dev = get_oned_device(oned_pool);
                
                ControllerPool &ct = get_controller(oned_pool);
                vct_ite ct_fica = ct.ite_ctrl_class; 
                {
                    AutoPoolLock lo((*ct_fica)->get_mon());
                    OneDController *tmp_odc = 
                        static_cast<OneDController *>(obj_ite->old_ctrl);
                    oned_dev->set_ctrl(tmp_odc);
                    oned_dev->ctrl_online();
                }
            }
//
// Is it a Two D Exp Channel ?
//

            else if (obj_ite->type == TWOD_CTRL)
            {
                PoolElementTypeIt ite_twod_rest = element_types.lower_bound(TWOD_ELEM);
                advance(ite_twod_rest, obj_ite->dist);
                
                TwoDExpChannelPool &twod_pool = get_twod(ite_twod_rest->second);
                TwoDExpChannel_ns::TwoDExpChannel *twod_dev = get_twod_device(twod_pool);
                
                ControllerPool &ct = get_controller(twod_pool);
                vct_ite ct_fica = ct.ite_ctrl_class; 
                {
                    AutoPoolLock lo((*ct_fica)->get_mon());
                    TwoDController *tmp_odc = 
                        static_cast<TwoDController *>(obj_ite->old_ctrl);
                    twod_dev->set_ctrl(tmp_odc);
                    twod_dev->ctrl_online();
                }
            }
            
//
// Is it a Communication Channel ?
//
            else if (obj_ite->type == COM_CTRL)
            {
                PoolElementTypeIt ite_ch_rest = element_types.lower_bound(COM_ELEM);
                advance(ite_ch_rest, obj_ite->dist);
                
                CommunicationChannelPool &cc_pool = 
                    get_communication_channel(ite_ch_rest->second);
                CommunicationChannel_ns::CommunicationChannel *comch_dev = 
                    get_communication_channel_device(cc_pool);
                
                ControllerPool &ct = get_controller(cc_pool);
                vct_ite ct_fica = ct.ite_ctrl_class;
                {
                    AutoPoolLock lo((*ct_fica)->get_mon());
                    ComController *tmp_ccc =
                        static_cast<ComController *>(obj_ite->old_ctrl);
                    comch_dev->set_ctrl(tmp_ccc);
                    comch_dev->ctrl_online();
                }
            }
//
// Is it a IORegister ?
//

            else if (obj_ite->type == IOREGISTER_CTRL)
            {
                PoolElementTypeIt ite_ch_rest = element_types.lower_bound(IOREGISTER_ELEM);
                advance(ite_ch_rest, obj_ite->dist);
                
                IORegisterPool &ior_pool = get_ioregister(ite_ch_rest->second);
                IORegister_ns::IORegister *ior_dev = get_ioregister_device(ior_pool);
                
                ControllerPool &ct = get_controller(ior_pool);
                vct_ite ct_fica = ct.ite_ctrl_class;
                {
                    AutoPoolLock lo((*ct_fica)->get_mon());
                    IORegisterController *tmp_ccc =
                        static_cast<IORegisterController *>(obj_ite->old_ctrl);
                    ior_dev->set_ctrl(tmp_ccc);
                    ior_dev->ctrl_online();
                }
            }
//
// Is it a Constraint?
//
            else if (obj_ite->type == CONSTRAINT_CTRL)
            {
                // Nothing to restore
            }
        }
    }
}

//------------------------------------------------------------------------------
// Pool::create_proxies
//
void Pool::create_proxies()
{
    for(ElemIdMapIt elem_it = element_ids.begin(); elem_it != element_ids.end(); ++elem_it)
    {
        PoolElement &pe = *elem_it->second;
        
        if(pe.get_type() == CTRL_ELEM || pe.get_type() == INSTRUMENT_ELEM)
            continue;
        
        if (!has_element_proxy(elem_it->first))
        {
            Tango::DeviceProxy *proxy = new Tango::DeviceProxy(pe.get_full_name().c_str());
            proxy->set_transparency_reconnection(true);
            set_element_proxy(pe, proxy);
        }
    }
}

//------------------------------------------------------------------------------
// Pool::except_2_ctrl_status
//
 void Pool::except_2_ctrl_status(Tango::DevFailed &e,string &ctrl_status)
{
    if (get_logger()->is_info_enabled())
        Tango::Except::print_exception(e);

    string except_desc_0(e.errors[0].desc);
    string except_desc_1;
    uint32_t except_size = e.errors.length();
    if (except_size >= 2)
        except_desc_1 = e.errors[1].desc;

    ctrl_status = ctrl_status + ".\nThe reported error description is";
    ctrl_status = ctrl_status + "\n\t" + except_desc_0;
    if (except_size >= 2)
        ctrl_status = ctrl_status + "\n\t" + except_desc_1;
}

//------------------------------------------------------------------------------
// Pool::set_moving_state
//
void Pool::set_moving_state()
{
    Tango::AutoTangoMonitor atm(this);

    if (moving_state_requested == false)
    {
        moving_state_requested = true;

        for (PoolElementTypeIt mot_it = element_types.lower_bound(MOTOR_ELEM);
             mot_it != element_types.upper_bound(MOTOR_ELEM); ++mot_it)
        {
            get_motor_device(mot_it->second)->pool_shutdown();
            
        }

        for (PoolElementTypeIt ct_it = element_types.lower_bound(COTI_ELEM);
             ct_it != element_types.upper_bound(COTI_ELEM); ++ct_it)
        {
            get_countertimer_device(ct_it->second)->pool_shutdown();
        }

//
// Send an event on the state attribute in case some client(s)
// are listenning on Pool device state
//

        set_state(Tango::MOVING);
        Tango::Attribute &state_att = dev_attr->get_attr_by_name("state");
        state_att.fire_change_event();
    }
}

//------------------------------------------------------------------------------
// Pool::check_property_data
//
void Pool::check_property_data(string &inst_name,string &class_name,
                               vector<string> &info, int start)
{
    Tango::Util *util = Tango::Util::instance();
    Tango::Database *db = util->get_database();

    Tango::DbData db_data_instance_level;

//
// Try to get all the properties from the Database
//
    vector<string>::iterator ite;
    for(ite = info.begin() + start; ite != info.end(); ite += 4)
    {
        string final_prop_name = inst_name + "/" + (*ite);
        db_data_instance_level.push_back(Tango::DbDatum(final_prop_name));
    }

    db->get_device_property(get_name(), db_data_instance_level);

    int i = 0;
    for(ite = info.begin() + start; ite != info.end(); ite += 4)
    {
        string &dft_value = *(ite+3);
//
// If property is not defined in the database and the property has no default
// value it is an error
//
        if(db_data_instance_level[i].is_empty() && dft_value == "")
        {
            TangoSys_OMemStream o;
            o << "Pool Property '" << (*ite) << "' must be defined in the "
                 " database" << ends;
            Tango::Except::throw_exception(
                    (const char *)"Pool_MissingDatabaseProperty",o.str(),
                    (const char *)"Pool::check_property_data");

        }
        i++;
    }
}

//------------------------------------------------------------------------------
// Pool::check_property_data
//
void Pool::check_property_data(vector<PropertyData *> &prop_list)
{
    for(vector<PropertyData *>::iterator it = prop_list.begin();
        it != prop_list.end(); ++it)
    {   
        PropertyData& prop_data = **it;
        if ((prop_data.is_defined_in_db() == false) &&
            (prop_data.has_dft_value == false))
        {
            TangoSys_OMemStream o;
            o << "Property '" << prop_data.name;
            o << "' does not have any value defined in database or as default "
                 "value" << ends;
            Tango::Except::throw_exception(
                    (const char *)"Pool_MissingPropertyValue",o.str(),
                    (const char *)"Pool::check_property_data");
        }
    }
}

//------------------------------------------------------------------------------
// Pool::find_property_data
//
PropertyData *
Pool::find_property_data(vector<PropertyData*> &prop_data,string &prop_name)
{
    if(prop_data.size() > 0)
    {
        string prop_name_lower(prop_name);
        transform(prop_name_lower.begin(), prop_name_lower.end(),
                  prop_name_lower.begin(), ::tolower);

        vector<PropertyData*>::iterator ite = prop_data.begin();
        for(; ite != prop_data.end(); ite++)
        {
            PropertyData& prop_data = **ite;
            string curr_prop_name_lower(prop_data.name);
            transform(curr_prop_name_lower.begin(), curr_prop_name_lower.end(),
                      curr_prop_name_lower.begin(), ::tolower);
            if(prop_name_lower == curr_prop_name_lower)
                return &prop_data;
        }
    }
    TangoSys_OMemStream o;
    o << "Property '" << prop_name << "' does not exist ";
    o << "on the given arrray" << ends;
    Tango::Except::throw_exception(
            (const char *)"Pool_UnknownProperty",o.str(),
            (const char *)"Pool::find_property_data");
    
    // To quiet the compiler
    return NULL;
}

//------------------------------------------------------------------------------
// Pool::build_property_data
//
void Pool::build_property_data(const string &inst_name, const string &class_name,
                               vector<pair<string,string> > &prop_pairs,
                               vector<PropertyData*> &prop_data)
{
    if(prop_data.size() == 0)
        return;

    Tango::DbData db_data_put, db_data_instance_level;

    if(prop_pairs.size() > 0)
    {
//
// First put all given properties in the Database
//
        vector<pair<string,string> >::iterator pair_ite;
        for(pair_ite = prop_pairs.begin(); pair_ite != prop_pairs.end(); pair_ite++)
        {
            string final_prop_name = inst_name + "/" + pair_ite->first;

            PropertyData *pdata = find_property_data(prop_data,pair_ite->first);

            Tango::DbDatum datum(final_prop_name);
            string &data = pair_ite->second;

//
// Special case for string arrays
//
            if(pdata->get_type() == Tango::DEVVAR_STRINGARRAY)
            {
                vector<string> data_arr;
                string::iterator data_ite = data.begin();
                string curr_elem;
                for(;data_ite != data.end(); ++data_ite)
                {
                    if('\n' == (*data_ite))
                    {
                        if('\n' == (*(data_ite+1)) )
                        {
                            curr_elem += *data_ite;
                            ++data_ite;
                        }
                        else
                        {
                            data_arr.push_back(curr_elem);
                            curr_elem.clear();
                        }
                    }
                    else
                    {
                        curr_elem += *data_ite;
                    }
                }
                data_arr.push_back(curr_elem);
                datum << data_arr;
            }
            else
                datum << data;

            db_data_put.push_back(datum);
        }
        get_db_device()->put_property(db_data_put);
    }

//
// Try to get all the properties from the Database
//

    vector<PropertyData*>::iterator ite;
    for(ite = prop_data.begin(); ite != prop_data.end(); ite++)
    {
        string final_prop_name = inst_name + "/" + (*ite)->name;
        db_data_instance_level.push_back(Tango::DbDatum(final_prop_name));
        (*ite)->clear_db_flag();
    }
    get_db_device()->get_property(db_data_instance_level);

    int i = 0;
    for(ite = prop_data.begin(); ite != prop_data.end(); ite++)
    {
        Tango::DbDatum *db_data = NULL;

        PropertyData &prop = *(*ite);

        // If data exists at the instance level use it
        if(!db_data_instance_level[i].is_empty())
        {
            db_data = &db_data_instance_level[i];
        }
        // Otherwise use the Default Value.

        if(db_data == NULL)
        {
//
// If there is no DefaultValue we make a default value
//
            if(!prop.has_dft_value)
            {
                Tango::CmdArgType type = prop.get_type();
                if(type == Tango::DEV_BOOLEAN)
                    prop.set_value(false);
                else if(type == Tango::DEV_LONG)
                    prop.set_value((int32_t)0);
                else if(type == Tango::DEV_DOUBLE)
                    prop.set_value(0.0);
                else if(type == Tango::DEV_STRING)
                    prop.set_value("");
                // for array data types we keep them with zero elements
            }
        }
        else
        {
//
// The property is defined in the Database: Update the PropertyData vector with
// its value.
//
            string s; *db_data >> s; prop.set_value(s);

            Tango::CmdArgType type = prop.get_type();
            if(type == Tango::DEV_BOOLEAN)
            { bool b; *db_data >> b; prop.set_value(b); }
            else if(type == Tango::DEV_LONG)
            { Tango::DevLong l; *db_data >> l; prop.set_value((int32_t)l); }
            else if(type == Tango::DEV_DOUBLE)
            { double d; *db_data >> d; prop.set_value(d); }
            else if(type == Tango::DEV_STRING)
            { /* nothing to do on string. value_str member already contains the value.*/ }
            else if(type == Tango::DEVVAR_BOOLEANARRAY)
            {
                vector<bool> &prop_v = *prop.get_bool_v();
                vector<Tango::DevLong> tmp_vect;
                *db_data >> tmp_vect;
                prop_v.clear();
                for(vector<Tango::DevLong>::iterator it = tmp_vect.begin(); 
                    it != tmp_vect.end(); ++it )
                    prop_v.push_back(*it);
                // force the string value to be updated
                prop.set_value(&prop_v);
            }
            else if(type == Tango::DEVVAR_LONGARRAY)
            {
                vector<int32_t> &prop_v = *prop.get_int32_v();
                vector<Tango::DevLong> tmp_vect;
                *db_data >> tmp_vect;
                prop_v.clear();
                for(vector<Tango::DevLong>::iterator it = tmp_vect.begin(); 
                    it != tmp_vect.end(); ++it )
                    prop_v.push_back((int32_t)(*it));
                // force the string value to be updated
                prop.set_value(&prop_v);
            }
            else if(type == Tango::DEVVAR_DOUBLEARRAY)
            {
                vector<double> &v = *prop.get_double_v();
                *db_data >> v;
                // force the string value to be updated
                prop.set_value(&v);
            }
            else if(type == Tango::DEVVAR_STRINGARRAY)
            {
                vector<string> &v = *prop.get_string_v();
                *db_data >> v;
                // force the string value to be updated
                prop.set_value(&v);
            }

            prop.is_in_db();
        }
        i++;
    }
}

//------------------------------------------------------------------------------
// Pool::properties_2_py_dict
//
PyObject* Pool::properties_2_py_dict(vector<PropertyData*> &properties)
{
    PyObject *arg_prop = PyDict_New();

    vector<PropertyData*>::iterator ite;
    for(ite = properties.begin(); ite != properties.end(); ite++)
    {
        PyPropertyData *prop = (PyPropertyData*)(*ite);
        PyObject *value = prop->to_py();
        PyDict_SetItemString(arg_prop,prop->name.c_str(),value);
        Py_DECREF(value);
    }

    return arg_prop;
}

//------------------------------------------------------------------------------
// Pool::properties_2_cpp_vect
//
vector<Controller::Properties> *Pool::properties_2_cpp_vect(
                                              vector<PropertyData*> &properties)
{
    vector<Controller::Properties> *arg_prop =
        new vector<Controller::Properties>;

    vector<PropertyData*>::iterator ite;
    for(ite = properties.begin(); ite != properties.end(); ite++)
    {
        CppPropertyData *prop = (CppPropertyData*)(*ite);
        Controller::Properties val = prop->to_cpp();
        arg_prop->push_back(val);
    }

    return arg_prop;
}

//------------------------------------------------------------------------------
// Pool::post_init_device
//
void Pool::post_init_device()
{
//
// For each pseudo counter subscribe for events coming from each channel it
// uses
//
    for (PoolElementTypeIt pc_it = element_types.lower_bound(PSEUDO_COUNTER_ELEM);
         pc_it != element_types.upper_bound(PSEUDO_COUNTER_ELEM); ++pc_it)
    {
        PseudoCounterPool &pcp = get_pseudo_counter(pc_it->second);
        ElemIdVectorIt ite = pcp.ch_elts.begin();
        for(; ite != pcp.ch_elts.end(); ++ite)
        {
            get_element(*ite)->add_pool_elem_listener(&pcp);
        }
    }

//
// For each pseudo motor fill the missing motor group information
// and subscribe to events coming from the motor group.
// Also fill information about siblings
//
    typedef map<ElementId, PseudoMotor_ns::PseudoMotor*> PseudoMap;
    typedef map<int32_t, PseudoMap > PseudoCtrlMap;
    typedef PseudoMap::iterator PseudoCtrlMapIt;

    PseudoCtrlMap ctrl_pseudos;
    
    // First initialize the necessary temporary map
    /*
    for (PoolElementTypeIt ctrl_it = element_types.lower_bound(CTRL_ELEM);
         ctrl_it != element_types.upper_bound(CTRL_ELEM); ++ctrl_it)
    {
        ControllerPool &ctrlpool = get_controller(ctrl_it->second);
    
        if(ctrlpool.ctrl_class_built == true)
        {
            if(ctrlpool.get_ctrl_obj_type() == PSEUDO_MOTOR_CTRL)
            {
                PseudoVector::size_type n = ctrlpool.MaxDevice;
                PseudoVector v(n, NULL);
                ctrl_pseudos.insert(make_pair(ctrlpool.get_id(), v));
            }
        }
    }
    */

    for (PoolElementTypeIt pm_it = element_types.lower_bound(PSEUDO_MOTOR_ELEM);
         pm_it != element_types.upper_bound(PSEUDO_MOTOR_ELEM); ++pm_it)
    {
        PseudoMotorPool &pmp = get_pseudo_motor(pm_it->second);
        MotorGroupPool &mgp = get_motor_group(pmp.motor_group_id);

        PseudoMotor_ns::PseudoMotor *pm_dev = get_pseudo_motor_device(pmp);
        pm_dev->fix_pending_elements(&pmp);

        mgp.add_pool_elem_listener(&pmp);
        ctrl_pseudos[pmp.get_ctrl_id()][pm_dev->get_axis() - 1] = pm_dev;
    }

    //Set the siblings for each pseudo motor
    for (PoolElementTypeIt pm_it = element_types.lower_bound(PSEUDO_MOTOR_ELEM);
         pm_it != element_types.upper_bound(PSEUDO_MOTOR_ELEM); ++pm_it)
    {
        PseudoMotorPool &pmp = get_pseudo_motor(pm_it->second);
        PseudoMotor_ns::PseudoMotor *pm_dev = get_pseudo_motor_device(pm_it->second);
        pm_dev->set_siblings(ctrl_pseudos[pmp.get_ctrl_id()]);
    }
//
// For each motor group subscribe to the internal events coming from
// each motor of the motor group
//

    for (PoolElementTypeIt elem_it = element_types.lower_bound(MOTOR_GROUP_ELEM);
         elem_it != element_types.upper_bound(MOTOR_GROUP_ELEM); ++elem_it)
    {
        MotorGroupPool &mgp = get_motor_group(elem_it->second);

        //TODO decide if ghost has to be informed of internal events
        if(mgp.id == 0)
            continue;

        ElemIdVectorIt ite = mgp.group_elts.begin();
        for(; ite != mgp.group_elts.end(); ++ite)
        {
            get_element(*ite)->add_pool_elem_listener(&mgp);
        }
    }

//
// For each measurement group subscribe to the internal events coming from
// each channel of the measurement group
//
    for (PoolElementTypeIt elem_it = element_types.lower_bound(MEASUREMENT_GROUP_ELEM);
         elem_it != element_types.upper_bound(MEASUREMENT_GROUP_ELEM); ++elem_it)
    {
        MeasurementGroupPool &mgp = get_measurement_group(elem_it->second);

        //TODO decide if ghost has to be informed of internal events
        if(mgp.id == 0)
            continue;

        ElemIdVectorIt ite = mgp.group_elts.begin();
        for(; ite != mgp.group_elts.end(); ++ite)
        {
            get_element(*ite)->add_pool_elem_listener(&mgp);
        }
    }
}

//------------------------------------------------------------------------------
// Pool::find_and_invalidate_motor
//
void Pool::find_and_invalidate_motor(vector<CtrlBkp> &ctrls,
                                     vector<ObjBkp> &objs)
{
    PoolElementTypeIt first_mot = element_types.lower_bound(MOTOR_ELEM);
    for (PoolElementTypeIt elem_it = first_mot;
         elem_it != element_types.upper_bound(MOTOR_ELEM); ++elem_it)
    {
        MotorPool &motor_pool = get_physical_motor(elem_it->second);
        Motor_ns::Motor *motor = get_motor_device(motor_pool);
        
        vector<Pool::CtrlBkp>::iterator ite;
        for (ite = ctrls.begin();ite != ctrls.end();++ite)
        {
            if (motor_pool.get_ctrl_id() == ite->idx)
            {
                PoolElementTypeIt ctrl_it, ctrl_beg, ctrl_end;
                get_all_controller(ctrl_beg, ctrl_end);
                ctrl_it = ctrl_beg;
                advance(ctrl_it, ite->dist);
                ControllerPool *ct = &get_controller(ctrl_it->second);

//
// Get motor device monitor to be sure that nobody else will do something
// on the motor. As the monitor is re-entrant, it is still possible for
// us to call its state command
//

                if (ct->ctrl_class_built == true)
                {
                    Tango::AutoTangoMonitor atm(motor);
                    Tango::DevState sta;
                    try
                    {
                        sta = get_element_proxy(motor_pool)->state();
                    }
                    catch(Tango::DevFailed &e)
                    {
                        sta = Tango::UNKNOWN;
                    }

//
// If one motor is moving, refuse to reload controller code
// in this code, reset all motor previously found to valid controller code
//

                    if (sta == Tango::MOVING)
                    {
                        restore_ctrl_obj((vector<Pool::CtrlBkp> *)NULL,&objs);

                        TangoSys_OMemStream o;
                        o << "Motor " << motor_pool.name << " (";
                        o << motor_pool.get_full_name() << ") is moving. ";
                        o << "It is not allowed to reload controller code while"
                             " a motor is moving" << ends;

                        Tango::Except::throw_exception(
                            (const char *)"Pool_CantUnloadController",o.str(),
                            (const char *)"Pool::reload_controller_code");
                    }

//
// Invalidate motor
//

                    vct_ite ct_fica = ct->ite_ctrl_class;
                    {
                        AutoPoolLock lo((*ct_fica)->get_mon());
                        motor->ctrl_offline();
                        motor->set_ctrl(NULL);
                    }
                }

//
// Memorize some motor info
//

                Pool::ObjBkp obj_bkp;
                obj_bkp.old_ctrl = motor->get_controller();
                obj_bkp.idx = motor_pool.id;
                obj_bkp.dist = distance(first_mot, elem_it);
                obj_bkp.type = MOTOR_CTRL;
                obj_bkp.listeners = motor_pool.get_pool_elem_listeners();
                objs.push_back(obj_bkp);
                break;
            }
        }
    }
}

//------------------------------------------------------------------------------
// Pool::find_and_invalidate_pseudo_motor
//
void Pool::find_and_invalidate_pseudo_motor(vector<CtrlBkp> &ctrls,
                                            vector<ObjBkp> &objs)
{
    PoolElementTypeIt beg = element_types.lower_bound(PSEUDO_MOTOR_ELEM);
    
    for (PoolElementTypeIt elem_it = beg;
         elem_it != element_types.upper_bound(PSEUDO_MOTOR_ELEM); ++elem_it)
    {
        PseudoMotorPool &pmp = get_pseudo_motor(elem_it->second);

        vector<Pool::CtrlBkp>::iterator ite;
        for (ite = ctrls.begin();ite != ctrls.end();++ite)
        {
            if (pmp.get_ctrl_id() == ite->idx)
            {
                PoolElementTypeIt ctrl_it, ctrl_beg, ctrl_end;
                get_all_controller(ctrl_beg, ctrl_end);
                ctrl_it = ctrl_beg;
                advance(ctrl_it, ite->dist);
                ControllerPool *ct = &get_controller(ctrl_it->second);
                
                PseudoMotor_ns::PseudoMotor *pm_dev = get_pseudo_motor_device(pmp);
//
// Get pseudo motor device monitor to be sure that nobody else will do something
// on the pseudo motor. As the monitor is re-entrant, it is still possible for
// us to call its state command
//

                if (ct->ctrl_class_built == true)
                {   
                    Tango::AutoTangoMonitor atm(pm_dev);
                    Tango::DevState sta;
                    try
                    {
                        sta = get_element_proxy(pmp)->state();
                    }
                    catch(Tango::DevFailed &e)
                    {
                        sta = Tango::UNKNOWN;
                    }

//
// If one pseudo motor is moving, refuse to reload controller code. In this
// code, reset all pseudo motor previously found to valid controller code
//

                    if (sta == Tango::MOVING)
                    {
                        restore_ctrl_obj((vector<Pool::CtrlBkp> *)NULL,&objs);

                        TangoSys_OMemStream o;
                        o << "Pseudo Motor " << pmp.name << " (";
                        o << pmp.get_full_name() << ") is moving. ";
                        o << "It is not allowed to reload controller code while"
                             " a pseudo motor is moving" << ends;

                        Tango::Except::throw_exception(
                            (const char *)"Pool_CantUnloadController",o.str(),
                            (const char *)"Pool::reload_controller_code");
                    }

//
// Invalidate pseudo motor
//

                    vct_ite ct_fica = ct->ite_ctrl_class;
                    {
                        AutoPoolLock lo((*ct_fica)->get_mon());
                        pm_dev->ctrl_offline();
                        pm_dev->set_ctrl(NULL);
                    }
                }

//
// Memorize some pseudo motor info
//

                Pool::ObjBkp obj_bkp;
                obj_bkp.old_ctrl = pm_dev->get_controller();
                obj_bkp.idx = pmp.get_id();
                obj_bkp.dist = distance(beg, elem_it);
                obj_bkp.type = PSEUDO_MOTOR_CTRL;
                obj_bkp.listeners = pmp.get_pool_elem_listeners();
                objs.push_back(obj_bkp);
                break;
            }
        }
    }
}

//------------------------------------------------------------------------------
// Pool::find_and_invalidate_pseudo_counter
//
void Pool::find_and_invalidate_pseudo_counter(vector<CtrlBkp> &ctrls,
                                            vector<ObjBkp> &objs)
{
    PoolElementTypeIt beg = element_types.lower_bound(PSEUDO_MOTOR_ELEM);
    
    for (PoolElementTypeIt elem_it = beg;
         elem_it != element_types.upper_bound(PSEUDO_COUNTER_ELEM); ++elem_it)
    {
        PseudoCounterPool &pcp = get_pseudo_counter(elem_it->second);

        vector<Pool::CtrlBkp>::iterator ite;
        for (ite = ctrls.begin();ite != ctrls.end();++ite)
        {
            if (pcp.get_ctrl_id() == ite->idx)
            {

                PoolElementTypeIt ctrl_it, ctrl_beg, ctrl_end;
                get_all_controller(ctrl_beg, ctrl_end);
                ctrl_it = ctrl_beg;
                advance(ctrl_it, ite->dist);
                ControllerPool *ct = &get_controller(ctrl_it->second);
                
                PseudoCounter_ns::PseudoCounter *pc_dev = get_pseudo_counter_device(pcp);
//
// Get pseudo motor device monitor to be sure that nobody else will do something
// on the pseudo motor. As the monitor is re-entrant, it is still possible for
// us to call its state command
//

                if (ct->ctrl_class_built == true)
                {
                    Tango::AutoTangoMonitor atm(pc_dev);
                    Tango::DevState sta;
                    try
                    {
                        sta = get_element_proxy(pcp)->state();
                    }
                    catch(Tango::DevFailed &e)
                    {
                        sta = Tango::UNKNOWN;
                    }

//
// If one pseudo counter is counting, refuse to reload controller code. In this
// code, reset all pseudo counter previously found to valid controller code
//

                    if (sta == Tango::MOVING)
                    {
                        restore_ctrl_obj((vector<Pool::CtrlBkp> *)NULL,&objs);

                        TangoSys_OMemStream o;
                        o << "Pseudo Counter " << pcp.name << " (";
                        o << pcp.get_full_name() << ") is moving. ";
                        o << "It is not allowed to reload controller code while"
                             " a pseudo counter is counting" << ends;

                        Tango::Except::throw_exception(
                            (const char *)"Pool_CantUnloadController",o.str(),
                            (const char *)"Pool::reload_controller_code");
                    }

//
// Invalidate pseudo counter
//

                    vct_ite ct_fica = ct->ite_ctrl_class;
                    {
                        AutoPoolLock lo((*ct_fica)->get_mon());
                        pc_dev->ctrl_offline();
                        pc_dev->set_ctrl(NULL);
                    }
                }

//
// Memorize some pseudo counter info
//

                Pool::ObjBkp obj_bkp;
                obj_bkp.old_ctrl = pc_dev->get_controller();
                obj_bkp.idx = pcp.get_id();
                obj_bkp.dist = distance(beg, elem_it);
                obj_bkp.type = PSEUDO_COUNTER_CTRL;
                obj_bkp.listeners = pcp.get_pool_elem_listeners();
                objs.push_back(obj_bkp);
                break;
            }
        }
    }
}

//------------------------------------------------------------------------------
// Pool::find_and_invalidate_ct
//
void Pool::find_and_invalidate_ct(vector<CtrlBkp> &ctrls,vector<ObjBkp> &objs)
{
    PoolElementTypeIt beg = element_types.lower_bound(COTI_ELEM);
    
    for (PoolElementTypeIt elem_it = beg;
         elem_it != element_types.upper_bound(COTI_ELEM); ++elem_it)
    {
        CTExpChannelPool &ct_pool = get_countertimer(elem_it->second);
        
        vector<Pool::CtrlBkp>::iterator ite;
        for (ite = ctrls.begin();ite != ctrls.end();++ite)
        {
            if (ct_pool.get_ctrl_id() == ite->idx)
            {
                PoolElementTypeIt ctrl_it, ctrl_beg, ctrl_end;
                get_all_controller(ctrl_beg, ctrl_end);
                ctrl_it = ctrl_beg;
                advance(ctrl_it, ite->dist);
                ControllerPool *ct = &get_controller(ctrl_it->second);
                
                CTExpChannel_ns::CTExpChannel *ct_dev = 
                    get_countertimer_device(ct_pool);
                
//
// Get CT device monitor to be sure that nobody else will do something
// on the CT. As the monitor is re-entrant, it is still possible for
// us to call its state command
//
                if (ct->ctrl_class_built == true)
                {
                    Tango::AutoTangoMonitor atm(ct_dev);
                    Tango::DevState sta;
                    try
                    {
                        sta = get_element_proxy(ct_pool)->state();
                    }
                    catch(Tango::DevFailed &e)
                    {
                        sta = Tango::UNKNOWN;
                    }

//
// If one CT is moving, refuse to reload controller code
// in this code, reset all CT previously found to valid controller code
//

                    if (sta == Tango::MOVING)
                    {
                        restore_ctrl_obj((vector<Pool::CtrlBkp> *)NULL,&objs);

                        TangoSys_OMemStream o;
                        o << "CounterTimer " << ct_pool.name << " (";
                        o << ct_pool.get_full_name() << ") is counting. ";
                        o << "It is not allowed to reload controller code while"
                             " a CounterTimer is counting" << ends;

                        Tango::Except::throw_exception(
                            (const char *)"Pool_CantUnloadController",o.str(),
                            (const char *)"Pool::reload_controller_code");
                    }

//
// Invalidate C/T
//

                    vct_ite ct_fica = ct->ite_ctrl_class;
                    {
                        AutoPoolLock lo((*ct_fica)->get_mon());
                        ct_dev->ctrl_offline();
                        ct_dev->set_ctrl(NULL);
                    }
                }

//
// Memorize some C/T info
//

                Pool::ObjBkp obj_bkp;
                obj_bkp.old_ctrl = ct_dev->get_controller();
                obj_bkp.idx = ct_pool.get_id();
                obj_bkp.dist = distance(beg, elem_it);
                obj_bkp.type = COTI_CTRL;
                obj_bkp.listeners = ct_pool.get_pool_elem_listeners();
                objs.push_back(obj_bkp);

                break;
            }
        }
    }
}

//------------------------------------------------------------------------------
// Pool::find_and_invalidate_zerod
//
void Pool::find_and_invalidate_zerod(vector<CtrlBkp> &ctrls,
                                     vector<ObjBkp> &objs)
{
    PoolElementTypeIt beg = element_types.lower_bound(ZEROD_ELEM);
    
    for (PoolElementTypeIt elem_it = beg;
         elem_it != element_types.upper_bound(ZEROD_ELEM); ++elem_it)
    {
        ZeroDExpChannelPool &zerod_pool = get_zerod(elem_it->second);
        
        vector<Pool::CtrlBkp>::iterator ite;
        for (ite = ctrls.begin();ite != ctrls.end();++ite)
        {
            if (zerod_pool.get_ctrl_id() == ite->idx)
            {

                PoolElementTypeIt ctrl_it, ctrl_beg, ctrl_end;
                get_all_controller(ctrl_beg, ctrl_end);
                ctrl_it = ctrl_beg;
                advance(ctrl_it, ite->dist);
                ControllerPool *ct = &get_controller(ctrl_it->second);
                
                ZeroDExpChannel_ns::ZeroDExpChannel *zerod_dev = 
                    get_zerod_device(zerod_pool);
                
//
// Get ZeroD device monitor to be sure that nobody else will do something
// on the ZeroD. As the monitor is re-entrant, it is still possible for
// us to call its state command
//

                if (ct->ctrl_class_built == true)
                {
                    Tango::AutoTangoMonitor atm(zerod_dev);
                    Tango::DevState sta;
                    try
                    {
                        sta = get_element_proxy(zerod_pool)->state();
                    }
                    catch(Tango::DevFailed &e)
                    {
                        sta = Tango::UNKNOWN;
                    }

//
// If one channel is acquiring data, refuse to reload controller code
// in this code, reset all channel previously found to valid controller code
//

                    if (sta == Tango::MOVING)
                    {
                        restore_ctrl_obj((vector<Pool::CtrlBkp> *)NULL,&objs);

                        TangoSys_OMemStream o;
                        o << "Experiment Channel " << zerod_pool.name << " (";
                        o << zerod_pool.get_full_name() << ") is acquiring data. ";
                        o << "It is not allowed to reload controller code while "
                             "a channel is acquiring" << ends;

                        Tango::Except::throw_exception(
                            (const char *)"Pool_CantUnloadController",o.str(),
                            (const char *)"Pool::reload_controller_code");
                    }

//
// Invalidate channel
//

                    vct_ite ct_fica = ct->ite_ctrl_class;
                    {
                        AutoPoolLock lo((*ct_fica)->get_mon());
                        zerod_dev->ctrl_offline();
                        zerod_dev->set_ctrl(NULL);
                    }
                }

//
// Memorize some Channel info
//

                Pool::ObjBkp obj_bkp;
                obj_bkp.old_ctrl = zerod_dev->get_controller();
                obj_bkp.idx = zerod_pool.get_id();
                obj_bkp.dist = distance(beg, elem_it);
                obj_bkp.type = ZEROD_CTRL;
                obj_bkp.listeners = zerod_pool.get_pool_elem_listeners();
                objs.push_back(obj_bkp);

                break;
            }
        }
    }
}

//------------------------------------------------------------------------------
// Pool::find_and_invalidate_oned
//
void Pool::find_and_invalidate_oned(vector<CtrlBkp> &ctrls,
                                     vector<ObjBkp> &objs)
{		
    PoolElementTypeIt beg = element_types.lower_bound(ONED_ELEM);
    
    for (PoolElementTypeIt elem_it = beg;
         elem_it != element_types.upper_bound(ONED_ELEM); ++elem_it)
    {
        OneDExpChannelPool &oned_pool = get_oned(elem_it->second);
    
        vector<Pool::CtrlBkp>::iterator ite;
        for (ite = ctrls.begin();ite != ctrls.end();++ite)
        {
            if (oned_pool.get_ctrl_id() == ite->idx)
            {

                PoolElementTypeIt ctrl_it, ctrl_beg, ctrl_end;
                get_all_controller(ctrl_beg, ctrl_end);
                ctrl_it = ctrl_beg;
                advance(ctrl_it, ite->dist);
                ControllerPool *ct = &get_controller(ctrl_it->second);
                
                OneDExpChannel_ns::OneDExpChannel *oned_dev = get_oned_device(oned_pool);
                
//
// Get OneD device monitor to be sure that nobody else will do something
// on the OneD. As the monitor is re-entrant, it is still possible for
// us to call its state command
//

                if (ct->ctrl_class_built == true)
                {
                    Tango::AutoTangoMonitor atm(oned_dev);
                    Tango::DevState sta;
                    try
                    {
                        sta = get_element_proxy(oned_pool)->state();
                    }
                    catch(Tango::DevFailed &e)
                    {
                        sta = Tango::UNKNOWN;
                    }
                    
//
// If one channel is acquiring data, refuse to reload controller code
// in this code, reset all channel previously found to valid controller code
//
                    
                    if (sta == Tango::MOVING)
                    {
                        restore_ctrl_obj((vector<Pool::CtrlBkp> *)NULL,&objs);
                    
                        TangoSys_OMemStream o;
                        o << "Experiment Channel " << oned_pool.name << " (";
                        o << oned_pool.get_full_name() << ") is acquiring data. ";
                        o << "It is not allowed to reload controller code while "
                             "a channel is acquiring" << ends;
            
                        Tango::Except::throw_exception(
                            (const char *)"Pool_CantUnloadController",o.str(),
                            (const char *)"Pool::reload_controller_code");
                    }

//
// Invalidate channel
//
                    
                    vct_ite ct_fica = ct->ite_ctrl_class; 
                    {
                        AutoPoolLock lo((*ct_fica)->get_mon());
                        oned_dev->ctrl_offline();
                        oned_dev->set_ctrl(NULL);
                    }
                }
                    
//
// Memorize some Channel info
//

                Pool::ObjBkp obj_bkp;
                obj_bkp.old_ctrl = oned_dev->get_controller();
                obj_bkp.idx = oned_pool.get_id();
                obj_bkp.dist = distance(beg, elem_it);
                obj_bkp.type = ONED_CTRL;
                obj_bkp.listeners = oned_pool.get_pool_elem_listeners();
                objs.push_back(obj_bkp);
                
                break;
            }
        }
    }
}

//------------------------------------------------------------------------------
// Pool::find_and_invalidate_twod
//
void Pool::find_and_invalidate_twod(vector<CtrlBkp> &ctrls,
                                     vector<ObjBkp> &objs)
{		
    PoolElementTypeIt beg = element_types.lower_bound(TWOD_ELEM);
    
    for (PoolElementTypeIt elem_it = beg;
         elem_it != element_types.upper_bound(TWOD_ELEM); ++elem_it)
    {
        TwoDExpChannelPool &twod_pool = get_twod(elem_it->second);
    
        vector<Pool::CtrlBkp>::iterator ite;
        for (ite = ctrls.begin();ite != ctrls.end();++ite)
        {
            if (twod_pool.get_ctrl_id() == ite->idx)
            {

                PoolElementTypeIt ctrl_it, ctrl_beg, ctrl_end;
                get_all_controller(ctrl_beg, ctrl_end);
                ctrl_it = ctrl_beg;
                advance(ctrl_it, ite->dist);
                ControllerPool *ct = &get_controller(ctrl_it->second);
                
                TwoDExpChannel_ns::TwoDExpChannel *twod_dev = get_twod_device(twod_pool);
                
//
// Get TwoD device monitor to be sure that nobody else will do something
// on the OneD. As the monitor is re-entrant, it is still possible for
// us to call its state command
//

                if (ct->ctrl_class_built == true)
                {
                    Tango::AutoTangoMonitor atm(twod_dev);
                    Tango::DevState sta;
                    try
                    {
                        sta = get_element_proxy(twod_pool)->state();
                    }
                    catch(Tango::DevFailed &e)
                    {
                        sta = Tango::UNKNOWN;
                    }
                    
//
// If one channel is acquiring data, refuse to reload controller code
// in this code, reset all channel previously found to valid controller code
//
                    
                    if (sta == Tango::MOVING)
                    {
                        restore_ctrl_obj((vector<Pool::CtrlBkp> *)NULL,&objs);
                    
                        TangoSys_OMemStream o;
                        o << "Experiment Channel " << twod_pool.name << " (";
                        o << twod_pool.get_full_name() << ") is acquiring data. ";
                        o << "It is not allowed to reload controller code while "
                             "a channel is acquiring" << ends;
            
                        Tango::Except::throw_exception(
                            (const char *)"Pool_CantUnloadController",o.str(),
                            (const char *)"Pool::reload_controller_code");						
                    }

//
// Invalidate channel
//
                    
                    vct_ite ct_fica = ct->ite_ctrl_class; 
                    {
                        AutoPoolLock lo((*ct_fica)->get_mon());
                        twod_dev->ctrl_offline();
                        twod_dev->set_ctrl(NULL);
                    }
                }
                    
//
// Memorize some Channel info
//

                Pool::ObjBkp obj_bkp;
                obj_bkp.old_ctrl = twod_dev->get_controller();
                obj_bkp.idx = twod_pool.get_id();
                obj_bkp.dist = distance(beg, elem_it);
                obj_bkp.type = TWOD_CTRL;
                obj_bkp.listeners = twod_pool.get_pool_elem_listeners();
                objs.push_back(obj_bkp);
                
                break;
            }
        }
    }
}

//------------------------------------------------------------------------------
// Pool::find_and_invalidate_comch
//
void Pool::find_and_invalidate_comch(vector<CtrlBkp> &ctrls, vector<ObjBkp> &objs)
{
    PoolElementTypeIt beg = element_types.lower_bound(COM_ELEM);
    
    for (PoolElementTypeIt elem_it = beg;
         elem_it != element_types.upper_bound(COM_ELEM); ++elem_it)
    {
        CommunicationChannelPool &cc_pool = get_communication_channel(elem_it->second);

        vector<Pool::CtrlBkp>::iterator ite;
        for (ite = ctrls.begin();ite != ctrls.end();++ite)
        {
            if (cc_pool.get_ctrl_id() == ite->idx)
            {

                PoolElementTypeIt ctrl_it, ctrl_beg, ctrl_end;
                get_all_controller(ctrl_beg, ctrl_end);
                ctrl_it = ctrl_beg;
                advance(ctrl_it, ite->dist);
                ControllerPool *ct = &get_controller(ctrl_it->second);
                
                CommunicationChannel_ns::CommunicationChannel *comch_dev = 
                    get_communication_channel_device(cc_pool);
                
//
// Get com device monitor to be sure that nobody else will do something
// on the com. As the monitor is re-entrant, it is still possible for
// us to call its state command
//

                if (ct->ctrl_class_built == true)
                {
                    Tango::AutoTangoMonitor atm(comch_dev);
                    Tango::DevState sta;
                    try
                    {
                        sta = get_element_proxy(cc_pool)->state();
                    }
                    catch(Tango::DevFailed &e)
                    {
                        sta = Tango::UNKNOWN;
                    }

//
// Invalidate com com channel
//

                    vct_ite ct_fica = ct->ite_ctrl_class;
                    {
                        AutoPoolLock lo((*ct_fica)->get_mon());
                        comch_dev->ctrl_offline();
                        comch_dev->set_ctrl(NULL);
                    }
                }

//
// Memorize some Com channel info
//

                Pool::ObjBkp obj_bkp;
                obj_bkp.old_ctrl = comch_dev->get_controller();
                obj_bkp.idx = cc_pool.get_id();
                obj_bkp.dist = distance(beg, elem_it);
                obj_bkp.type = COM_CTRL;
                obj_bkp.listeners = cc_pool.get_pool_elem_listeners();
                objs.push_back(obj_bkp);

                break;
            }
        }
    }
}

//------------------------------------------------------------------------------
// Pool::find_and_invalidate_ioregister
//
void Pool::find_and_invalidate_ioregister(vector<CtrlBkp> &ctrls,vector<ObjBkp> &objs)
{
    PoolElementTypeIt beg = element_types.lower_bound(IOREGISTER_ELEM);
    
    for (PoolElementTypeIt elem_it = beg;
         elem_it != element_types.upper_bound(IOREGISTER_ELEM); ++elem_it)
    {
        IORegisterPool &ior_pool = get_ioregister(elem_it->second);
        
        vector<Pool::CtrlBkp>::iterator ite;
        for (ite = ctrls.begin();ite != ctrls.end();++ite)
        {
            if (ior_pool.get_ctrl_id() == ite->idx)
            {

                PoolElementTypeIt ctrl_it, ctrl_beg, ctrl_end;
                get_all_controller(ctrl_beg, ctrl_end);
                ctrl_it = ctrl_beg;
                advance(ctrl_it, ite->dist);
                ControllerPool *ct = &get_controller(ctrl_it->second);

                IORegister_ns::IORegister *ior_dev = get_ioregister_device(ior_pool);
//
// Get ioregister device monitor to be sure that nobody else will do something
// on the ioregister. As the monitor is re-entrant, it is still possible for
// us to call its state command
//

                if (ct->ctrl_class_built == true)
                {
                    Tango::AutoTangoMonitor atm(ior_dev);
                    Tango::DevState sta;
                    try
                    {
                        sta = get_element_proxy(ior_pool)->state();
                    }
                    catch(Tango::DevFailed &e)
                    {
                        sta = Tango::UNKNOWN;
                    }

//
// Invalidate ioregister
//

                    vct_ite ct_fica = ct->ite_ctrl_class;
                    {
                        AutoPoolLock lo((*ct_fica)->get_mon());
                        ior_dev->ctrl_offline();
                        ior_dev->set_ctrl(NULL);
                    }
                }

//
// Memorize some Com channel info
//

                Pool::ObjBkp obj_bkp;
                obj_bkp.old_ctrl = ior_dev->get_controller();
                obj_bkp.idx = ior_pool.get_id();
                obj_bkp.dist = distance(beg, elem_it);
                obj_bkp.type = IOREGISTER_CTRL;
                obj_bkp.listeners = ior_pool.get_pool_elem_listeners();
                objs.push_back(obj_bkp);

                break;
            }
        }
    }
}

//------------------------------------------------------------------------------
// Pool::restore_motor
//
void Pool::restore_motor(vector<ObjBkp> &mots,
                         ControllerPool &ctl,
                         vector<Pool::CtrlBkp>::iterator &ite)
{
    list<IPoolElementListener*> listeners;
    vector<Pool::ObjBkp>::iterator mot_ite;

    for (mot_ite = mots.begin();mot_ite != mots.end();++mot_ite)
    {
        PoolElementTypeIt it = element_types.lower_bound(MOTOR_ELEM);
        advance(it, mot_ite->dist);
        MotorPool *mtl = &get_physical_motor(it->second);

        if (ctl.id == mtl->get_ctrl_id())
        {
            vct_ite ct_fica = ctl.ite_ctrl_class;
            {
                AutoPoolLock lo((*ct_fica)->get_mon());
                Motor_ns::Motor *mtl_dev = get_motor_device(*mtl);
                mtl_dev->ctrl_online();

                {
                    Tango::AutoTangoMonitor atm(mtl_dev);
                    ElementId m_id = mtl->id;
                    get_element_proxy(*mtl)->command_inout("Init");
                    if (ite->old_fica_built == false)
                    {
                        Motor_ns::Motor *mot_dev = get_motor_device(m_id);
                        mot_dev->create_dyn_attr();
                        mot_dev->remove_unwanted_dyn_attr_from_device();
                    }
                }
            }

            MotorPool &mot_in_pool = get_physical_motor(mot_ite->idx);
//
// Restore the listeners
//
            mot_in_pool.set_pool_elem_listeners(mot_ite->listeners);

//
// Inform the listeners that the motor changed structure
//
            if(mot_in_pool.has_listeners())
            {
                PoolElementEvent evt(ElementStructureChange,&mot_in_pool);
                mot_in_pool.fire_pool_elem_change(&evt);
            }
        }
    }
}

//------------------------------------------------------------------------------
// Pool::restore_pseudo_motor
//
void Pool::restore_pseudo_motor(vector<ObjBkp> &mots,
                                ControllerPool &ctl,
                                vector<Pool::CtrlBkp>::iterator &ite)
{
    list<IPoolElementListener*> listeners;
    vector<Pool::ObjBkp>::iterator mot_ite;
    for (mot_ite = mots.begin();mot_ite != mots.end();++mot_ite)
    {
        PoolElementTypeIt mtl = element_types.lower_bound(PSEUDO_MOTOR_ELEM);
        advance(mtl, mot_ite->dist);

        PseudoMotorPool &pmp = get_pseudo_motor(mtl->second);

        if (ctl.id == pmp.get_ctrl_id())
        {
            vct_ite ct_fica = ctl.ite_ctrl_class;
            {
                PseudoMotor_ns::PseudoMotor *mtl_dev = 
                    get_pseudo_motor_device(mtl->second);
                
                AutoPoolLock lo((*ct_fica)->get_mon());

                mtl_dev->ctrl_online();

                {
                    Tango::AutoTangoMonitor atm(mtl_dev);
                    ElementId m_id = pmp.get_id();
                    get_element_proxy(m_id)->command_inout("Init");
                    if (ite->old_fica_built == false)
                    {
                        PseudoMotor_ns::PseudoMotor *pm_dev = 
                            get_pseudo_motor_device(m_id);
                        pm_dev->create_dyn_attr();
                        pm_dev->remove_unwanted_dyn_attr_from_device();
                    }
                }
            }

            PseudoMotorPool &mot_in_pool = get_pseudo_motor(mot_ite->idx);
//
// Restore the listeners
//
            mot_in_pool.set_pool_elem_listeners(mot_ite->listeners);

//
// Inform the listeners that the motor changed structure
//
            if(mot_in_pool.has_listeners())
            {
                PoolElementEvent evt(ElementStructureChange,&mot_in_pool);
                mot_in_pool.fire_pool_elem_change(&evt);
            }
        }
    }
}

//------------------------------------------------------------------------------
// Pool::restore_pseudo_counter
//
void Pool::restore_pseudo_counter(vector<ObjBkp> &pcs,
                                ControllerPool &ctl,
                                vector<Pool::CtrlBkp>::iterator &ite)
{
    list<IPoolElementListener*> listeners;
    vector<Pool::ObjBkp>::iterator co_ite;
    for (co_ite = pcs.begin();co_ite != pcs.end();++co_ite)
    {
        PoolElementTypeIt mtl = element_types.lower_bound(PSEUDO_MOTOR_ELEM);
        advance(mtl, co_ite->dist);

        PseudoCounterPool &pcp = get_pseudo_counter(mtl->second);

        if (ctl.id == pcp.get_ctrl_id())
        {
            vct_ite ct_fica = ctl.ite_ctrl_class;
            {
                PseudoCounter_ns::PseudoCounter *pcl_dev = 
                    get_pseudo_counter_device(pcp);
                
                AutoPoolLock lo((*ct_fica)->get_mon());
                
                pcl_dev->ctrl_online();

                {
                    Tango::AutoTangoMonitor atm(pcl_dev);
                    ElementId pc_id = pcp.get_id();
                    get_element_proxy(pc_id)->command_inout("Init");
                    if (ite->old_fica_built == false)
                    {
                        PseudoCounter_ns::PseudoCounter *pc_dev = 
                            get_pseudo_counter_device(pc_id);
                        pc_dev->create_dyn_attr();
                        pc_dev->remove_unwanted_dyn_attr_from_device();
                    }
                }
            }

            PseudoCounterPool &pc_in_pool = get_pseudo_counter(co_ite->idx);
//
// Restore the listeners
//
            pc_in_pool.set_pool_elem_listeners(co_ite->listeners);

//
// Inform the listeners that the pseudo counter changed structure
//
            if(pc_in_pool.has_listeners())
            {
                PoolElementEvent evt(ElementStructureChange, &pc_in_pool);
                pc_in_pool.fire_pool_elem_change(&evt);
            }
        }
    }
}

//------------------------------------------------------------------------------
// Pool::restore_ct
//
void Pool::restore_ct(vector<ObjBkp> &cts, ControllerPool &ctl,
                      vector<Pool::CtrlBkp>::iterator &ite)
{
    list<IPoolElementListener*> listeners;
    vector<Pool::ObjBkp>::iterator ct_ite;
    for (ct_ite = cts.begin();ct_ite != cts.end();++ct_ite)
    {
        PoolElementTypeIt mtl = element_types.lower_bound(COTI_ELEM);
        advance(mtl, ct_ite->dist);

        CTExpChannelPool &ct_pool = get_countertimer(mtl->second);

        if (ctl.id == ct_pool.get_ctrl_id())
        {
            vct_ite ct_fica = ctl.ite_ctrl_class;
            {
                CTExpChannel_ns::CTExpChannel *mtl_dev = 
                    get_countertimer_device(ct_pool);
                
                AutoPoolLock lo((*ct_fica)->get_mon());
                    
                mtl_dev->ctrl_online();

                {
                    Tango::AutoTangoMonitor atm(mtl_dev);
                    ElementId m_id = ct_pool.get_id();
                    get_element_proxy(m_id)->command_inout("Init");
                    if (ite->old_fica_built == false)
                    {
                        CTExpChannel_ns::CTExpChannel *ct_dev = 
                            get_countertimer_device(m_id);
                        ct_dev->create_dyn_attr();
                        ct_dev->remove_unwanted_dyn_attr_from_device();
                    }
                }
            }
            PoolElement *ct_in_pool = get_element(ct_ite->idx);
//
// Restore the listeners
//
            ct_in_pool->set_pool_elem_listeners(ct_ite->listeners);

//
// Inform the listeners that the channel changed structure
//
            if(ct_in_pool->has_listeners())
            {
                PoolElementEvent evt(ElementStructureChange, ct_in_pool);
                ct_in_pool->fire_pool_elem_change(&evt);
            }
        }
    }
}

//------------------------------------------------------------------------------
// Pool::restore_zerod
//
void Pool::restore_zerod(vector<ObjBkp> &cts,
                         ControllerPool &ctl,
                         vector<Pool::CtrlBkp>::iterator &ite)
{
    vector<Pool::ObjBkp>::iterator zerod_ite;
    for (zerod_ite = cts.begin();zerod_ite != cts.end();++zerod_ite)
    {
        PoolElementTypeIt mtl = element_types.lower_bound(ZEROD_ELEM);
        advance(mtl, zerod_ite->dist);

        ZeroDExpChannelPool &zerod_pool = get_zerod(mtl->second);

        if (ctl.id == zerod_pool.get_ctrl_id())
        {
            vct_ite ct_fica = ctl.ite_ctrl_class;
            {
                ZeroDExpChannel_ns::ZeroDExpChannel *mtl_dev = 
                    get_zerod_device(zerod_pool);
                    
                AutoPoolLock lo((*ct_fica)->get_mon());
                
                mtl_dev->ctrl_online();

                {
                    Tango::AutoTangoMonitor atm(mtl_dev);
                    ElementId m_id = zerod_pool.get_id();
                    get_element_proxy(zerod_pool)->command_inout("Init");
                    if (ite->old_fica_built == false)
                    {
                        ZeroDExpChannel_ns::ZeroDExpChannel *zerod_dev = 
                            get_zerod_device(m_id);
                        zerod_dev->create_dyn_attr();
                        zerod_dev->remove_unwanted_dyn_attr_from_device();
                    }
                }
            }
            PoolElement *zerod_in_pool = get_element(zerod_ite->idx);

//
// Restore the listeners
//
            zerod_in_pool->set_pool_elem_listeners(zerod_ite->listeners);

//
// Inform the listeners that the channel changed structure
//
            if(zerod_in_pool->has_listeners())
            {
                PoolElementEvent evt(ElementStructureChange, zerod_in_pool);
                zerod_in_pool->fire_pool_elem_change(&evt);
            }
        }
    }
}

//------------------------------------------------------------------------------
// Pool::restore_oned
//
void Pool::restore_oned(vector<ObjBkp> &cts,
                         ControllerPool &ctl,
                         vector<Pool::CtrlBkp>::iterator &ite)
{
    vector<Pool::ObjBkp>::iterator oned_ite;
    for (oned_ite = cts.begin();oned_ite != cts.end();++oned_ite)
    {
        PoolElementTypeIt mtl = element_types.lower_bound(ONED_ELEM);
        advance(mtl, oned_ite->dist);

        OneDExpChannelPool &oned_pool = get_oned(mtl->second);
        
        if (ctl.id == oned_pool.get_ctrl_id())
        {
            vct_ite ct_fica = ctl.ite_ctrl_class; 
            {
                OneDExpChannel_ns::OneDExpChannel *mtl_dev = 
                    get_oned_device(oned_pool);
                
                AutoPoolLock lo((*ct_fica)->get_mon());
                
                mtl_dev->ctrl_online();
                
                {
                    Tango::AutoTangoMonitor atm(mtl_dev);
                    ElementId m_id = oned_pool.get_id();
                    get_element_proxy(m_id)->command_inout("Init");
                    if (ite->old_fica_built == false)
                    {
                        OneDExpChannel_ns::OneDExpChannel *oned_dev = 
                            get_oned_device(m_id);
                        oned_dev->create_dyn_attr();
                        oned_dev->remove_unwanted_dyn_attr_from_device();
                    }
                }								
            }
            PoolElement *oned_in_pool = get_element(oned_ite->idx);
//
// Restore the listeners
//
            oned_in_pool->set_pool_elem_listeners(oned_ite->listeners);
            
//
// Inform the listeners that the channel changed structure
//			
            if(oned_in_pool->has_listeners())
            {
                PoolElementEvent evt(ElementStructureChange, oned_in_pool);
                oned_in_pool->fire_pool_elem_change(&evt);
            }			
        }
    }
}	

//------------------------------------------------------------------------------
// Pool::restore_twod
//
void Pool::restore_twod(vector<ObjBkp> &cts,
                         ControllerPool &ctl,
                         vector<Pool::CtrlBkp>::iterator &ite)
{
    vector<Pool::ObjBkp>::iterator twod_ite;
    for (twod_ite = cts.begin();twod_ite != cts.end();++twod_ite)
    {
        PoolElementTypeIt mtl = element_types.lower_bound(TWOD_ELEM);
        advance(mtl, twod_ite->dist);

        TwoDExpChannelPool &twod_pool = get_twod(mtl->second);
        
        if (ctl.id == twod_pool.get_ctrl_id())
        {
            vct_ite ct_fica = ctl.ite_ctrl_class; 
            {
                TwoDExpChannel_ns::TwoDExpChannel *mtl_dev = 
                    get_twod_device(twod_pool);
                
                AutoPoolLock lo((*ct_fica)->get_mon());
                
                mtl_dev->ctrl_online();
                
                {
                    Tango::AutoTangoMonitor atm(mtl_dev);
                    ElementId m_id = twod_pool.get_id();
                    get_element_proxy(m_id)->command_inout("Init");
                    if (ite->old_fica_built == false)
                    {
                        TwoDExpChannel_ns::TwoDExpChannel *twod_dev = 
                            get_twod_device(m_id);
                        twod_dev->create_dyn_attr();
                        twod_dev->remove_unwanted_dyn_attr_from_device();
                    }
                }								
            }
            PoolElement *twod_in_pool = get_element(twod_ite->idx);
//
// Restore the listeners
//
            twod_in_pool->set_pool_elem_listeners(twod_ite->listeners);
            
//
// Inform the listeners that the channel changed structure
//			
            if(twod_in_pool->has_listeners())
            {
                PoolElementEvent evt(ElementStructureChange, twod_in_pool);
                twod_in_pool->fire_pool_elem_change(&evt);
            }			
        }
    }
}	

//------------------------------------------------------------------------------
// Pool::restore_comch
//
void Pool::restore_comch(vector<ObjBkp> &cts,
                         ControllerPool &ctl,
                         vector<Pool::CtrlBkp>::iterator &ite)
{
    list<IPoolElementListener*> listeners;
    vector<Pool::ObjBkp>::iterator comch_ite;
    for (comch_ite = cts.begin();comch_ite != cts.end();++comch_ite)
    {
        PoolElementTypeIt mtl = element_types.lower_bound(COM_ELEM);
        advance(mtl, comch_ite->dist);

        CommunicationChannelPool &cc_pool = get_communication_channel(mtl->second);
    
        if (ctl.id == cc_pool.get_ctrl_id())
        {
            vct_ite ct_fica = ctl.ite_ctrl_class;
            {
                CommunicationChannel_ns::CommunicationChannel *mtl_dev = 
                    get_communication_channel_device(cc_pool);
                
                AutoPoolLock lo((*ct_fica)->get_mon());
                
                mtl_dev->ctrl_online();

                {
                    Tango::AutoTangoMonitor atm(mtl_dev);
                    ElementId m_id = cc_pool.get_id();
                    get_element_proxy(m_id)->command_inout("Init");
                    if (ite->old_fica_built == false)
                    {
                        CommunicationChannel_ns::CommunicationChannel *comch_dev = 
                            get_communication_channel_device(m_id);

                        comch_dev->create_dyn_attr();
                        comch_dev->remove_unwanted_dyn_attr_from_device();
                    }
                }
            }
            PoolElement *comch_in_pool = get_element(comch_ite->idx);
//
// Restore the listeners
//
            comch_in_pool->set_pool_elem_listeners(comch_ite->listeners);

//
// Inform the listeners that the channel changed structure
//
            if(comch_in_pool->has_listeners())
            {
                PoolElementEvent evt(ElementStructureChange, comch_in_pool);
                comch_in_pool->fire_pool_elem_change(&evt);
            }
        }
    }
}

//------------------------------------------------------------------------------
// Pool::restore_ioregister
//
void Pool::restore_ioregister(vector<ObjBkp> &cts,
                         ControllerPool &ctl,
                         vector<Pool::CtrlBkp>::iterator &ite)
{
    list<IPoolElementListener*> listeners;
    vector<Pool::ObjBkp>::iterator ior_ite;
    for (ior_ite = cts.begin();ior_ite != cts.end();++ior_ite)
    {
        PoolElementTypeIt mtl = element_types.lower_bound(IOREGISTER_ELEM);
        advance(mtl, ior_ite->dist);

        IORegisterPool &ior_pool = get_ioregister(mtl->second);

        if (ctl.id == ior_pool.get_ctrl_id())
        {
            vct_ite ct_fica = ctl.ite_ctrl_class;
            {
                IORegister_ns::IORegister *mtl_dev = get_ioregister_device(ior_pool);
                
                AutoPoolLock lo((*ct_fica)->get_mon());
                
                mtl_dev->ctrl_online();

                {
                    Tango::AutoTangoMonitor atm(mtl_dev);
                    ElementId m_id = ior_pool.get_id();
                    get_element_proxy(m_id)->command_inout("Init");
                    if (ite->old_fica_built == false)
                    {
                        IORegister_ns::IORegister *ior_dev = 
                            get_ioregister_device(m_id);
                        ior_dev->create_dyn_attr();
                        ior_dev->remove_unwanted_dyn_attr_from_device();
                    }
                }
            }
            PoolElement *ioregister_in_pool = get_element(ior_ite->idx);
//
// Restore the listeners
//
            ioregister_in_pool->set_pool_elem_listeners(ior_ite->listeners);

//
// Inform the listeners that the channel changed structure
//
            if(ioregister_in_pool->has_listeners())
            {
                PoolElementEvent evt(ElementStructureChange, ioregister_in_pool);
                ioregister_in_pool->fire_pool_elem_change(&evt);
            }
        }
    }
}

//------------------------------------------------------------------------------
// Pool::motor_group_elts_changed
//
void Pool::motor_group_elts_changed(ElementId mg_id)
{
    Tango::AutoTangoMonitor synch(this);
    Tango::Attribute &mgs = dev_attr->get_attr_by_name("MotorGroupList");
    read_MotorGroupList(mgs);
    mgs.fire_change_event();
}

//------------------------------------------------------------------------------
// Pool::measurement_group_elts_changed
//
void Pool::measurement_group_elts_changed(ElementId mg_id)
{
    Tango::AutoTangoMonitor synch(this);
    Tango::Attribute &mgs = dev_attr->get_attr_by_name("MeasurementGroupList");
    read_MeasurementGroupList(mgs);
    mgs.fire_change_event();
}

//------------------------------------------------------------------------------
// Pool::handle_tmp_motor_groups
//
void Pool::handle_tmp_motor_groups()
{
    vector<string> del_vec;
    for (PoolElementTypeIt elem_it = element_types.lower_bound(MOTOR_GROUP_ELEM);
         elem_it != element_types.upper_bound(MOTOR_GROUP_ELEM); ++elem_it)
    {
        ElementId mg_id = elem_it->second;
        MotorGroupPool &mgp = get_motor_group(mg_id);

        MotorGroup_ns::MotorGroup *mg_dev = get_motor_group_device(mg_id);
        if(!mg_dev->is_temporary())
            continue;
//
// First increase the age of the temporary motor group
//
        mg_dev->aging();

//
// If it as been inactive for long enough mark it for deletion
//
        if(mg_dev->get_age() >= tmpElement_MaxInactTime)
        {
            DEBUG_STREAM << "Marking temporary motor group " << mgp.name
                         << " for garbage collection due to inactivity" << endl;
            del_vec.push_back(mgp.name);
        }
    }

//
// Delete all marked temporary motor groups
//
    vector<string>::size_type del_nb = del_vec.size();
    if (del_nb > 0)
    {
        Tango::DeviceProxy tg_pool(device_name);

        for(vector<string>::size_type l = 0; l < del_nb; l++)
        {
            DEBUG_STREAM << "Motor group " << del_vec[l]
                         << " was garbage collected" << endl;
            Tango::DeviceData din, dout;
            din << del_vec[l];
            try
            {
                dout = tg_pool.command_inout("DeleteMotorGroup", din);
            }
            catch(Tango::DevFailed &e)
            {
                WARN_STREAM << "Failed to delete temporary motor group "
                            << del_vec[l] << endl;
            }
        }
    }
}

//------------------------------------------------------------------------------
// Pool::handle_tmp_measurement_groups
//
void Pool::handle_tmp_measurement_groups()
{
    vector<string> del_vec;

    for (PoolElementTypeIt elem_it = element_types.lower_bound(MEASUREMENT_GROUP_ELEM);
         elem_it != element_types.upper_bound(MEASUREMENT_GROUP_ELEM); ++elem_it)
    {
        MeasurementGroupPool &mg_pool = get_measurement_group(elem_it->second);
        MeasurementGroup_ns::MeasurementGroup *mg_dev = 
                                get_measurement_group_device(elem_it->second);
                                
        if(!mg_dev->is_temporary())
            continue;
//
// First increase the age of the temporary motor group
//
        mg_dev->aging();

//
// If it as been inactive for long enough mark it for deletion
//
        if(mg_dev->get_age() >= tmpElement_MaxInactTime)
        {
            DEBUG_STREAM << "Marking temporary measurement group " << mg_pool.name
                         << " for garbage collection due to inactivity" << endl;
            del_vec.push_back(mg_pool.name);
        }
    }

//
// Delete all marked temporary motor groups
//
    vector<string>::size_type del_nb = del_vec.size();
    if (del_nb > 0)
    {
        Tango::DeviceProxy tg_pool(device_name);

        for(vector<string>::size_type l = 0; l < del_nb; l++)
        {
            DEBUG_STREAM << "Measurement group " << del_vec[l]
                         << " was garbage collected" << endl;
            Tango::DeviceData din,dout;
            din << del_vec[l];
            try
            {
                dout = tg_pool.command_inout("DeleteMeasurementGroup", din);
            }
            catch(Tango::DevFailed &e)
            {
                WARN_STREAM << "Failed to delete temporary measurement group "
                            << del_vec[l] << endl;
            }
        }
    }
}

//------------------------------------------------------------------------------
// Pool::build_property_params
//
void Pool::build_property_params(const Tango::DevVarStringArray *argin,
                                 vector<pair<string,string> > & value_pairs,
                                 int start)
{
    for(CORBA::ULong i = start; i < argin->length(); i++)
    {
        string prop_name((*argin)[i++].in());
        string prop_value((*argin)[i].in());
        value_pairs.push_back(make_pair(prop_name,prop_value));
    }
}

//------------------------------------------------------------------------------
// Pool::create_pseudo_motor_ctrl_elems
//
void Pool::create_pseudo_motor_ctrl_elems(string &ctrl_inst_name,
                                          PseudoMotCtrlFiCa *fica,
                                          std::vector<std::string> &pseudo_mot_names,
                                          std::vector<std::string> &mot_names)
{
//----------------------------------------------------
// Check if we don't have already enough pseudo motors
//
    vector<string>::size_type pm_nb = pseudo_mot_names.size();
    vector<string>::size_type m_nb = mot_names.size();
    if (get_pseudo_motor_nb() + pm_nb > MAX_PSEUDO_MOTOR)
    {
        Tango::Except::throw_exception((const char *)"Pool_TooManyPseudoMotor",
                           (const char *)"Too many pseudo motor in your pool",
                           (const char *)"Pool::create_pseudo_motor");
    }

//---------------------------------------------------------
// Check if motors are member of this pool
//

    string mg_name;
    {
        stringstream mg_name_stream;
        mg_name_stream << PSEUDO_MOTOR_MG_PREFIX << "_" << ctrl_inst_name;
        mg_name  = mg_name_stream.str();
    }

    ElemIdVector motor_ids;
    for (vector<string>::size_type ul = 0; ul < m_nb ;ul++)
    {
        string &motor_name = mot_names[ul];
        try
        {
            PoolElement &pe = get_motor(motor_name);
            motor_ids.push_back(pe.get_id());
        }
        catch(Tango::DevFailed &df)
        {
            TangoSys_OMemStream o;
            o << "Motor '" << motor_name << "' is not defined in this pool. ";
            o << "Can't create the pseudo motor controller." << ends;

            Tango::Except::re_throw_exception(df, "Pool_MotorNotDefined", o.str(),
                                              "Pool::create_pseudo_motor");
        }
    }

//
// Build tango names
//
    vector<string> pm_tg_dev_names;

    for (vector<string>::size_type ul = 0; ul < pm_nb ;ul++)
    {
        stringstream role_idx;
        role_idx << ul + 1;
        string dev_name = "pm/" + ctrl_inst_name + "/" + role_idx.str();
        pm_tg_dev_names.push_back(dev_name);
    }

//---------------------------------------------------------
// Check if the Motor Group already exists
//
    bool grp_exists = motor_group_exists(mg_name);

    if(grp_exists)
    {
        DEBUG_STREAM << "Group " << mg_name << " already exists."
                     << " Will use this one" << endl;
    }

//---------------------------------------------------------
// Build Tango device name for Pseudo Motor and Motor Group
//

    Tango::Util	*tg = Tango::Util::instance();

//----------------------------------------------------
// Check if at least one device is already defined in database
// Check by device alias and by Tango device name
//
    Tango::Database *db = tg->get_database();

    Tango::DbDevImportInfo my_device_import;
    bool device_exist = false;
    bool by_alias = false;
    vector<string> existing_pm;

    for (std::vector<std::string>::size_type i = 0; i < pm_nb ;i++)
    {
        bool curr_device_exist = false;
        try
        {
            my_device_import = db->import_device(pseudo_mot_names[i]);
            curr_device_exist = device_exist = true;
            by_alias = true;
            existing_pm.push_back(pseudo_mot_names[i]);
        }
        catch (Tango::DevFailed &e)
        {
            if (::strcmp(e.errors[0].reason.in(),"DB_DeviceNotDefined") != 0)
            {
                curr_device_exist = device_exist = true;
                existing_pm.push_back(pm_tg_dev_names[i]);
            }
        }

        if (curr_device_exist == false)
        {
            try
            {
                my_device_import = db->import_device(pm_tg_dev_names[i]);
                device_exist = true;
                existing_pm.push_back(pm_tg_dev_names[i]);
            }
            catch (Tango::DevFailed &e)
            {
                if (::strcmp(e.errors[0].reason.in(),"DB_DeviceNotDefined")!=0)
                {
                    device_exist = true;
                    existing_pm.push_back(pm_tg_dev_names[i]);
                }
            }
        }
    }

    if (device_exist == true)
    {
        TangoSys_OMemStream o;
        o << "The following device" << ((existing_pm.size() > 1) ? "s " : " ");
        for(vector<string>::size_type i = 0; i < existing_pm.size(); i++)
            o << existing_pm[i] << " ";
        o << ((existing_pm.size() > 1) ? "are " : "is ");
        o << "already defined" << ends;

        Tango::Except::throw_exception(
                (const char *)"Pool_PseudoMotorAlreadyCreated",o.str(),
                (const char *)"Pool::create_pseudo_motor");
    }

//---------------------------------------------------------
// If the devices are not defined in database, create them in database, set
// their alias and define its properties used to store its ID, its device pool
// and its motor group
//

    if (device_exist == false)
    {

        DEBUG_STREAM << "Trying to create devices entry in database" << endl;

        //
        // Prepare the Motor Group
        //
        if(!grp_exists)
        {
            Tango::DevVarStringArray in;
            Tango::DeviceData din,dout;

            in.length(m_nb + 1);

            in[0] = CORBA::string_dup(mg_name.c_str());
            for (vector<string>::size_type ul = 0; ul < m_nb ;ul++)
                in[ul+1] = CORBA::string_dup(mot_names[ul].c_str());
            din << in;

            try
            {
                Tango::DeviceProxy tg_pool(device_name);
                dout = tg_pool.command_inout("CreateMotorGroup", din);
                DEBUG_STREAM << "Created Motor Group Device " << mg_name <<
                                " for pseudo motor" << endl;
            }
            catch(Tango::DevFailed &ex)
            {
                TangoSys_OMemStream o;
                o << "Can't create motor group for pseudo motor controller ";
                o << ctrl_inst_name << ends;

                Tango::Except::re_throw_exception(ex,
                        (const char *)"Pool_CantCreatePseudoMotor",o.str(),
                        (const char *)"Pool::create_pseudo_motor");
            }
        }

        vector<string> created_pm_dev;
        try
        {
            ControllerPool &ctrl_pool = get_controller(ctrl_inst_name, true);
            MotorGroupPool &motor_group_pool = get_motor_group(mg_name);

            std::vector<Tango::DevLong> tg_motor_ids;
            PoolTango::toTango(motor_ids, tg_motor_ids);
                
            for(vector<string>::size_type ul = 0; ul < pm_nb ;ul++)
            {
                Tango::DbDevInfo my_device_info;
                my_device_info.name = pm_tg_dev_names[ul].c_str();
                my_device_info._class = "PseudoMotor";
                my_device_info.server = tg->get_ds_name().c_str();

                db->add_device(my_device_info);

                created_pm_dev.push_back(pm_tg_dev_names[ul]);
                db->put_device_alias(pm_tg_dev_names[ul],pseudo_mot_names[ul]);

                Tango::DbDatum id_prop(ID_PROP);
                Tango::DbDatum ctrl_id_prop(CTRL_ID_PROP);
                Tango::DbDatum axis_prop(AXIS_PROP);
                Tango::DbDatum motor_group_id_prop(PSEUDO_MOTOR_MG_ID);
                Tango::DbDatum motor_list_prop(PSEUDO_MOTOR_LIST);
                Tango::DbData db_data;

                ElementId pseudo_mot_id = get_new_id();
                id_prop << (Tango::DevLong)pseudo_mot_id;
                db_data.push_back(id_prop);

                ctrl_id_prop << (Tango::DevLong)ctrl_pool.get_id();
                db_data.push_back(ctrl_id_prop);

                axis_prop << (Tango::DevLong)(ul + 1);
                db_data.push_back(axis_prop);

                motor_group_id_prop << (Tango::DevLong)motor_group_pool.get_id();
                db_data.push_back(motor_group_id_prop);

                motor_list_prop << tg_motor_ids;
                db_data.push_back(motor_list_prop);

                db->put_device_property(pm_tg_dev_names[ul].c_str(),db_data);

                Tango::DbDatum pos("Position"),abs_ch("abs_change");
                db_data.clear();
                pos << (Tango::DevLong)1;
                abs_ch << defaultMotPos_AbsChange;
                db_data.push_back(pos);
                db_data.push_back(abs_ch);
                db->put_device_attribute_property(pm_tg_dev_names[ul].c_str(),
                                                  db_data);

                DEBUG_STREAM << "Device " << pseudo_mot_names[ul] << " created"
                                " in database (with alias)" << endl;
            }
        }
        catch (Tango::DevFailed &e)
        {
            TangoSys_OMemStream o;
            // Something went wrong: Clean the Motor Group and pseudo motors
            // if necessary

            if(!grp_exists)
            {
                try
                {
                    Tango::DeviceProxy tg_pool(device_name);
                    Tango::DeviceData din;
                    din << mg_name;
                    tg_pool.command_inout("DeleteMotorGroup", din);
                }
                catch(Tango::DevFailed &ex)
                {
                    TangoSys_OMemStream o;
                    o << "Can't delete motor group for pseudo motor and ";
                }
            }

            for(vector<string>::size_type ul = 0; ul < created_pm_dev.size(); ul++)
            {
                try
                {
                    db->delete_device(created_pm_dev[ul]);
                }
                catch(Tango::DevFailed &ex)
                {
                    TangoSys_OMemStream o;
                    o << "Can't delete temporary created pseudo motor and ";
                    o << pseudo_mot_names[ul] << endl;
                }
            }

            o << "Can't create pseudo motor in database" << ends;

            Tango::Except::re_throw_exception(e,
                    (const char *)"Pool_CantCreatePseudoMotor",o.str(),
                    (const char *)"Pool::create_pseudo_motor");
        }

//
// Find the Tango PseudoMotor class and create the pseudo motor
//
        const vector<Tango::DeviceClass *> *cl_list = tg->get_class_list();
        for (vector<Tango::DeviceClass *>::size_type i = 0;i < cl_list->size();i++)
        {
            if ((*cl_list)[i]->get_name() == "PseudoMotor")
            {
                DEBUG_STREAM << "Found PseudoMotor Class" << endl;
                try
                {
                    for(vector<string>::size_type pm_index = 0; pm_index < pm_nb ;pm_index++)
                    {
                        Tango::DevVarStringArray na;
                        na.length(1);
                        na[0] = pm_tg_dev_names[pm_index].c_str();
                        (*cl_list)[i]->device_factory(&na);
                    }
                    break;
                }
                catch (Tango::DevFailed &e)
                {
                    DEBUG_STREAM << "Exception while trying to create "
                                    "PseudoMotor device" << endl;

                    TangoSys_OMemStream o;
                    // Something went wrong: Clean the Motor Group if necessary

                    if(!grp_exists)
                    {
                        try
                        {
                            DEBUG_STREAM << "Motor group " << mg_name << " was"
                            " created specifically for this pseudo motor. "
                            "Deleting it..." << endl;

                            Tango::DeviceProxy tg_pool(device_name);
                            Tango::DeviceData din;
                            din << mg_name;
                            tg_pool.command_inout("DeleteMotorGroup", din);
                        }
                        catch(Tango::DevFailed &ex)
                        {
                            TangoSys_OMemStream o;
                            o << "Can't delete motor group for pseudo motor"
                                 " and " << endl;
                        }
                    }

//
// The delete_device will also delete device property(ies)
//
                    o << "Can't create pseudo motor device " << ends;

                    Tango::Except::re_throw_exception(e,
                            (const char *)"Pool_CantCreatePseudoMotor",o.str(),
                            (const char *)"Pool::create_pseudo_motor");
                }
            }
        }
    }

//
// Build the list of siblings
//
    std::vector<PseudoMotor_ns::PseudoMotor*> pm_siblings;
    for(std::vector<std::string>::iterator it = pseudo_mot_names.begin();
        it != pseudo_mot_names.end(); ++it)
    {
        PseudoMotorPool &pmp = get_pseudo_motor(*it);
        PseudoMotor_ns::PseudoMotor *pm = get_pseudo_motor_device(pmp);
        pm_siblings.push_back(pm);
    }
//
// Create a Tango device proxy on the newly created pseudo motor(s)
// and set its connection to automatic re-connection
// Also subscribe to events comming from the motor group
//
    for(std::vector<std::string>::iterator it = pseudo_mot_names.begin();
        it != pseudo_mot_names.end(); ++it)
    {
        PseudoMotorPool &pmp = get_pseudo_motor(*it);
        
        Tango::DeviceProxy *proxy = new Tango::DeviceProxy(pmp.get_full_name().c_str());
        proxy->set_transparency_reconnection(true);
        set_element_proxy(pmp, proxy);
        MotorGroupPool &mg_pool = get_motor_group(pmp.motor_group_id);
        mg_pool.add_pool_elem_listener(&pmp);
        
        PseudoMotor_ns::PseudoMotor *pm = get_pseudo_motor_device(pmp);
        pm->set_siblings(pm_siblings);
    }

}

//------------------------------------------------------------------------------
// Pool::create_pseudo_counter_ctrl_elems
//
void Pool::create_pseudo_counter_ctrl_elems(string &ctrl_inst_name,
                                            PseudoCoCtrlFiCa *fica,
                                            vector<string> &pseudo_counter_names,
                                            vector<string> &counter_names)
{
//----------------------------------------------------
// Check if we don't have already enough pseudo counters
//
    vector<string>::size_type pc_nb = pseudo_counter_names.size();
    vector<string>::size_type co_nb = counter_names.size();
    if (get_pseudo_counter_nb() + pc_nb > MAX_PSEUDO_COUNTER)
    {
        Tango::Except::throw_exception(
            (const char *)"Pool_TooManyPseudoMotor",
            (const char *)"Too many pseudo counters in your pool",
            (const char *)"Pool::create_pseudo_counter");
    }

//---------------------------------------------------------
// Check if counters are member of this pool
//
    ElemIdVector channel_ids;
    for (vector<string>::size_type ul = 0; ul < co_nb ;ul++)
    {
        string &counter_name = counter_names[ul];
        
        try
        {
            PoolElement &pe = get_experiment_channel(counter_name);
            channel_ids.push_back(pe.get_id());
        }
        catch(Tango::DevFailed &df)
        {
            TangoSys_OMemStream o;
            o << "Counter/0D channel '" << counter_name
              << "' is not defined in this pool. "
              << "Can't create the pseudo counter controller." << ends;

            Tango::Except::re_throw_exception(df, "Pool_CounterNotDefined", o.str(),
                                              "Pool::create_pseudo_counter");
        }
    }

//
// Build tango names
//
    vector<string> pc_tg_dev_names;

    for (vector<string>::size_type ul = 0; ul < pc_nb ;ul++)
    {
        stringstream role_idx;
        role_idx << ul + 1;
        string dev_name = "pseudocounter/" + ctrl_inst_name + "/" + role_idx.str();
        pc_tg_dev_names.push_back(dev_name);
    }

//---------------------------------------------------------
// Build Tango device name for Pseudo Motor and Motor Group
//

    Tango::Util	*tg = Tango::Util::instance();

//----------------------------------------------------
// Check if at least one device is already defined in database
// Check by device alias and by Tango device name
//
    Tango::Database *db = tg->get_database();

    Tango::DbDevImportInfo my_device_import;
    bool device_exist = false;
    bool by_alias = false;
    vector<string> existing_pc;

    for (vector<string>::size_type i = 0; i < pc_nb ;i++)
    {
        bool curr_device_exist = false;
        try
        {
            my_device_import = db->import_device(pseudo_counter_names[i]);
            curr_device_exist = device_exist = true;
            by_alias = true;
            existing_pc.push_back(pseudo_counter_names[i]);
        }
        catch (Tango::DevFailed &e)
        {
            if (::strcmp(e.errors[0].reason.in(),"DB_DeviceNotDefined") != 0)
            {
                curr_device_exist = device_exist = true;
                existing_pc.push_back(pc_tg_dev_names[i]);
            }
        }

        if (curr_device_exist == false)
        {
            try
            {
                my_device_import = db->import_device(pc_tg_dev_names[i]);
                device_exist = true;
                existing_pc.push_back(pc_tg_dev_names[i]);
            }
            catch (Tango::DevFailed &e)
            {
                if (::strcmp(e.errors[0].reason.in(),"DB_DeviceNotDefined")!=0)
                {
                    device_exist = true;
                    existing_pc.push_back(pc_tg_dev_names[i]);
                }
            }
        }
    }

    if (device_exist == true)
    {
        TangoSys_OMemStream o;
        o << "The following device" << ((existing_pc.size() > 1) ? "s " : " ");
        for(vector<string>::size_type i = 0; i < existing_pc.size(); i++)
            o << existing_pc[i] << " ";
        o << ((existing_pc.size() > 1) ? "are " : "is ");
        o << "already defined" << ends;

        Tango::Except::throw_exception(
                (const char *)"Pool_PseudoCounterAlreadyCreated",o.str(),
                (const char *)"Pool::create_pseudo_counter");
    }

//---------------------------------------------------------
// If the devices are not defined in database, create them in database, set
// their alias and define its properties used to store its ID, its device pool
//

    if (device_exist == false)
    {

        DEBUG_STREAM << "Trying to create devices entry in database" << endl;

        vector<string> created_pc_dev;
        
        std::vector<Tango::DevLong> tg_channel_ids;
        PoolTango::toTango(channel_ids, tg_channel_ids);
                    
        try
        {
            ControllerPool &ctrl_pool = get_controller(ctrl_inst_name, true);
            for(vector<string>::size_type ul = 0; ul < pc_nb ;ul++)
            {
                Tango::DbDevInfo my_device_info;
                my_device_info.name = pc_tg_dev_names[ul].c_str();
                my_device_info._class = "PseudoCounter";
                my_device_info.server = tg->get_ds_name().c_str();

                db->add_device(my_device_info);

                created_pc_dev.push_back(pc_tg_dev_names[ul]);
                db->put_device_alias(pc_tg_dev_names[ul],pseudo_counter_names[ul]);


                Tango::DbDatum id_prop(ID_PROP);
                Tango::DbDatum ctrl_id_prop(CTRL_ID_PROP);
                Tango::DbDatum axis_prop(AXIS_PROP);
                Tango::DbDatum channel_list_prop(PSEUDO_COUNTER_LIST);
                Tango::DbData db_data;

                ElementId exp_channel_id = get_new_id();
                id_prop << (Tango::DevLong)exp_channel_id;
                db_data.push_back(id_prop);

                ctrl_id_prop << (Tango::DevLong)ctrl_pool.get_id();
                db_data.push_back(ctrl_id_prop);

                axis_prop << (Tango::DevLong)(ul + 1);
                db_data.push_back(axis_prop);

                channel_list_prop << tg_channel_ids;
                db_data.push_back(channel_list_prop);

                db->put_device_property(pc_tg_dev_names[ul].c_str(),db_data);

                Tango::DbDatum val("Value"),abs_ch("abs_change");
                db_data.clear();
                val << (Tango::DevLong)1;
                abs_ch << defaultCtVal_AbsChange;
                db_data.push_back(val);
                db_data.push_back(abs_ch);

                db->put_device_attribute_property(pc_tg_dev_names[ul].c_str(),
                                                  db_data);

                DEBUG_STREAM << "Device " << pseudo_counter_names[ul] << " created"
                                " in database (with alias)" << endl;
            }
        }
        catch (Tango::DevFailed &e)
        {
            TangoSys_OMemStream o;
            // Something went wrong: Clean the pseudo counters if necessary

            for(vector<string>::size_type ul = 0; ul < created_pc_dev.size(); ul++)
            {
                try
                {
                    db->delete_device(created_pc_dev[ul]);
                }
                catch(Tango::DevFailed &ex)
                {
                    TangoSys_OMemStream o;
                    o << "Can't delete temporary created pseudo counter and ";
                    o << pseudo_counter_names[ul] << endl;
                }
            }

            o << "Can't create pseudo counter in database" << ends;

            Tango::Except::re_throw_exception(e,
                    (const char *)"Pool_CantCreatePseudoCounter",o.str(),
                    (const char *)"Pool::create_pseudo_counter");
        }

//
// Find the Tango PseudoMotor class and create the pseudo counter
//
        const vector<Tango::DeviceClass *> *cl_list = tg->get_class_list();
        for (vector<Tango::DeviceClass *>::size_type i = 0;i < cl_list->size();i++)
        {
            if ((*cl_list)[i]->get_name() == "PseudoCounter")
            {
                DEBUG_STREAM << "Found PseudoCounter Class" << endl;
                try
                {
                    for(vector<string>::size_type pc_index = 0; pc_index < pc_nb ;pc_index++)
                    {
                        Tango::DevVarStringArray na;
                        na.length(1);
                        na[0] = pc_tg_dev_names[pc_index].c_str();
                        (*cl_list)[i]->device_factory(&na);
                    }
                    break;
                }
                catch (Tango::DevFailed &e)
                {
                    DEBUG_STREAM << "Exception while trying to create "
                                    "PseudoCounter device" << endl;

                    TangoSys_OMemStream o;
//
// The delete_device will also delete device property(ies)
//
                    o << "Can't create pseudo counter device " << ends;

                    Tango::Except::re_throw_exception(e,
                            (const char *)"Pool_CantCreatePseudoCounter",o.str(),
                            (const char *)"Pool::create_pseudo_counter");
                }
            }
        }
    }

//
// Create a Tango device proxy on the newly created pseudo counter(s)
// and set its connection to automatic re-connection
//
    for(std::vector<std::string>::iterator it = pseudo_counter_names.begin();
        it != pseudo_counter_names.end(); ++it)
    {
        PseudoCounterPool &pcp = get_pseudo_counter(*it);
        
        Tango::DeviceProxy *proxy = new Tango::DeviceProxy(pcp.get_full_name().c_str());
        proxy->set_transparency_reconnection(true);
        set_element_proxy(pcp, proxy);
    }
}

//------------------------------------------------------------------------------
// Pool::user_elems_to_phy_elems
//
void Pool::user_elems_to_phy_elems(ElemIdVector &user_elems,
                                   ElemIdVector &phy_elems, 
                                   vector<ElementType> &filter, 
                                   bool unique /* = true */)
{
    ElemIdVectorIt user_ite = user_elems.begin();
    for ( ; user_ite != user_elems.end() ; ++user_ite)
        user_elem_to_phy_elems(*user_ite, phy_elems, filter, unique);
}

//------------------------------------------------------------------------------
// Pool::user_elem_to_phy_elems
//
void Pool::user_elem_to_phy_elems(ElementId user_elem_id, ElemIdVector &phy_elems,
                                  vector<ElementType> &filter, bool unique)
{
    PoolElement *elem = get_element(user_elem_id);
    ElementType elem_type = elem->get_type();
    
    // If the user element is a physical element
    if (IS_PHYSICAL(elem_type))
    {
        if(unique && find(phy_elems.begin(), phy_elems.end(), user_elem_id) != phy_elems.end())
            return;
        
        phy_elems.push_back(user_elem_id);
        return;
    }
    
    // If it is not a physical element then check if we ignore it has non physical
    if (find(filter.begin(), filter.end(), elem_type) != filter.end())
    {
        if(unique && find(phy_elems.begin(), phy_elems.end(), user_elem_id) != phy_elems.end())
            return;
        phy_elems.push_back(user_elem_id);
        return;
    }

    // If the user element is a group or a pseudo element
    if (IS_GROUP(elem_type) || IS_PSEUDO(elem_type))
    {
        user_elems_to_phy_elems(*elem->get_elems(), phy_elems, filter, unique);
    }
}

//------------------------------------------------------------------------------
// Pool::user_elem_to_phy_elems
//
void Pool::user_elem_to_phy_elems(ElementId user_elem_id, std::vector<std::string> &phy_elems,
                                  vector<ElementType> &filter, bool unique)
{
    ElemIdVector phy_elem_ids;
    user_elem_to_phy_elems(user_elem_id, phy_elem_ids, filter, unique);
    for(ElemIdVectorIt it = phy_elem_ids.begin(); it!= phy_elem_ids.end(); ++it)
    {
        phy_elems.push_back(get_element(*it)->get_name());
    }
}



}	//	namespace
