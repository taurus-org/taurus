//+=============================================================================
//
// file :         MotorThread.cpp
//
// description :  C++ source for the MotorThread file.
//                  This is simply a forward to method defined in the Pool
//                  object
//
// project :      Sardana Pool Device Server
//
// $Author: tiagocoutinho $
//
// $Revision: 296 $
//
// $Log: MotorThread.cpp,v $
// Revision 1.41  2007/08/30 12:40:39  tcoutinho
// - changes to support Pseudo counters.
//
// Revision 1.40  2007/08/23 10:28:08  tcoutinho
// - fix deadlock when motor group movement throws exception
// - fix order of sending events. Now, when a motion ends, the thread waits for the instability time (if any) to pass, send a final position event and send a final state event
//
// Revision 1.39  2007/08/17 13:07:30  tcoutinho
// - pseudo motor restructure
// - pool base dev class restructure
// - initial commit for pseudo counters
//
// Revision 1.38  2007/08/03 09:32:42  tcoutinho
// this version still has a bug
//
// Revision 1.37  2007/07/30 11:00:59  tcoutinho
// Fix bug 5 : Additional information for controllers
//
// Revision 1.36  2007/07/12 13:12:56  tcoutinho
// - removed extra msg
//
// Revision 1.35  2007/06/13 15:18:58  etaurel
// - Fix memory leak
//
// Revision 1.34  2007/05/31 09:54:40  etaurel
// - Fix some memory leaks
//
// Revision 1.33  2007/05/25 12:48:10  tcoutinho
// fix the same dead locks found on motor system to the acquisition system since release labeled for Josep Ribas
//
// Revision 1.32  2007/05/24 09:25:25  tcoutinho
// - fixes to the position attribute quality
// - removed unnecessary locks
// - removed junk code
//
// Revision 1.31  2007/05/22 16:25:31  tcoutinho
// - dead lock fix & state event fix
//
// Revision 1.30  2007/05/22 13:42:04  tcoutinho
// - fix dead lock on internal event propagation in case of an abort command
//
// Revision 1.29  2007/05/18 09:24:22  tcoutinho
// - second try to fix dead lock bug
//
// Revision 1.28  2007/05/18 09:04:06  tcoutinho
// - first try to fix dead lock bug
//
// Revision 1.27  2007/05/16 16:26:22  tcoutinho
// - fix dead lock
//
// Revision 1.26  2007/05/16 07:53:17  tcoutinho
// - added some logging to find bug
//
// Revision 1.25  2007/02/08 08:51:16  etaurel
// - Many changes. I don't remember the list
//
// Revision 1.24  2007/01/26 08:36:48  etaurel
// - We now have a first release of ZeroDController
//
// Revision 1.23  2007/01/23 08:27:22  tcoutinho
// - fix some pm bugs found with the test procedure
// - added internal event for MotionEnded
//
// Revision 1.22  2007/01/17 09:38:14  tcoutinho
// - internal events bug fix.
//
// Revision 1.21  2007/01/16 14:32:22  etaurel
// - Coomit after a first release with CT
//
// Revision 1.20  2006/12/28 15:36:58  etaurel
// - Fire events also on the motor limit_switches attribute
// - Throw events even in simulation mode
// - Mange motor position limit switches dependant of the offset attribute
//
// Revision 1.19  2006/12/20 10:25:36  tcoutinho
// - changes to support internal event propagation
// - bug fix in motor groups containing other motor groups or pseudo motors
//
// Revision 1.18  2006/12/18 11:37:10  etaurel
// - Features are only boolean values invisible from the external world
// - ExtraFeature becomes ExtraAttribute with data type of the old features
//
// Revision 1.17  2006/11/20 14:32:43  etaurel
// - Add ghost group and event on motor group position attribute
//
// Revision 1.16  2006/11/07 14:57:09  etaurel
// - Now, the pool really supports different kind of controllers (cpp and py)
//
// Revision 1.15  2006/11/03 15:48:59  etaurel
// - Miscellaneous changes that I don't remember
//
// Revision 1.14  2006/10/25 10:04:31  etaurel
// - Complete implementation of the ReloadControllerCode command
// - Handle end of movment when reading position in polling mode
//
// Revision 1.13  2006/10/24 14:50:53  etaurel
// - The test suite is now back into full success
//
// Revision 1.12  2006/10/20 15:37:30  etaurel
// - First release with GetControllerInfo command supported and with
// controller properties
//
// Revision 1.11  2006/08/08 12:17:19  etaurel
// - It now uses the multi-motor controller interface
//
// Revision 1.10  2006/07/07 12:38:43  etaurel
// - Some changes in file header
// - Commit after implementing the group multi motor read
//
//
// copyleft :     CELLS/ALBA
//                  Edifici Ciències Nord. Mòdul C-3 central.
//                Campus Universitari de Bellaterra. Universitat Autònoma de Barcelona
//                08193 Bellaterra, Barcelona
//                Spain
//
//+=============================================================================

#include "PyUtils.h"
#include "Pool.h"
#include "PoolUtil.h"
#include "MotorThread.h"
#include "Motor.h"
#include "MotorGroup.h"

#include <limits>

namespace Pool_ns
{

void MotInMove::Lock()
{
    try 
    {
        atm_ptr = new Tango::AutoTangoMonitor(motor);
    }
    catch (Tango::DevFailed &e)
    {
        cout << endl << "\tMotInMove: UNEXPECTED - failed to get AutoTangoMonitor for " 
             << mot.name << ": " << endl;
        Tango::Except::print_exception(e);
        throw e;
    }
}

void MotInMove::Unlock()
{
    SAFE_DELETE(atm_ptr);
}

GrpInMove::GrpInMove(MotorGroupPool &ref, MotorGroup_ns::MotorGroup *dev):
    ElemInMove(dev), mgp(ref), grp(dev)
{
    grp_proxy=new Tango::DeviceProxy(grp->get_name());
}

void CtrlInMove::lock()
{
    if (!lock_ptr)
        lock_ptr = new AutoPoolLock(ct.get_ctrl_class_mon());
}

void CtrlInMove::unlock()
{
    if(lock_ptr)
    {
        delete lock_ptr;
        lock_ptr = NULL;
    }
}

GrpInMove &GrpInMove::operator=(const GrpInMove &rhs)
{
    grp=rhs.grp; grp_proxy=rhs.grp_proxy ; state_att=rhs.state_att;
    return *this;
}

//+------------------------------------------------------------------
/**
 *    method:    MotorThread::run
 *
 *    description:    The run method of the thread taking care of the
 *                     running move. This is simply a call to the
 *                     forward_move of the 
 *
 * arg(s) : - mot_ids: The vector
 *             - positions: The memorized motor(s)
 */
//+------------------------------------------------------------------

void MotorThread::run(void *ptr)
{
    AutoCleanPythonGIL auto_clean_gil;
    
    cout4 << "The MotorThread is talking" << endl;

    try
    {
        pool_dev->forward_move(mot_ids,positions,this);
    }
    catch (Tango::DevFailed &e)
    {
        Tango::Device_4Impl *dev_impl = NULL;
        
        if(group_id != -1) 
            dev_impl = failed_group;
        else
            dev_impl = failed_mot;
        
        Tango::DevError &de = e.errors[0];
        dev_impl->get_logger()->error_stream() 
            << log4tango::LogInitiator::_begin_log 
            << "Tango exception in motor thread: [" 
            << de.origin << "] (" 
            << de.reason << ") " 
            << de.desc << endl;
            
        Tango::Except::print_exception(e);

        for (unsigned long loop = 0;loop < mot_ids.size();loop++)
        {
            MotorPool &mot_ref = 
                pool_dev->get_physical_motor(mot_ids[loop]);
            Motor_ns::Motor *mot_dev = pool_dev->get_motor_device(mot_ref);
            mot_dev->set_mov_th_id(0);
        }
        
        if (group_id != -1)
        {
            failed_group->th_failed = true;
            failed_group->th_except = e.errors;
            MotorGroup_ns::MotorGroup *tmp_grp_ptr = 
                pool_dev->get_motor_group_device(group_id);
            tmp_grp_ptr->set_mov_th_id(0);
        }
        else
        {        
            failed_mot->th_failed = true;    
            failed_mot->th_except = e.errors;
        }
        
        {
            omni_mutex_lock lo(*mon_ptr);
            mon_ptr->signal();
        }
    }
}

//+------------------------------------------------------------------
/**
 *    method:    Pool::forward_move
 *
 *    description:    Move motor(s) to the wanted position(s)
 *                     This method as run by a separate thread
 *
 * arg(s) : - mot_ids: The vector
 *             - positions: The memorized motor(s)
 *             - pos_backlash: The final position if a backlash has to be applied
 *                             0 otherwise
 *             - th : The thread object
 */
//+------------------------------------------------------------------


void Pool::forward_move(vector<ElementId> &mot_ids, vector<double> &positions,
                        MotorThread *th, bool wait_flag)
{
    vector<CtrlInMove>             implied_ctrls;
    vector<MotInMove>             implied_mots;
    auto_ptr<GrpInMove>            implied_group;
    vector<double>                 back_pos(mot_ids.size(),0.0);
    vector<bool>                 obj_ext_trigg(mot_ids.size() + 1,true);
        
//
// Send the info to the controller(s)
//
    try
    {
        send_to_ctrl(mot_ids, positions, th, wait_flag, 
                     implied_ctrls, implied_mots,
                     implied_group, back_pos);
    }
    catch (Tango::DevFailed &df)
    {
        Tango::Except::re_throw_exception(df, "Pool_MotorThreadFailed", "Not able to execute send_to_ctrl", "Pool::forward_move");
    }

//
// Leave method if we don't want to wait for the end of moving
//
    
    if (wait_flag == false)
        return;
        
//
// Set all devices implied in this move as externally triggered polling
// The unset is done just before sending the event to the customer
// If done elsewhere, it could happend that the state is switched to
// ON but the pos. info is still in the polling buffer and will be
// returned to the caller.
//
    try
    {
        set_ext_trigg(implied_mots, implied_group, th, obj_ext_trigg);
    }
    catch (Tango::DevFailed &df)
    {
        Tango::Except::re_throw_exception(df, "Pool_MotorThreadFailed", "Not able to execute set_ext_trigg", "Pool::forward_move");
    }

//
// Wait for end of moving
//

    try
    {
        moving_loop(implied_ctrls, implied_mots, implied_group, th, back_pos,
                    obj_ext_trigg);
    }
    catch (Tango::DevFailed &df)
    {
        Tango::Except::re_throw_exception(df, "Pool_MotorThreadFailed", "Not able to execute moving_loop", "Pool::forward_move");
    }
}

//+------------------------------------------------------------------
/**
 *    method:    Pool::send_to_ctrl
 *
 *    description:    Send position to controller(s)
 *
 * arg(s) : - mot_ids: The vector
 *             - positions: The memorized motor(s)
 *             - th: The thread object
 *             - wait_flag: 
 *             - implied_ctrls:
 *             - implied_mots:
 *             - implied_group:
 *             - pos_backlash: The final position if a backlash has to be applied
 *                             0 otherwise
 */
//+------------------------------------------------------------------

void Pool::send_to_ctrl(vector<ElementId> &mot_ids,
                        vector<double> &positions,
                        MotorThread *th,
                        bool wait_flag,
                        vector<CtrlInMove> &implied_ctrls,
                        vector<MotInMove> &implied_mots,
                        auto_ptr<GrpInMove> &implied_group,
                        vector<double> &back_pos)
{

    long mot_nb = mot_ids.size();
    long loop;
//
// Find which ctrls are implied in this move and init motor infos
// This part of code looks into pool device data. Lock the pool device
// to protect this part of code
//
    {
        Tango::AutoTangoMonitor atm(this);

//
// Retrieve motor group object if needed
        if (th->group_id != -1)
        {
            MotorGroupPool &mgp = get_motor_group(th->group_id);
            MotorGroup_ns::MotorGroup *mg_dev = get_motor_group_device(mgp);
            GrpInMove *grp_mv = new GrpInMove(mgp, mg_dev);
            auto_ptr<GrpInMove> tmp_ptr(grp_mv);
            implied_group = tmp_ptr;
            th->failed_group = implied_group->grp;
        }

//
// Find which ctrls are implied in this move and init motor infos
//
        for (loop = 0;loop < mot_nb;loop++)
        {
            MotorPool &mot_ref = get_physical_motor(mot_ids[loop]);
            Motor_ns::Motor *mot_dev = get_motor_device(mot_ref);
            ControllerPool &ctrl_ref = get_controller_from_element(mot_ids[loop]);
            
            int32_t idx_in_grp = -1;
            if(th->group_id != -1)
            {
                idx_in_grp = implied_group->grp->get_physical_index_in_group(mot_ref.id);
            }
            MotInMove tmp_mot(mot_ids[loop], mot_ref, mot_dev, ctrl_ref, idx_in_grp);
            
            implied_mots.push_back(tmp_mot);
            
            ElementId ct_id = ctrl_ref.id;
    
            CtrlInMove tmp_ctrl(ct_id,ctrl_ref);
            if (implied_ctrls.empty() == true)
                implied_ctrls.push_back(tmp_ctrl);
            else
            {
                bool ctrl_added = false;
                for (unsigned long l = 0;l < implied_ctrls.size();l++)
                {
                    if (implied_ctrls[l].ctrl_id == ct_id)
                    {
                        ctrl_added = true;
                        break;
                    }
                }
                if (!ctrl_added)
                    implied_ctrls.push_back(tmp_ctrl);
            }
        }

//
// Init what could failed if there is no motor group
//
        if (th->group_id == -1)
            th->failed_mot = implied_mots[0].motor;
                
//
// Create motor proxies if not already done
// Take the oportunity to do it now while the pool device is
// already locked
//

        if (proxy_created == false)
        {
            create_proxies();
            proxy_created = true;
        }
    }

    vector<DelayedEvt> internal_events;

    string except_func("PreStartAll");
    bool state_changed = false;
    vector<CtrlInMove>::iterator impl_ctrl_ite;
    vector<CtrlInMove>::reverse_iterator impl_ctrl_rite;
    
    int th_id = omni_thread::self()->id();
    
    try
    {
        
//
// Lock all the motors implied in this move only if request coming
// from a group movement. In the other case, the motor lock is already taken
// by the ORB thread which executes the write_attribute request
// Takes this oportunity to write the movement thread id in Motor object
//

        if (th->group_id != -1)
        {
            for (loop = 0;loop < mot_nb;loop++)
            {
                implied_mots[loop].Lock();
                Motor_ns::Motor *mot_dev = implied_mots[loop].motor;
                mot_dev->set_mov_th_id(th_id);
            }
            implied_group->grp->set_mov_th_id(th_id);
        }
        else
            implied_mots[0].motor->set_mov_th_id(th_id);
        
//
// Lock all the controllers implied in this move
//
        
        for (impl_ctrl_ite = implied_ctrls.begin();
             impl_ctrl_ite != implied_ctrls.end();
             ++impl_ctrl_ite)
        {
            impl_ctrl_ite->lock();
        }
                            
//
// Send the PreStartAll to all implied controller
//

        loop = -1;
        
        for (impl_ctrl_ite = implied_ctrls.begin();
             impl_ctrl_ite != implied_ctrls.end();
             ++impl_ctrl_ite)
        {
            ControllerPool &cp = impl_ctrl_ite->ct;
            MotorController *mc = static_cast<MotorController *>(cp.get_controller());
            mc->PreStartAll();
        }
                
//
// Send PreStartOne and StartOne to each implied motor
//

        double send_pos;
        double backlash;
                
        for (loop = 0;loop < mot_nb;loop++)
        {
            MotorPool &mp = implied_mots[loop].mot;
            ControllerPool &cp = implied_mots[loop].ct;
            Motor_ns::Motor *mot_dev = get_motor_device(mp);
//
// If the request comes from a group movement, we need to check that
// each motor member of the group is not already moving and we need
// to convert the position into dial position
// When this method is called due to a backlash (flag wait_flag set to
// false), we already have a valid position
//

            except_func = "NoFunc";
            if (th->group_id != -1)
            {
                if (wait_flag == true)
                {
                    mot_dev->set_group_movement(true);
                    Tango::DeviceAttribute da("Position", positions[loop]);
                    get_element_proxy(mp)->write_attribute(da);
                    send_pos = mot_dev->get_dial_pos();
                    backlash = mot_dev->get_back_pos();
                    if (mot_dev->has_backlash_enabled())
                    {
                        back_pos[loop] = backlash;
                    }
                    mot_dev->set_group_movement(false);
                }
                else
                {
                    send_pos = positions[loop];
                }
            }
            else
            {
                send_pos = positions[loop];
                backlash = mot_dev->get_back_pos();
                if ((mot_dev->has_backlash_enabled()) && (wait_flag == true))
                    back_pos[loop] = backlash;
            }
                        
            MotorController *mc = static_cast<MotorController *>(cp.get_controller());
            except_func = "PreStartOne";
            bool ret = mc->PreStartOne(mp.get_axis(), send_pos);
                
            if (ret == true)
            {
                except_func = "StartOne";
                mc->StartOne(mp.get_axis(), send_pos);
            }
            else
            {
                TangoSys_OMemStream o;
                o << "Impossible to move motor device " << 
                     implied_mots[loop].mot.name << " (" << 
                     implied_mots[loop].mot.get_full_name() << ")" <<
                     ". The PreStartOne() function returns false" << ends;
    
                Tango::Except::throw_exception(
                        (const char *)"Pool_PrestartOne",o.str(),
                        (const char *)"Pool::forward_move");
            }
        }
    
//
// Send a User Event and internal event on state attribute for each implied 
// motors. It is not necessary to lock the device between the state setting 
// and the event firing because the user thread is still in the motor 
// write_Position method and therefore, the motor device is locked.
// Locking the motor device by this thread at that moment will be
// a dead lock
//

        state_changed = true;
        for (loop = 0;loop < mot_nb;loop++)
        {
            MotorPool &mp = implied_mots[loop].mot;
            Motor_ns::Motor *mot_dev = get_motor_device(mp);
            Tango::DevState old_state = mot_dev->get_state();
            mot_dev->set_state(Tango::MOVING);
            
            if (wait_flag == true)
            {
                implied_mots[loop].state_att.fire_change_event();
                
                if(mp.has_listeners())
                {
                    DelayedEvt delayed_evt(StateChange, &mp);
                    delayed_evt.evt.old.state = PoolTango::toPool(old_state);
                    delayed_evt.evt.curr.state = MOVING;
                    
                    if (th->group_id != -1)
                        delayed_evt.exception = &implied_group->mgp;
                    
                    internal_events.push_back(delayed_evt);
                }
            }
        }
        
        if (th->group_id != -1)
        {
            implied_group->grp->clear_event_fired_array();
            Tango::DevState old_state = implied_group->grp->get_state();
            implied_group->grp->set_state(Tango::MOVING);
            
            if (wait_flag == true)
            {
                implied_group->state_att.fire_change_event();
                
                if(implied_group->mgp.has_listeners())
                {
                    DelayedEvt delayed_evt(StateChange, &implied_group->mgp);
                    delayed_evt.evt.old.state = PoolTango::toPool(old_state);
                    delayed_evt.evt.curr.state = MOVING;
                    internal_events.push_back(delayed_evt);
                }
            }
        }
            
//
// Send the StartAll to all implied controller
//

        except_func = "StartAll";    
        loop = -1;
        for (impl_ctrl_ite = implied_ctrls.begin();
             impl_ctrl_ite != implied_ctrls.end();
             ++impl_ctrl_ite)
        {
            ControllerPool &cp = impl_ctrl_ite->ct;
            MotorController *mc = static_cast<MotorController *>(cp.get_controller());
            mc->StartAll();
        }
    }
    catch (Tango::DevFailed &e)
    {
        DEBUG_STREAM << "Tango exception in mov. thread: managing thread exception..." << endl;
        th->manage_thread_exception(e, implied_ctrls, implied_mots,
                                    implied_group, except_func, state_changed,
                                    loop);    
        DEBUG_STREAM << "Tango exception in mov. thread: thread exception managed." << endl;
    }
    catch (...)
    {
        Tango::DevErrorList err_list(1);
        err_list.length(1);

        err_list[0].severity = Tango::ERR;
        err_list[0].origin = CORBA::string_dup("Pool::forward_move");
        err_list[0].reason = CORBA::string_dup("Motor_ControllerFailed");
        err_list[0].desc = 
            CORBA::string_dup("Controller has sent an unknown exception");
    
        Tango::DevFailed e(err_list);
        th->manage_thread_exception(e, implied_ctrls, implied_mots, 
                                    implied_group, except_func,
                                    state_changed, loop);
    }

//
// Unlock all the controllers implied in this move
//

    for (impl_ctrl_rite = implied_ctrls.rbegin();
         impl_ctrl_rite != implied_ctrls.rend();
         ++impl_ctrl_rite)
    {
        impl_ctrl_rite->unlock();
    }

//
// Unlock all motors (only for group)
//

    if (th->group_id != -1)
    {
        for (long ctr = mot_nb-1; ctr >=0; --ctr)
        {
            implied_mots[ctr].Unlock();
        }
    }
            
//
// Inform motor/group device that all the check are OK
//

    if (th->group_id == -1)
        implied_mots[0].motor->th_failed = false;
    else
        implied_group->grp->th_failed = false;

    {
        omni_mutex_lock lo(*(th->mon_ptr));
        th->mon_ptr->signal();
    }

//
// Send pending internal events
//

    vector<DelayedEvt>::iterator evt_ite = internal_events.begin();
    for(;evt_ite != internal_events.end(); evt_ite++)
    {
        evt_ite->src->fire_pool_elem_change(&evt_ite->evt,evt_ite->exception);     
    }
}

//+------------------------------------------------------------------
/**
 *    method:    Pool::moving_loop
 *
 *    description:    Wait for end of moving and send appropriate
 *                     event(s) to the right device at the right moment
 *
 * arg(s) : - implied_ctrls:
 *             - implied_mots:
 *             - implied_group:
 *             - th: The thread object
 *             - pos_backlash: The final position if a backlash has to be applied
 *                             0 otherwise
 *             - obj_trigg :
 */
//+------------------------------------------------------------------

void Pool::moving_loop(vector<CtrlInMove> &implied_ctrls,
                       vector<MotInMove> &implied_mots,
                       auto_ptr<GrpInMove> &implied_group,
                       MotorThread *th,
                       vector<double> &back_pos,
                       vector<bool> &obj_trigg)
{

    long mot_nb = implied_mots.size();

//
// Wait for state to be something different than MOVING
// Read controller every 10 mS and fire an event as soon
// as the state is something different than MOVING
// Lock the device between the state reading and the event
// firing
// If we are in a shutdown phase, while a motor is moving, the 
// motor object is made unavailable from Proxy devices.
// In such a case, use direct motor access
//        

    Tango::DevState d_state = Tango::UNKNOWN;
    struct timespec wait,rem;
        
    wait.tv_sec = 0;
    wait.tv_nsec = motThreadLoop_SleepTime * 1000000;

    Tango::DeviceImpl *running_dev;
    Tango::DeviceProxy *proxy_dev;
    
    MotorPool &mp = implied_mots[0].mot;
    Motor_ns::Motor *m_dev = implied_mots[0].motor;
    
//
// Init some data according to group or motor
//

    if (th->group_id == -1)
    {
        running_dev = m_dev;
        proxy_dev = get_element_proxy(mp);
    }
    else
    {
        running_dev = implied_group->grp;
        proxy_dev = implied_group->grp_proxy; 
    }
    
    bool by_proxy = true;
    long read_ctr = 0;
    bool abort_cmd_executed = false;
    std::string except_func = "NoFunc";

    // end of motion external events
    std::vector<ElemInMove*> end_mot_ext_evts;
    // end of motion internal events
    std::vector<DelayedEvt> end_mot_int_evts;
    
    while(1)
    {
        std::vector<DelayedEvt> internal_events;
        {
            Tango::AutoTangoMonitor atm(running_dev);
            
//
// Read state
//
            try
            {
                if (by_proxy == true)
                {
                    d_state = proxy_dev->state();
                }
                else
                {
                    running_dev->always_executed_hook();
                    d_state = running_dev->get_state();
                }
            }
            catch (Tango::DevFailed &e)
            {
                string err_reason(e.errors[0].reason.in());
                if (err_reason == "API_DeviceNotExported")
                {
                    by_proxy = false;
                    continue;
                }
            }
            abort_cmd_executed = (th->group_id != -1) ? 
                implied_group->grp->abort_cmd_executed : 
                m_dev->abort_cmd_executed;

//
// For group, it is possible that we need to send event(s) for some motor(s)
// before we send the group event (for motor with small movement)
// E.x.: old motor positions are (100,100) new movement to (110,5000). It is
// expected that the first motor reaches the final position much sooner than
// the second motor (if they have the same velocity). In this case send the 
// state event for the first motor now!
//
            bool do_any_backlash = false;
            if ((th->group_id != -1) && (abort_cmd_executed == false))
            {
                vector<Tango::DevState> &sta_array = 
                    implied_group->grp->get_state_array();
                
                vector<bool> &event_array = 
                    implied_group->grp->get_event_fired_array();
                
                vector<ElementId> back_id;
                vector<double> ba;
                
                for (long loop = 0;loop < mot_nb;loop++)
                {
                    if ((sta_array[loop] != Tango::MOVING) && 
                        (event_array[loop] != true))
                    {
                        MotInMove &mot_mv = implied_mots[loop];
                        MotorPool &mot = mot_mv.mot;
                        Motor_ns::Motor *mot_dev = mot_mv.motor;
                        bool mot_abort = mot_dev->abort_cmd_executed; 
                        abort_cmd_executed |= mot_abort;
                            
                        if (mot_abort == false)
                        {
                            if (mot_dev->has_backlash_enabled())
                            {
                                // Only perform backlash if the motion ended well
                                if(sta_array[loop] == Tango::ON)
                                {
                                    back_id.push_back(mot_mv.mot_id);
                                    ba.push_back(back_pos[loop]);
                                    do_any_backlash = true;
                                }
                                // clear the backlash flag so the second forward_move 
                                // for doing the backlash doesn't try to redo it again
                                mot_dev->set_backlash_enabled(false);
                                back_pos[loop] = 0.0;
                            }
                            else
                            {
                                mot_mv.state_att.fire_change_event();
                                
                                if(mot.has_listeners())
                                {
                                    PoolElementEvent evt(StateChange,&mot);
                                    evt.old.state = MOVING;
                                    evt.curr.state = PoolTango::toPool(sta_array[loop]);
                                    mot.fire_pool_elem_change(&evt, 
                                            &implied_group->mgp);
                                }
                                
                                event_array[loop] = true;
                            }
                        }
                    }
                }

//
// If the state of the group is ALARM meaning that it has reached a limit,
// abort all the group motion
//

                if (d_state == Tango::ALARM)
                {
                    proxy_dev->command_inout("Abort");
                }
                
//
// If some motors which are group members have some backlash
// defined, do it now
//
                
                if (back_id.size() != 0)
                {
                    try
                    {    
                        forward_move(back_id, ba, th, false);
                        continue;
                    }
                    catch (Tango::DevFailed &e)
                    {
                        th->manage_thread_exception(e,implied_ctrls,
                                implied_mots,implied_group,
                                except_func,true,-1);
                    }
                }
            }

            if (d_state != Tango::MOVING)
            {
                if (th->group_id != -1)
                {
                        
//
// This is the end of the motion, we have to remove the position from the Tango
// polling buffer but we cant do this now (possible dead lock with Tango polling 
// thread). We can do this only after the device has been unlocked. In order 
// that a client listenning on event get the correct value in its event callback
// (if he requires it), read the value and store it into the polling buffer but 
// do not fire position event
//

                    read_pos_while_moving(implied_mots,implied_group,NULL,
                            th,obj_trigg,false,false);
                    
//
// If an abort was issued then send state event for each pending motor
//
                    if(abort_cmd_executed == true)
                    {
                        vector<Tango::DevState> &sta_array = 
                            implied_group->grp->get_state_array();
                        
                        vector<bool> &event_array = 
                            implied_group->grp->get_event_fired_array();
                        
                        vector<long> back_id;
                        vector<double> ba;
                        
                        for (long loop = 0;loop < mot_nb;loop++)
                        {    
                            if (event_array[loop] != true)
                            {
                                MotInMove &mot_mv = implied_mots[loop];
                                MotorPool &mot = mot_mv.mot;
                                mot_mv.state_att.fire_change_event();
                                
                                if(mot.has_listeners())
                                {
                                    DelayedEvt delayed_evt(StateChange,&mot);
                                    delayed_evt.evt.old.state = MOVING;
                                    delayed_evt.evt.curr.state = PoolTango::toPool(sta_array[loop]);
                                    delayed_evt.exception = &implied_group->mgp;
                                    end_mot_int_evts.push_back(delayed_evt);
                                }
                                event_array[loop] = true;
                            }
                        }
                    }
//
// Delay sending state event: A state event should be sent
// only after a 'potential' instability time as passed and
// after the last position event as been sent
//
                    // implied_group->state_att.fire_change_event();
                    end_mot_ext_evts.push_back(implied_group.get());
                    
                    // Only send event if not doing backlash to avoid ON - MOVING - ON - MOVING - ON
                    // sequence of events
                    if (!do_any_backlash)
                    {
                        if(implied_group->mgp.has_listeners())
                        {
                            DelayedEvt delayed_evt(StateChange, 
                                                   &implied_group->mgp);
                            delayed_evt.evt.old.state = MOVING;
                            delayed_evt.evt.curr.state = PoolTango::toPool(d_state);
                            delayed_evt.exception = &implied_group->mgp;
                            end_mot_int_evts.push_back(delayed_evt);
                        }
                    }
                    break;
                }
                else
                {
                    // do backlash for individual motor movement
                    if (m_dev->has_backlash_enabled() && abort_cmd_executed == false)
                    {
                        // clear the backlash flag so the second forward_move 
                        // for doing the backlash doesn't try to redo it again
                        m_dev->set_backlash_enabled(false);
                        double backlash = back_pos[0];
                        back_pos[0] = 0.0;

                        // Only perform backlash if the motion ended well
                        if(d_state == Tango::ON)
                        {
                            vector<ElementId> back_id;
                            vector<double> ba;

                            back_id.push_back(implied_mots[0].mot_id);
                            ba.push_back(backlash);

                            try
                            {
                                forward_move(back_id, ba, th, false);
                            }
                            catch (Tango::DevFailed &e)
                            {
                                th->manage_thread_exception(e,implied_ctrls,
                                        implied_mots,implied_group,
                                        except_func, true, -1);
                            }
                        }
                    }
                    else
                    {
                            
//
// This is the end of the motion, we  have to remove the position from the Tango
// polling buffer but we cant do this now (possible dead lock with Tango polling 
// thread). We can do this only after the device has been unlocked. In order 
// that a client listenning on event get the correct value in its event callback
// (if he requires it), read the value and store it into the polling buffer but 
// do not fire position event
//
                        read_pos_while_moving(implied_mots,implied_group,NULL,
                                th, obj_trigg, false, false);
//
// Delay sending state event: A state event should be sent
// only after a 'potential' instability time as passed and
// after the last position event as been sent
//
                        // implied_mots[0].state_att.fire_change_event();
                        end_mot_ext_evts.push_back(&(implied_mots[0]));
                        
                        if(mp.has_listeners())
                        {
                            DelayedEvt delayed_evt(StateChange,&mp);
                            delayed_evt.evt.old.state = MOVING;
                            delayed_evt.evt.curr.state = PoolTango::toPool(d_state);
                            end_mot_int_evts.push_back(delayed_evt);
                        }
                        break;
                    }
                }
            }

//
// Is it time to read the position ?
//
        
            read_ctr++;
            if (read_ctr == nbStatePerRead)
            {
                read_ctr = 0;
                read_pos_while_moving(implied_mots,implied_group,
                                      &internal_events,th,obj_trigg,false,true);
            }
        }

//
// Send any pending internal events. It is done here (outside the monitor)
// to avoid dead lock. 
// 
        vector<DelayedEvt>::iterator evt_ite = internal_events.begin();
        
        for(;evt_ite != internal_events.end(); evt_ite++)
        {
            evt_ite->src->fire_pool_elem_change(&evt_ite->evt,
                                                evt_ite->exception);
        }
        
//
// Sleep a while
//
            
        nanosleep(&wait,&rem);
    }  // End while(1)
    
//
// Remove position from polling buffer
// Do this after the lock on motor/group has been
// removed. Otherwise, it could generates a dead-lock with
// the polling thread
//

    if (by_proxy == true)
        reset_ext_trigg(implied_mots, implied_group, th, obj_trigg);
        
//
// Read the position a last time and send a forced user event
// but wait for the "Sleep_before_last_read" property value
//

    long sleep_time;
    if (th->group_id == -1)
    {
        sleep_time = m_dev->sleep_bef_last_read;
        if (sleep_time != 0)
        {
            wait.tv_sec = m_dev->sbr_sec;
            wait.tv_nsec = m_dev->sbr_nsec;

            nanosleep(&wait,&rem);
        }
    }
    else
    {
        sleep_time = implied_group->grp->sleep_bef_last_read;
        if (sleep_time != 0)
        {
            wait.tv_sec = implied_group->grp->sbr_sec;
            wait.tv_nsec = implied_group->grp->sbr_nsec;
            
            nanosleep(&wait,&rem);
        }
    }

//
// Disable range checking to force last event to be changed
//
    vector<DelayedEvt> internal_events;
    for (long ctr = 0;ctr < mot_nb;ctr++)
        implied_mots[ctr].pos_att.set_change_event(true,false);
    if (th->group_id != -1)
        implied_group->pos_att.set_change_event(true,false);
        
    {
        Tango::AutoTangoMonitor atm(running_dev);
        read_pos_while_moving(implied_mots,implied_group,&internal_events,th,
                              obj_trigg,true,true);
    }
    
//
// Send pending internal events from the above read_pos_while_moving. 
// It is done here (outside the above monitor) to avoid dead lock.
//
    vector<DelayedEvt>::iterator int_evt_ite = internal_events.begin();
    
    for(;int_evt_ite != internal_events.end(); int_evt_ite++)
    {
        int_evt_ite->src->fire_pool_elem_change(&int_evt_ite->evt,
                                                int_evt_ite->exception);
    }
    
//
// Restore value checking on the position
//

    for (long ctr = 0;ctr < mot_nb;ctr++)
        implied_mots[ctr].pos_att.set_change_event(true,true);
    if (th->group_id != -1)
        implied_group->pos_att.set_change_event(true,true);
    
//
// Send external end of motion events to clients
//
    proxy_dev->state();

    vector<ElemInMove*>::iterator dl_ext_evt_ite = end_mot_ext_evts.begin();
    for(;dl_ext_evt_ite != end_mot_ext_evts.end(); dl_ext_evt_ite++)
    {
        (*dl_ext_evt_ite)->state_att.fire_change_event();
    }
    
//
// Send pending end-of-motion internal events now that the lock on the device
// that originated the motion has been released
//
    vector<DelayedEvt>::iterator dl_int_evt_ite = end_mot_int_evts.begin();

    for(;dl_int_evt_ite != end_mot_int_evts.end(); dl_int_evt_ite++)
    {
        dl_int_evt_ite->src->fire_pool_elem_change(&dl_int_evt_ite->evt,
                                                   dl_int_evt_ite->exception);
    }
    
//
// Inform all internal motion listeners that the movement has finally ended
// This is necessary because the internal listerners cannot rely on the state change
// to ON to assume the motion ended (because there can be a non zero
// instability time
//
    if (th->group_id != -1)
    {
        if(implied_group->mgp.has_listeners())
        {
            PoolElementEvent evt(MotionEnded,&implied_group->mgp);
            implied_group->mgp.fire_pool_elem_change(&evt, &implied_group->mgp);
        }
    }
    else
    {
        if(mp.has_listeners())
        {
            PoolElementEvent evt(MotionEnded,&mp);
            mp.fire_pool_elem_change(&evt);
        }
    }

//
// Update motor and group data that the motion thread has ended
//
    
    for (long loop = 0;loop < mot_nb;loop++)
        implied_mots[loop].motor->set_mov_th_id(0);
    
    if (th->group_id != -1)
        implied_group->grp->set_mov_th_id(0);
}    

//+------------------------------------------------------------------
/**
 *    method:    Pool::read_pos_while_moving()
 *
 *    description:    Read motor(s) position while they are moving
 *
 * arg(s) : - implied_mots:
 *             - implied_group:
 *             - th: The thread object
 *             - obj_trigg:
 */
//+------------------------------------------------------------------

void Pool::read_pos_while_moving(vector<MotInMove> &implied_mots,
                                 auto_ptr<GrpInMove> &implied_group,
                                 vector<DelayedEvt> *internal_events,
                                 MotorThread *th,
                                 vector<bool> &obj_trigg,
                                 bool last_call,
                                 bool send_event)
{
    long mot_nb = implied_mots.size();
    long ctr;
    bool delay_evt = internal_events != NULL;
    bool has_int_listeners;
    
//
// Check if the element has internal listeners and 
// if a group is moving, lock motor device(s).
// Not necessary to lock group device because it is already done
//
    if (th->group_id != -1)
    {
        has_int_listeners = implied_group->mgp.has_listeners();
        for (ctr = 0;ctr < mot_nb;ctr++)
            implied_mots[ctr].Lock();
    }
    else
    {
        has_int_listeners = implied_mots[0].mot.has_listeners();
    }

/*
// Do all the following in a try/catch block to be protected
// against major Tango error (should never happen...)
// in order to unlock locked device
*/
    try
    {
        
//
// Read position and send event
// For group, read position once with group attribute and
// send event using data gathered from this read
//

        Tango::Util *tg = Tango::Util::instance();
        string attr_name("Position");
        //time_t when = time(NULL);
        struct timeval when;
        gettimeofday(&when, NULL);
        Tango::DevFailed except;
        bool read_except = false;

        if (th->group_id != -1)
        {
            MotorGroup_ns::MotorGroup *grp = implied_group->grp;
            MotorGroupPool &mgp = implied_group->mgp;
            try
            {
                implied_group->grp->read_Position(implied_group->pos_att);
                if (send_event == true)
                {
                    implied_group->pos_att.fire_change_event();
                    
                    if(has_int_listeners)
                    {
                        if(delay_evt)
                        {
                            DelayedEvt delayed_evt(PositionArrayChange, &mgp);
                            delayed_evt.evt.old.position_array = NULL;
                            delayed_evt.evt.curr.position_array = 
                                grp->attr_Position_read;
                            delayed_evt.evt.priority = last_call;
                            delayed_evt.evt.dim = grp->pos_spectrum_dim_x;
                            delayed_evt.exception = &mgp; 
                            internal_events->push_back(delayed_evt);
                        }
                        else
                        {
                            Pool_ns::PoolElementEvent evt(
                                    PositionArrayChange, &mgp);
                            evt.old.position_array = NULL;
                            evt.curr.position_array = grp->attr_Position_read;
                            evt.priority = last_call;
                            evt.dim = grp->pos_spectrum_dim_x; 
                            mgp.fire_pool_elem_change(&evt,&mgp);
                        }
                    }
                }
            }
            catch (Tango::DevFailed &e)
            {
                except = e;
                read_except = true;
                if (send_event == true)
                {
                    implied_group->pos_att.fire_change_event(&e);
                    
                    if(has_int_listeners)
                    {
                        if(delay_evt)
                        {
                            DelayedEvt delayed_evt(PositionArrayChange, &mgp);
                            delayed_evt.evt.old.position_array = NULL;
                            delayed_evt.evt.curr.position_array = NULL;
                            delayed_evt.evt.priority = last_call;
                            delayed_evt.evt.dim = 0;
                            delayed_evt.exception = &mgp; 
                            internal_events->push_back(delayed_evt);
                        }
                        else
                        {
                            Pool_ns::PoolElementEvent evt(
                                    PositionArrayChange, &mgp);
                            evt.old.position_array = NULL;
                            evt.curr.position_array = 0;
                            evt.priority = last_call;
                            evt.dim = 0; 
                            mgp.fire_pool_elem_change(&evt,&mgp);
                        }
                    }                    
                }
            }

//
// Free memory allocated by the call to the read_Position on the attribute
// This memory freeing is normally done by Tango (CORBA layer). We are directly
// accessing the attribute here: therefore, we have to do the free
// This is necessary only for groups because memory management is not the
// same for SCALAR attribute
//

            if ((send_event == false) && (read_except == false))
                delete implied_group->pos_att.get_double_value();
            
//
// Fill polling buffer with the read value
// Do this only if the device was successfully set as externally
// polled.
// If the read sent an exception, send this exception in the
// polling buffer
//
        
            if ((obj_trigg[mot_nb] == true) && (last_call == false))
            {
                Tango::AttrHistoryStack<Tango::DevDouble> ahs;
                ahs.length(1);
    
                if (read_except == false)
                {
                    Tango::TimedAttrData<Tango::DevDouble> tad(
                            grp->attr_Position_read,mot_nb,
                            Tango::ATTR_CHANGING,when);
                    ahs.push(tad);
                }
                else
                {
                    Tango::TimedAttrData<Tango::DevDouble> tad(except.errors,
                                                               when);
                    ahs.push(tad);
                }
                tg->fill_attr_polling_buffer(grp,attr_name,ahs);
                
            }    
                    
            for (long ctr = 0;ctr < mot_nb;ctr++)
            {
                MotInMove &mot_mv = implied_mots[ctr];
                MotorPool &mot = mot_mv.mot;
                Motor_ns::Motor *motor = mot_mv.motor;
                
                double pos = grp->get_phys_motor_pos(mot_mv.idx_in_grp);
                
                if (send_event == true)
                {
                    {
                        Tango::DevState m_state = motor->get_state();
                        
                        Tango::AutoTangoMonitor synch(motor);
                        
                        Tango::AttrQuality quality = Tango::ATTR_VALID;
                        if (m_state == Tango::MOVING)
                            quality = Tango::ATTR_CHANGING;
                        else if (m_state == Tango::ALARM)
                            quality = Tango::ATTR_ALARM;
                        
                        mot_mv.pos_att.set_value_date_quality(&pos, when, quality);
                        
                        mot_mv.pos_att.fire_change_event(read_except == true ? 
                                                         &except : NULL);
                    }
                                        
                    if(has_int_listeners)
                    {
                        if(delay_evt)
                        {
                            DelayedEvt delayed_evt(PositionChange, &mot);
                            delayed_evt.evt.old.position = (double)LONG_MIN;
                            delayed_evt.evt.curr.position = pos;
                            delayed_evt.evt.priority = last_call;
                            delayed_evt.exception = &mgp;
                            internal_events->push_back(delayed_evt);
                        }
                        else
                        {
                            Pool_ns::PoolElementEvent evt(PositionChange, &mot);
                            evt.old.position = (double)LONG_MIN;
                            evt.curr.position = pos;
                            evt.priority = last_call;
                            mot_mv.mot.fire_pool_elem_change(&evt, &mgp);
                        }
                    }
                }
                
                if ((obj_trigg[ctr] == true) && (last_call == false))
                {
                    Tango::AttrHistoryStack<Tango::DevDouble> ahs;
                    ahs.length(1);
    
                    if (read_except == false)
                    {    
                        Tango::TimedAttrData<Tango::DevDouble> 
                            tad(&(pos), Tango::ATTR_CHANGING,when);
                        ahs.push(tad);
                    }
                    else
                    {
                        Tango::TimedAttrData<Tango::DevDouble> tad(
                                except.errors, when);
                        ahs.push(tad);
                    }
        
                    tg->fill_attr_polling_buffer(motor,attr_name,ahs);
                }
            }
        }
        else
        {
            MotInMove &mot_mv = implied_mots[0];
            MotorPool &mot = mot_mv.mot;
            Motor_ns::Motor *motor = mot_mv.motor;
//
// The same thing for motor
//
            try
            {
                motor->read_Position(mot_mv.pos_att);
            }
            catch (Tango::DevFailed &e)
            {
                except = e;
                read_except = true;

            }
            
            if (send_event == true)
            {
                if (read_except == false)
                {
                    Tango::DevState m_state = motor->get_state();
                    Tango::AttrQuality quality = Tango::ATTR_VALID;
                    if (m_state == Tango::MOVING)
                        quality = Tango::ATTR_CHANGING;
                    else if (m_state == Tango::ALARM)
                        quality = Tango::ATTR_ALARM;
                    mot_mv.pos_att.set_quality(quality);
                    mot_mv.pos_att.fire_change_event();

                    if(has_int_listeners)
                    {
                        if(delay_evt)
                        {
                            DelayedEvt delayed_evt(PositionChange, &mot);
                            delayed_evt.evt.old.position = (double)LONG_MIN;
                            delayed_evt.evt.curr.position = 
                                *motor->attr_Position_read;
                            delayed_evt.evt.priority = last_call;
                            internal_events->push_back(delayed_evt);
                        }
                        else
                        {
                            Pool_ns::PoolElementEvent evt(PositionChange, 
                                                                &mot);
                            evt.old.position = (double)LONG_MIN;
                            evt.curr.position = *motor->attr_Position_read;
                            evt.priority = last_call;
                            mot.fire_pool_elem_change(&evt);
                        }
                    }
                }
                else
                {
                    mot_mv.pos_att.fire_change_event(&except);

                    if(has_int_listeners)
                    {
                        if(delay_evt)
                        {
                            DelayedEvt delayed_evt(PositionChange, &mot);
                            delayed_evt.evt.old.position = (double)LONG_MIN;
                            delayed_evt.evt.curr.position = (double)LONG_MIN;
                            delayed_evt.evt.priority = last_call;
                            internal_events->push_back(delayed_evt);
                        }
                        else
                        {
                            Pool_ns::PoolElementEvent evt(PositionChange, 
                                                                &mot);
                            evt.old.position = (double)LONG_MIN;
                            evt.curr.position = (double)LONG_MIN;
                            evt.priority = last_call;
                            implied_mots[0].mot.fire_pool_elem_change(&evt);
                        }
                    }
                }
            }

            struct timeval when;
            gettimeofday(&when, NULL);
            Tango::DevFailed except;
        
            if ((obj_trigg[0] == true) && (last_call == false))
            {
                Tango::AttrHistoryStack<Tango::DevDouble> ahs;
                ahs.length(1);
    
                if (read_except == false)
                {
                    Tango::TimedAttrData<Tango::DevDouble> tad(
                            motor->attr_Position_read,
                            Tango::ATTR_CHANGING,when);
                    ahs.push(tad);
                }
                else
                {
                    Tango::TimedAttrData<Tango::DevDouble> tad(except.errors,
                                                               when);
                    ahs.push(tad);
                }
    
                tg->fill_attr_polling_buffer(motor,attr_name,ahs);
            }
        }
    }
    catch (Tango::DevFailed &e)
    {
        if (th->group_id != -1)
        {
            for (ctr = 0;ctr < mot_nb;ctr++)
            {
                implied_mots[ctr].Unlock();
            }
        }
        throw;
    }
 
//
// Unlock devices
//

    if (th->group_id != -1)
    {
        for (ctr = mot_nb-1;ctr >=0;--ctr)
        {
            implied_mots[ctr].Unlock();
        }
    }
}

//+------------------------------------------------------------------
/**
 *    method:    Pool::set_ext_trigg()
 *
 *    description:    Add all object implied in this movement to the
 *                     list of externally triggered polled objects
 *
 * arg(s) : - implied_mots:
 *             - implied_group:
 *             - th: The thread object
 *             - obj_trigg : A vector of flag to memorize which objects 
 *                           is externally triggered
 */
//+------------------------------------------------------------------

void Pool::set_ext_trigg(vector<MotInMove> &implied_mots,
                         auto_ptr<GrpInMove> &implied_group,MotorThread *th,
                         vector<bool> &obj_trigg)
{
    long mot_nb = implied_mots.size();
    long ctr;

//
// Get process admin device
//

    Tango::Util *tg = Tango::Util::instance();
    Tango::DServer *adm_dev = tg->get_dserver_device();
    
//
// For each mmotor(s)
//

    Tango::DevVarLongStringArray dvlsa;
    dvlsa.lvalue.length(1);
    dvlsa.svalue.length(3);
    
    dvlsa.lvalue[0] = 0;
    dvlsa.svalue[1] = CORBA::string_dup("attribute");
    dvlsa.svalue[2] = CORBA::string_dup("Position");
    
    for (ctr = 0;ctr < mot_nb;ctr++)
    {
        MotorPool &mot = implied_mots[ctr].mot;

        try
        {
            dvlsa.svalue[0] = CORBA::string_dup(mot.get_full_name().c_str());
            {
                Tango::AutoTangoMonitor atm(adm_dev);
                adm_dev->add_obj_polling(&dvlsa,false);
            }
        }
        catch (Tango::DevFailed &e)
        {
//
// If we have an error API_AlreadyPolled, this means that the
// last rem_obj_polling command executed for this attribute failed
// and the attribute is still in the polling buffer
// This should normally not happened but...
//

            string reas = e.errors[0].reason.in();
            if (reas != "API_AlreadyPolled")
                obj_trigg[ctr] = false;
        }
    }
            
//
// Even for group if necessary
//

    if (th->group_id != -1)
    {
        try
        {
            MotorGroup_ns::MotorGroup *grp = implied_group->grp;
            
            dvlsa.svalue[0] = CORBA::string_dup(grp->get_name().c_str());
            {
                Tango::AutoTangoMonitor atm(adm_dev);
                adm_dev->add_obj_polling(&dvlsa,false);
            }
        }
        catch (Tango::DevFailed &e)
        {
            string reas = e.errors[0].reason.in();
            if (reas != "API_AlreadyPolled")
                obj_trigg[ctr] = false;
        }
    }
    
}


//+------------------------------------------------------------------
/**
 *    method:    Pool::reset_ext_trigg()
 *
 *    description:    Remove all object implied in this movement from the
 *                     list of externally triggered polled objects
 *
 * arg(s) : - implied_mots:
 *             - implied_group:
 *             - th: The thread object
 *             - obj_trigg : A vector of flag to memorize which objects 
 *                           is externally triggered
 */
//+------------------------------------------------------------------

void Pool::reset_ext_trigg(vector<MotInMove> &implied_mots,
                           auto_ptr<GrpInMove> &implied_group, MotorThread *th,
                           vector<bool> &obj_trigg)
{
    long mot_nb = implied_mots.size();
    long ctr;

//
// Get process admin device
//

    Tango::Util *tg = Tango::Util::instance();
    Tango::DServer *adm_dev = tg->get_dserver_device();
    
//
// For each motor(s)
//

    Tango::DevVarStringArray dvsa;
    dvsa.length(3);
    
    dvsa[1] = CORBA::string_dup("attribute");
    dvsa[2] = CORBA::string_dup("Position");

    std::string curr_name = "";
    for (ctr = 0;ctr < mot_nb;ctr++)
    {
        try
        {
            if (obj_trigg[ctr] == true)
            {
                MotInMove &mot_mv = implied_mots[ctr];
                MotorPool &mot = mot_mv.mot;
                curr_name = mot.get_name();
                dvsa[0] = mot.get_full_name().c_str();
                {
                    Tango::AutoTangoMonitor atm(adm_dev);
                    adm_dev->rem_obj_polling(&dvsa,false);
                }
            }
        }
        catch (Tango::DevFailed &e)
        {
            cout << "Gasp, an exception while removing '" << curr_name 
                 << "'from externally triggered polling" << endl;
            Tango::Except::print_exception(e);
        }
    }

//
// Even for group if necessary
//

    if ((th->group_id != -1) && (obj_trigg[ctr] == true))
    {
        try
        {
            curr_name = implied_group->mgp.name;
            MotorGroup_ns::MotorGroup *grp = implied_group->grp;
            dvsa[0] = CORBA::string_dup(grp->get_name().c_str());
            {
                Tango::AutoTangoMonitor atm(adm_dev);
                adm_dev->rem_obj_polling(&dvsa,false);
            }
        }
        catch (Tango::DevFailed &e)
        {
            cout << "Gasp, an exception while removing '" << curr_name 
                 << "'from externally triggered polling" << endl;
            Tango::Except::print_exception(e);
        }
    }
    
}

//+------------------------------------------------------------------
/**
 *    method:    MotorThread::manage_thread_exception
 *
 *    description:    Take all the necessary actions if something failed
 *                  during the movement starting phase
 *
 * arg(s) : 
 */
//+------------------------------------------------------------------    
        
void MotorThread::manage_thread_exception(Tango::DevFailed &e,
                                         vector<CtrlInMove> &implied_ctrls,
                                         vector<MotInMove> &implied_mots,
                                         auto_ptr<GrpInMove> &implied_group,
                                         string &except_func, 
                                         bool state_changed, long loop)
{
        
//
// Unlock all the implied controllers
//
    vector<CtrlInMove>::reverse_iterator impl_ctrl_rite = implied_ctrls.rbegin();
    for (;impl_ctrl_rite != implied_ctrls.rend();++impl_ctrl_rite)
        impl_ctrl_rite->unlock();

//
// Inform motors that the movement is aborted (only for group)
//

/*    if (th->group_id != -1)
    {
        for (long ctr = 0;ctr < loop;ctr++)
            implied_mots[loop].mot.motor->abort_grp_movement();
    }*/

//
// Reset the motor state to ON if already changed to MOVING
//

    if (state_changed == true)
    {
        Pool_ns::MotorGroupPool *mgp = (group_id != -1) ?
                &implied_group->mgp : NULL;
        
        for (unsigned long ll = 0;ll < implied_mots.size();ll++)
        {
            MotInMove &mot_mv = implied_mots[ll];
            Pool_ns::MotorPool &mot = mot_mv.mot;
            Motor_ns::Motor *motor = mot_mv.motor;
            
            Tango::DevState old_state = motor->get_state();
            motor->set_state(Tango::ON);
            mot_mv.state_att.fire_change_event();
            if(mot.has_listeners())
            {
                PoolElementEvent evt(StateChange,&mot);
                evt.old.state = PoolTango::toPool(old_state);
                evt.curr.state = ON;
                
                // We really have to exclude the motor group (if existing)
                // from the internal event propagation. Otherwise a deadlock
                // can occur
                mot.fire_pool_elem_change(&evt, mgp);
            }
        }
        
        if (group_id != -1)
        {
            MotorGroup_ns::MotorGroup *grp = implied_group->grp;
            
            Tango::DevState old_state = grp->get_state();
            grp->set_state(Tango::ON);
            implied_group->state_att.fire_change_event();
            
            if(mgp->has_listeners())
            {
                PoolElementEvent evt(StateChange,mgp);
                evt.old.state = PoolTango::toPool(old_state);
                evt.curr.state = ON;
                mgp->fire_pool_elem_change(&evt);
            }
        }
    }
//
// Unlock all motors (only for group)
//
    if (group_id != -1)
    {
        for (unsigned long ctr = 0;ctr < implied_mots.size();ctr++)
        {
            implied_mots[ctr].Unlock();
        }
    }
        
    TangoSys_OMemStream o;
    if (loop != -1)
    {
        o << "Impossible to move motor device " << 
             implied_mots[loop].mot.name << " (";
        o << implied_mots[loop].mot.get_full_name() << ")";
    }
    if (except_func != "NoFunc")
        o << ". The " << except_func << "() controller method throws an "
             "exception" << ends;

    Tango::Except::re_throw_exception(e,
                        (const char *)"Motor_ControllerFailed", o.str(),
                        (const char *)"Pool::forward_move");    
}    
    
}    //    namespace
