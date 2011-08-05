//+=============================================================================
//
// file :         MeasurementGroup.cpp
//
// description :  C++ source for the MeasurementGroup and its commands.
//                The class is derived from Device. It represents the
//                CORBA servant object which will be accessed from the
//                network. All commands which can be executed on the
//                MeasurementGroup are implemented in this file.
//
// project :      TANGO Device Server
//
// $Author$
//
// $Revision$
//
// $Log: MeasurementGroup.cpp,v $
// Revision 1.39  2007/09/08 10:33:45  tcoutinho
// bug fixes
//
// Revision 1.38  2007/09/07 15:00:07  tcoutinho
// safety commit
//
// Revision 1.37  2007/08/30 12:40:39  tcoutinho
// - changes to support Pseudo counters.
//
// Revision 1.36  2007/08/24 15:55:26  tcoutinho
// safety weekend commit
//
// Revision 1.35  2007/08/17 13:07:29  tcoutinho
// - pseudo motor restructure
// - pool base dev class restructure
// - initial commit for pseudo counters
//
// Revision 1.34  2007/07/26 10:25:15  tcoutinho
// - Fix bug 1 :  Automatic temporary MotorGroup/MeasurementGroup deletion
//
// Revision 1.33  2007/07/26 07:05:42  tcoutinho
// fix bug 10 : Change all tango commands from Stop to Abort
//
// Revision 1.32  2007/07/24 07:11:06  tcoutinho
// fix bug: in data acquisition with a measurement it is necessary to check the state of the master channel in order to know when to stop all other channels
//
// Revision 1.31  2007/07/23 16:41:38  tcoutinho
// fix bug: Stop all channels when master stops during acquisition
//
// Revision 1.29  2007/06/28 07:16:08  tcoutinho
// safety commit during comunication channels development
//
// Revision 1.28  2007/06/26 12:34:20  tcoutinho
// fix bug with swapped channels
//
// Revision 1.27  2007/06/11 09:50:15  tcoutinho
// - fix bug deleting a channel that is the timer
//
// Revision 1.26  2007/06/11 09:17:31  tcoutinho
// small changes
//
// Revision 1.25  2007/05/31 09:52:59  etaurel
// - Fix some memory leaks
//
// Revision 1.24  2007/05/30 14:46:01  etaurel
// - Add a call to the clear() method on the vector used to store group
// element ids in the build_xxx_id() methods set
// - Do not get state from hardware while an "init" command is being executed
// on the pool device (via the ghost group)
// - Change the way the group state_array vactor is populated when element is added/removed from the group
//
// Revision 1.23  2007/05/25 12:48:10  tcoutinho
// fix the same dead locks found on motor system to the acquisition system since release labeled for Josep Ribas
//
// Revision 1.22  2007/05/16 16:26:21  tcoutinho
// - fix dead lock
//
// Revision 1.21  2007/05/15 07:18:15  etaurel
// - Small change in a log message
//
// Revision 1.20  2007/05/11 08:11:17  tcoutinho
// - added new property channel_list
// - fixed some bugs
//
// Revision 1.19  2007/04/30 15:47:05  tcoutinho
// - new attribute "Channels"
// - new device property "Channel_List"
// - when add/remove channel, pool sends a change event on the MeasurementGroupList
//
// Revision 1.18  2007/04/30 14:48:50  tcoutinho
// - fixed memory allocation related bugs
//
// Revision 1.17  2007/04/26 08:22:33  tcoutinho
// - fixed bug when adding/removing elements in the mg
// - fixed error messages
//
// Revision 1.16  2007/04/24 14:14:36  tcoutinho
// - changed: measurement group stops only when all channels have stopped and not when master stops
//
// Revision 1.15  2007/04/23 15:17:59  tcoutinho
// - changes according to Sardana metting 26-03-2007: identical measurement groups can be created, Add/Remove  Exp. channel from a MG, etc
//
// Revision 1.14  2007/04/03 07:17:05  tcoutinho
// - following decision made on Sardana metting 26-03-2007, the save config feature will not be implemented on a measurement group basis.
//
// Revision 1.13  2007/03/02 16:33:11  tcoutinho
// - fix bugs - event related, attribute quality, etc
//
// Revision 1.12  2007/03/01 13:12:18  tcoutinho
// - measurement group event related fixes
//
// Revision 1.11  2007/02/28 16:21:52  tcoutinho
// - support for 0D channels
// - basic fixes after running first battery of tests on measurement group
//
// Revision 1.10  2007/02/22 14:08:07  tcoutinho
// - config support (not finished)
//
// Revision 1.9  2007/02/22 11:56:22  tcoutinho
// - added support for ghost measurement group
// - added support for init/reload controller operations
// - fix some possible concurrency
// - added support for configuration (not finished)
//
// Revision 1.8  2007/02/16 10:01:16  tcoutinho
// - development checkin
//
// Revision 1.7  2007/02/13 14:39:42  tcoutinho
// - fix bug in motor group when a motor or controller are recreated due to an InitController command
//
// Revision 1.6  2007/02/08 16:18:13  tcoutinho
// - controller safety on PoolGroupBaseDev
//
// Revision 1.5  2007/02/07 16:53:05  tcoutinho
// safe guard commit
//
// Revision 1.4  2007/02/06 19:36:51  tcoutinho
// safe guard commit
//
// Revision 1.3  2007/02/06 19:11:23  tcoutinho
// safe guard commit
//
// Revision 1.2  2007/02/06 09:42:34  tcoutinho
// - safe development commit
//
// Revision 1.1  2007/02/03 15:20:38  tcoutinho
// - new Measurement Group Tango device
//
//
// copyleft :     European Synchrotron Radiation Facility
//                BP 220, Grenoble 38043
//                FRANCE
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
//  Command's name    |  Method's name
//	----------------------------------------
//  State             |  dev_state()
//  Status            |  dev_status()
//  Start             |  start()
//  Abort             |  abort()
//  AddExpChannel     |  add_exp_channel()
//  RemoveExpChannel  |  remove_exp_channel()
//
//===================================================================

#include "PyUtils.h"
#include "CtrlFiCa.h"
#include "Utils.h"
#include "Pool.h"
#include "PoolUtil.h"
#include "MeasurementGroup.h"
#include "MeasurementGroupClass.h"
#include "MeasurementGroupUtil.h"
#include "CTPoolThread.h"
#include "ZeroDThread.h"
#include "OneDThread.h"
#include "TwoDThread.h"
#include "PseudoCounter.h"
#include "PseudoMotor.h"

#include <pool/Ctrl.h>
#include <pool/CoTiCtrl.h>
#include <pool/ZeroDCtrl.h>
#include <pool/OneDCtrl.h>
#include <pool/TwoDCtrl.h>
#include <pool/PseudoCoCtrl.h>
#include <pool/PseudoMotCtrl.h>
#include <tango.h>

namespace MeasurementGroup_ns
{

using namespace Pool_ns;

//------------------------------------------------------------------------------
// Counter/Timer Controller 
//

void MeasurementGroup::CTCtrlInGrp::PreReadAll()
{
    get_ct_ctrl()->PreReadAll();
}

void MeasurementGroup::CTCtrlInGrp::ReadAll()
{
    get_ct_ctrl()->ReadAll();
}

CoTiController *
MeasurementGroup::CTCtrlInGrp::get_ct_ctrl()
{
    return static_cast<CoTiController*>(ct->get_controller());
}


//------------------------------------------------------------------------------
// 0D Controller 
//

void MeasurementGroup::ZeroDCtrlInGrp::PreReadAll()
{
    get_zerod_ctrl()->PreReadAll();
}

void MeasurementGroup::ZeroDCtrlInGrp::ReadAll()
{
    get_zerod_ctrl()->ReadAll();
}

ZeroDController *
MeasurementGroup::ZeroDCtrlInGrp::get_zerod_ctrl()
{
    return static_cast<ZeroDController*>(ct->get_controller());
}


//------------------------------------------------------------------------------
// 1D Controller 
//

void MeasurementGroup::OneDCtrlInGrp::PreReadAll()
{
    get_oned_ctrl()->PreReadAll();
}

void MeasurementGroup::OneDCtrlInGrp::ReadAll()
{
    get_oned_ctrl()->ReadAll();
}

OneDController *
MeasurementGroup::OneDCtrlInGrp::get_oned_ctrl()
{
    return static_cast<OneDController*>(ct->get_controller());
}


//------------------------------------------------------------------------------
// 2D Controller 
//

void MeasurementGroup::TwoDCtrlInGrp::PreReadAll()
{
    get_twod_ctrl()->PreReadAll();
}

void MeasurementGroup::TwoDCtrlInGrp::ReadAll()
{
    get_twod_ctrl()->ReadAll();
}


TwoDController *
MeasurementGroup::TwoDCtrlInGrp::get_twod_ctrl()
{
    return static_cast<TwoDController*>(ct->get_controller());
}


//------------------------------------------------------------------------------
// Pseudo counter Controller 
//

PseudoCounterController *
MeasurementGroup::PseudoCoCtrlInGrp::get_pc_ctrl()
{
    return static_cast<PseudoCounterController*>(ct->get_controller());
}

//------------------------------------------------------------------------------
// Motor Controller 
//

void MeasurementGroup::MotorCtrlInGrp::PreReadAll()
{
    get_motor_ctrl()->PreReadAll();
}

void MeasurementGroup::MotorCtrlInGrp::ReadAll()
{
    get_motor_ctrl()->ReadAll();
}

MotorController *
MeasurementGroup::MotorCtrlInGrp::get_motor_ctrl()
{
    return static_cast<MotorController*>(ct->get_controller());
}


//------------------------------------------------------------------------------
// Pseudo Motor Controller 
//

MotorController *
MeasurementGroup::PseudoMotorCtrlInGrp::get_motor_ctrl()
{
    Tango::Except::throw_exception(
        (const char *)"Pool_CantGetMotorCtrlFromPseudoMotorCtrl",
        (const char *)"Trying to get MotorController from PseudoMotorController",
        (const char *)"MeasurementGroup::PseudoMotorCtrlInGrp::get_motor_ctrl");
    
    // Make the compiler quiet
    return NULL;
}

PseudoMotorController *
MeasurementGroup::PseudoMotorCtrlInGrp::get_pseudo_motor_ctrl()
{
    return static_cast<PseudoMotorController*>(ct->get_controller());
}


//------------------------------------------------------------------------------
// Counter/Timer 
//

MeasurementGroup::CTInGrp::CTInGrp(Pool_ns::CTExpChannelPool &ref, 
                                   CtrlGrp *ctrl_ptr,
                                   Tango::Device_4Impl *device,
                                   Pool_ns::ElementId grp, 
                                   Tango::Device_4Impl *logger):
    MeasurementGroup::SingleValChInGrp(ref, ctrl_ptr, device, grp, logger)
{}

const char *
MeasurementGroup::CTInGrp::get_family()
{ return "Counter/Timer"; }

MntGrpEltType
MeasurementGroup::CTInGrp::get_type()
{ return CT_EXP_CHANNEL; }

void
MeasurementGroup::CTInGrp::PreReadOne()
{ static_cast<CoTiController*>(ctrl_grp->ct->get_controller())->PreReadOne(pe->get_axis()); }

void
MeasurementGroup::CTInGrp::ReadOne()
{ value = static_cast<CoTiController*>(ctrl_grp->ct->get_controller())->ReadOne(pe->get_axis()); }

Pool_ns::CTExpChannelPool &
MeasurementGroup::CTInGrp::get_ct()
{ return *static_cast<Pool_ns::CTExpChannelPool*>(pe); }

CTExpChannel_ns::CTExpChannel* MeasurementGroup::CTInGrp::get_countertimer_device()
{ return static_cast<CTExpChannel_ns::CTExpChannel *>(dev); }

//------------------------------------------------------------------------------
// 0D
//

MeasurementGroup::ZeroDInGrp::ZeroDInGrp(Pool_ns::ZeroDExpChannelPool &ref,
                                         CtrlGrp *ctrl_ptr, 
                                         Tango::Device_4Impl *device, 
                                         Pool_ns::ElementId grp, 
                                         Tango::Device_4Impl *logger):
    MeasurementGroup::SingleValChInGrp(ref, ctrl_ptr, device, grp, logger)
{}

const char *
MeasurementGroup::ZeroDInGrp::get_family()
{ return "0D Experiment Channel"; }

MntGrpEltType
MeasurementGroup::ZeroDInGrp::get_type()
{ return ZEROD_EXP_CHANNEL; }

void
MeasurementGroup::ZeroDInGrp::PreReadOne()
{ static_cast<ZeroDController*>(ctrl_grp->ct->get_controller())->PreReadOne(pe->get_axis()); }

void
MeasurementGroup::ZeroDInGrp::ReadOne()
{ value = static_cast<ZeroDController*>(ctrl_grp->ct->get_controller())->ReadOne(pe->get_axis()); }

Pool_ns::ZeroDExpChannelPool &
MeasurementGroup::ZeroDInGrp::get_zerod()
{ return *static_cast<Pool_ns::ZeroDExpChannelPool*>(pe); }

ZeroDExpChannel_ns::ZeroDExpChannel* MeasurementGroup::ZeroDInGrp::get_zerod_device()
{ return static_cast<ZeroDExpChannel_ns::ZeroDExpChannel *>(dev); }

//------------------------------------------------------------------------------
// Pseudo counter
//

MeasurementGroup::PseudoCoInGrp::PseudoCoInGrp(Pool_ns::PseudoCounterPool &ref,
                                               CtrlGrp *ctrl_ptr, 
                                               Tango::Device_4Impl *device, 
                                               Pool_ns::ElementId grp, 
                                               Tango::Device_4Impl *logger):
    MeasurementGroup::SingleValChInGrp(ref, ctrl_ptr, device, grp, logger)
{}

const char *
MeasurementGroup::PseudoCoInGrp::get_family()
{ return "PseudoCounter"; }

MntGrpEltType
MeasurementGroup::PseudoCoInGrp::get_type()
{ return PSEUDO_EXP_CHANNEL; }

void
MeasurementGroup::PseudoCoInGrp::PreReadOne()
{  }

void
MeasurementGroup::PseudoCoInGrp::ReadOne()
{
    PseudoCounter_ns::PseudoCounter *pc = get_pseudo_counter_device();
    vector<double> &ch_values = pc->ch_values;
    uint32_t size = uses.size();
    if(ch_values.size() != size)
    {
cout << "Pseudo counter reports using " << ch_values.size() << " but mntgrp reports " << size<<endl;
        assert(ch_values.size() == size);
    }
    for(uint32_t ul = 0; ul < size; ul++)
        ch_values[ul] = uses[ul]->value;
    value = pc->calc();
}

Pool_ns::PseudoCounterPool &
MeasurementGroup::PseudoCoInGrp::get_pc()
{ return *static_cast<Pool_ns::PseudoCounterPool*>(pe); }

PseudoCounter_ns::PseudoCounter* MeasurementGroup::PseudoCoInGrp::get_pseudo_counter_device()
{ return static_cast<PseudoCounter_ns::PseudoCounter *>(dev); }

//------------------------------------------------------------------------------
// 1D
//

MeasurementGroup::OneDInGrp::OneDInGrp(Pool_ns::OneDExpChannelPool &ref, 
                                       CtrlGrp *ctrl_ptr,
                                       Tango::Device_4Impl *device, 
                                       Pool_ns::ElementId grp, 
                                       Tango::Device_4Impl *logger):
    MeasurementGroup::ChInGrp(ref, ctrl_ptr, device, grp, logger)
{}

const char *
MeasurementGroup::OneDInGrp::get_family()
{ return "1D Experiment Channel"; }


MntGrpEltType
MeasurementGroup::OneDInGrp::get_type()
{ return ONED_EXP_CHANNEL; }

void
MeasurementGroup::OneDInGrp::PreReadOne()
{ static_cast<OneDController*>(ctrl_grp->ct->get_controller())->PreReadOne(pe->get_axis()); }

void
MeasurementGroup::OneDInGrp::ReadOne()
{ static_cast<OneDController*>(ctrl_grp->ct->get_controller())->ReadOne(pe->get_axis()); }

Pool_ns::OneDExpChannelPool &
MeasurementGroup::OneDInGrp::get_oned()
{ return *static_cast<Pool_ns::OneDExpChannelPool*>(pe); }

OneDExpChannel_ns::OneDExpChannel* MeasurementGroup::OneDInGrp::get_oned_device()
{ return static_cast<OneDExpChannel_ns::OneDExpChannel *>(dev); }

MeasurementGroup::TwoDInGrp::TwoDInGrp(TwoDExpChannelPool &ref,
                                       CtrlGrp *ctrl_ptr,
                                       Tango::Device_4Impl *device, 
                                       Pool_ns::ElementId grp,
                                       Tango::Device_4Impl *logger):
    MeasurementGroup::ChInGrp(ref, ctrl_ptr, device, grp, logger)
{}

const char *
MeasurementGroup::TwoDInGrp::get_family()
{ return "2D Experiment Channel"; }

MntGrpEltType
MeasurementGroup::TwoDInGrp::get_type()
{ return TWOD_EXP_CHANNEL; }


void
MeasurementGroup::TwoDInGrp::PreReadOne()
{ static_cast<CoTiController*>(ctrl_grp->ct->get_controller())->PreReadOne(pe->get_axis()); }

void
MeasurementGroup::TwoDInGrp::ReadOne()
{ static_cast<ZeroDController*>(ctrl_grp->ct->get_controller())->ReadOne(pe->get_axis()); }

TwoDExpChannelPool &
MeasurementGroup::TwoDInGrp::get_twod()
{ return *static_cast<TwoDExpChannelPool*>(pe); }

TwoDExpChannel_ns::TwoDExpChannel* MeasurementGroup::TwoDInGrp::get_twod_device()
{ return static_cast<TwoDExpChannel_ns::TwoDExpChannel *>(dev); }

//------------------------------------------------------------------------------
// Motor
//
MeasurementGroup::MotorInGrp::MotorInGrp(Pool_ns::PoolElement &ref, 
                                         CtrlGrp *ctrl_ptr, 
                                         Tango::Device_4Impl *device,
                                         Pool_ns::ElementId grp, 
                                         Tango::Device_4Impl *logger):
    MeasurementGroup::SingleValChInGrp(ref, ctrl_ptr, device, grp, logger)
{}

const char *
MeasurementGroup::MotorInGrp::get_family()
{ return "Motor"; }

MntGrpEltType
MeasurementGroup::MotorInGrp::get_type()
{ return MOTOR_CHANNEL; }

void
MeasurementGroup::MotorInGrp::PreReadOne()
{ static_cast<MotorController*>(ctrl_grp->ct->get_controller())->PreReadOne(pe->get_axis()); }

void
MeasurementGroup::MotorInGrp::ReadOne()
{ value = static_cast<MotorController*>(ctrl_grp->ct->get_controller())->ReadOne(pe->get_axis()); }

Pool_ns::MotorPool &
MeasurementGroup::MotorInGrp::get_motor()
{ return *static_cast<Pool_ns::MotorPool*>(pe); }

Motor_ns::Motor* MeasurementGroup::MotorInGrp::get_motor_device()
{ return static_cast<Motor_ns::Motor *>(dev); }

//------------------------------------------------------------------------------
// Pseudo Motor
//
MeasurementGroup::PseudoMotorInGrp::PseudoMotorInGrp(Pool_ns::PoolElement &ref, 
                                                     CtrlGrp *ctrl_ptr, 
                                                     Tango::Device_4Impl *device,
                                                     Pool_ns::ElementId grp, 
                                                     Tango::Device_4Impl *logger):
    MeasurementGroup::MotorInGrp(ref, ctrl_ptr, device, grp, logger)
{}

const char *
MeasurementGroup::PseudoMotorInGrp::get_family()
{ return "PseudoMotor"; }

void
MeasurementGroup::PseudoMotorInGrp::ReadOne()
{ 
    //WARNING: this is not absolutely the best way to get the value. When a restructure
    // is done this must be taken into account. Also not very efficient.
    value = get_pseudo_motor_device()->get_value(false);
}

Pool_ns::MotorPool &
MeasurementGroup::PseudoMotorInGrp::get_motor()
{
    Tango::Except::throw_exception(
        (const char *)"Pool_CantGetMotorFromPseudoMotor",
        (const char *)"Trying to get Motor from PseudoMotor",
        (const char *)"MeasurementGroup::PseudoMotorInGrp::get_motor");

    // Make the compiler quiet
    return *((Pool_ns::MotorPool *)NULL);
}

Pool_ns::PseudoMotorPool &
MeasurementGroup::PseudoMotorInGrp::get_pseudo_motor()
{ return *static_cast<Pool_ns::PseudoMotorPool*>(pe); }

PseudoMotor_ns::PseudoMotor* MeasurementGroup::PseudoMotorInGrp::get_pseudo_motor_device()
{ return static_cast<PseudoMotor_ns::PseudoMotor *>(dev); }

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::MeasurementGroup(string &s)
//
// description : 	constructor for simulated MeasurementGroup
//
// in : - cl : Pointer to the DeviceClass object
//      - s : Device name
//
//-----------------------------------------------------------------------------
MeasurementGroup::MeasurementGroup(Tango::DeviceClass *cl,string &s)
//:Tango::Device_4Impl(cl,s.c_str())
:PoolGroupBaseDev(cl,s.c_str())
{
    init_device();
}

MeasurementGroup::MeasurementGroup(Tango::DeviceClass *cl,const char *s)
//:Tango::Device_4Impl(cl,s)
:PoolGroupBaseDev(cl,s)
{
    init_device();
}

MeasurementGroup::MeasurementGroup(Tango::DeviceClass *cl,const char *s,const char *d)
//:Tango::Device_4Impl(cl,s,d)
:PoolGroupBaseDev(cl,s,d)
{
    init_device();
}
//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::delete_device()
//
// description : 	will be called at device destruction or at init command.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::delete_device()
{
    //	Delete device's allocated object
    DEBUG_STREAM << "Entering delete_device for dev " << get_name() << endl;

//
// To know that we are executing this code due to a pool shutdown and not due to a
// "Init" command, we are using the polling thread ptr which is cleared in the DS
// shutdown sequence before the device destruction
//

    Tango::Util *tg = Tango::Util::instance();
    if (tg->get_polling_thread_object() != NULL)
    {
        if (get_state() == Tango::MOVING)
        {
            TangoSys_OMemStream o;
            o << "Init command on measurement group device is not allowed "
                 "while it is taking data" << ends;

            Tango::Except::throw_exception(
                    (const char *)"MeasurementGroup_InitNotAllowed",o.str(),
                    (const char *)"MeasurementGroup::delete_device");
        }
    }

    for (vector<PseudoCoInGrp*>::iterator p_it = pseudo_elts.begin();
         p_it != pseudo_elts.end(); ++p_it)
         delete *p_it;
    pseudo_elts.clear();

    for (vector<PseudoCoCtrlInGrp*>::iterator p_ctrl_it = implied_pseudo_ctrls.begin();
         p_ctrl_it != implied_pseudo_ctrls.end(); ++p_ctrl_it)
         delete *p_ctrl_it;
    implied_pseudo_ctrls.clear();

    SAFE_DELETE_ARRAY(attr_Counters_read);
    SAFE_DELETE_ARRAY(attr_ZeroDExpChannels_read);
    SAFE_DELETE_ARRAY(attr_OneDExpChannels_read);
    SAFE_DELETE_ARRAY(attr_TwoDExpChannels_read);
    SAFE_DELETE_ARRAY(attr_PseudoCounters_read);
    SAFE_DELETE_ARRAY(attr_Channels_read);
    SAFE_DELETE_ARRAY(attr_Motors_read);
    
    delete_from_pool();
    delete_utils();
    
    PoolGroupBaseDev::delete_device();
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::init_device()
//
// description : 	will be called at device initialization.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::init_device()
{
    INFO_STREAM << "MeasurementGroup::MeasurementGroup() create device " << device_name << endl;

    // Initialize variables to default values
    //--------------------------------------------
    PoolGroupBaseDev::init_device();

    master = NULL;

    if(!init_cmd)
    {
        first_write_timer = true;
        first_write_monitor = true;
        first_write_integration_time = true;
        first_write_integration_count = true;
        attr_Integration_count_write = 0;
        attr_Integration_time_write = 0.0;

        aq_mode = aqNone;
        timer = NOT_INITIALIZED;
        monitor = NOT_INITIALIZED;

        attr_Counters_read = NULL;
        attr_ZeroDExpChannels_read = NULL;
        attr_OneDExpChannels_read = NULL;
        attr_TwoDExpChannels_read = NULL;
        attr_PseudoCounters_read = NULL;
        attr_Channels_read = NULL;
        attr_Motors_read = NULL;
    }

    attr_Integration_count_read = &attr_Integration_count_write;
    attr_Integration_time_read = &attr_Integration_time_write;

    if (is_ghost())
    {
        alias = "The_mntgrp_ghost";

//
// Init channel list for the ghost group
//
        user_group_elt.clear();
        phys_group_elt.clear();

        ct_List.clear();
        ct_nb = pool_dev->get_countertimer_nb();

        zeroDExpChannel_List.clear();
        zeroD_nb = pool_dev->get_zerod_nb();

        oneDExpChannel_List.clear();
        oneD_nb = pool_dev->get_oned_nb();

        twoDExpChannel_List.clear();
        twoD_nb = pool_dev->get_twod_nb();

        pc_nb = 0;
        mot_nb = 0;

        usr_elt_nb = ct_nb + zeroD_nb + oneD_nb + twoD_nb + pc_nb;
        ind_elt_nb = usr_elt_nb;

        state_array.clear();
        state_array.insert(state_array.begin(), usr_elt_nb, Tango::UNKNOWN);
    }
    else
    {
        ct_nb = (int32_t)ct_List.size();
        zeroD_nb = (int32_t)zeroDExpChannel_List.size();
        oneD_nb = (int32_t)oneDExpChannel_List.size();
        twoD_nb = (int32_t)twoDExpChannel_List.size();
        pc_nb = (int32_t)pseudoCounter_List.size();
        mot_nb = (int32_t)motor_List.size();
        usr_elt_nb = ct_nb + zeroD_nb + oneD_nb + twoD_nb + pc_nb + mot_nb;
        ind_elt_nb = (int32_t)phys_group_elt.size();

        assert((int32_t)user_group_elt.size() == usr_elt_nb);
    }

//
// We will push change event on State attributes
//

    Tango::Attribute &state_att = dev_attr->get_attr_by_name("state");
    state_att.set_change_event(true,false);

    Tango::Attribute &time_att = dev_attr->get_attr_by_name("Integration_time");
    time_att.set_change_event(true,false);

    Tango::Attribute &count_att = dev_attr->get_attr_by_name("Integration_count");
    count_att.set_change_event(true,false);

    Tango::Attribute &timer_att = dev_attr->get_attr_by_name("Timer");
    timer_att.set_change_event(true,false);

    Tango::Attribute &monitor_att = dev_attr->get_attr_by_name("Monitor");
    monitor_att.set_change_event(true,false);

    Tango::Attribute &counters_att = dev_attr->get_attr_by_name("Counters");
    counters_att.set_change_event(true,false);

    Tango::Attribute &channels_att = dev_attr->get_attr_by_name("Channels");
    channels_att.set_change_event(true,false);

    Tango::Attribute &zerod_att = dev_attr->get_attr_by_name("ZeroDExpChannels");
    zerod_att.set_change_event(true,false);

    Tango::Attribute &oned_att = dev_attr->get_attr_by_name("OneDExpChannels");
    oned_att.set_change_event(true,false);

    Tango::Attribute &twod_att = dev_attr->get_attr_by_name("TwoDExpChannels");
    twod_att.set_change_event(true,false);

    Tango::Attribute &pc_att = dev_attr->get_attr_by_name("PseudoCounters");
    pc_att.set_change_event(true,false);

    Tango::Attribute &mot_att = dev_attr->get_attr_by_name("Motors");
    mot_att.set_change_event(true,false);
    
//
// Build the PoolBaseUtils class depending on the
// controller type
//

    set_utils(new MeasurementGroupUtil(pool_dev));

    build_grp();

    Pool_ns::MeasurementGroupPool *mg_pool_ptr = new Pool_ns::MeasurementGroupPool;

    init_pool_element(mg_pool_ptr);

//
// Inform Pool of our birth
//
    if(!is_ghost())
    {
        attr_Counters_read = (ct_nb > 0) ? new Tango::DevString[ct_nb] : NULL;
        attr_ZeroDExpChannels_read = (zeroD_nb > 0) ? new Tango::DevString[zeroD_nb] : NULL;
        attr_OneDExpChannels_read = (oneD_nb > 0) ? new Tango::DevString[oneD_nb] : NULL;
        attr_TwoDExpChannels_read = (twoD_nb > 0) ? new Tango::DevString[twoD_nb] : NULL;
        attr_PseudoCounters_read = (pc_nb > 0) ? new Tango::DevString[pc_nb] : NULL;
        attr_Motors_read = (mot_nb > 0) ? new Tango::DevString[mot_nb] : NULL;
        attr_Channels_read = (usr_elt_nb > 0) ? new Tango::DevString[usr_elt_nb] : NULL;

        {
            Tango::AutoTangoMonitor atm(pool_dev);
            pool_dev->add_element(mg_pool_ptr);
        }
//
// Push change_event to inform client listenning on events
// We skip the memorized ones on startup because the write methods will take care
// of sending the events for them.
// The "Counters" attribute is also skipped because its value depends on the
// memorized value of timer. Therefore the write_Timer will also send the a change
// event for the "Counters" attribute
//
        if (!init_cmd)
        {
            read_Integration_time(time_att);
            time_att.fire_change_event();

            read_Integration_count(count_att);
            count_att.fire_change_event();

            read_Timer(timer_att);
            timer_att.fire_change_event();

            read_Monitor(monitor_att);
            monitor_att.fire_change_event();

            read_Channels(channels_att);
            channels_att.fire_change_event();

            read_Counters(counters_att);
            counters_att.fire_change_event();

            read_ZeroDExpChannels(zerod_att);
            zerod_att.fire_change_event();

            read_OneDExpChannels(oned_att);
            oned_att.fire_change_event();

            read_TwoDExpChannels(twod_att);
            twod_att.fire_change_event();

            read_PseudoCounters(pc_att);
            pc_att.fire_change_event();
            
            read_Motors(mot_att);
            mot_att.fire_change_event();
        }
    }
}


//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::update_state_from_ctrls
//
// description : 	Updates the state attribute
//
//-----------------------------------------------------------------------------

void MeasurementGroup::update_state_from_ctrls(int32_t idx, Tango::DevState state)
{
    Tango::DevState old_state = get_state();

//
// Read all states
//

    vector<Tango::DevState> old_state_array(state_array);
    state_array = vector<Tango::DevState>(ind_elts.size(), Tango::UNKNOWN);

    int32_t loop;
    read_state_from_ctrls();

    string &_status = get_status();
    _status.clear();

//
// If it is the ghost group and if the request comes from the polling
// thread, eventually forward state event on channel devices
//

    int th_id = omni_thread::self()->id();
    if (is_ghost() && (th_id == get_polling_thread_id()))
    {
        send_state_event(old_state_array,state_array);
    }

//
// Are there any channels in FAULT
//

    int32_t nb;
    vector<Tango::DevState>::iterator v_sta_start, v_sta_stop;
    vector<IndEltGrp*>::iterator im_ite = ind_elts.begin();

    if ((nb = count(state_array.begin(),state_array.end(),Tango::FAULT)) != 0)
    {
        set_state(Tango::FAULT);
        v_sta_start = state_array.begin();
        for (loop = 0;loop < nb;loop++)
        {
            v_sta_stop = find(v_sta_start,state_array.end(),Tango::FAULT);
            int32_t dist = distance(state_array.begin(),v_sta_stop);
            vector<IndEltGrp*>::iterator im_ite = ind_elts.begin();
            advance(im_ite,dist);
            IndEltGrp *ind = *im_ite;
            if (loop != 0)
                _status = _status + '\n';
            _status = _status + ind->get_family() + " " + ind->get_alias() + " is in FAULT";
            v_sta_start = v_sta_stop;
            v_sta_start++;
        }
    }

//
// Are there any channels in UNKNOWN
//

    else if ((nb = count(state_array.begin(),state_array.end(),Tango::UNKNOWN)) != 0)
    {
        set_state(Tango::UNKNOWN);
        v_sta_start = state_array.begin();
        for (loop = 0;loop < nb;loop++)
        {
            v_sta_stop = find(v_sta_start,state_array.end(),Tango::UNKNOWN);
            int32_t dist = distance(state_array.begin(),v_sta_stop);
            vector<IndEltGrp*>::iterator im_ite = ind_elts.begin();
            advance(im_ite,dist);
            IndEltGrp *ind = *im_ite;
            if (loop != 0)
                _status = _status + '\n';
            _status = _status + ind->get_family() + " " + ind->get_alias() + " is in UNKNOWN state";
            v_sta_start = v_sta_stop;
            v_sta_start++;
        }
    }

//
// Are there any channels(s) in ALARM
//

    else if ((nb = count(state_array.begin(),state_array.end(),Tango::ALARM)) != 0)
    {
        set_state(Tango::ALARM);
        v_sta_start = state_array.begin();
        for (loop = 0;loop < nb;loop++)
        {
            v_sta_stop = find(v_sta_start,state_array.end(),Tango::ALARM);
            int32_t dist = distance(state_array.begin(),v_sta_stop);
            vector<IndEltGrp*>::iterator im_ite = ind_elts.begin();
            advance(im_ite,dist);
            IndEltGrp *ind = *im_ite;
            if (loop != 0)
                _status = _status + '\n';
            _status = _status + ind->get_family() + " " + ind->get_alias() + " is in ALARM";
            v_sta_start = v_sta_stop;
            v_sta_start++;
        }
    }

//
// Are there any channels moving
//

    else if ((nb = count(state_array.begin(),state_array.end(),Tango::MOVING)) != 0)
    {
        v_sta_start = state_array.begin();
        for (loop = 0;loop < nb;loop++)
        {
            v_sta_stop = find(v_sta_start,state_array.end(),Tango::MOVING);
            int32_t dist = distance(state_array.begin(),v_sta_stop);
            vector<IndEltGrp*>::iterator im_ite = ind_elts.begin();
            advance(im_ite,dist);
            IndEltGrp *ind = *im_ite;
            if (loop != 0)
                _status = _status + '\n';
            _status = _status + ind->get_family() + " " + ind->get_alias() + " is MOVING";
            v_sta_start = v_sta_stop;
            v_sta_start++;
        }
        set_state(Tango::MOVING);
    }

//
// All channels are ON
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
 *	method:	MeasurementGroup::dev_state
 *
 *	description:	method to execute "State"
 *	This command gets the device state (stored in its <i>device_state</i> data member) and returns it to the caller.
 *
 * @return	State Code
 *
 */
//+------------------------------------------------------------------
Tango::DevState MeasurementGroup::dev_state()
{
    PoolGroupBaseDev::dev_state();
    DEBUG_STREAM << "MeasurementGroup::dev_state(): entering... !" << endl;

    //	Add your own code to control device here

    if (pool_init_cmd == true)
        set_state(Tango::UNKNOWN);
    else
    {
        update_state_from_ctrls();

        if(get_state() != Tango::FAULT && get_state() != Tango::UNKNOWN)
        {
            if(timer == NOT_INITIALIZED && monitor == NOT_INITIALIZED)
            {
                set_state(Tango::ALARM);
                string &_status = get_status();
                _status.clear();
                _status = ALARM_STATUS_MSG;
            }
        }
    }
    return get_state();
}

void MeasurementGroup::init_pool_element(PoolElement *pe)
{
    PoolGroupBaseDev::init_pool_element(pe);

    MeasurementGroupPool *mgp =
        static_cast<MeasurementGroupPool *>(pe);

    if(is_ghost())
        return;

    Tango::AutoTangoMonitor atm(pool_dev);

    Pool_ns::PoolTango::toPool(user_group_elt, mgp->group_elts);
    Pool_ns::PoolTango::toPool(phys_group_elt, mgp->ch_ids);

    mgp->update_info();
}

Pool_ns::MeasurementGroupPool &MeasurementGroup::get_measurement_group_obj()
{ 
    return pool_dev->get_measurement_group(get_id()); 
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::build_grp
//
// description : 	build group information based on the given properties
//
//-----------------------------------------------------------------------------

void MeasurementGroup::build_grp()
{
    Tango::AutoTangoMonitor atm(pool_dev);

    if(is_ghost())
    {
        Pool_ns::Pool::PoolElementTypeIt elem_it, elem_beg, elem_end;
        pool_dev->get_all_countertimer(elem_beg, elem_end);
        for (elem_it = elem_beg; elem_it != elem_end; ++elem_it)
        {
            Pool_ns::CTExpChannelPool &ct_pool = pool_dev->get_countertimer(elem_it->second);
            ind_elts.push_back(build_ct(ct_pool));
        }

        pool_dev->get_all_zerod(elem_beg, elem_end);
        for (elem_it = elem_beg; elem_it != elem_end; ++elem_it)
        {
            Pool_ns::ZeroDExpChannelPool &zerod_pool = pool_dev->get_zerod(elem_it->second);
            ind_elts.push_back(build_zerod(zerod_pool));
        }

        pool_dev->get_all_oned(elem_beg, elem_end);
        for (elem_it = elem_beg; elem_it != elem_end; ++elem_it)
        {
            Pool_ns::OneDExpChannelPool &oned_pool = pool_dev->get_oned(elem_it->second);
            ind_elts.push_back(build_oned(oned_pool));
        }

        pool_dev->get_all_twod(elem_beg, elem_end);
        for (elem_it = elem_beg; elem_it != elem_end; ++elem_it)
        {
            Pool_ns::TwoDExpChannelPool &twod_pool = pool_dev->get_twod(elem_it->second);
            ind_elts.push_back(build_twod(twod_pool));
        }
        ind_elts_sorted = ind_elts;
        sort(ind_elts.begin(), ind_elts.end(), Pool_ns::ielt_id_cmp);
        return;
    }

//
// Build CT information
//
    for(int32_t idx = 0; idx < ct_nb; idx++)
    {
        CTExpChannelPool &ct_ref = pool_dev->get_countertimer(ct_List[idx]);
        CTInGrp *ptr = build_ct(ct_ref);
        ind_elts.push_back(ptr);
    }

//
// Build 0D information
//
    for(int32_t idx = 0; idx < zeroD_nb; idx++)
    {
        ZeroDExpChannelPool &zeroD_ref = pool_dev->get_zerod(zeroDExpChannel_List[idx]);
        ZeroDInGrp *ptr = build_zerod(zeroD_ref);
        ind_elts.push_back(ptr);
    }

//
// Build 1D information
//
    for(int32_t idx = 0; idx < oneD_nb; idx++)
    {
        OneDExpChannelPool &oneD_ref = pool_dev->get_oned(oneDExpChannel_List[idx]);
        OneDInGrp *ptr = build_oned(oneD_ref);
        ind_elts.push_back(ptr);
    }

//
// Build 2D information
//
    for(int32_t idx = 0; idx < twoD_nb; idx++)
    {
        TwoDExpChannelPool &twoD_ref = pool_dev->get_twod(twoDExpChannel_List[idx]);
        TwoDInGrp *ptr = build_twod(twoD_ref);
        ind_elts.push_back(ptr);
    }

//
// Build Pseudo counter information
//
    for(int32_t idx = 0; idx < pc_nb; idx++)
    {
        PseudoCounterPool &pc_ref =	pool_dev->get_pseudo_counter(pseudoCounter_List[idx]);
        PseudoCoInGrp *ptr = build_pc(pc_ref);
        pseudo_elts.push_back(ptr);
    }
    
//
// Build Motor information
//
    for(int32_t idx = 0; idx < mot_nb; idx++)
    {
        try
        {
            MotorPool &mot_ref = pool_dev->get_physical_motor(motor_List[idx]);
            MotorInGrp *ptr = build_motor(mot_ref);
            ind_elts.push_back(ptr);
        }
        catch(Tango::DevFailed &e)
        {
            PseudoMotorPool &pm_ref = pool_dev->get_pseudo_motor(motor_List[idx]);
            PseudoMotorInGrp *ptr = build_pm(pm_ref);
            ind_elts.push_back(ptr);
        }
    }
    ind_elts_sorted = ind_elts;
    sort(ind_elts.begin(), ind_elts.end(), Pool_ns::ielt_id_cmp);
}

MeasurementGroup::CTCtrlInGrp *
MeasurementGroup::build_ct_ctrl(ControllerPool &ctrl_ref)
{
    return new CTCtrlInGrp(ctrl_ref, this);
}

MeasurementGroup::ZeroDCtrlInGrp *
MeasurementGroup::build_zerod_ctrl(ControllerPool &ctrl_ref)
{
    return new ZeroDCtrlInGrp(ctrl_ref, this);
}

MeasurementGroup::OneDCtrlInGrp *
MeasurementGroup::build_oned_ctrl(ControllerPool &ctrl_ref)
{
    return new OneDCtrlInGrp(ctrl_ref, this);
}

MeasurementGroup::TwoDCtrlInGrp *
MeasurementGroup::build_twod_ctrl(ControllerPool &ctrl_ref)
{
    return new TwoDCtrlInGrp(ctrl_ref, this);
}

MeasurementGroup::PseudoCoCtrlInGrp *
MeasurementGroup::build_pc_ctrl(ControllerPool &ctrl_ref)
{
    return new PseudoCoCtrlInGrp(ctrl_ref, this);
}

MeasurementGroup::MotorCtrlInGrp *
MeasurementGroup::build_motor_ctrl(ControllerPool &ctrl_ref)
{
    return new MotorCtrlInGrp(ctrl_ref, this);
}

MeasurementGroup::PseudoMotorCtrlInGrp *
MeasurementGroup::build_pm_ctrl(ControllerPool &ctrl_ref)
{
    return new PseudoMotorCtrlInGrp(ctrl_ref, this);
}

MeasurementGroup::CTInGrp *
MeasurementGroup::build_ct(CTExpChannelPool &ct_ref)
{
    ControllerPool &ctrl_ref = pool_dev->get_controller(ct_ref);
    CTExpChannel_ns::CTExpChannel *ct_dev = 
        pool_dev->get_countertimer_device(ct_ref);
    int32_t ctrlgrp_idx;
    Pool_ns::CtrlGrp *ctrl_grp = NULL;
    try
    {
        ctrl_grp = &get_ctrl_grp_from_id(ctrl_ref.id, ctrlgrp_idx);
    }
    catch(Tango::DevFailed &e)
    {
        ctrl_grp = build_ct_ctrl(ctrl_ref);
        ctrlgrp_idx = implied_ctrls.size();
        implied_ctrls.push_back(ctrl_grp);
        implied_ctrls_sorted = implied_ctrls;
        sort(implied_ctrls_sorted.begin(), implied_ctrls_sorted.end(), Pool_ns::ictrl_id_cmp);
    }

    CTInGrp *ct_grp = new CTInGrp(ct_ref, ctrl_grp, ct_dev, get_id(), this);
    ct_grp->idx_in_grp = (int32_t)ind_elts.size();
    ct_grp->idx_in_ctrlgrp = ctrlgrp_idx;
    ct_grp->obj_proxy = new Tango::DeviceProxy(ct_ref.get_full_name().c_str());
    ct_grp->obj_proxy->set_transparency_reconnection(true);

    return ct_grp;
}

MeasurementGroup::ZeroDInGrp *
MeasurementGroup::build_zerod(ZeroDExpChannelPool &zeroD_ref)
{
    ControllerPool &ctrl_ref = pool_dev->get_controller(zeroD_ref);
    ZeroDExpChannel_ns::ZeroDExpChannel *zerod_dev = 
        pool_dev->get_zerod_device(zeroD_ref);

    int32_t ctrlgrp_idx;
    Pool_ns::CtrlGrp *ctrl_grp = NULL;
    try
    {
        ctrl_grp = &get_ctrl_grp_from_id(ctrl_ref.id, ctrlgrp_idx);
    }
    catch(Tango::DevFailed &e)
    {
        ctrl_grp = build_zerod_ctrl(ctrl_ref);
        ctrlgrp_idx = implied_ctrls.size();
        implied_ctrls.push_back(ctrl_grp);
        implied_ctrls_sorted = implied_ctrls;
        sort(implied_ctrls_sorted.begin(), implied_ctrls_sorted.end(), Pool_ns::ictrl_id_cmp);
    }

    ZeroDInGrp *zerod_grp = new ZeroDInGrp(zeroD_ref, ctrl_grp, zerod_dev, get_id(), this);
    zerod_grp->idx_in_grp = (int32_t)ind_elts.size();
    zerod_grp->idx_in_ctrlgrp = ctrlgrp_idx;
    zerod_grp->obj_proxy = new Tango::DeviceProxy(zeroD_ref.get_full_name().c_str());
    zerod_grp->obj_proxy->set_transparency_reconnection(true);

    return zerod_grp;
}

MeasurementGroup::OneDInGrp *
MeasurementGroup::build_oned(OneDExpChannelPool &oneD_ref)
{
    ControllerPool &ctrl_ref = pool_dev->get_controller(oneD_ref);
    OneDExpChannel_ns::OneDExpChannel *oned_dev = 
        pool_dev->get_oned_device(oneD_ref);

    int32_t ctrlgrp_idx;
    Pool_ns::CtrlGrp *ctrl_grp = NULL;
    try
    {
        ctrl_grp = &get_ctrl_grp_from_id(ctrl_ref.id, ctrlgrp_idx);
    }
    catch(Tango::DevFailed &e)
    {
        ctrl_grp = build_oned_ctrl(ctrl_ref);
        implied_ctrls.push_back(ctrl_grp);
        implied_ctrls_sorted = implied_ctrls;
        sort(implied_ctrls_sorted.begin(), implied_ctrls_sorted.end(), Pool_ns::ictrl_id_cmp);
    }
    
    OneDInGrp *oned_grp = new OneDInGrp(oneD_ref,ctrl_grp,oned_dev,get_id(),this);
    oned_grp->idx_in_grp = (int32_t)ind_elts.size();
    oned_grp->idx_in_ctrlgrp = ctrlgrp_idx;
    oned_grp->obj_proxy = new Tango::DeviceProxy(oneD_ref.get_full_name().c_str());
    oned_grp->obj_proxy->set_transparency_reconnection(true);
    
    return oned_grp;
}

MeasurementGroup::TwoDInGrp *
MeasurementGroup::build_twod(TwoDExpChannelPool &twoD_ref)
{
    ControllerPool &ctrl_ref = pool_dev->get_controller(twoD_ref);
    TwoDExpChannel_ns::TwoDExpChannel *twod_dev = 
        pool_dev->get_twod_device(twoD_ref);
    
    int32_t ctrlgrp_idx;
    Pool_ns::CtrlGrp *ctrl_grp = NULL;
    try
    {
        ctrl_grp = &get_ctrl_grp_from_id(ctrl_ref.id, ctrlgrp_idx);
    }
    catch(Tango::DevFailed &e)
    {
        ctrl_grp = build_twod_ctrl(ctrl_ref);
        implied_ctrls.push_back(ctrl_grp);
        implied_ctrls_sorted = implied_ctrls;
        sort(implied_ctrls_sorted.begin(), implied_ctrls_sorted.end(), Pool_ns::ictrl_id_cmp);
    }
    
    TwoDInGrp *twod_grp = new TwoDInGrp(twoD_ref,ctrl_grp,twod_dev,get_id(),this);
    twod_grp->idx_in_grp = (int32_t)ind_elts.size();
    twod_grp->idx_in_ctrlgrp = ctrlgrp_idx;
    twod_grp->obj_proxy = new Tango::DeviceProxy(twoD_ref.get_full_name().c_str());
    twod_grp->obj_proxy->set_transparency_reconnection(true);
    
    return twod_grp;
}

MeasurementGroup::PseudoCoInGrp *
MeasurementGroup::build_pc(PseudoCounterPool &pc_ref)
{
    PseudoCounter_ns::PseudoCounter *pc_dev = 
        pool_dev->get_pseudo_counter_device(pc_ref);
    ControllerPool &ctrl_ref = pool_dev->get_controller(pc_ref);

    int32_t ctrlgrp_idx;
    PseudoCoCtrlInGrp *ctrl_grp = NULL;
    try
    {
        ctrl_grp = &get_pc_ctrl_grp_from_id(ctrl_ref.id, ctrlgrp_idx);
    }
    catch(Tango::DevFailed &e)
    {
        ctrl_grp = build_pc_ctrl(ctrl_ref);
        ctrlgrp_idx = implied_pseudo_ctrls.size();
        implied_pseudo_ctrls.push_back(ctrl_grp);
        implied_ctrls_sorted = implied_ctrls;
        sort(implied_ctrls_sorted.begin(), implied_ctrls_sorted.end(), Pool_ns::ictrl_id_cmp);
    }

    PseudoCoInGrp *pc_grp = new PseudoCoInGrp(pc_ref,ctrl_grp,pc_dev,get_id(),this);
    pc_grp->idx_in_grp = (int32_t)ind_elts.size();
    pc_grp->idx_in_ctrlgrp = ctrlgrp_idx;
    pc_grp->obj_proxy = new Tango::DeviceProxy(pc_ref.get_full_name().c_str());
    pc_grp->obj_proxy->set_transparency_reconnection(true);

    Pool_ns::ElemIdVector &ch_elts = pc_ref.ch_elts;

    pc_grp->is_virtual = ch_elts.empty();

    for(unsigned long ul = 0; ul < ch_elts.size(); ul++)
    {
        Pool_ns::ElementId ch_id = ch_elts[ul];
        PoolElement *ch_elem = pool_dev->get_element(ch_id);
        
        SingleValChInGrp *single_elt = NULL;
        try
        {
            ChInGrp &elt = get_channel_from_name(ch_elem->get_name());
            single_elt = static_cast<SingleValChInGrp*>(&elt);
        }
        catch(Tango::DevFailed &e)
        {
            PseudoCounter_ns::PseudoCounter::ChannelType type = pc_dev->get_type_from_index(ul);

            switch(type)
            {
                case PseudoCounter_ns::PseudoCounter::COUNTER_TIMER:
                {
                    CTExpChannelPool &ct_ref = *static_cast<CTExpChannelPool *>(ch_elem);
                    CTInGrp *ct = build_ct(ct_ref);
                    ind_elts.push_back(ct);
                    single_elt = ct;
                    break;
                }
                case PseudoCounter_ns::PseudoCounter::ZEROD:
                {
                    ZeroDExpChannelPool &zerod_ref = *static_cast<ZeroDExpChannelPool *>(ch_elem);
                    ZeroDInGrp *zerod = build_zerod(zerod_ref);
                    ind_elts.push_back(zerod);
                    single_elt = zerod;
                    break;
                }
                case PseudoCounter_ns::PseudoCounter::PSEUDO_COUNTER:
                {
                    PseudoCounterPool &pc_ref = *static_cast<PseudoCounterPool *>(ch_elem);
                    PseudoCoInGrp *pc_elt = build_pc(pc_ref);
                    pseudo_elts.push_back(pc_elt);
                    single_elt = pc_elt;
                    break;
                }
            }
        }
        single_elt->used_by.push_back(pc_grp);
        pc_grp->uses.push_back(single_elt);

        MntGrpEltType type = single_elt->get_type();

        if(CT_EXP_CHANNEL == type)
        {
            CTInGrp *ct_elt = static_cast<CTInGrp*>(single_elt);
            if(find(pc_grp->uses_ct.begin(),pc_grp->uses_ct.end(),ct_elt) == pc_grp->uses_ct.end())
            {
                pc_grp->uses_ct.push_back(ct_elt);
            }
        }
        else if(ZEROD_EXP_CHANNEL == type)
        {
            ZeroDInGrp *zerod_elt = static_cast<ZeroDInGrp*>(single_elt);
            if(find(pc_grp->uses_0D.begin(),pc_grp->uses_0D.end(),zerod_elt) == pc_grp->uses_0D.end())
            {
                pc_grp->uses_0D.push_back(zerod_elt);
            }
        }
        else if(PSEUDO_EXP_CHANNEL == type)
        {
            PseudoCoInGrp *pc_elt = static_cast<PseudoCoInGrp*>(single_elt);
            if(find(pc_grp->uses_pc.begin(),pc_grp->uses_pc.end(),pc_elt) == pc_grp->uses_pc.end())
            {
                for(unsigned long ul = 0 ; ul < pc_elt->uses_ct.size() ; ul++)
                {
                    CTInGrp *ct = pc_elt->uses_ct[ul];
                    if(find(pc_grp->uses_ct.begin(),pc_grp->uses_ct.end(),ct) == pc_grp->uses_ct.end())
                    {
                        pc_grp->uses_ct.push_back(ct);
                    }
                }
                for(unsigned long ul = 0 ; ul < pc_elt->uses_0D.size() ; ul++)
                {
                    ZeroDInGrp *zerod = pc_elt->uses_0D[ul];
                    if(find(pc_grp->uses_0D.begin(),pc_grp->uses_0D.end(),zerod) == pc_grp->uses_0D.end())
                    {
                        pc_grp->uses_0D.push_back(zerod);
                    }
                }
                for(unsigned long ul = 0 ; ul < pc_elt->uses_pc.size() ; ul++)
                {
                    PseudoCoInGrp *pc = pc_elt->uses_pc[ul];
                    if(find(pc_grp->uses_pc.begin(),pc_grp->uses_pc.end(),pc) == pc_grp->uses_pc.end())
                    {
                        pc_grp->uses_pc.push_back(pc);
                    }
                }
                pc_grp->uses_pc.push_back(pc_elt);
            }
        }
    }
    ind_elts_sorted = ind_elts;
    sort(ind_elts.begin(), ind_elts.end(), Pool_ns::ielt_id_cmp);
    return pc_grp;
}

MeasurementGroup::MotorInGrp *
MeasurementGroup::build_motor(MotorPool &motor_ref)
{
    ControllerPool &ctrl_ref = pool_dev->get_controller(motor_ref);
    Motor_ns::Motor *motor_dev = pool_dev->get_motor_device(motor_ref);
    
    int32_t ctrlgrp_idx;
    Pool_ns::CtrlGrp *ctrl_grp = NULL;
    try
    {
        ctrl_grp = &get_ctrl_grp_from_id(ctrl_ref.id, ctrlgrp_idx);
    }
    catch(Tango::DevFailed &e)
    {
        ctrl_grp = build_motor_ctrl(ctrl_ref);
        ctrlgrp_idx = implied_ctrls.size();
        implied_ctrls.push_back(ctrl_grp);
        implied_ctrls_sorted = implied_ctrls;
        sort(implied_ctrls_sorted.begin(), implied_ctrls_sorted.end(), Pool_ns::ictrl_id_cmp);
    }

    MotorInGrp *motor_grp = new MotorInGrp(motor_ref, ctrl_grp, motor_dev, get_id(), this);
    motor_grp->idx_in_grp = (int32_t)ind_elts.size();
    motor_grp->idx_in_ctrlgrp = ctrlgrp_idx;
    motor_grp->obj_proxy = new Tango::DeviceProxy(motor_ref.get_full_name().c_str());
    motor_grp->obj_proxy->set_transparency_reconnection(true);

    return motor_grp;
}

MeasurementGroup::PseudoMotorInGrp *
MeasurementGroup::build_pm(PseudoMotorPool &motor_ref)
{
    ControllerPool &ctrl_ref = pool_dev->get_controller(motor_ref);
    PseudoMotor_ns::PseudoMotor *pm_dev = pool_dev->get_pseudo_motor_device(motor_ref);
    
    int32_t ctrlgrp_idx;
    Pool_ns::CtrlGrp *ctrl_grp = NULL;
    try
    {
        ctrl_grp = &get_ctrl_grp_from_id(ctrl_ref.id, ctrlgrp_idx);
    }
    catch(Tango::DevFailed &e)
    {
        ctrl_grp = build_pm_ctrl(ctrl_ref);
        ctrlgrp_idx = implied_ctrls.size();
        implied_ctrls.push_back(ctrl_grp);
        implied_ctrls_sorted = implied_ctrls;
        sort(implied_ctrls_sorted.begin(), implied_ctrls_sorted.end(), Pool_ns::ictrl_id_cmp);
    }

    PseudoMotorInGrp *motor_grp = new PseudoMotorInGrp(motor_ref, ctrl_grp, pm_dev, get_id(), this);
    motor_grp->idx_in_grp = (int32_t)ind_elts.size();
    motor_grp->idx_in_ctrlgrp = ctrlgrp_idx;
    motor_grp->obj_proxy = new Tango::DeviceProxy(motor_ref.get_full_name().c_str());
    motor_grp->obj_proxy->set_transparency_reconnection(true);

    return motor_grp;
}

void MeasurementGroup::get_limits(MntGrpEltType type, int32_t &start, int32_t &end)
{
    switch(type)
    {
        case ANY_CHANNEL:
        {
            start = 0;
            end = ind_elt_nb;
        }
        break;
        case CT_EXP_CHANNEL:
        {
            start = 0;
            end = ct_nb;
        }
        break;
        case ZEROD_EXP_CHANNEL:
        {
            start = ct_nb;
            end = start + zeroD_nb;
        }
        break;
        case ONED_EXP_CHANNEL:
        {
            start = ct_nb + zeroD_nb;
            end = start + oneD_nb;
        }
        break;
        case TWOD_EXP_CHANNEL:
        {
            start = ct_nb + zeroD_nb + oneD_nb;
            end = start + twoD_nb;
        }
        case MOTOR_CHANNEL:
        {
            start = ct_nb + zeroD_nb + oneD_nb + twoD_nb;
            end = start + mot_nb;
        }
        break;

// Pseudos have different indexes because they are not stored in the ind_elts
// vector but on the pseudo_elts vector instead
        case PSEUDO_EXP_CHANNEL:
        {
            start = 0;
            end = pc_nb;
        }
        break;
    }
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::create_dyn_attr
//
// description : 	Creates the dynamic attributes
//
//-----------------------------------------------------------------------------
void MeasurementGroup::create_dyn_attr()
{
    DEBUG_STREAM << "Adding dynamic attributes for measurement group " << device_name << endl;

//
// Don't create extra attributes for the ghost measurement group.
// It simply doesn't need them.
//
    if(is_ghost())
    {
        return;
    }

    for(long idx = 0; idx < ct_nb; idx++)
        create_one_extra_attr(pool_dev->get_element(ct_List[idx])->get_name(), COTI_ELEM);

    for(long idx = 0; idx < zeroD_nb; idx++)
        create_one_extra_attr(pool_dev->get_element(zeroDExpChannel_List[idx])->get_name(), ZEROD_ELEM);

    for(long idx = 0; idx < oneD_nb; idx++)
        create_one_extra_attr(pool_dev->get_element(oneDExpChannel_List[idx])->get_name(), ONED_ELEM);

    for(long idx = 0; idx < twoD_nb; idx++)
        create_one_extra_attr(pool_dev->get_element(twoDExpChannel_List[idx])->get_name(), TWOD_ELEM);

    for(long idx = 0; idx < pc_nb; idx++)
        create_one_extra_attr(pool_dev->get_element(pseudoCounter_List[idx])->get_name(), PSEUDO_COUNTER_ELEM);

    for(long idx = 0; idx < mot_nb; idx++)
        create_one_extra_attr(pool_dev->get_element(motor_List[idx])->get_name(), MOTOR_ELEM, false);

    DEBUG_STREAM << "Finished adding dynamic attributes for measurement group "
                 << device_name << endl;
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::create_one_extra_attr
//
// description : 	Create one dynamic attribute for the channel
//
// args : - name : name of the data aquisition element
//			type : attribute element type
//          change_event  : tell if the attribute will be change event enabled
//
//-----------------------------------------------------------------------------
void MeasurementGroup::create_one_extra_attr(const string &name,
                                             ElementType type,
                                             bool change_event /* = true */)
{
    if(is_ghost())
    {
        Tango::Except::throw_exception(
            (const char *)"Pool_InvalidIntegrationTime",
            (const char *)"Unexpected call to create extra attributes on the ghost measurement group.",
            (const char *)"MeasurementGroup::create_one_extra_attr");
    }

//
// Create the attribute
//
    string name_lower(name + DYN_ATTR_SUFIX);
    transform(name_lower.begin(),name_lower.end(),
              name_lower.begin(),::tolower);

    Tango::Attr *new_attr = NULL;

    if (type == COTI_ELEM)
        new_attr = new Dou_CT_R_Attrib(name_lower);
    else if (type == ZEROD_ELEM)
        new_attr = new Dou_R_Scl_Attrib(name_lower);
    else if (type == PSEUDO_COUNTER_ELEM)
        new_attr = new Dou_PC_R_Attrib(name_lower);
    else if (type == ONED_ELEM)
    {
        const int32_t DIMENSION = 10000;


        map<string,double*>::iterator map_ite = spectrum_data.find(name_lower);
        if (map_ite == spectrum_data.end())
        {
            double *data = new double[DIMENSION];
            for(int32_t l = 0; l < DIMENSION; l++) data[l] = (double)l;

            pair<map<string,double*>::iterator,bool> status;
            status = spectrum_data.insert(make_pair(name_lower,data));

            if (status.second == false)
            {
                delete [] data;
                TangoSys_OMemStream o;
                o << "Can't create storage for attribute ";
                o << name_lower << ends;
                Tango::Except::throw_exception(
                    (const char *)"Pool_CantCreateExtraDataStorage",o.str(),
                    (const char *)"MeasurementGroup::create_one_extra_attr()");
            }
        }
        new_attr = new Dou_R_Sptrm_Attrib(name_lower, DIMENSION);
    }
    else if (type == TWOD_ELEM)
    {
        const int32_t DIMENSION_X = 2000;
        const int32_t DIMENSION_Y = 2000;

        map<string,double*>::iterator map_ite = image_data.find(name_lower);
        if (map_ite == image_data.end())
        {
            double *data = new double[DIMENSION_X*DIMENSION_Y]; // 16x16

            for(int32_t row = 0; row < DIMENSION_X; row++)
                for(int32_t col = 0; col < DIMENSION_X; col++)
                    data[row*col] = (double)col;

            pair<map<string,double*>::iterator,bool> status;
            status = image_data.insert(make_pair(name_lower,data));

            if (status.second == false)
            {
                delete [] data;
                TangoSys_OMemStream o;
                o << "Can't create storage for attribute ";
                o << name_lower << ends;
                Tango::Except::throw_exception(
                    (const char *)"Pool_CantCreateExtraDataStorage",o.str(),
                    (const char *)"MeasurementGroup::create_one_extra_attr()");
            }
        }
        new_attr = new Dou_R_Img_Attrib(name_lower, DIMENSION_X, DIMENSION_Y);
    }
    else if (type == MOTOR_ELEM)
        new_attr = new Dou_MOT_R_Attrib(name_lower);

    this->add_attribute(new_attr);

    DEBUG_STREAM << "Added dyn attribute " << name_lower << " for channel " << name << endl;

    if(change_event == true)
    {
        Tango::Attribute &attr = dev_attr->get_attr_by_name(name_lower.c_str());
        attr.set_change_event(true);
    }
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::remove_unwanted_dyn_attr_from_device
//
// description : 	Remove the dynamic attributes (if any) attached to this
//					device
//
//-----------------------------------------------------------------------------
void MeasurementGroup::remove_unwanted_dyn_attr_from_device()
{
    if(is_ghost())
        return;

//
// Get how many attributes this device has
// (static and added)
//

    int32_t nb_static = utils->get_static_attr_nb(get_device_class());
    int32_t nb_att = dev_attr->get_attr_nb();

    int32_t nb_added_attr = usr_elt_nb;

//
// Leave method if the device does not have any unwanted attribute
//

    int32_t nb_unwanted = nb_att - (nb_static + nb_added_attr);

//
// Get the number of real "static" attribute (remove the state
// and status one)
//
    nb_static = nb_static - 2;

    if (nb_unwanted > 0)
    {
//
// Build the complete list of extra attributes
//
        vector<string> data_aq_attr;
        data_aq_attr.reserve(usr_elt_nb);

        for(int32_t idx = 0 ; idx < ct_nb ; idx++)
        {
            std::string attr_name = pool_dev->get_element(ct_List[idx])->get_name();
            attr_name += DYN_ATTR_SUFIX;
            data_aq_attr.push_back(attr_name);
        }
        for(int32_t idx = 0 ; idx < zeroD_nb ; idx++)
        {
            std::string attr_name = pool_dev->get_element(zeroDExpChannel_List[idx])->get_name();
            attr_name += DYN_ATTR_SUFIX;
            data_aq_attr.push_back(attr_name);
        }
        for(int32_t idx = 0 ; idx < oneD_nb ; idx++)
        {
            std::string attr_name = pool_dev->get_element(oneDExpChannel_List[idx])->get_name();
            attr_name += DYN_ATTR_SUFIX;
            data_aq_attr.push_back(attr_name);
        }
        for(int32_t idx = 0 ; idx < twoD_nb ; idx++)
        {
            std::string attr_name = pool_dev->get_element(twoDExpChannel_List[idx])->get_name();
            attr_name += DYN_ATTR_SUFIX;
            data_aq_attr.push_back(attr_name);
        }
        for(int32_t idx = 0 ; idx < pc_nb ; idx++)
        {
            std::string attr_name = pool_dev->get_element(pseudoCounter_List[idx])->get_name();
            attr_name += DYN_ATTR_SUFIX;
            data_aq_attr.push_back(attr_name);
        }
        for(int32_t idx = 0 ; idx < mot_nb ; idx++)
        {
            std::string attr_name = pool_dev->get_element(motor_List[idx])->get_name();
            attr_name += DYN_ATTR_SUFIX;
            data_aq_attr.push_back(attr_name);
        }

        assert((int32_t)data_aq_attr.size() == usr_elt_nb);

        vector<string> remove_attr_list;
//
// Removing unwanted extra attributes
//
        for(int32_t idx = nb_static; idx < nb_att; idx++)
        {
            bool continue_loop = false;
            string &att_name_lower = dev_attr->get_attr_by_ind(idx).get_name_lower();
            if ((att_name_lower == "state") || (att_name_lower == "status"))
                continue;
            for(int32_t extraidx = 0; extraidx < usr_elt_nb; extraidx++)
            {
                string extra_name_lower(data_aq_attr[extraidx]);
                transform(extra_name_lower.begin(),extra_name_lower.end(),extra_name_lower.begin(),::tolower);
                if(extra_name_lower == att_name_lower)
                {
                    continue_loop = true;
                    break;
                }
            }
            if(continue_loop)
                continue;
            remove_attr_list.push_back(att_name_lower);
        }
        
        
        for(vector<string>::size_type rem_idx = 0; 
            rem_idx < remove_attr_list.size(); rem_idx++)
        {
#if TANGO_VERSION_HEX < 0x07020000
            dev_attr->remove_attribute(remove_attr_list[rem_idx]);
#else
            dev_attr->remove_attribute(remove_attr_list[rem_idx], true);
#endif
        }
    }

//
// Update attribute indexes
//
    update_attr2channel_indexes();
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::update_attr2channel_indexes
//
// description : 	Update the extra attribute index corresponding to each
//                  experiment channel in the measurement group
//
//-----------------------------------------------------------------------------
void MeasurementGroup::update_attr2channel_indexes()
{
    int32_t nb_static = utils->get_static_attr_nb(get_device_class()) - 2;

    attr_channel_map.clear();
    attr_name_channel_map.clear();

    for(int32_t idx = nb_static; idx < nb_static + usr_elt_nb; idx++)
    {
        Tango::Attribute &attr = dev_attr->get_attr_by_ind(idx);
        string &attr_name = attr.get_name();
        string channel_name = attr_name;
        channel_name = channel_name.substr(0,attr.get_name_lower().rfind("_value"));

        ChInGrp &ch = get_channel_from_name(channel_name);
        ch.attr_idx = idx;

        attr_channel_map[idx] = &ch;
        attr_name_channel_map[attr_name] = &ch;
    }
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::is_ExtraAttr_allowed
//
// description : 	Default metod for the extra attribute is_allowed method
//
//-----------------------------------------------------------------------------
bool MeasurementGroup::is_ExtraAttr_allowed(Tango::AttReqType type)
{
    if (get_state() == Tango::FAULT	||
        get_state() == Tango::UNKNOWN)
        return false;
    else
    {
        if ((type == Tango::WRITE_REQ) && (pool_sd == true))
            return false;
    }
    return true;
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::get_device_property()
//
// description : 	Read the device properties from database.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::get_device_property()
{
    //	Initialize your default values here (if not done with  POGO).
    //------------------------------------------------------------------
    PoolGroupBaseDev::get_device_property();

    //	Read device properties from database.(Automatic code generation)
    //------------------------------------------------------------------
    Tango::DbData	dev_prop;
    dev_prop.push_back(Tango::DbDatum("User_group_elt"));
    dev_prop.push_back(Tango::DbDatum("Ct_List"));
    dev_prop.push_back(Tango::DbDatum("ZeroDExpChannel_List"));
    dev_prop.push_back(Tango::DbDatum("OneDExpChannel_List"));
    dev_prop.push_back(Tango::DbDatum("TwoDExpChannel_List"));
    dev_prop.push_back(Tango::DbDatum("Phys_group_elt"));
    dev_prop.push_back(Tango::DbDatum("pseudoCounter_List"));
    dev_prop.push_back(Tango::DbDatum("motor_List"));
    
    //	Call database and extract values
    //--------------------------------------------
    if (Tango::Util::instance()->_UseDb==true)
        get_db_device()->get_property(dev_prop);
    Tango::DbDatum	def_prop, cl_prop;
    MeasurementGroupClass	*ds_class =
        (static_cast<MeasurementGroupClass *>(get_device_class()));
    int	i = -1;

    //	Try to initialize User_group_elt from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  user_group_elt;
    //	Try to initialize User_group_elt from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  user_group_elt;
    //	And try to extract User_group_elt value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  user_group_elt;

    //	Try to initialize Ct_List from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  ct_List;
    //	Try to initialize Ct_List from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  ct_List;
    //	And try to extract Ct_List value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  ct_List;

    //	Try to initialize ZeroDExpChannel_List from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  zeroDExpChannel_List;
    //	Try to initialize ZeroDExpChannel_List from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  zeroDExpChannel_List;
    //	And try to extract ZeroDExpChannel_List value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  zeroDExpChannel_List;

    //	Try to initialize OneDExpChannel_List from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  oneDExpChannel_List;
    //	Try to initialize OneDExpChannel_List from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  oneDExpChannel_List;
    //	And try to extract OneDExpChannel_List value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  oneDExpChannel_List;

    //	Try to initialize TwoDExpChannel_List from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  twoDExpChannel_List;
    //	Try to initialize TwoDExpChannel_List from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  twoDExpChannel_List;
    //	And try to extract TwoDExpChannel_List value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  twoDExpChannel_List;

    //	Try to initialize Phys_group_elt from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  phys_group_elt;
    //	Try to initialize Phys_group_elt from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  phys_group_elt;
    //	And try to extract Phys_group_elt value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  phys_group_elt;

    //	Try to initialize pseudoCounter_List from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  pseudoCounter_List;
    //	Try to initialize pseudoCounter_List from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  pseudoCounter_List;
    //	And try to extract pseudoCounter_List value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  pseudoCounter_List;

    //	Try to initialize motor_List from class property
    cl_prop = ds_class->get_class_property(dev_prop[++i].name);
    if (cl_prop.is_empty()==false)	cl_prop  >>  motor_List;
    //	Try to initialize motor_List from default device value
    def_prop = ds_class->get_default_device_property(dev_prop[i].name);
    if (def_prop.is_empty()==false)	def_prop  >>  motor_List;
    //	And try to extract motor_List value from database
    if (dev_prop[i].is_empty()==false)	dev_prop[i]  >> motor_List;

    //	End of Automatic code generation
    //------------------------------------------------------------------

}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::always_executed_hook()
//
// description : 	method always executed before any command is executed
//
//-----------------------------------------------------------------------------
void MeasurementGroup::always_executed_hook()
{
    PoolGroupBaseDev::always_executed_hook();

//
// Check that the controllers implied in this group are correctly built
//
    vector<CtrlGrp*>::iterator impl_ctrl_ite;
    for (impl_ctrl_ite = implied_ctrls.begin();impl_ctrl_ite != implied_ctrls.end();++impl_ctrl_ite)
    {
        ControllerPool *cp = (*impl_ctrl_ite)->ct;

        if ((cp->ctrl_class_built == false) || (cp->get_controller() == NULL))
        {
            set_state(Tango::FAULT);
            break;
        }
    }

    if(get_state() != Tango::FAULT)
    {
        vector<PseudoCoCtrlInGrp*>::iterator impl_pseudo_ctrl_ite;

        for (impl_pseudo_ctrl_ite = implied_pseudo_ctrls.begin();
             impl_pseudo_ctrl_ite != implied_pseudo_ctrls.end();
             ++impl_pseudo_ctrl_ite)
        {
            ControllerPool *cp = (*impl_pseudo_ctrl_ite)->ct;

            if ((cp->ctrl_class_built == false) || (cp->get_controller() == NULL))
            {
                set_state(Tango::FAULT);
                break;
            }
        }
    }
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_attr_hardware
//
// description : 	Hardware acquisition for attributes.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::read_attr_hardware(vector<long> &attr_list)
{
    DEBUG_STREAM << "MeasurementGroup::read_attr_hardware(vector<long> &attr_list) entering... "<< endl;
    //	Add your own code here

    if (get_state() != Tango::MOVING)
    {
//
// 'Eventually' read values from the hardware
//
        vector<long>::const_iterator
            begin = attr_list.begin(),
            end = attr_list.end();

        read_ct_values_from_ctrls(begin, end);
        read_zerod_values_from_ctrls(begin, end);
        read_oned_values_from_ctrls(begin,end);
        read_twod_values_from_ctrls(begin,end);
        read_pc_values_from_ctrls(begin, end);
        read_motor_values_from_ctrls(begin, end);
    }
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_pc_values_from_ctrls
//
// description : 	Hardware acquisition for attributes.
//
//-----------------------------------------------------------------------------
template<class LongIterator>
void MeasurementGroup::read_pc_values_from_ctrls(LongIterator begin, LongIterator end)
{
    vector<PseudoCoInGrp*> involved_channels;

//
// Retrive all Pseudo channels from the "<channel>_value" attributes in the list
//
    typedef typename std::iterator_traits<LongIterator>::value_type value_type;
    for(LongIterator it = begin; it != end; ++it)
    {
        value_type attr_idx(*it);

        ChInGrp* ch = attr_channel_map[attr_idx];

        if(ch == NULL || ch->get_type() != PSEUDO_EXP_CHANNEL)
            continue;
//
// If it is an attribute corresponding to a pseudo counter value
//
        PseudoCoInGrp *pseudo = static_cast<PseudoCoInGrp*>(ch);
        if(find(involved_channels.begin(),involved_channels.end(),pseudo) == involved_channels.end())
        {
            for(unsigned long ul = 0 ; ul < pseudo->uses_pc.size() ; ul++)
            {
                PseudoCoInGrp *pc = pseudo->uses_pc[ul];
                if(find(involved_channels.begin(),involved_channels.end(),pc) == involved_channels.end())
                    involved_channels.push_back(pc);
            }
            involved_channels.push_back(pseudo);
        }
    }

//
// If there are no "<channel>_value" attributes to be read return
//
    if(involved_channels.empty())
        return;

    vector<PseudoCoInGrp*>::iterator it = involved_channels.begin();
    for(; it != involved_channels.end(); it++)
    {
        (*it)->ReadOne();
    }
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_zerod_values_from_ctrls
//
// description : 	Hardware acquisition for attributes.
//
//-----------------------------------------------------------------------------
template<class LongIterator>
void MeasurementGroup::read_zerod_values_from_ctrls(LongIterator begin, LongIterator end)
{
//
// key = 	channel ID in the Pool
// value =	pointer to channel struct in the measurement group
// A map is used here to avoid duplicates
//
    map<Pool_ns::ElementId, ZeroDInGrp*> involved_channels;

//
// Retrive all ZeroD channels from the "<channel>_value" attributes in the list
//
    typedef typename std::iterator_traits<LongIterator>::value_type value_type;
    for(LongIterator it = begin; it != end; ++it)
    {
        value_type attr_idx(*it);

        ChInGrp* ch = attr_channel_map[attr_idx];

        if(ch == NULL) continue;
//
// If it is an attribute corresponding to a 0D value
        if(ch->get_type() == ZEROD_EXP_CHANNEL)
        {
            ZeroDInGrp *zerod = static_cast<ZeroDInGrp*>(ch);
            involved_channels[zerod->id] = zerod;
        }

//
// If it is an attribute corresponding to a pseudo counter value
//
        else if(ch->get_type() == PSEUDO_EXP_CHANNEL)
        {
            PseudoCoInGrp *pseudo = static_cast<PseudoCoInGrp*>(ch);
            for(unsigned long ul = 0 ; ul < pseudo->uses_0D.size() ; ul++)
            {
                ZeroDInGrp *zerod = pseudo->uses_0D[ul];
                involved_channels[zerod->id] = zerod;
            }
        }
    }

//
// If there are no "<channel>_value" attributes to be read return
//
    if(involved_channels.empty())
        return;

    map<Pool_ns::ElementId, ZeroDInGrp*>::iterator it = involved_channels.begin();

    for(;it != involved_channels.end(); it++)
    {
        ZeroDInGrp *zerod = (*it).second;
        Tango::DeviceAttribute dev_attr = zerod->obj_proxy->read_attribute("CumulatedValue");
        dev_attr >> (zerod->value);
    }
}
//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_oned_values_from_ctrls
// 
// description : 	Hardware acquisition for attributes.
//
//-----------------------------------------------------------------------------
template<class LongIterator>
void MeasurementGroup::read_oned_values_from_ctrls(LongIterator begin, LongIterator end)
{
//
// key = 	channel ID in the Pool 
// value =	pointer to channel struct in the measurement group 
// A map is used here to avoid duplicates 
//	
    map<Pool_ns::ElementId, OneDInGrp*> involved_channels;

//
// Retrive all OneD channels from the "<channel>_value" attributes in the list
//	
    typedef typename std::iterator_traits<LongIterator>::value_type value_type;
    for(LongIterator it = begin; it != end; ++it)
    {
        value_type attr_idx(*it);
        
        ChInGrp* ch = attr_channel_map[attr_idx];
        
        if(ch == NULL) continue;
//
// If it is an attribute corresponding to a 1D value 
        if(ch->get_type() == ONED_EXP_CHANNEL)
        {
            OneDInGrp *oned = static_cast<OneDInGrp*>(ch); 
            involved_channels[oned->id] = oned;
        }
        
    }
    
//			  
// If there are no "<channel>_value" attributes to be read return
//		
    if(involved_channels.empty())
        return;	

    map<Pool_ns::ElementId, OneDInGrp*>::iterator it = involved_channels.begin();

    vector<double> value_tmp;

    for(;it != involved_channels.end(); it++)
    {
        OneDInGrp *oned = (*it).second;
        Tango::DeviceAttribute dev_attr = oned->obj_proxy->read_attribute("Data");
        dev_attr >> value_tmp;
        for (vector<double>::size_type i = 0; i < value_tmp.size(); i++)
        {   
            oned->value[i] = value_tmp[i];
        }
        oned->data_length = value_tmp.size();
 
    }
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_twod_values_from_ctrls
// 
// description : 	Hardware acquisition for attributes.
//
//-----------------------------------------------------------------------------
template<class LongIterator>
void MeasurementGroup::read_twod_values_from_ctrls(LongIterator begin, LongIterator end)
{
//
// key = 	channel ID in the Pool 
// value =	pointer to channel struct in the measurement group 
// A map is used here to avoid duplicates 
//	
    map<long, TwoDInGrp*> involved_channels;

//
// Retrive all TwoD channels from the "<channel>_value" attributes in the list
//	
    typedef typename std::iterator_traits<LongIterator>::value_type value_type;
    for(LongIterator it = begin; it != end; ++it)
    {
        value_type attr_idx(*it);
        
        ChInGrp* ch = attr_channel_map[attr_idx];
        
        if(ch == NULL) continue;
//
// If it is an attribute corresponding to a 2D value 
        if(ch->get_type() == TWOD_EXP_CHANNEL)
        {
            TwoDInGrp *twod = static_cast<TwoDInGrp*>(ch); 
            involved_channels[twod->id] = twod;
        }
        
    }
    
//			  
// If there are no "<channel>_value" attributes to be read return
//		
    if(involved_channels.empty())
        return;	

    map<long, TwoDInGrp*>::iterator it = involved_channels.begin();

    vector<double> value_tmp;
    long xdim;
    long ydim;

    for(;it != involved_channels.end(); it++)
    {
        TwoDInGrp *twod = (*it).second;
        Tango::DeviceAttribute dev_attr = twod->obj_proxy->read_attribute("Value");
        dev_attr >> value_tmp;
        for (std::vector<double>::size_type i = 0; i < value_tmp.size(); i++)
        {   
            twod->value[i] = value_tmp[i];
        }
        Tango::DeviceAttribute dev_attr_xdim = twod->obj_proxy->read_attribute("XDim");
        dev_attr_xdim >> xdim;
        twod->xdim = xdim;
        Tango::DeviceAttribute dev_attr_ydim = twod->obj_proxy->read_attribute("YDim");
        dev_attr_ydim >> ydim;
        twod->ydim = ydim;
    }
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_ct_values_from_ctrls
//
// description : 	Hardware acquisition for attributes.
//
//-----------------------------------------------------------------------------
template<class LongIterator>
void MeasurementGroup::read_ct_values_from_ctrls(LongIterator begin, LongIterator end)
{
    DEBUG_STREAM << "MeasurementGroup::read_ct_values_from_ctrls(vector<long> &attr_list) entering... "<< endl;

//
// key = 	channel ID in the Pool
// value =	pointer to channel struct in the measurement group
// A map is used here to avoid duplicates
//
    map<Pool_ns::ElementId, CTInGrp*> involved_channels;

//
// key = 	controller index in the measurement group
// value =	pointer to controller struct in the measurement group
// A map is used here to avoid duplicates
//
    map<Pool_ns::ElementId, ChCtrlInGrp*> involved_ctrls;

//
// Retrive all CT channels from the "<channel>_value" attributes in the list
//
    typedef typename std::iterator_traits<LongIterator>::value_type value_type;
    for(LongIterator it = begin; it != end; ++it)
    {
        value_type attr_idx(*it);

        ChInGrp* ch = attr_channel_map[attr_idx];

        if(ch == NULL) continue;
//
// If it is an attribute corresponding to a counter/timer value
        if(ch->get_type() == CT_EXP_CHANNEL)
        {
            CTInGrp *ct = static_cast<CTInGrp*>(ch);
            involved_channels[ct->id] = ct;

            int32_t ctrl_idx = ct->get_ctrl_idx_in_grp();
            ChCtrlInGrp *ch_ctrl = static_cast<ChCtrlInGrp*>(implied_ctrls[ctrl_idx]);
            involved_ctrls[ctrl_idx] = ch_ctrl;
        }

//
// If it is an attribute corresponding to a pseudo counter value
//
        else if(ch->get_type() == PSEUDO_EXP_CHANNEL)
        {
            PseudoCoInGrp *pseudo = static_cast<PseudoCoInGrp*>(attr_channel_map[attr_idx]);
            for(unsigned long ul = 0 ; ul < pseudo->uses_ct.size() ; ul++)
            {
                CTInGrp *ct = pseudo->uses_ct[ul];
                involved_channels[ct->id] = ct;

                int32_t ctrl_idx = ct->get_ctrl_idx_in_grp();
                ChCtrlInGrp *ch_ctrl = static_cast<ChCtrlInGrp*>(implied_ctrls[ctrl_idx]);
                involved_ctrls[ctrl_idx] = ch_ctrl;
            }
        }
    }

//
// If there are no "<channel>_value" attributes to be read return
//
    if(involved_channels.empty())
        return;



    vector<Controller*> failed;
//
//	Lock the implied channels
//
    DEBUG_STREAM << "read_ct_values_from_ctrls() - locking selected channels"<<endl;
    for_each(involved_channels.begin(), involved_channels.end(),
             with_data( mem_fun(&IndEltGrp::Lock)) );

//
// Lock the implied controllers
//
    for_each(involved_ctrls.begin(),involved_ctrls.end(),
             with_data( bind2nd(mem_fun(&CtrlGrp::Lock),&failed)) );

    string except_func;
    try
    {
//
// Send PreReadAll to all implied controllers
//
        except_func = "PreReadAll";
        for_each(involved_ctrls.begin(), involved_ctrls.end(),
                 with_data( mem_fun(&ChCtrlInGrp::PreReadAll) ));

//
// Send PreReadOne to each implied channel
//
        except_func = "PreReadOne";
        for_each(involved_channels.begin(), involved_channels.end(),
                 with_data( mem_fun(&ChInGrp::PreReadOne) ));

//
// Send ReadAll to all implied controllers
//
        except_func = "ReadAll";
        for_each(involved_ctrls.begin(), involved_ctrls.end(),
                 with_data( mem_fun(&ChCtrlInGrp::ReadAll) ));

//
// Get each channel value
//
        except_func = "ReadOne";
        for_each(involved_channels.begin(), involved_channels.end(),
                 with_data( mem_fun(&ChInGrp::ReadOne) ));
    }
    catch (Tango::DevFailed &e)
    {
//
// Unlock the implied controllers
//
        for_each(involved_ctrls.rbegin(),involved_ctrls.rend(),
                 with_data( mem_fun(&CtrlGrp::Unlock) ));
//
// Unlock the implied channels
//
        DEBUG_STREAM << "read_ct_values_from_ctrls() - Unlocking selected channels (ir error)"<<endl;
        for_each(involved_channels.rbegin(), involved_channels.rend(),
                 with_data( mem_fun(&IndEltGrp::Unlock) ));

        TangoSys_OMemStream o;
        o << "Impossible to read value in measurement group " << get_name();
        o << ". The " << except_func << "() controller method throws an exception" << ends;
        Tango::Except::re_throw_exception(e,
                (const char *)"MeasurementGroup_ControllerFailed",o.str(),
                (const char *)"MeasurementGroup::read_attr_hardware");
    }

//
// Unlock the implied controllers
//
    for_each(involved_ctrls.rbegin(),involved_ctrls.rend(),
             with_data( mem_fun(&CtrlGrp::Unlock) ));
//
// Unlock the implied channels
//
    DEBUG_STREAM << "read_ct_values_from_ctrls() - Unlocking selected channels"<<endl;
    for_each(involved_channels.rbegin(), involved_channels.rend(),
             with_data( mem_fun(&IndEltGrp::Unlock) ));
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_motor_values_from_ctrls
//
// description : 	Hardware acquisition for attributes.
//
//-----------------------------------------------------------------------------
template<class LongIterator>
void MeasurementGroup::read_motor_values_from_ctrls(LongIterator begin, LongIterator end)
{
    DEBUG_STREAM << "MeasurementGroup::read_motor_values_from_ctrls(vector<long> &attr_list) entering... "<< endl;

//
// key = 	channel ID in the Pool
// value =	pointer to channel struct in the measurement group
// A map is used here to avoid duplicates
//
    map<Pool_ns::ElementId, MotorInGrp*> involved_channels;

//
// key = 	controller index in the measurement group
// value =	pointer to controller struct in the measurement group
// A map is used here to avoid duplicates
//
    map<Pool_ns::ElementId, ChCtrlInGrp*> involved_ctrls;

//
// Retrive all CT channels from the "<channel>_value" attributes in the list
//
    typedef typename std::iterator_traits<LongIterator>::value_type value_type;
    for(LongIterator it = begin; it != end; ++it)
    {
        value_type attr_idx(*it);

        ChInGrp* ch = attr_channel_map[attr_idx];

        if(ch == NULL) continue;
//
// If it is an attribute corresponding to a physical motor value
        if(ch->get_type() == MOTOR_CHANNEL)
        {
            MotorInGrp *motor = static_cast<MotorInGrp*>(ch);
            involved_channels[motor->id] = motor;

            int32_t ctrl_idx = motor->get_ctrl_idx_in_grp();
            ChCtrlInGrp *ch_ctrl = static_cast<ChCtrlInGrp*>(implied_ctrls[ctrl_idx]);
            involved_ctrls[ctrl_idx] = ch_ctrl;
        }        
    }

//
// If there are no "<channel>_value" attributes to be read return
//
    if(involved_channels.empty())
        return;

    vector<Controller*> failed;
//
//	Lock the implied channels
//
    DEBUG_STREAM << "read_motor_values_from_ctrls() - locking selected channels"<<endl;
    for_each(involved_channels.begin(), involved_channels.end(),
             with_data( mem_fun(&IndEltGrp::Lock)) );

//
// Lock the implied controllers
//
    for_each(involved_ctrls.begin(),involved_ctrls.end(),
             with_data( bind2nd(mem_fun(&CtrlGrp::Lock),&failed)) );

    string except_func;
    try
    {
//
// Send PreReadAll to all implied controllers
//
        except_func = "PreReadAll";
        for_each(involved_ctrls.begin(), involved_ctrls.end(),
                 with_data( mem_fun(&ChCtrlInGrp::PreReadAll) ));

//
// Send PreReadOne to each implied channel
//
        except_func = "PreReadOne";
        for_each(involved_channels.begin(), involved_channels.end(),
                 with_data( mem_fun(&ChInGrp::PreReadOne) ));

//
// Send ReadAll to all implied controllers
//
        except_func = "ReadAll";
        for_each(involved_ctrls.begin(), involved_ctrls.end(),
                 with_data( mem_fun(&ChCtrlInGrp::ReadAll) ));

//
// Get each channel value
//
        except_func = "ReadOne";
        for_each(involved_channels.begin(), involved_channels.end(),
                 with_data( mem_fun(&ChInGrp::ReadOne) ));
    }
    catch (Tango::DevFailed &e)
    {
//
// Unlock the implied controllers
//
        for_each(involved_ctrls.rbegin(),involved_ctrls.rend(),
                 with_data( mem_fun(&CtrlGrp::Unlock) ));
//
// Unlock the implied channels
//
        DEBUG_STREAM << "read_motor_values_from_ctrls() - Unlocking selected channels (ir error)"<<endl;
        for_each(involved_channels.rbegin(), involved_channels.rend(),
                 with_data( mem_fun(&IndEltGrp::Unlock) ));

        TangoSys_OMemStream o;
        o << "Impossible to read value in measurement group " << get_name();
        o << ". The " << except_func << "() controller method throws an exception" << ends;
        Tango::Except::re_throw_exception(e,
                (const char *)"MeasurementGroup_ControllerFailed",o.str(),
                (const char *)"MeasurementGroup::read_attr_hardware");
    }

//
// Unlock the implied controllers
//
    for_each(involved_ctrls.rbegin(),involved_ctrls.rend(),
             with_data( mem_fun(&CtrlGrp::Unlock) ));
//
// Unlock the implied channels
//
    DEBUG_STREAM << "read_motor_values_from_ctrls() - Unlocking selected channels"<<endl;
    for_each(involved_channels.rbegin(), involved_channels.rend(),
             with_data( mem_fun(&IndEltGrp::Unlock) ));
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_values
//
// description : 	Simulates reading the channel values. This method should
//                  be called only when you have the lock on this device.
//
//-----------------------------------------------------------------------------

void MeasurementGroup::read_values(MntGrpEltType type /*= ANY_CHANNEL*/)
{
    set<int32_t> attr_set;

    if(type == PSEUDO_EXP_CHANNEL)
    {
//
// Read the pseudo counter values for those pseudo counters that don't have
// any physical counters attached to them (we call them virtual pseudo counters)
//
        for(unsigned long ul = 0; ul < pseudo_elts.size(); ul++)
        {
            PseudoCoInGrp *pc = pseudo_elts[ul];
            if(pc->attr_idx >= 0 && pc->is_virtual == true)
            {
                attr_set.insert(pc->attr_idx);
            }
        }
    }
    else
    {
        int32_t start_idx, end_idx;
        get_limits(type,start_idx,end_idx);
        //long value_nb = end_idx - start_idx;

    //
    // determine which Counter/timer attributes to read
    //

        for(int32_t l = start_idx; l < end_idx ; l++)
        {
            ChInGrp *ch = static_cast<ChInGrp*>(ind_elts[l]);
            attr_set.insert(ch->attr_idx);
        }

    //
    // Determine if any pseudo counters will also be implicitly updated and update
    // the values from the controllers
    //
        if(type == CT_EXP_CHANNEL ||
           type == ZEROD_EXP_CHANNEL ||
           type == ONED_EXP_CHANNEL ||
           type == ANY_CHANNEL)
        {
            for(unsigned long ul = 0; ul < pseudo_elts.size(); ul++)
            {
                PseudoCoInGrp *pc = pseudo_elts[ul];

                // Don't worry to much about adding repeated channels. The
                // read_xxx_values_from_ctrls will filter this.

                if (type == CT_EXP_CHANNEL || type == ANY_CHANNEL)
                {
                    if(pc->uses_ct.size() > 0 && pc->attr_idx >= 0)
                    {
                        attr_set.insert(pc->attr_idx);
                        //value_nb++;
                        continue;
                    }
                }
                if (type == ZEROD_EXP_CHANNEL || type == ANY_CHANNEL)
                {
                    if(pc->uses_0D.size() > 0 && pc->attr_idx >= 0)
                    {
                        attr_set.insert(pc->attr_idx);
                        //value_nb++;
                    }
                }
                if (type == ONED_EXP_CHANNEL || type == ANY_CHANNEL)
                {
                    if(pc->uses_1D.size() > 0 && pc->attr_idx >= 0)
                    {
                        attr_set.insert(pc->attr_idx);
                        //value_nb++;
                    }
                }
            }
        }
    }

    set<int32_t>::const_iterator
        begin = attr_set.begin(),
        end =   attr_set.end();

    if (type == CT_EXP_CHANNEL)
    {
        read_ct_values_from_ctrls(begin, end);
        read_pc_values_from_ctrls(begin, end);
    }
    else if (type == ZEROD_EXP_CHANNEL)
    {
        read_zerod_values_from_ctrls(begin, end);
        read_pc_values_from_ctrls(begin, end);
    }
    else if (type == ONED_EXP_CHANNEL)
    {
        read_oned_values_from_ctrls(begin, end);
    }
    else if (type == TWOD_EXP_CHANNEL)
    {
        read_twod_values_from_ctrls(begin, end);
    }
    else if (type == PSEUDO_EXP_CHANNEL)
    {
        read_pc_values_from_ctrls(begin, end);
    }
    else if (type == MOTOR_CHANNEL)
    {
        read_motor_values_from_ctrls(begin, end);
    }
    else if(type == ANY_CHANNEL)
    {
        read_ct_values_from_ctrls(begin, end);
        read_zerod_values_from_ctrls(begin, end);
        read_oned_values_from_ctrls(begin, end);
        read_twod_values_from_ctrls(begin, end);
        read_pc_values_from_ctrls(begin, end);
        read_motor_values_from_ctrls(begin, end);
    }

    vector<Tango::Attr *> &attr_vect = device_class->get_class_attr()->get_attr_list();
    set<int32_t>::const_iterator it = begin;
    for(; it != end; ++it)
    {
        Tango::Attribute &att = dev_attr->get_attr_by_ind(*it);
        attr_vect[att.get_attr_idx()]->read(this,att);
    }
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_master
//
// description : 	Simulates reading the master value. This method should
//                  be called only when you have the lock on this device.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::read_master()
{
    vector<long> attr_list;

    string &master_name = aq_mode == aqTimer ? timer : monitor;
    int32_t static_nb = utils->get_static_attr_nb(device_class) - 2;

    for(int32_t loop = 0; loop < ct_nb; loop++)
    {
        if(ind_elts[loop]->get_alias() == master_name)
        {
            attr_list.push_back((long) (static_nb+loop));
            break;
        }
    }
    read_attr_hardware(attr_list);
    vector<Tango::Attr *> &attr_vect = device_class->get_class_attr()->get_attr_list();
    Tango::Attribute &att = dev_attr->get_attr_by_ind(attr_list[0]);
    attr_vect[att.get_attr_idx()]->read(this,att);
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_PseudoCounters
//
// description : 	Extract real attribute values for PseudoCounters acquisition result.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::read_PseudoCounters(Tango::Attribute &attr)
{
    DEBUG_STREAM << "MeasurementGroup::read_PseudoCounters(Tango::Attribute &attr) entering... "<< endl;

    uint32_t l = 0;
    std::vector<Tango::DevLong>::iterator ite = pseudoCounter_List.begin();
    for (;ite != pseudoCounter_List.end();++ite,++l)
    {
        Pool_ns::PseudoCounterPool &pcp = pool_dev->get_pseudo_counter((Pool_ns::ElementId)*ite);
        attr_PseudoCounters_read[l] = const_cast<char *>(pcp.get_name().c_str());
    }

    attr.set_value(attr_PseudoCounters_read, pc_nb);
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_Counters
//
// description : 	Extract real attribute values for Counters acquisition result.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::read_Counters(Tango::Attribute &attr)
{
    DEBUG_STREAM << "MeasurementGroup::read_Counters(Tango::Attribute &attr) entering... "<< endl;

    bool timer_set = false;
    uint32_t ul = 0;
    std::vector<Tango::DevLong>::iterator ite = ct_List.begin();
    for (;ite != ct_List.end();++ite,++ul)
    {
        Pool_ns::CTExpChannelPool &ctp = pool_dev->get_countertimer((Pool_ns::ElementId)*ite);
        const std::string &ct_name = ctp.get_name();

        // Skip the timer
        if((aq_mode != aqMonitor) && (ct_name == timer))
        {
            timer_set = true;
            continue;
        }

        attr_Counters_read[ul] = const_cast<char *>(ct_name.c_str());
    }

    if(timer_set == true)
        attr.set_value(attr_Counters_read, ct_nb - 1);
    else
        attr.set_value(attr_Counters_read, ct_nb);
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_Channels
//
// description : 	Extract real attribute values for Channels acquisition result.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::read_Channels(Tango::Attribute &attr)
{
    DEBUG_STREAM << "MeasurementGroup::read_Channels(Tango::Attribute &attr) entering... "<< endl;

    uint32_t ul = 0;
    std::vector<Tango::DevLong>::iterator ite = user_group_elt.begin();
    for (;ite != user_group_elt.end();++ite)
    {
        Pool_ns::PoolElement &pe = pool_dev->get_experiment_channel((Pool_ns::ElementId)*ite);
        attr_Channels_read[ul++] = const_cast<char *>(pe.get_name().c_str());
    }
    attr.set_value(attr_Channels_read, usr_elt_nb);
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_ZeroDExpChannels
//
// description : 	Extract real attribute values for ZeroDExpChannels acquisition result.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::read_ZeroDExpChannels(Tango::Attribute &attr)
{
    DEBUG_STREAM << "MeasurementGroup::read_ZeroDExpChannels(Tango::Attribute &attr) entering... "<< endl;

    uint32_t l = 0;
    std::vector<Tango::DevLong>::iterator ite = zeroDExpChannel_List.begin();
    for (;ite != zeroDExpChannel_List.end();++ite,++l)
    {
        Pool_ns::ZeroDExpChannelPool &zerodp = pool_dev->get_zerod((Pool_ns::ElementId)*ite);
        attr_ZeroDExpChannels_read[l] = const_cast<char *>(zerodp.get_name().c_str());
    }

    attr.set_value(attr_ZeroDExpChannels_read, zeroD_nb);
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_OneDExpChannels
//
// description : 	Extract real attribute values for OneDExpChannels acquisition result.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::read_OneDExpChannels(Tango::Attribute &attr)
{
    DEBUG_STREAM << "MeasurementGroup::read_OneDExpChannels(Tango::Attribute &attr) entering... "<< endl;

    uint32_t l = 0;
    std::vector<Tango::DevLong>::iterator ite = oneDExpChannel_List.begin();
    for (;ite != oneDExpChannel_List.end();++ite,++l)
    {
        Pool_ns::OneDExpChannelPool &onedp = pool_dev->get_oned((Pool_ns::ElementId)*ite);
        attr_OneDExpChannels_read[l] = const_cast<char *>(onedp.get_name().c_str());
    }

    attr.set_value(attr_OneDExpChannels_read, oneD_nb);
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_TwoDExpChannels
//
// description : 	Extract real attribute values for TwoDExpChannels acquisition result.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::read_TwoDExpChannels(Tango::Attribute &attr)
{
    DEBUG_STREAM << "MeasurementGroup::read_TwoDExpChannels(Tango::Attribute &attr) entering... "<< endl;

    uint32_t l = 0;
    std::vector<Tango::DevLong>::iterator ite = twoDExpChannel_List.begin();
    for (;ite != twoDExpChannel_List.end();++ite,++l)
    {
        Pool_ns::TwoDExpChannelPool &twodp = pool_dev->get_twod((Pool_ns::ElementId)*ite);
        attr_TwoDExpChannels_read[l] = const_cast<char *>(twodp.get_name().c_str());
    }

    attr.set_value(attr_TwoDExpChannels_read, twoD_nb);
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_Motors
//
// description : 	Extract real attribute values for Motors acquisition result.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::read_Motors(Tango::Attribute &attr)
{
    DEBUG_STREAM << "MeasurementGroup::read_TwoDExpChannels(Tango::Attribute &attr) entering... "<< endl;

    uint32_t l = 0;
    std::vector<Tango::DevLong>::iterator ite = motor_List.begin();
    for (;ite != motor_List.end();++ite,++l)
    {
        Pool_ns::PoolElement &motorp = pool_dev->get_motor((Pool_ns::ElementId)*ite);
        attr_Motors_read[l] = const_cast<char *>(motorp.get_name().c_str());
    }

    attr.set_value(attr_Motors_read, mot_nb);
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_Integration_time
//
// description : 	Extract real attribute values for Integration_time acquisition result.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::read_Integration_time(Tango::Attribute &attr)
{
    DEBUG_STREAM << "MeasurementGroup::read_Integration_time(Tango::Attribute &attr) entering... "<< endl;

    attr.set_value(attr_Integration_time_read);
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::write_Integration_time
//
// description : 	Write Integration_time attribute values to hardware.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::write_Integration_time(Tango::WAttribute &attr)
{
    DEBUG_STREAM << "MeasurementGroup::write_Integration_time(Tango::WAttribute &attr) entering... "<< endl;

    Tango::DevDouble new_time;
    attr.get_write_value(new_time);

    if(new_time < 0.0)
    {
        TangoSys_OMemStream o;
        o << "Invalid integration time.";
        o << "Integration time must be bigger or equal to zero" << ends;

        Tango::Except::throw_exception((const char *)"Pool_InvalidIntegrationTime",o.str(),
                        (const char *)"MeasurementGroup::write_Integration_time");
    }

    attr_Integration_time_write = new_time;

//
// If this write is being called in the initialization phase (because it is a memorized attribute with
// memorized_init set to true)
//
// There is a trick here:
// It can also happen in the first write after the device is created due to a CreateMeasurementGroup in the pool.
// In this case, because there is no value for integration time in the database, the code will enter
// here for the first time. For this case we simulate that the integration count has been changed and we send
// an event for it
// This is done for consistency: every time the int. time is changed an event is sent to int. time and another event
// for int. count
//
    if(first_write_integration_time == true)
    {
        first_write_integration_time = false;

        if(!Pool_ns::doubleEqual(new_time,0.0))
            attr_Integration_count_write = 0;

        Tango::MultiAttribute *dev_attrs = get_device_attr();
        Tango::Attribute &integration_count_att = dev_attrs->get_attr_by_name("Integration_count");

        {
            Tango::AutoTangoMonitor synch(this);
            read_Integration_count(integration_count_att);
            integration_count_att.fire_change_event();
        }
    }

//
// If being called by a usual client request...
//
    else
    {
//
// Disable the integration count. We must do this through the CORBA layer because the attribute is memorized.
// We want this disable to be written into the DB so that the next time the device is started it will be in
// a consistent state
//
        if(!Pool_ns::doubleEqual(new_time,0.0))
        {
            string full_attr_name = get_name() + "/Integration_count";
            Tango::AttributeProxy int_count_proxy(full_attr_name);
            Tango::DeviceAttribute int_count_attr("Integration_count", (Tango::DevLong)0);
            int_count_proxy.write(int_count_attr);
        }

    }

    if(new_time > 0.0)
        aq_mode = aqTimer;
    else if(Pool_ns::doubleEqual(new_time,0.0))
        if (attr_Integration_count_write == 0)
            aq_mode = aqNone;

    Tango::MultiAttribute *dev_attrs = get_device_attr();
    Tango::Attribute &integration_time_att = dev_attrs->get_attr_by_name("Integration_time");

    {
        Tango::AutoTangoMonitor synch(this);
        read_Integration_time(integration_time_att);
        integration_time_att.fire_change_event();
    }
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_Integration_count
//
// description : 	Extract real attribute values for Integration_count acquisition result.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::read_Integration_count(Tango::Attribute &attr)
{
    DEBUG_STREAM << "MeasurementGroup::read_Integration_count(Tango::Attribute &attr) entering... "<< endl;

    attr.set_value(attr_Integration_count_read);
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::write_Integration_count
//
// description : 	Write Integration_count attribute values to hardware.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::write_Integration_count(Tango::WAttribute &attr)
{
    DEBUG_STREAM << "MeasurementGroup::write_Integration_count(Tango::WAttribute &attr) entering... "<< endl;

    Tango::DevLong new_count;
    attr.get_write_value(new_count);

/*
    if(new_count < 0)
    {
        TangoSys_OMemStream o;
        o << "Invalid integration count.";
        o << "Integration count must be bigger or equal to zero" << ends;

        Tango::Except::throw_exception((const char *)"Pool_InvalidIntegrationCount",o.str(),
                        (const char *)"MeasurementGroup::write_Integration_count");
    }
*/
    attr_Integration_count_write = new_count;

//
// If this write is being called in the initialization phase (because it is a memorized attribute with
// memorized_init set to true)
//
// There is a trick here:
// It can also happen in the first write after the device is created due to a CreateMeasurementGroup in the pool.
// In this case, because there is no value for integration count in the database, the code will enter
// here for the first time. For this case we simulate that the integration time has been changed and we send
// an event for it
// This is done for consistency: every time the int. count is changed an event is sent to int. count and another event
// for int. time
//
    if(first_write_integration_count == true)
    {
        first_write_integration_count = false;

        if(new_count > 0)
            attr_Integration_time_write = 0.0;

        Tango::MultiAttribute *dev_attrs = get_device_attr();
        Tango::Attribute &integration_time_att = dev_attrs->get_attr_by_name("Integration_time");

        {
            Tango::AutoTangoMonitor synch(this);
            read_Integration_time(integration_time_att);
            integration_time_att.fire_change_event();
        }
    }
//
// If being called by a usual client request...
//
    else
    {
//
// Disable the integration time. We must do this through the CORBA layer because the attribute is memorized.
// We want this disable to be written into the DB so that the next time the device is started it will be in
// a consistent state
//
        if(new_count > 0)
        {
            string full_attr_name = get_name() + "/Integration_time";
            Tango::AttributeProxy int_time_proxy(full_attr_name);
            Tango::DeviceAttribute int_time_attr("Integration_time", 0.0);
            int_time_proxy.write(int_time_attr);
        }
    }

    if(new_count > 0.0)
        aq_mode = aqMonitor;
    else if(attr_Integration_count_write == 0)
        if(Pool_ns::doubleEqual(attr_Integration_time_write,0.0))
            aq_mode = aqNone;

    Tango::MultiAttribute *dev_attrs = get_device_attr();
    Tango::Attribute &integration_count_att = dev_attrs->get_attr_by_name("Integration_count");

    {
        Tango::AutoTangoMonitor synch(this);
        read_Integration_count(integration_count_att);
        integration_count_att.fire_change_event();
    }
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_Timer
//
// description : 	Extract real attribute values for Timer acquisition result.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::read_Timer(Tango::Attribute &attr)
{
    DEBUG_STREAM << "MeasurementGroup::read_Timer(Tango::Attribute &attr) entering... "<< endl;

    char *timer_name = const_cast<char*>(timer.c_str());

    attr.set_value(&timer_name);
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::write_Timer
//
// description : 	Write Timer attribute values to hardware.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::write_Timer(Tango::WAttribute &attr)
{
    DEBUG_STREAM << "MeasurementGroup::write_Timer(Tango::WAttribute &attr) entering... "<< endl;

    Tango::DevString new_timer_str;
    attr.get_write_value(new_timer_str);
    string new_timer_name(new_timer_str);

    bool state_changed = false;
    Tango::DevState st = get_state();
    string &_status = get_status();

//
// If this write is being called in the initialization phase (because it is a memorized attribute with
// memorized_init set to true)
//
    if(first_write_timer)
    {
        first_write_timer = false;
//
// Allow to disable the timer
//
        if(new_timer_name == NOT_INITIALIZED)
        {
            timer = new_timer_name;


//
// If monitor has been written from DB and both timer and monitor are not
// initialized then set the state to alarm
//
            if(!first_write_monitor && monitor == NOT_INITIALIZED)
            {
                if(st != Tango::FAULT && st != Tango::UNKNOWN && st != Tango::ALARM)
                {
                    set_state(Tango::ALARM);
                    state_changed = true;
                    _status.clear();
                    _status = ALARM_STATUS_MSG;
                }
            }
        }
        else
        {
            try
            {
                pool_dev->get_experiment_channel(new_timer_name);

                //TODO tell the channel that is now a timer (if necessary)
            }
            catch(Tango::DevFailed &e)
            {
                // The channel was deleted by hand. Very naughty!
                // Try to recover from this by disabling the timer
                new_timer_name = NOT_INITIALIZED;
            }

            timer = new_timer_name;

            if(new_timer_name != NOT_INITIALIZED && st == Tango::ALARM)
            {
                set_state(Tango::ON);
                state_changed = true;
                _status = StatusNotSet;
                DeviceImpl::dev_status();
            }
            else if(new_timer_name == NOT_INITIALIZED)
            {
                if(!first_write_monitor && monitor == NOT_INITIALIZED)
                {
                    if(st != Tango::FAULT && st != Tango::UNKNOWN && st != Tango::ALARM)
                    {
                        set_state(Tango::ALARM);
                        state_changed = true;
                        _status.clear();
                        _status = ALARM_STATUS_MSG;
                    }
                }
            }
        }
    }
//
// If being called by a usual client request...
//
    else
    {
        string old_timer_name = timer;


        if(old_timer_name == new_timer_name)
            return;

        if(old_timer_name != NOT_INITIALIZED)
        {
            //TODO tell the old channel that it is not longer a timer (if necessary)
        }

//
// Allow to disable the timer
//
        if(new_timer_name == NOT_INITIALIZED)
        {
            timer = new_timer_name;

            if(monitor == NOT_INITIALIZED && st != Tango::FAULT && st != Tango::ALARM)
            {
                set_state(Tango::ALARM);
                state_changed = true;
                _status.clear();
                _status = ALARM_STATUS_MSG;
            }
        }
        else
        {
//
// Check if the given channel exists
//
            pool_dev->get_experiment_channel(new_timer_name);
            timer = new_timer_name;

            //TODO tell the channel that is now a timer (if necessary)

            if(st == Tango::ALARM)
            {
                set_state(Tango::ON);
                state_changed = true;
                _status = StatusNotSet;
                DeviceImpl::dev_status();
            }
        }


    }

    Tango::MultiAttribute *dev_attrs = get_device_attr();

    if(state_changed)
    {
        Tango::Attribute &state_att = dev_attrs->get_attr_by_name("State");
        state_att.fire_change_event();
    }

    Tango::Attribute &timer_att = dev_attrs->get_attr_by_name("Timer");
    Tango::Attribute &counters_att = dev_attrs->get_attr_by_name("Counters");

    {
        Tango::AutoTangoMonitor synch(this);
        read_Timer(timer_att);
        timer_att.fire_change_event();
    }

    {
        Tango::AutoTangoMonitor synch(this);
        read_Counters(counters_att);
        counters_att.fire_change_event();
    }
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_Monitor
//
// description : 	Extract real attribute values for Monitor acquisition result.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::read_Monitor(Tango::Attribute &attr)
{
    DEBUG_STREAM << "MeasurementGroup::read_Monitor(Tango::Attribute &attr) entering... "<< endl;

    char *monitor_name = const_cast<char*>(monitor.c_str());

    attr.set_value(&monitor_name);
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::write_Monitor
//
// description : 	Write Monitor attribute values to hardware.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::write_Monitor(Tango::WAttribute &attr)
{
    DEBUG_STREAM << "MeasurementGroup::write_Monitor(Tango::WAttribute &attr) entering... "<< endl;

    Tango::DevString new_monitor_str;
    attr.get_write_value(new_monitor_str);
    string new_monitor_name(new_monitor_str);

    bool state_changed = false;
    Tango::DevState st = get_state();
    string &_status = get_status();

//
// If this write is being called in the initialization phase (because it is a memorized attribute with
// memorized_init set to true)
//
    if(first_write_monitor == true)
    {
        first_write_monitor = false;
//
// Allow to disable the monitor
//
        if(new_monitor_name == NOT_INITIALIZED)
        {
            monitor = new_monitor_name;

//
// If timer has been written from DB and both timer and monitor are not
// initialized then set the state to alarm
//
            if(!first_write_timer && timer == NOT_INITIALIZED)
            {
                if(st != Tango::FAULT && st != Tango::UNKNOWN && st != Tango::ALARM)
                {
                    set_state(Tango::ALARM);
                    state_changed = true;
                }
            }
        }
        else
        {
            try
            {
                pool_dev->get_experiment_channel(new_monitor_name);

                //TODO tell the channel that is now a monitor (if necessary)
            }
            catch(Tango::DevFailed &e)
            {
                // The channel was deleted by hand. Very naughty!
                // Try to recover from this by disabling the monitor
                new_monitor_name = NOT_INITIALIZED;
            }

            monitor = new_monitor_name;

            if(new_monitor_name != NOT_INITIALIZED && st == Tango::ALARM)
            {
                set_state(Tango::ON);
                state_changed = true;
                _status.clear();
                _status = "The device is in ON state.";
            }
            else if( new_monitor_name == NOT_INITIALIZED )
            {
                if(!first_write_timer && timer == NOT_INITIALIZED)
                {
                    if(st != Tango::FAULT && st != Tango::UNKNOWN && st != Tango::ALARM)
                    {
                        set_state(Tango::ALARM);
                        state_changed = true;
                        _status.clear();
                        _status = ALARM_STATUS_MSG;
                    }
                }
            }
        }
    }
//
// If being called by a usual client request...
//
    else
    {
        string old_monitor_name = monitor;

        if(old_monitor_name == new_monitor_name)
            return;

        if(old_monitor_name != NOT_INITIALIZED)
        {
            //TODO tell the old channel that it is not longer a monitor (if necessary)
        }

//
// Allow to disable the timer
//
        if(new_monitor_name == NOT_INITIALIZED)
        {
            monitor = new_monitor_name;

            if(timer == NOT_INITIALIZED && st != Tango::FAULT && st != Tango::ALARM)
            {
                set_state(Tango::ALARM);
                state_changed = true;
                _status.clear();
                _status = ALARM_STATUS_MSG;
            }
        }
        else
        {
//
// Check if the given channel exists
//
            pool_dev->get_experiment_channel(new_monitor_name);
            monitor = new_monitor_name;

            //TODO tell the channel that is now a monitor (if necessary)

            if(st == Tango::ALARM)
            {
                set_state(Tango::ON);
                state_changed = true;
                _status.clear();
                _status = "The device is in ON state.";
            }
        }
    }

    Tango::MultiAttribute *dev_attrs = get_device_attr();

    if(state_changed)
    {
        Tango::Attribute &state_att = dev_attrs->get_attr_by_name("State");
        state_att.fire_change_event();
    }

    Tango::Attribute &monitor_att = dev_attrs->get_attr_by_name("Monitor");

    {
        Tango::AutoTangoMonitor synch(this);
        read_Monitor(monitor_att);
        monitor_att.fire_change_event();
    }
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_CT_Attr
//
// description : 	Extract real attribute values for scalar acquisition result.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::read_CT_Attr(Tango::Attribute &attr)
{
    DEBUG_STREAM << "MeasurementGroup::read_CT_Attr(Tango::Attribute &attr) entering... "<< endl;

    string &attr_name = attr.get_name();
    CTInGrp *ct = static_cast<CTInGrp*>(attr_name_channel_map[attr_name]);

    attr.set_value(&(ct->value));

    Tango::DevState st = get_state();

    if (st == Tango::MOVING)
        attr.set_quality(Tango::ATTR_CHANGING);
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_0D_Attr
//
// description : 	Extract real attribute values for scalar acquisition result.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::read_0D_Attr(Tango::Attribute &attr)
{
    DEBUG_STREAM << "MeasurementGroup::read_0D_Attr(Tango::Attribute &attr) entering... "<< endl;

    string &attr_name = attr.get_name();
    ZeroDInGrp *zerod = static_cast<ZeroDInGrp*>(attr_name_channel_map[attr_name]);

    Tango::DeviceAttribute dev_attr = zerod->obj_proxy->read_attribute("CumulatedValue");

    dev_attr >> (zerod->value);

    attr.set_value(&(zerod->value));

    Tango::DevState st = get_state();

    if (st == Tango::MOVING)
        attr.set_quality(Tango::ATTR_CHANGING);
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_1D_Attr
//
// description : 	Extract real attribute values for spectrum acquisition result.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::read_1D_Attr(Tango::Attribute &attr)
{
    DEBUG_STREAM << "MeasurementGroup::read_1D_Attr(Tango::Attribute &attr) entering... "<< endl;

    string &attr_name = attr.get_name();
    OneDInGrp *oned = static_cast<OneDInGrp*>(attr_name_channel_map[attr_name]);

    attr.set_value(oned->value, oned->data_length, 0);

    Tango::DevState st = get_state();

    if (st == Tango::MOVING)
        attr.set_quality(Tango::ATTR_CHANGING);
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_2D_Attr
//
// description : 	Extract real attribute values for image acquisition result.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::read_2D_Attr(Tango::Attribute &attr)
{
    DEBUG_STREAM << "MeasurementGroup::read_2D_Attr(Tango::Attribute &attr) entering... "<< endl;

    string &attr_name = attr.get_name();
    TwoDInGrp *twod = static_cast<TwoDInGrp*>(attr_name_channel_map[attr_name]);

    attr.set_value(twod->value, twod->xdim, twod->ydim);

    Tango::DevState st = get_state();

    if (st == Tango::MOVING)
        attr.set_quality(Tango::ATTR_CHANGING);
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_PC_Attr
//
// description : 	Extract real attribute values for scalar acquisition result.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::read_PC_Attr(Tango::Attribute &attr)
{
    DEBUG_STREAM << "MeasurementGroup::read_PC_Attr(Tango::Attribute &attr) entering... "<< endl;

    string &attr_name = attr.get_name();
    PseudoCoInGrp *ct = static_cast<PseudoCoInGrp*>(attr_name_channel_map[attr_name]);

    attr.set_value(&(ct->value));

    Tango::DevState st = get_state();

    if (st == Tango::MOVING)
        attr.set_quality(Tango::ATTR_CHANGING);
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::read_MOT_Attr
//
// description : 	Extract real attribute values for scalar acquisition result.
//
//-----------------------------------------------------------------------------
void MeasurementGroup::read_MOT_Attr(Tango::Attribute &attr)
{
    DEBUG_STREAM << "MeasurementGroup::read_MOT_Attr(Tango::Attribute &attr) entering... "<< endl;

    string &attr_name = attr.get_name();
    MotorInGrp *motor = static_cast<MotorInGrp*>(attr_name_channel_map[attr_name]);

    attr.set_value(&(motor->value));

    Tango::DevState st = get_state();

    if (st == Tango::MOVING)
        attr.set_quality(Tango::ATTR_CHANGING);
}

//+------------------------------------------------------------------
/**
 *	method:	MeasurementGroup::start
 *
 *	description:	method to execute "Start"
 *	Start counting using the active configuration
 *
 *
 */
//+------------------------------------------------------------------
void MeasurementGroup::start()
{
    DEBUG_STREAM << "MeasurementGroup::start(): entering... !" << endl;

    //	Add your own code to control device here
    AquisitionInfo aq_info;
    double cumulation_time = 0.0;
//
// Check that the timer, monitor and integration time and count have correct values
//
    if(aq_mode == aqNone)
    {
        TangoSys_OMemStream o;
        o << "Invalid integration mode.";
        o << "Integration count or Integration time must be set with values bigger than zero" << ends;

        Tango::Except::throw_exception((const char *)"Pool_InvalidIntegrationMode",o.str(),
                                       (const char *)"MeasurementGroup::start");
    }
    else if(aq_mode == aqTimer)
    {
        if(timer == NOT_INITIALIZED)
        {
            Tango::Except::throw_exception((const char *)"Pool_UninitializedTimer",
                                           (const char *)"A valid Timer must be set before aquiring data.",
                                           (const char *)"MeasurementGroup::start");
        }
        master = &get_channel_from_name(timer);
        aq_info.master_value = attr_Integration_time_write;
        cumulation_time = attr_Integration_time_write;
    }
    else if(aq_mode == aqMonitor)
    {
        if(monitor == NOT_INITIALIZED)
        {
            Tango::Except::throw_exception((const char *)"Pool_UninitializedMonitor",
                                           (const char *)"A valid Monitor must be set before aquiring data.",
                                           (const char *)"MeasurementGroup::start");
        }
        master = &get_channel_from_name(monitor);
        aq_info.master_value = -attr_Integration_count_write;
        cumulation_time = 0.0;
    }

    aq_info.master_id = master->id;
    aq_info.master_idx_in_grp = get_ind_elt_idx_from_id(master->id);
    aq_info.mode = aq_mode;

//
// Clean up
//
    // For CT is mandatory specially if the channel is a monitor because
    // we check in the monitor if the value is increasing or decreasing so we
    // need a clean value for the first comparison
    for(int32_t idx = 0; idx < ct_nb; idx++)
    {
        CTInGrp &ct = get_ct_from_index(idx);
        ct.get_base_device()->abort_cmd_executed = false;
        ct.value = 0.0;
        aq_info.ct_ids.push_back(ct.id);
    }

    if(zeroD_nb > 0)
    {
        Tango::DeviceAttribute attr("CumulationTime",cumulation_time);
        for(int32_t idx = 0; idx < zeroD_nb; idx++)
        {
            ZeroDInGrp &zd = get_zerod_from_index(idx);
            zd.value = 0.0;
//          
// 0D Special: Set the cumulation time in all 0D Channels
//
            zd.obj_proxy->write_attribute(attr);
        }
    }

    for(int32_t idx = 0; idx < pc_nb; idx++)
    {
        PseudoCoInGrp *pc = pseudo_elts[idx];
        if(pc->attr_idx >= 0 && pc->is_virtual == true)
            aq_info.virt_pc_ids.push_back(pc->id);
    }
    //TODO Same thing for 1D and 2D. Or maybe not...


    th_failed = false;
    abort_cmd_executed = false;

//
// Create the counting thread(s), but start it only while the pos_mon
// lock is taken. Otherwise, a dead-lock can happen, if the thread
// start excuting its code just after the start and before this code
// enter into the wait. The thread will send the signal but while
// this thread is not yet waiting for it and afterwards, we will have
// a dead-lock...
//
    Pool_ns::PoolMonitor *mon = get_pool_obj().get_notification_monitor();
    CTPoolThread *ct_pool_th = new CTPoolThread(aq_info, pool_dev, mon, get_id());

    {
        omni_mutex_lock lo(*mon);
        ct_pool_th->start();
        mon->wait();
    }

    if (th_failed == true)
    {
        Tango::DevFailed ex(th_except);
        throw ex;
    }

//
// Start on all 0D Channels
//

    for(int32_t idx = 0; idx < zeroD_nb; idx++)
    {
        INFO_STREAM << "CALL START ON 0D (idx=" << idx << ")" << std::endl;
        Tango::DeviceProxy *zerod_proxy = get_zerod_from_index(idx).obj_proxy;
        zerod_proxy->command_inout("Start");
        INFO_STREAM << "FINISH CALL START ON 0D (idx=" << idx << ")" << std::endl;
    }
//
// Start on all 1D Channels
//
    for(int32_t idx = 0; idx < oneD_nb; idx++)
    {
        get_oned_from_index(idx).obj_proxy->command_inout("Start");
    }

//
// Start on all 2D Channels
//
    for(long idx = 0; idx < twoD_nb; idx++)
    {
        get_twod_from_index(idx).obj_proxy->command_inout("Start");
    }
   
    DEBUG_STREAM << "MeasurementGroup::start(): leaving" << endl;
}

//+------------------------------------------------------------------
/**
 *	method:	MeasurementGroup::abort
 *
 *	description:	method to execute "Abort"
 *	Abort the acquisition
 *
 *
 */
//+------------------------------------------------------------------
void MeasurementGroup::abort()
{
    DEBUG_STREAM << "MeasurementGroup::abort(): entering... !" << endl;

    //	Add your own code to control device here
    base_abort(true);
}
//+------------------------------------------------------------------
/**
 *	method:	MeasurementGroup::abort
 *
 *	description:	method to execute "Abort"
 *	Abort the acquisition
 *
 *
 */
//+------------------------------------------------------------------
void MeasurementGroup::base_abort(bool send_evt)
{


    vector<Tango::DevFailed> v_except;
    abort_cmd_executed = true;
//
// Send Abort first to the master
//
    if(master != NULL)
    {
        try
        {
            master->obj_proxy->command_inout("Abort");
        }
        catch (Tango::DevFailed &e)
        {
            v_except.push_back(e);
        }
    }

//
// Send abort to all members of the group
//
    try
    {
        // Another abort is sent to the master but this second time it will
        // discard it (see code on the channel abort command)
        abort_all_channels(v_except);
    }
    catch (Tango::DevFailed &e)
    {
        v_except.push_back(e);
    }

    if(send_evt)
    {
        Tango::MultiAttribute *dev_attrs = get_device_attr();
        int32_t nb_static = utils->get_static_attr_nb(get_device_class()) - 2;
        int32_t nb_att = dev_attr->get_attr_nb();

    //
    // Update the quality factor on all "value" attributes
    //
        for(int32_t idx = nb_static; idx < nb_att; idx++)
        {
            dev_attrs->get_attr_by_ind(idx).set_quality(Tango::ATTR_VALID);
        }

    //
    // Get the new group state and send event
    //

        dev_state();
        Tango::Attribute &state_att = dev_attrs->get_attr_by_name("State");
        state_att.fire_change_event();
    }

//
// Report exception to caller in case of
//

    if (v_except.size() != 0)
    {
        if (v_except.size() == 1)
        {
            Tango::Except::re_throw_exception(v_except[0],(const char *)"CTExpChannel_ExceptStop",
                                            (const char *)"CounterTimer throw exception during Stop command",
                                            (const char *)"MeasurementGroup::Abort");
        }
        else
        {
        }
    }
}

//+------------------------------------------------------------------
/**
 *	method:	MeasurementGroup::abort_all_channels
 *
 *	description:	method to execute "Abort" on all channels (except
 * 					the master. Should be called only when having a lock
 *                  on the controllers
 */
//+------------------------------------------------------------------
void MeasurementGroup::abort_all_channels(vector<Tango::DevFailed> &v_except)
{
    for_each(ind_elts.begin(), ind_elts.end(),
             bind2nd(mem_fun(&IndEltGrp::abort_no_evt),&v_except));
}

void MeasurementGroup::State_ctrl_ind(Pool_ns::CtrlGrp *ctrl_grp, vector<Controller *> &failed_ctrls)
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
        Pool_ns::IndEltGrp &elt = *(elts_it->second);
        Tango::DeviceImpl *dev = (elt.get_device());
        int32_t elt_idx = elt.idx_in_grp;
        
        try
        {
            Controller::CtrlState mi;

            if (elt.atm_ptr == NULL)
            {
                dev->set_state(Tango::UNKNOWN);
                state_array[elt_idx] = Tango::UNKNOWN;
                continue;
            }

            ctrl->StateOne(elt.idx_in_ctrl, &mi);

            if(idx < ct_nb)
            {
                CTExpChannel_ns::CTExpChannel *ct_dev = 
                    static_cast<CTExpChannel_ns::CTExpChannel *>(dev);
                ct_dev->set_state_from_group(mi);
            }
            else if((idx >= ct_nb) && (idx < (ct_nb + zeroD_nb)))
            {
                // TODO
                //ZeroDExpChannel_ns::ZeroDExpChannel *zerod_dev = 
                //    static_cast<ZeroDExpChannel_ns::ZeroDExpChannel *>(dev);
                //zerod_dev->set_state_from_group(mi);
            }
            else if((idx >= (ct_nb + zeroD_nb)) && (idx < (ct_nb + zeroD_nb + oneD_nb)))
            {
                // TODO
                //OneDExpChannel_ns::OneDExpChannel *oned_dev = 
                //    static_cast<OneDExpChannel_ns::OneDExpChannel *>(dev);
                //oned_dev->set_state_from_group(mi);
            }
            else if((idx >= (ct_nb + zeroD_nb + oneD_nb)) && (idx < (ct_nb + zeroD_nb + oneD_nb + twoD_nb)))
            {
                // TODO
                //TwoDExpChannel_ns::TwoDExpChannel *twod_dev = 
                //    static_cast<TwoDExpChannel_ns::TwoDExpChannel *>(dev);
                //twod_dev->set_state_from_group(mi);
            }
            else
            {
                assert(false);
            }
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
 *	method:	MeasurementGroup::State_all_ind
 *
 *	description:	Get each channel element state
 */
//+------------------------------------------------------------------

void MeasurementGroup::State_all_ind(vector<Controller *> &failed_ctrls)
{
//
// Get each element state
//
    vector<Controller *>::iterator pos;
    Controller *ctrl;

    for (int32_t idx = 0; idx < ind_elt_nb ;idx++)
    {
        Pool_ns::IndEltGrp *ind = ind_elts[idx];
        PoolIndBaseDev *dev = static_cast<PoolIndBaseDev *>(ind->get_device());
        
        try
        {
            Controller::CtrlState mi;
            ControllerPool &cp = *ind->ctrl_grp->ct;
            ctrl = cp.get_controller();

            if (ctrl != NULL)
            {
                if (failed_ctrls.empty() != true)
                {
                    pos = find(failed_ctrls.begin(),failed_ctrls.end(),ctrl);
                    if (pos != failed_ctrls.end())
                    {
                        dev->set_state(Tango::UNKNOWN);
                        state_array[idx] = Tango::UNKNOWN;
                        continue;
                    }
                }

                if (ind->atm_ptr == NULL)
                {
                    dev->set_state(Tango::UNKNOWN);
                    state_array[idx] = Tango::UNKNOWN;
                    continue;
                }

                ctrl->StateOne(ind->idx_in_ctrl,&mi);

                if(idx < ct_nb)
                {
                    CTExpChannel_ns::CTExpChannel *ct_dev = 
                        static_cast<CTExpChannel_ns::CTExpChannel *>(dev);
                    ct_dev->set_state_from_group(mi);
                }
                else if((idx >= ct_nb) && (idx < (ct_nb + zeroD_nb)))
                {
                    // TODO
                    //ZeroDExpChannel_ns::ZeroDExpChannel *zerod_dev = 
                    //    static_cast<ZeroDExpChannel_ns::ZeroDExpChannel *>(dev);
                    //zerod_dev->set_state_from_group(mi);
                }
                else if((idx >= (ct_nb + zeroD_nb)) && (idx < (ct_nb + zeroD_nb + oneD_nb)))
                {
                    // TODO
                    //OneDExpChannel_ns::OneDExpChannel *oned_dev = 
                    //    static_cast<OneDExpChannel_ns::OneDExpChannel *>(dev);
                    //oned_dev->set_state_from_group(mi);
                }
                else if((idx >= (ct_nb + zeroD_nb + oneD_nb)) && (idx < (ct_nb + zeroD_nb + oneD_nb + twoD_nb)))
                {
                    // TODO
                    //TwoDExpChannel_ns::TwoDExpChannel *twod_dev = 
                    //    static_cast<TwoDExpChannel_ns::TwoDExpChannel *>(dev);
                    //twod_dev->set_state_from_group(mi);
                }
                else
                {
                    assert(false);
                }
                
            }
            else
                dev->set_state(Tango::FAULT);
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
 *	method:	MeasurementGroup::get_ct_from_name
 *
 *	description: Obtains the CTInGrp structure for
 *               the given ind element name
 *
 * @return A reference to an CTInGrp data structure
 *         for the given ind element name
 */
//+------------------------------------------------------------------

MeasurementGroup::CTInGrp &MeasurementGroup::get_ct_from_name(const std::string &name)
{
    const int32_t ct_start = 0;
    for(int32_t l = ct_start; l < (ct_start + ct_nb); l++)
    {
        CTInGrp *ct = static_cast<CTInGrp*>(ind_elts[l]);
        if(ct->name == name)
            return *ct;
    }

    TangoSys_OMemStream o;
    o << "No CTInGrp with name " << name << " found in Counter/Timer list" << ends;

    Tango::Except::throw_exception((const char *)"MeasurementGroup_BadArgument",o.str(),
                                   (const char *)"MeasurementGroup::get_ct_from_name");

    // Make the compiler quiet
    return *((MeasurementGroup::CTInGrp *)NULL);    
}


//+------------------------------------------------------------------
/**
 *	method:	MeasurementGroup::get_ct_from_index
 *
 *	description: Obtains the CTInGrp structure for
 *               the given Counter/Timer index
 *
 * @return A reference to an CTInGrp data structure
 *         for the given ind element index
 */
//+------------------------------------------------------------------

MeasurementGroup::CTInGrp &MeasurementGroup::get_ct_from_index(int32_t ct_index)
{
    if(ct_index >= ct_nb)
    {
        TangoSys_OMemStream o;
        o << "No CTInGrp with index " << ct_index << " found in Counter/Timer list" << ends;

        Tango::Except::throw_exception((const char *)"MeasurementGroup_BadArgument",o.str(),
                                       (const char *)"MeasurementGroup::get_ct_from_index");
    }

    return *static_cast<CTInGrp*>(ind_elts[ct_index]);
}

//+------------------------------------------------------------------
/**
 *	method:	MeasurementGroup::get_zerod_from_name
 *
 *	description: Obtains the ZeroDInGrp structure for
 *               the given ind element name
 *
 * @return A reference to an ZeroDInGrp data structure
 *         for the given ind element name
 */
//+------------------------------------------------------------------

MeasurementGroup::ZeroDInGrp &MeasurementGroup::get_zerod_from_name(const std::string &name)
{
    const int32_t zerod_start = ct_nb;
    for(int32_t l = zerod_start; l < (zerod_start + zeroD_nb); l++)
    {
        ZeroDInGrp *zerod = static_cast<ZeroDInGrp*>(ind_elts[l]);
        if(zerod->name == name)
            return *zerod;
    }

    TangoSys_OMemStream o;
    o << "No ZeroDInGrp with name " << name << " found in 0D channel list" << ends;

    Tango::Except::throw_exception((const char *)"MeasurementGroup_BadArgument",o.str(),
                                   (const char *)"MeasurementGroup::get_ct_from_name");

    // Make the compiler quiet
    return *((MeasurementGroup::ZeroDInGrp *)NULL);    
}

//+------------------------------------------------------------------
/**
 *	method:	MeasurementGroup::get_zerod_from_index
 *
 *	description: Obtains the ZeroDInGrp structure for
 *               the given 0D experiment channel index
 *
 * @return A reference to an ZeroDInGrp data structure
 *         for the given ind element index
 */
//+------------------------------------------------------------------

MeasurementGroup::ZeroDInGrp &MeasurementGroup::get_zerod_from_index(int32_t zeroD_index)
{
    if(zeroD_index >= zeroD_nb)
    {
        TangoSys_OMemStream o;
        o << "No ZeroDInGrp with index " << zeroD_index << " found in 0D channel list" << ends;

        Tango::Except::throw_exception((const char *)"MeasurementGroup_BadArgument",o.str(),
                                       (const char *)"MeasurementGroup::get_zerod_from_index");
    }

    return *static_cast<ZeroDInGrp*>(ind_elts[ct_nb + zeroD_index]);
}

//+------------------------------------------------------------------
/**
 *	method:	MeasurementGroup::get_oned_from_name
 *
 *	description: Obtains the OneDInGrp structure for
 *               the given ind element name
 *
 * @return A reference to an OneDInGrp data structure
 *         for the given ind element name
 */
//+------------------------------------------------------------------

MeasurementGroup::OneDInGrp &MeasurementGroup::get_oned_from_name(const std::string &name)
{
    const int32_t oned_start = ct_nb + zeroD_nb;
    for(int32_t l = oned_start; l < (oned_start + oneD_nb); l++)
    {
        OneDInGrp *oned = static_cast<OneDInGrp*>(ind_elts[l]);
        if(oned->name == name)
            return *oned;
    }

    TangoSys_OMemStream o;
    o << "No OneDInGrp with name " << name << " found in 1D channel list" << ends;

    Tango::Except::throw_exception((const char *)"MeasurementGroup_BadArgument",o.str(),
                                   (const char *)"MeasurementGroup::get_oned_from_name");

    // Make the compiler quiet
    return *((MeasurementGroup::OneDInGrp *)NULL);    
}

//+------------------------------------------------------------------
/**
 *	method:	MeasurementGroup::get_oned_from_index
 *
 *	description: Obtains the OneDInGrp structure for
 *               the given 1D experiment channel index
 *
 * @return A reference to an OneDInGrp data structure
 *         for the given ind element index
 */
//+------------------------------------------------------------------

MeasurementGroup::OneDInGrp &MeasurementGroup::get_oned_from_index(int32_t oneD_index)
{
    if(oneD_index >= oneD_nb)
    {
        TangoSys_OMemStream o;
        o << "No OneDInGrp with index " << oneD_index << " found in 1D channel list" << ends;

        Tango::Except::throw_exception((const char *)"MeasurementGroup_BadArgument",o.str(),
                                       (const char *)"MeasurementGroup::get_oned_from_index");
    }

    return *static_cast<OneDInGrp*>(ind_elts[ct_nb + zeroD_nb + oneD_index]);
}

//+------------------------------------------------------------------
/**
 *	method:	MeasurementGroup::get_twod_from_name
 *
 *	description: Obtains the TwoDInGrp structure for
 *               the given ind element name
 *
 * @return A reference to an TwoDInGrp data structure
 *         for the given ind element name
 */
//+------------------------------------------------------------------

MeasurementGroup::TwoDInGrp &MeasurementGroup::get_twod_from_name(const std::string &name)
{
    const int32_t twod_start = ct_nb + zeroD_nb + oneD_nb;
    for(int32_t l = twod_start; l < (twod_start + twoD_nb); l++)
    {
        TwoDInGrp *twod = static_cast<TwoDInGrp*>(ind_elts[l]);
        if(twod->name == name)
            return *twod;
    }

    TangoSys_OMemStream o;
    o << "No TwoDInGrp with name " << name << " found in 2D channel list" << ends;

    Tango::Except::throw_exception((const char *)"MeasurementGroup_BadArgument",o.str(),
                                   (const char *)"MeasurementGroup::get_twod_from_name");
    
    // Make the compiler quiet
    return *((MeasurementGroup::TwoDInGrp *)NULL);
}

//+------------------------------------------------------------------
/**
 *	method:	MeasurementGroup::get_twod_from_index
 *
 *	description: Obtains the TwoDInGrp structure for
 *               the given 2D experiment channel index
 *
 * @return A reference to an TwoDInGrp data structure
 *         for the given ind element index
 */
//+------------------------------------------------------------------

MeasurementGroup::TwoDInGrp &MeasurementGroup::get_twod_from_index(int32_t twoD_index)
{
    if(twoD_index >= twoD_nb)
    {
        TangoSys_OMemStream o;
        o << "No TwoDInGrp with index " << twoD_index << " found in 2D channel list" << ends;

        Tango::Except::throw_exception((const char *)"MeasurementGroup_BadArgument",o.str(),
                                       (const char *)"MeasurementGroup::get_twod_from_index");
    }

    return *static_cast<TwoDInGrp*>(ind_elts[ct_nb + zeroD_nb + oneD_nb + twoD_index]);
}

//+------------------------------------------------------------------
/**
 *	method:	MeasurementGroup::get_zerod_from_name
 *
 *	description: Obtains the PseudoCoInGrp structure for
 *               the given ind element name
 *
 * @return A reference to an PseudoCoInGrp data structure
 *         for the given ind element name
 */
//+------------------------------------------------------------------

MeasurementGroup::PseudoCoInGrp &MeasurementGroup::get_pc_from_name(const std::string &name)
{
    string name_lower(name);
    transform(name_lower.begin(),name_lower.end(),name_lower.begin(),::tolower);

    vector<PseudoCoInGrp*>::iterator ind_ite = pseudo_elts.begin();
    for(; ind_ite != pseudo_elts.end(); ind_ite++)
    {
        PseudoCoInGrp *ind = (*ind_ite);

        string ind_name_lower(ind->name);
        transform(ind_name_lower.begin(),ind_name_lower.end(),ind_name_lower.begin(),::tolower);
        if(ind_name_lower == name_lower)
            break;
    }

    if (ind_ite == pseudo_elts.end())
    {
        TangoSys_OMemStream o;
        o << "No PseudoCoInGrp with name " << name << " found in pseudo element list" << ends;

        Tango::Except::throw_exception((const char *)"Pool_BadArgument",o.str(),
                                       (const char *)"PoolGroupBaseDev::get_pc_from_name");
    }
    return *(*ind_ite);
}

//+------------------------------------------------------------------
/**
 *	method:	MeasurementGroup::get_pc_from_index
 *
 *	description: Obtains the PseudoCoInGrp structure for
 *               the given pseudo counter channel index
 *
 * @return A reference to an PseudoCoInGrp data structure
 *         for the given ind element index
 */
//+------------------------------------------------------------------

MeasurementGroup::PseudoCoInGrp &MeasurementGroup::get_pc_from_index(int32_t pc_index)
{
    if(pc_index >= pc_nb)
    {
        TangoSys_OMemStream o;
        o << "No PseudoCoInGrp with index " << pc_index << " found in pseudo counter channel list" << ends;

        Tango::Except::throw_exception((const char *)"MeasurementGroup_BadArgument",o.str(),
                                       (const char *)"MeasurementGroup::get_pc_from_index");
    }

    return *static_cast<PseudoCoInGrp*>(pseudo_elts[pc_index]);
}

MeasurementGroup::ChInGrp &MeasurementGroup::get_channel_from_name(const std::string &name)
{
    try
    {
        return static_cast<ChInGrp&>(get_ind_elt_from_name(name));
    }
    catch(Tango::DevFailed &e) {}

    try
    {
        return get_pc_from_name(name);
    }
    catch(Tango::DevFailed &e)
    {
        TangoSys_OMemStream o;
        o << "No channel with name " << name << " found in the measurement ";
        o << "group" << ends;

        Tango::Except::throw_exception(
                (const char *)"MeasurementGroup_BadArgument",o.str(),
                (const char *)"MeasurementGroup::get_channel_from_name");
    }
    
    // Make the compiler quiet
    return *((MeasurementGroup::ChInGrp *)NULL);
}

//+------------------------------------------------------------------
/**
 *	method:	MeasurementGroup::get_ct_data_from_id
 *
 *	description: Obtains the double data pointer for
 *               the given CT element id
 *
 * @return A double data pointer containing the value
 *         for the given CT element id
 */
//+------------------------------------------------------------------
Tango::DevDouble* MeasurementGroup::get_ct_data_from_index(int32_t ct_index)
{
    assert(ct_index < ct_nb);
    return &get_ct_from_index(ct_index).value;
}

//+------------------------------------------------------------------
/**
 *	method:	MeasurementGroup::pool_elem_changed
 *
 *	description: This method is called when the src object has changed
 *               and an event is generated
 *
 * arg(s) : - evt [in]: The event that has occured
 *          - forward_evt [out]: the new internal event data to be sent
 *                               to all listeners
 */
//+------------------------------------------------------------------

void MeasurementGroup::pool_elem_changed(PoolElemEventList &evt_lst,
                                         PoolElementEvent &forward_evt)
{
    PoolElementEvent *evt = evt_lst.back();
    PoolElement *src = evt->src;

    forward_evt.priority = evt->priority;

//
// State change from a channel
//
    switch(evt->type)
    {
        case StateChange:
        {
            Tango::DevState old_state = get_state();

            //TODO: Decide if the mg should change group:
            // - never when any individual channel reports that is taking data
            // - only change if the master channel reports that is taking data
            // - change if any channel is taking data

            forward_evt.type = StateChange;
            forward_evt.old.state = Pool_ns::PoolTango::toPool(old_state);
            forward_evt.curr.state = Pool_ns::PoolTango::toPool(old_state);
        }
        break;

//
// The structure of the elements/controlllers has changed.
//
        case ElementStructureChange:
        {
            int32_t ctrl_grp_idx;
            Tango::AutoTangoMonitor atm(pool_dev);
            ControllerPool &ctrl_ref = pool_dev->get_controller_from_element(src->id);
            CtrlGrp &ctrl_grp = get_ctrl_grp_from_id(ctrl_ref.id, ctrl_grp_idx);
//
// Update controller data
//
            ctrl_grp.ct = &ctrl_ref;
//
// Update channel data
//          
            ChInGrp &elt = get_channel_from_id(src->id, src->get_type());
            elt.pe = src;
        }
        break;

        default:
        {
            assert(false);
        }
        break;
    }
}

//+------------------------------------------------------------------
/**
 *	method:	MeasurementGroup::add_ct_to_ghost_group
 *
 *	description:	Add a new counter/timer channel to the GHOST group
 *
 *  arg(s) : In : ch_id : The channel identifier
 */
//+------------------------------------------------------------------

void MeasurementGroup::add_ct_to_ghost_group(Pool_ns::ElementId ch_id)
{
    DEBUG_STREAM << "MeasurementGroup::add_ct_to_ghost_group()"  << endl;

    assert(is_ghost());

//
// Return if the channel is already member of the group
//

    try
    {
        get_channel_from_id(ch_id, Pool_ns::COTI_ELEM);
        return;
    }
    catch(Tango::DevFailed &e)
    {}

//
// Update internal data structures
//
    ind_elt_nb++;
    usr_elt_nb++;
    ct_nb++;

    {
        Tango::AutoTangoMonitor atm(pool_dev);

        CTExpChannelPool &ct_ref = pool_dev->get_countertimer(ch_id);

        CTInGrp *ct_grp = build_ct(ct_ref);

        //ct_List.push_back(ct_ref.name);
        //user_group_elt.push_back(ct_ref.name);
        //phys_group_elt.push_back(ct_ref.name);
        ind_elts.push_back(ct_grp);
        ind_elts_sorted = ind_elts;
        sort(ind_elts.begin(), ind_elts.end(), Pool_ns::ielt_id_cmp);
    }

//
// Update list array
//

//	SAFE_DELETE_ARRAY(attr_Counters_read);
//	attr_Counters_read = (ct_nb > 0) ? new Tango::DevString[ct_nb] : NULL;
//	SAFE_DELETE_ARRAY(attr_Channels_read);
//	attr_Channels_read = (ind_elt_nb > 0) ? new Tango::DevString[ind_elt_nb] : NULL;

//
// Add entry in the state array
//

    state_array.push_back(Tango::ON);
}

//+------------------------------------------------------------------
/**
 *	method:	MeasurementGroup::add_zerod_to_ghost_group
 *
 *	description:	Add a new 0D channel to the GHOST group
 *
 *  arg(s) : In : ch_id : The channel identifier
 */
//+------------------------------------------------------------------

void MeasurementGroup::add_zerod_to_ghost_group(Pool_ns::ElementId ch_id)
{
    DEBUG_STREAM << "MeasurementGroup::add_zerod_to_ghost_group(), adding channel " << ch_id << endl;

    assert(is_ghost());
//
// Return if the channel is already member of the group
//

    try
    {
        get_channel_from_id(ch_id, Pool_ns::ZEROD_ELEM);
        return;
    }
    catch(Tango::DevFailed &e)
    {}

//
// Update internal data structures
//
    ind_elt_nb++;
    usr_elt_nb++;
    zeroD_nb++;

    {
        Tango::AutoTangoMonitor atm(pool_dev);

        ZeroDExpChannelPool &zerod_ref = pool_dev->get_zerod(ch_id);

        ZeroDInGrp *zerod_grp = build_zerod(zerod_ref);

        //zeroDExpChannel_List.push_back(zerod_ref.name);
        //user_group_elt.push_back(zerod_ref.name);
        //phys_group_elt.push_back(zerod_ref.name);
        ind_elts.push_back(zerod_grp);
        ind_elts_sorted = ind_elts;
        sort(ind_elts.begin(), ind_elts.end(), Pool_ns::ielt_id_cmp);
    }

//	SAFE_DELETE_ARRAY(attr_ZeroDExpChannels_read);
//	attr_ZeroDExpChannels_read = (zeroD_nb > 0) ? new Tango::DevString[zeroD_nb] : NULL;
//	SAFE_DELETE_ARRAY(attr_Channels_read);
//	attr_Channels_read = (ind_elt_nb > 0) ? new Tango::DevString[ind_elt_nb] : NULL;

//
// Add entry in the state array
//

    state_array.push_back(Tango::ON);
}

//+------------------------------------------------------------------
/**
 *	method:	MeasurementGroup::add_oned_to_ghost_group
 *
 *	description:	Add a new 1D channel to the GHOST group
 *
 *  arg(s) : In : ch_id : The channel identifier
 */
//+------------------------------------------------------------------

void MeasurementGroup::add_oned_to_ghost_group(Pool_ns::ElementId ch_id)
{
    DEBUG_STREAM << "MeasurementGroup::add_oned_to_group()"  << endl;

 
    assert(is_ghost());
//
// Return if the channel is already member of the group
//

    try
    {
        get_channel_from_id(ch_id, Pool_ns::ONED_ELEM);
        return;
    }
    catch(Tango::DevFailed &e)
    {}
                
// 
// Update internal data structures
//
    ind_elt_nb++;
    usr_elt_nb++;
    oneD_nb++;

    {
        Tango::AutoTangoMonitor atm(pool_dev);
                
        OneDExpChannelPool &oned_ref = pool_dev->get_oned(ch_id);

        OneDInGrp *oned_grp = build_oned(oned_ref);
        
        //zeroDExpChannel_List.push_back(zerod_ref.name);
        //user_group_elt.push_back(zerod_ref.name);
        //phys_group_elt.push_back(zerod_ref.name);
        ind_elts.push_back(oned_grp);
        ind_elts_sorted = ind_elts;
        sort(ind_elts.begin(), ind_elts.end(), Pool_ns::ielt_id_cmp);
    }

//	SAFE_DELETE_ARRAY(attr_ZeroDExpChannels_read);
//	attr_ZeroDExpChannels_read = (zeroD_nb > 0) ? new Tango::DevString[zeroD_nb] : NULL; 
//	SAFE_DELETE_ARRAY(attr_Channels_read);
//	attr_Channels_read = (ind_elt_nb > 0) ? new Tango::DevString[ind_elt_nb] : NULL; 

//
// Add entry in the state array
//

    state_array.push_back(Tango::ON);
}

//+------------------------------------------------------------------
/**
 *	method:	MeasurementGroup::add_twod_to_ghost_group
 *
 *	description:	Add a new 2D channel to the GHOST group
 *
 *  arg(s) : In : ch_id : The channel identifier
 */
//+------------------------------------------------------------------

void MeasurementGroup::add_twod_to_ghost_group(Pool_ns::ElementId ch_id)
{
    DEBUG_STREAM << "MeasurementGroup::add_twod_to_group()"  << endl;
    
    
    assert(is_ghost());
//
// Return if the channel is already member of the group
//

    try
    {
        get_channel_from_id(ch_id, Pool_ns::TWOD_ELEM);
        return;
    }
    catch(Tango::DevFailed &e)
    {}
    
// 
// Update internal data structures
//
    ind_elt_nb++;
    usr_elt_nb++;
    twoD_nb++;

    {
        Tango::AutoTangoMonitor atm(pool_dev);
        
        TwoDExpChannelPool &twod_ref = pool_dev->get_twod(ch_id);

        TwoDInGrp *twod_grp = build_twod(twod_ref);
        
        //zeroDExpChannel_List.push_back(zerod_ref.name);
        //user_group_elt.push_back(zerod_ref.name);
        //phys_group_elt.push_back(zerod_ref.name);
        ind_elts.push_back(twod_grp);
        ind_elts_sorted = ind_elts;
        sort(ind_elts.begin(), ind_elts.end(), Pool_ns::ielt_id_cmp);
    }

//	SAFE_DELETE_ARRAY(attr_ZeroDExpChannels_read);
//	attr_ZeroDExpChannels_read = (zeroD_nb > 0) ? new Tango::DevString[zeroD_nb] : NULL; 
//	SAFE_DELETE_ARRAY(attr_Channels_read);
//	attr_Channels_read = (ind_elt_nb > 0) ? new Tango::DevString[ind_elt_nb] : NULL; 

//
// Add entry in the state array
//

    state_array.push_back(Tango::ON);
}

//+------------------------------------------------------------------
/**
 *	method:	MeasurementGroup::remove_channel_from_ghost_group
 *
 *	description:	Remove a channel from a group
 *
 *  arg(s) : In : del_ch_id : The channel identifier
 */
//+------------------------------------------------------------------

void MeasurementGroup::remove_channel_from_ghost_group(Pool_ns::ElementId del_ch_id)
{
    DEBUG_STREAM << "MeasurementGroup::remove_channel_from_ghost_group()" << endl;

    assert(is_ghost());

    int32_t idx_in_array = 0;

//
// Assumptions:
// - this is the ghost measurement group
// - no pseudo counters are present. Just physical
// - usr_elt_nb = ind_elt_nb = ind_elts.size
// - user_group_elt.size = phys_group_elt.size = 0
//

//
// Find channel in group
//

    vector<IndEltGrp*>::iterator ite;

    for (ite = ind_elts.begin();ite != ind_elts.end();++ite,++idx_in_array)
        if ((*ite)->id == del_ch_id)
            break;
    if (ite == ind_elts.end())
    {
        TangoSys_OMemStream o;
        o << "Channel with id " << del_ch_id;
        o << " is not a member of this group" << ends;

        Tango::Except::throw_exception(
                (const char *)"MeasurementGroup_BadArgument",o.str(),
                (const char *)"MeasurementGroup::remove_channel_from_ghost_group");
    }
    ChInGrp *channel = static_cast<ChInGrp *>(*ite);
    Pool_ns::CtrlGrp *ctrl_grp = channel->ctrl_grp;

    MntGrpEltType type = channel->get_type();

    if(type == CT_EXP_CHANNEL) --ct_nb;
    else if(type == ZEROD_EXP_CHANNEL) --zeroD_nb;
    else if(type == ONED_EXP_CHANNEL) --oneD_nb;
    else if(type == TWOD_EXP_CHANNEL) --twoD_nb;
    else assert(false);

    usr_elt_nb--;
    ind_elt_nb--;

//
// Remove channel from group
//
    ind_elts.erase(ite);
    SAFE_DELETE(channel);

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

//
// Remove entry in the state array
//

    if (state_array.size() != 0)
    {
        vector<Tango::DevState>::iterator state_ite = state_array.begin();
        advance(state_ite,idx_in_array);
        state_array.erase(state_ite);
    }
}

// Helper method to update the list of channels into the database
void MeasurementGroup::write_list_props_to_db(string &add_prop_name,
                                              std::vector<Tango::DevLong> &add_prop_val)
{
    Tango::DbData dev_prop;
    Tango::DbDatum prop_lst(add_prop_name.c_str());
    Tango::DbDatum user_group_elt_lst("user_group_elt");
    Tango::DbDatum phys_group_elt_lst("phys_group_elt");
    prop_lst << add_prop_val;
    user_group_elt_lst << user_group_elt;
    phys_group_elt_lst << phys_group_elt;
    dev_prop.push_back(prop_lst);
    dev_prop.push_back(user_group_elt_lst);
    dev_prop.push_back(phys_group_elt_lst);
    get_db_device()->put_property(dev_prop);
}

//+------------------------------------------------------------------
/**
 *	method:	MeasurementGroup::add_exp_channel
 *
 *	description:	method to execute "AddExpChannel"
 *	Append a new experiment channel to the current list of channels in the measurement group.
 *
 * @param	argin	Experiment Channel name
 *
 */
//+------------------------------------------------------------------
void MeasurementGroup::add_exp_channel(Tango::DevString argin)
{
    DEBUG_STREAM << "MeasurementGroup::add_exp_channel(): entering... !" << endl;

    assert(!is_ghost());

    string channel_name(argin);

//
// Check if the channel exists in the pool
//
    PoolElement &ch_ref = pool_dev->get_experiment_channel(channel_name);
    ElementType type = ch_ref.get_type();
    
    bool already_exists = false;
    try
    {
        ChInGrp &element = get_channel_from_id(ch_ref.id, ch_ref.get_type());
        already_exists = element.attr_idx >= 0;
    }
    catch(Tango::DevFailed e) {}

//
// Check if the channel is not already in the measurement group as a user
// element
//

    if(already_exists == true)
    {
        TangoSys_OMemStream o;
        o << "The channel " << channel_name;
        o << " is already part of the measurement group";
        Tango::Except::throw_exception(
                (const char *)"MeasurementGroup_BadArgument",o.str(),
                (const char *)"MeasurementGroup::add_exp_channel");
    }

//
// First delete all channel information. (it is done because just adding the new
// channel can be very complicated due to dependencies of channels)
//
    unsigned long l;

    for(l = 0;l < ind_elts.size();l++) delete ind_elts[l];
    ind_elts.clear();

    for(l = 0; l < implied_ctrls.size(); l++) delete implied_ctrls[l];
    implied_ctrls.clear();

    for(l = 0;l < pseudo_elts.size();l++) delete pseudo_elts[l];
    pseudo_elts.clear();

    for(l = 0; l < implied_pseudo_ctrls.size(); l++) delete implied_pseudo_ctrls[l];
    implied_pseudo_ctrls.clear();

//
// Add information to the corresponding properties
//
    string attr_list_name;
    string property_name;
    vector<Tango::DevLong> *ch_list = NULL;
    long evts = true;

    if(type == COTI_ELEM)
    {
        attr_list_name = "Counters";
        property_name = "Ct_List";
        ch_list = &ct_List;
        ch_list->push_back((Tango::DevLong)ch_ref.get_id());
        ct_nb = ct_List.size();
        SAFE_DELETE_ARRAY(attr_Counters_read);
        attr_Counters_read = (ct_nb > 0) ? new Tango::DevString[ct_nb] : NULL;
    }
    else if(type == ZEROD_ELEM)
    {
        attr_list_name = "ZeroDExpChannels";
        property_name = "ZeroDExpChannel_List";
        ch_list = &zeroDExpChannel_List;
        ch_list->push_back((Tango::DevLong)ch_ref.get_id());
        zeroD_nb = zeroDExpChannel_List.size();
        SAFE_DELETE_ARRAY(attr_ZeroDExpChannels_read);
        attr_ZeroDExpChannels_read = (zeroD_nb > 0) ? new Tango::DevString[zeroD_nb] : NULL;
    }
    else if(type == ONED_ELEM)
    {
        attr_list_name = "OneDExpChannels";
        property_name = "OneDExpChannel_List";
        ch_list = &oneDExpChannel_List;
        ch_list->push_back((Tango::DevLong)ch_ref.get_id());
        oneD_nb = oneDExpChannel_List.size();
        SAFE_DELETE_ARRAY(attr_OneDExpChannels_read);
        attr_OneDExpChannels_read = (oneD_nb > 0) ? new Tango::DevString[oneD_nb] : NULL;
        evts = false;
    }
    else if(type == TWOD_ELEM)
    {
        attr_list_name = "TwoDExpChannels";
        property_name = "TwoDExpChannel_List";
        ch_list = &twoDExpChannel_List;
        ch_list->push_back((Tango::DevLong)ch_ref.get_id());
        twoD_nb = twoDExpChannel_List.size();
        SAFE_DELETE_ARRAY(attr_TwoDExpChannels_read);
        attr_TwoDExpChannels_read = (twoD_nb > 0) ? new Tango::DevString[twoD_nb] : NULL;
        evts = false;
    }
    else if(type == PSEUDO_COUNTER_ELEM)
    {
        attr_list_name = "PseudoCounters";
        property_name = "PseudoCounter_List";
        ch_list = &pseudoCounter_List;
        ch_list->push_back((Tango::DevLong)ch_ref.get_id());
        pc_nb = pseudoCounter_List.size();
        SAFE_DELETE_ARRAY(attr_PseudoCounters_read);
        attr_PseudoCounters_read = (pc_nb > 0) ? new Tango::DevString[pc_nb] : NULL;
    }
    else if(type == MOTOR_ELEM)
    {
        attr_list_name = "Motors";
        property_name = "Motor_List";
        ch_list = &motor_List;
        ch_list->push_back((Tango::DevLong)ch_ref.get_id());
        mot_nb = motor_List.size();
        SAFE_DELETE_ARRAY(attr_Motors_read);
        attr_Motors_read = (mot_nb > 0) ? new Tango::DevString[mot_nb] : NULL;
    }    
    user_group_elt.push_back(ch_ref.get_id());
    usr_elt_nb = ct_nb + zeroD_nb + oneD_nb + twoD_nb + pc_nb + mot_nb;
    assert((int32_t)user_group_elt.size() == usr_elt_nb);

    // Consider pseudo motors as physical elements since we get the values
    // directly from them
    vector<ElementType> filter;
    filter.push_back(PSEUDO_MOTOR_ELEM);    

    ElemIdVector phys_elems;
    pool_dev->user_elem_to_phy_elems(ch_ref.get_id(), phys_elems, filter, true);
    Pool_ns::PoolTango::toTango(phys_elems, phys_group_elt);
    ind_elt_nb = phys_group_elt.size();

    SAFE_DELETE_ARRAY(attr_Channels_read);
    attr_Channels_read = (usr_elt_nb > 0) ? new Tango::DevString[usr_elt_nb] : NULL;

//
// Update device properties
//
    write_list_props_to_db(property_name, *ch_list);

//
// Now start building all information.
//
    build_grp();

//
// Update pool data structure
//
    MeasurementGroupPool &mg = pool_dev->get_measurement_group(get_id());

    init_pool_element(&mg);

//
// Add entry in the state array
//
    state_array.push_back(Tango::ON);

//
// Update dynamic attributes
//
    create_one_extra_attr(ch_ref.name, type, evts);

//
// Update attribute indexes
//
    update_attr2channel_indexes();

//
// Send event on the proper channel list
//

    Tango::Attribute &list_att = dev_attr->get_attr_by_name(attr_list_name.c_str());
    Tango::Attribute &ch_list_att = dev_attr->get_attr_by_name("Channels");
    {
        Tango::AutoTangoMonitor synch(this);
        if(type == COTI_ELEM)
        {
            read_Counters(list_att);
        }
        else if(type == ZEROD_ELEM)
        {
            read_ZeroDExpChannels(list_att);
        }
        else if(type == ONED_ELEM)
        {
            read_OneDExpChannels(list_att);
        }
        else if(type == TWOD_ELEM)
        {
            read_TwoDExpChannels(list_att);
        }
        else if(type == MOTOR_ELEM)
        {
            read_Motors(list_att);
        } 
        list_att.fire_change_event();

        read_Channels(ch_list_att);
        ch_list_att.fire_change_event();
    }


//
// Inform the pool so it can send a change event on the measurement group list
//
    pool_dev->measurement_group_elts_changed(get_id());
}

//+------------------------------------------------------------------
/**
 *	method:	MeasurementGroup::remove_exp_channel
 *
 *	description:	method to execute "RemoveExpChannel"
 *	Removes the experiment channel from the list of experiment channels in
 *  the measurement group
 *
 * @param	argin	Experiment channel name
 *
 */
//+------------------------------------------------------------------
void MeasurementGroup::remove_exp_channel(Tango::DevString argin)
{
    DEBUG_STREAM << "MeasurementGroup::remove_exp_channel(): entering... !" << endl;

    //	Add your own code to control device here
    string channel_name(argin);

//
// Check if the channel exists in the pool
//
    PoolElement &channel = pool_dev->get_experiment_channel(channel_name);
    Pool_ns::ElementType type = channel.get_type();
    
    ChInGrp &ch = get_channel_from_name(channel_name);

    string ch_alias = ch.get_alias();

    if(ch.attr_idx < 0)
    {
        TangoSys_OMemStream o;
        o << "Channel " << channel_name << " is not a user member of the ";
        o << "measurement group" << ends;

        Tango::Except::throw_exception(
                (const char *)"MeasurementGroup_BadArgument",o.str(),
                (const char *)"MeasurementGroup::remove_exp_channel");
    }

    Pool_ns::ElemIdVector phy_elts_to_delete;

//
// update information to the corresponding properties
//
    string attr_list_name;
    string property_name;
    std::vector<Tango::DevLong>::iterator v_str_ite;
    std::vector<Tango::DevLong> *ch_list = NULL;
    Tango::DevLong ch_id = (Tango::DevLong)channel.get_id();
    long evts = true;

    if(type == COTI_ELEM)
    {
        attr_list_name = "Counters";
        property_name = "Ct_List";

        v_str_ite = find(ct_List.begin(),ct_List.end(), ch_id);
        assert(v_str_ite != ct_List.end());
        ct_List.erase(v_str_ite);

        ch_list = &ct_List;
        ct_nb = ct_List.size();

        SingleValChInGrp *single_val_ch = static_cast<SingleValChInGrp*>(&ch);
        if(single_val_ch->used_by.empty())
        {
            phy_elts_to_delete.push_back(channel.get_id());
        }

        SAFE_DELETE_ARRAY(attr_Counters_read);
        attr_Counters_read = (ct_nb > 0) ? new Tango::DevString[ct_nb] : NULL;
    }
    else if(type == ZEROD_ELEM)
    {
        attr_list_name = "ZeroDExpChannels";
        property_name = "ZeroDExpChannel_List";

        v_str_ite = find(zeroDExpChannel_List.begin(),zeroDExpChannel_List.end(),ch_id);
        assert(v_str_ite != zeroDExpChannel_List.end());
        zeroDExpChannel_List.erase(v_str_ite);

        ch_list = &zeroDExpChannel_List;
        zeroD_nb = zeroDExpChannel_List.size();

        SingleValChInGrp *single_val_ch = static_cast<SingleValChInGrp*>(&ch);
        if(single_val_ch->used_by.empty())
        {
            phy_elts_to_delete.push_back(channel.get_id());
        }

        SAFE_DELETE_ARRAY(attr_ZeroDExpChannels_read);
        attr_ZeroDExpChannels_read = (zeroD_nb > 0) ? new Tango::DevString[zeroD_nb] : NULL;
    }
    else if(type == ONED_ELEM)
    {
        attr_list_name = "OneDExpChannels";
        property_name = "OneDExpChannel_List";

        v_str_ite = find(oneDExpChannel_List.begin(),oneDExpChannel_List.end(),ch_id);
        assert(v_str_ite != oneDExpChannel_List.end());
        oneDExpChannel_List.erase(v_str_ite);

        ch_list = &oneDExpChannel_List;
        oneD_nb = oneDExpChannel_List.size();

        phy_elts_to_delete.push_back(channel.get_id());

        SAFE_DELETE_ARRAY(attr_OneDExpChannels_read);
        attr_OneDExpChannels_read = (oneD_nb > 0) ? new Tango::DevString[oneD_nb] : NULL;
        evts = false;
    }
    else if(type == TWOD_ELEM)
    {
        attr_list_name = "TwoDExpChannels";
        property_name = "TwoDExpChannel_List";

        v_str_ite = find(twoDExpChannel_List.begin(),twoDExpChannel_List.end(),ch_id);
        assert(v_str_ite != twoDExpChannel_List.end());
        twoDExpChannel_List.erase(v_str_ite);

        ch_list = &twoDExpChannel_List;
        twoD_nb = twoDExpChannel_List.size();

        phy_elts_to_delete.push_back(channel.get_id());

        SAFE_DELETE_ARRAY(attr_TwoDExpChannels_read);
        attr_TwoDExpChannels_read = (twoD_nb > 0) ? new Tango::DevString[twoD_nb] : NULL;
        evts = false;
    }
    else if(type == PSEUDO_COUNTER_ELEM)
    {
        attr_list_name = "PseudoCounters";
        property_name = "PseudoCounter_List";

        v_str_ite = find(pseudoCounter_List.begin(),pseudoCounter_List.end(),ch_id);
        assert(v_str_ite != pseudoCounter_List.end());
        pseudoCounter_List.erase(v_str_ite);

        ch_list = &pseudoCounter_List;
        pc_nb = pseudoCounter_List.size();

        SAFE_DELETE_ARRAY(attr_PseudoCounters_read);
        attr_PseudoCounters_read = (pc_nb > 0) ? new Tango::DevString[pc_nb] : NULL;

        PseudoCoInGrp *pc = static_cast<PseudoCoInGrp*>(&ch);
        vector<SingleValChInGrp*>::iterator pc_elem_it = pc->uses.begin();
        for(; pc_elem_it != pc->uses.end(); ++pc_elem_it)
        {
            SingleValChInGrp *pc_elem = *pc_elem_it;
            if(pc_elem->get_type() != PSEUDO_EXP_CHANNEL &&
               pc_elem->attr_idx < 0 &&
               is_elem_only_used_in_pc(pc, pc_elem))
            {
                phy_elts_to_delete.push_back(pc_elem->id);
            }
        }
    }
    else if(type == ZEROD_ELEM)
    {
        attr_list_name = "Motors";
        property_name = "Motor_List";

        v_str_ite = find(motor_List.begin(),motor_List.end(),ch_id);
        assert(v_str_ite != motor_List.end());
        motor_List.erase(v_str_ite);

        ch_list = &motor_List;
        mot_nb = motor_List.size();

        SingleValChInGrp *single_val_ch = static_cast<SingleValChInGrp*>(&ch);
        if(single_val_ch->used_by.empty())
        {
            phy_elts_to_delete.push_back(channel.get_id());
        }

        SAFE_DELETE_ARRAY(attr_Motors_read);
        attr_Motors_read = (mot_nb > 0) ? new Tango::DevString[mot_nb] : NULL;
    }    

//
// Delete all channel information. (it is done because just adding the new
// channel can be very complicated due to dependencies of channels)
//
    unsigned long l;

    for(l = 0;l < ind_elts.size();l++) delete ind_elts[l];
    ind_elts.clear();

    for(l = 0; l < implied_ctrls.size(); l++) delete implied_ctrls[l];
    implied_ctrls.clear();

    for(l = 0;l < pseudo_elts.size();l++) delete pseudo_elts[l];
    pseudo_elts.clear();

    for(l = 0; l < implied_pseudo_ctrls.size(); l++) delete implied_pseudo_ctrls[l];
    implied_pseudo_ctrls.clear();

//
// Remove element from list of user elements
//
    v_str_ite = find(user_group_elt.begin(),user_group_elt.end(),ch_id);
    assert(v_str_ite != user_group_elt.end());
    user_group_elt.erase(v_str_ite);

    usr_elt_nb = ct_nb + zeroD_nb + oneD_nb + twoD_nb + pc_nb;
    assert((int32_t)user_group_elt.size() == usr_elt_nb);

//
// Remove element(s) from list of physical elements
//
    for(unsigned long ul = 0; ul < phy_elts_to_delete.size(); ++ul)
    {
        v_str_ite = find(phys_group_elt.begin(), phys_group_elt.end(), phy_elts_to_delete[ul]);
        if(v_str_ite == phys_group_elt.end())
        {
cout << "Failed to delete physical element : "<<phy_elts_to_delete[ul]<< endl;
PRINT_ELEMENTS(phys_group_elt,"List of phys elems:");
assert(false);
        }
        assert(v_str_ite != phys_group_elt.end());
        phys_group_elt.erase(v_str_ite);
    }

    ind_elt_nb = phys_group_elt.size();

    SAFE_DELETE_ARRAY(attr_Channels_read);
    attr_Channels_read = (usr_elt_nb > 0) ? new Tango::DevString[usr_elt_nb] : NULL;

//
// Update device properties
//
    write_list_props_to_db(property_name, *ch_list);

//
// Now start building all information.
//
    build_grp();

//
// Update pool data structure
//
    MeasurementGroupPool &mg = get_measurement_group_obj();

    init_pool_element(&mg);

//
// Update attribute indexes
//
    update_attr2channel_indexes();

//
// Update Timer/Monitor attributes if necessary
//

    if(ch_alias == timer)
    {
        string not_initialized(NOT_INITIALIZED);
        Tango::DeviceAttribute attr("Timer",not_initialized);
        Tango::DeviceProxy proxy(get_name());
        proxy.write_attribute(attr);
    }
    if(ch_alias == monitor)
    {
        string not_initialized(NOT_INITIALIZED);
        Tango::DeviceAttribute attr("Monitor",not_initialized);
        Tango::DeviceProxy proxy(get_name());
        proxy.write_attribute(attr);
    }

//
// Send event on the proper channel list
//

    Tango::Attribute &list_att = dev_attr->get_attr_by_name(attr_list_name.c_str());
    Tango::Attribute &ch_list_att = dev_attr->get_attr_by_name("Channels");
    {
        Tango::AutoTangoMonitor synch(this);
        if(type == COTI_ELEM)
        {
            // if timer has been deleted, the counters event has already
            // been sent in the write_attribute method of the Timer attribute.
            // Even if we try to send the event it would be filtered anyway
            if(ch_alias != timer)
            {
                read_Counters(list_att);
            }
        }
        else if(type == ZEROD_ELEM)
        {
            read_ZeroDExpChannels(list_att);
        }
        else if(type == ONED_ELEM)
        {
            read_OneDExpChannels(list_att);
        }
        else if(type == TWOD_ELEM)
        {
            read_TwoDExpChannels(list_att);
        }
        else if(type == MOTOR_ELEM)
        {
            read_Motors(list_att);
        }
        list_att.fire_change_event();

        read_Channels(ch_list_att);
        ch_list_att.fire_change_event();
    }

//
// Inform the pool so it can send a change event on the measurement group list
//
    pool_dev->measurement_group_elts_changed(get_id());

}

bool MeasurementGroup::is_elem_only_used_in_pc(PseudoCoInGrp *pc, SingleValChInGrp *elem)
{
    vector<SingleValChInGrp*>::iterator used_by_it = elem->used_by.begin();
    for(; used_by_it != elem->used_by.end(); ++used_by_it)
    {
        if(find(pc->uses_pc.begin(),pc->uses_pc.end(),*used_by_it) == pc->uses_pc.end() &&
           *used_by_it != pc)
            return false;
    }
    return true;
}

//+----------------------------------------------------------------------------
//
// method : 		MeasurementGroup::handle_temporary_siblings
//
// description : 	should be invoked by the ghost measurement group periodically
//                  to increase the age of the temporary siblings and if
//					necessary delete them
//
//-----------------------------------------------------------------------------

void MeasurementGroup::handle_temporary_siblings()
{
    pool_dev->handle_tmp_measurement_groups();
}

//+------------------------------------------------------------------
/**
 *	method:	MeasurementGroup::get_pc_from_id
 *
 *	description: Obtains the PseudoCoInGrp structure for
 *               the given ind element id
 *
 * @return A reference to an PseudoCoInGrp data structure
 *         for the given ind element id
 */
//+------------------------------------------------------------------

MeasurementGroup::PseudoCoInGrp &MeasurementGroup::get_pc_from_id(Pool_ns::ElementId id)
{
    vector<PseudoCoInGrp*>::iterator ind_ite = pseudo_elts.begin();
    for(; ind_ite != pseudo_elts.end(); ind_ite++)
    {
        PseudoCoInGrp *ind = (*ind_ite);
        if(ind->id == id)
            break;
    }

    if (ind_ite == pseudo_elts.end())
    {
        TangoSys_OMemStream o;
        o << "No PseudoCoInGrp with id " << id;
        o << " found in ind pseudo counter list" << ends;

        Tango::Except::throw_exception(
                (const char *)"Pool_BadArgument",o.str(),
                (const char *)"MeasurementGroup::get_pc_from_id");
    }
    return *(*ind_ite);
}

Pool_ns::PoolElement &MeasurementGroup::get_pool_obj()
{
    return pool_dev->get_measurement_group(get_id());
}

//+------------------------------------------------------------------
/**
 *	method:	MeasurementGroup::get_pc_ctrl_grp_from_id
 *
 *	description: Obtains the CtrlGrp structure for
 *               the given ind element name
 *
 * @return A reference to an CtrlGrp data structure
 *         for the given ind element id
 */
//+------------------------------------------------------------------

MeasurementGroup::PseudoCoCtrlInGrp &
MeasurementGroup::get_pc_ctrl_grp_from_id(Pool_ns::ElementId ctrl_id, int32_t &pos)
{
    vector<PseudoCoCtrlInGrp*>::iterator ctrl_ite = implied_pseudo_ctrls.begin();
    int32_t p = 0;
    for(; ctrl_ite != implied_pseudo_ctrls.end(); ++ctrl_ite, ++p)
    {
        PseudoCoCtrlInGrp *ctrl = (*ctrl_ite);
        if(ctrl->ctrl_id == ctrl_id)
            break;
    }

    if (ctrl_ite == implied_pseudo_ctrls.end())
    {
        TangoSys_OMemStream o;
        o << "No PseudoCoCtrlInGrp with id " << ctrl_id <<
             " found in controller element list" << ends;

        Tango::Except::throw_exception(
                (const char *)"Pool_BadArgument",o.str(),
                (const char *)"MeasurementGroup::get_pc_ctrl_grp_from_id");
    }
    pos = p;
    return *(*ctrl_ite);
}

}	//	namespace
