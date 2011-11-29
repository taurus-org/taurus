//+=============================================================================
//
// file :         CTPoolThread.cpp
//
// description :  C++ source for the CTPoolThread file.
//				  This is simply a forward to method defined in the Pool
//				  object
//
// project :      Sardana Pool Device Server
//
// $Author: tiagocoutinho $
//
// $Revision: 296 $
//
// $Log: CTPoolThread.cpp,v $
// Revision 1.25  2007/08/30 12:40:39  tcoutinho
// - changes to support Pseudo counters.
//
// Revision 1.24  2007/07/26 07:10:29  tcoutinho
// fix bug 10 : Change all tango commands from Stop to Abort
//
// Revision 1.23  2007/07/24 07:11:06  tcoutinho
// fix bug: in data acquisition with a measurement it is necessary to check the state of the master channel in order to know when to stop all other channels
//
// Revision 1.22  2007/07/23 16:41:38  tcoutinho
// fix bug: Stop all channels when master stops during acquisition
//
// Revision 1.21  2007/06/28 07:15:34  tcoutinho
// safety commit during comunication channels development
//
// Revision 1.20  2007/06/13 15:18:58  etaurel
// - Fix memory leak
//
// Revision 1.19  2007/05/25 12:48:10  tcoutinho
// fix the same dead locks found on motor system to the acquisition system since release labeled for Josep Ribas
//
// Revision 1.18  2007/05/11 08:07:48  tcoutinho
// - added new propertie to allow different sleep time in CounterTimer
// - added new property to allow sleep time in 0D experiment channel
//
// Revision 1.17  2007/05/02 16:04:05  ahoms
// - added ifdef/endif BUGGY_GCC_335 around fill_attr_polling_buffer
//
// Revision 1.16  2007/04/23 15:21:56  tcoutinho
// - changes according to Sardana metting 26-03-2007: remove configuration from a measurement group
//
// Revision 1.15  2007/04/03 07:05:53  tcoutinho
// - small code adjustment. Commit before vacations
//
// Revision 1.14  2007/03/02 16:34:27  tcoutinho
// - fix bugs with measurement group - event related, attribute quality, active measurement group management, etc
//
// Revision 1.13  2007/02/28 16:21:52  tcoutinho
// - support for 0D channels
// - basic fixes after running first battery of tests on measurement group
//
// Revision 1.12  2007/02/26 09:46:57  tcoutinho
// - config support
//
// Revision 1.11  2007/02/22 12:00:20  tcoutinho
// - fixed bug in case of an exception occured with the message report
// - added support for monitor mode
//
// Revision 1.10  2007/02/16 10:01:26  tcoutinho
// - development checkin
//
// Revision 1.9  2007/02/14 11:22:33  tcoutinho
// - commit for labeling with Release_0_6 tag
//
// Revision 1.8  2007/02/13 14:39:43  tcoutinho
// - fix bug in motor group when a motor or controller are recreated due to an InitController command
//
// Revision 1.7  2007/02/08 16:18:13  tcoutinho
// - controller safety on PoolGroupBaseDev
//
// Revision 1.6  2007/02/08 10:49:28  etaurel
// - Some small changes after the merge
//
// Revision 1.5  2007/02/08 08:51:13  etaurel
// - Many changes. I don't remember the list
//
// Revision 1.4  2007/02/07 16:53:06  tcoutinho
// safe guard commit
//
// Revision 1.3  2007/02/06 09:41:02  tcoutinho
// - added MeasurementGroup
//
// Revision 1.2  2007/01/30 16:00:46  etaurel
// - The CT Value attribute is now a Double
// WARNING, this change has made us discouvering the GCC BUG  2834...
// Some code is now between ifdef/endif statement to compile using gcc 3.3
//
// Revision 1.1  2007/01/16 14:28:29  etaurel
// - Initial revicion of the CT thread code
//
//
// copyleft :     CELLS/ALBA
//				  Edifici Ciències Nord. Mòdul C-3 central.
//  			  Campus Universitari de Bellaterra. Universitat Autònoma de Barcelona
//  			  08193 Bellaterra, Barcelona
//  			  Spain
//
//+=============================================================================

#include "PyUtils.h"
#include "Pool.h"
#include "PoolUtil.h"
#include "CTPoolThread.h"
#include "CTExpChannel.h"

#include <pool/CoTiCtrl.h>
#include <limits>

namespace Pool_ns
{

//+------------------------------------------------------------------
/**
 *	method:	CTPoolThread::run
 *
 *	description:	The run method of the thread taking care of the
 * 					running move. This is simply a call to the
 * 					forward_move of the 
 */
//+------------------------------------------------------------------

void CTPoolThread::run(void *ptr)
{
    AutoCleanPythonGIL auto_clean_gil;
    
    try
    {
        pool_dev->forward_count(aq_info,this);
    }
    catch (Tango::DevFailed &e)
    {
        Tango::Device_4Impl *dev_impl = NULL;
        
        if(group_id != -1) 
            dev_impl = failed_group;
        else
            dev_impl = failed_channel;
        
        Tango::DevError &de = e.errors[0];
        dev_impl->get_logger()->error_stream() 
            << log4tango::LogInitiator::_begin_log 
            << "Tango exception in counter thread: [" 
            << de.origin << "] (" 
            << de.reason << ") " 
            << de.desc << endl;
            
        Tango::Except::print_exception(e);

        vector<int32_t> &ct_ids = aq_info.ct_ids;

        for (vector<int32_t>::size_type loop = 0;loop < ct_ids.size();loop++)
        {
            CTExpChannel_ns::CTExpChannel *ct_dev = pool_dev->get_countertimer_device(ct_ids[loop]);
            ct_dev->set_mov_th_id(0);
        }
        
        if (group_id != -1)
        {
            failed_group->th_failed = true;
            failed_group->th_except = e.errors;
            
            MeasurementGroup_ns::MeasurementGroup *tmp_grp_ptr = pool_dev->get_measurement_group_device(group_id);
            tmp_grp_ptr->set_mov_th_id(0);
        }
        else
        {
            failed_channel->th_failed = true;
            failed_channel->th_except = e.errors;
        }
        
        {
            omni_mutex_lock lo(*mon_ptr);
            mon_ptr->signal();
        }
    }
}

//+------------------------------------------------------------------
/**
 *	method:	Pool::forward_count
 *
 *	description:	Move motor(s) to the wanted position(s)
 * 					This method as run by a separate thread
 *
 * arg(s) : - ct_master_id: the master channel (timer/monitor)
 * 			- mot_ids: The vector
 * 			- positions: The memorized motor(s)
 * 			- pos_backlash: The final position if a backlash has to be applied
 * 							0 otherwise
 * 			- th : The thread object
 */
//+------------------------------------------------------------------


void Pool::forward_count(AquisitionInfo &aq_info,CTPoolThread *th)
{
    vector<CtrlInCount>         implied_ctrls;
    vector<CtInCount>           implied_cts;
    auto_ptr<GrpInCount>        implied_group;
    vector<bool>                obj_ext_trigg(aq_info.ct_ids.size() + 1,true);
        
//
// Send the info to the controller(s)
//

    try
    {
        send_to_ctrl(aq_info,th,implied_ctrls,implied_cts,implied_group);
    }
    catch (Tango::DevFailed &df)
    {
        Tango::Except::re_throw_exception(df, "Pool_CTThreadFailed", "Not able to execute send_to_ctrl", "Pool::forward_count");
    }
//
// Set all devices implied in this move as externally triggered polling
// The unset is done just before sending the event to the customer
// If done elsewhere, it could happend that the state is switched to
// ON but the pos. info is still in the polling buffer and will be
// returned to the caller.
//
    try
    {
        set_ext_trigg(implied_cts,implied_group,th,obj_ext_trigg);
    }
    catch (Tango::DevFailed &df)
    {
        Tango::Except::re_throw_exception(df, "Pool_CTThreadFailed", "Not able to execute set_ext_trigg", "Pool::forward_count");
    }

    
//
// Wait for end of counting
//
    try
    {
        counting_loop(aq_info,implied_ctrls,implied_cts,implied_group,th,obj_ext_trigg);
    }
    catch (Tango::DevFailed &df)
    {
        Tango::Except::re_throw_exception(df, "Pool_CTThreadFailed", "Not able to execute counting_loop", "Pool::forward_count");
    }
    
    
}

//+------------------------------------------------------------------
/**
 *	method:	Pool::send_to_ctrl
 *
 *	description:	Send start to controller(s)
 *
 * arg(s) : - ct_ids: The vector
 * 			- th: The thread object
 * 			- implied_ctrls:
 * 			- implied_cts:
 * 			- implied_group:
 */
//+------------------------------------------------------------------

void Pool::send_to_ctrl(AquisitionInfo &aq_info,
                        CTPoolThread *th,
                        vector<CtrlInCount> &implied_ctrls,
                        vector<CtInCount> &implied_cts,
                        auto_ptr<GrpInCount> &implied_group)
{
    
    vector<ElementId> &ct_ids = aq_info.ct_ids;
    vector<ElementId> &virt_pc_ids = aq_info.virt_pc_ids;
    int32_t ct_nb = (int32_t)ct_ids.size();
    int32_t loop = -1;
    
//
// Find which ctrls are implied in this count and init counter infos
// This part of code looks into pool device data. Lock the pool device
// to protect this part of code
//
    {
        Tango::AutoTangoMonitor atm(this);
        for (loop = 0;loop < (int32_t)ct_nb; ++loop)
        {
            CTExpChannelPool &ct_ref = get_countertimer(ct_ids[loop]);
            CTExpChannel_ns::CTExpChannel *ct_dev = get_countertimer_device(ct_ref);
            ControllerPool &ctrl_ref = get_controller(ct_ref);
            CtInCount tmp_ct(ct_ref, ct_dev, ctrl_ref);
            
            implied_cts.push_back(tmp_ct);
            
            ElementId ctrl_id = ctrl_ref.id;
    
            CtrlInCount tmp_ctrl(ctrl_id,ctrl_ref);	
            if (implied_ctrls.empty() == true)
                implied_ctrls.push_back(tmp_ctrl);
            else
            {
                bool exists = false;
                for (size_t l = 0;l < implied_ctrls.size();l++)
                {
                    if (implied_ctrls[l].ctrl_id == ctrl_id)
                        exists = true;
                }
                if(!exists)
                    implied_ctrls.push_back(tmp_ctrl);
            }
            
            if(ct_ref.id == aq_info.master_id)
                aq_info.master_idx_in_cts = loop;
        }

//
// Retrieve measurement group object if needed
// and init what could failed
//
        
        if (th->group_id != -1)
        {
            MeasurementGroupPool &mgp = get_measurement_group(th->group_id);
            MeasurementGroup_ns::MeasurementGroup *mg_dev = get_measurement_group_device(th->group_id);
            GrpInCount *grp_cnt = new GrpInCount(mgp, mg_dev);
            grp_cnt->set_channels(ct_ids, virt_pc_ids);
            auto_ptr<GrpInCount> tmp_ptr(grp_cnt);
            implied_group = tmp_ptr;
            th->failed_group = implied_group->grp;
        }
        else
            th->failed_channel = implied_cts[0].ct_dev;
                
//
// Create channel proxies if not already done
// Take the oportuninty to do it now while the pool device is
// already locked
//

        if (proxy_created == false)
        {
            create_proxies();
            proxy_created = true;
        }
    }

    vector<DelayedEvt> internal_events;

    string except_func("NoFunc");
    bool state_changed = false;
    vector<CtrlInCount>::iterator impl_ctrl_ite;
    
    int th_id = omni_thread::self()->id();
    
    try
    {
        
//
// Lock all the counters implied in this count only if request coming
// from a group movement. In the other case, the counter lock is already taken
// by the ORB thread which executes the start command
// Takes this oportunity to write the counting thread id in CTExpChannel object
//

        if (th->group_id != -1)
        {
            for(loop = 0; loop < (int32_t)implied_cts.size(); loop++)
            {
                implied_cts[loop].Lock();
                implied_cts[loop].set_mov_th_id(th_id);
            }
            implied_group->grp->set_mov_th_id(th_id);
        }
        else
            implied_cts[0].set_mov_th_id(th_id);
        
//
// Lock all the controllers implied in this count
//
        loop = -1;
        for_each(implied_ctrls.begin(), implied_ctrls.end(), mem_fun_ref(&CtrlInCount::Lock));

//
// Load the master timer/monitor with the proper value
//
        except_func = "LoadMaster";
        loop = -1;
        if (th->group_id != -1)
        {
            PoolElement &master = get_experiment_channel(aq_info.master_id);
            Tango::DeviceAttribute value("Value",aq_info.master_value);
            get_element_proxy(master)->write_attribute(value);
        }
                            
//
// Send the PreStartAllCT to all implied controllers
//
        loop = -1;
        except_func = "PreStartAllCT";
        for (impl_ctrl_ite = implied_ctrls.begin();impl_ctrl_ite != implied_ctrls.end();++impl_ctrl_ite)
        {
            ControllerPool &cp = impl_ctrl_ite->ct;
            CoTiController *mc = static_cast<CoTiController *>(cp.get_controller());
            mc->PreStartAllCT();
        }

//
// Send PreStartOneCT and StartOneCT to each implied counter except
// for the master
//
        for (loop = 0;loop < ct_nb;loop++)
        {
//
// Skip the master from receiving PreStartOneCT and StartOneCT now
//
            if(th->group_id != -1 && implied_cts[loop].ct_id == aq_info.master_id)
                continue;
                
            CTExpChannelPool &mp = implied_cts[loop].ct_pool;
            ControllerPool &cp = implied_cts[loop].cp;

//
// If the request comes from a group movement, we need to check that
// each counter member of the group is not already counting 
//

            except_func = "NoFunc";
                        
            CoTiController *mc = static_cast<CoTiController *>(cp.get_controller());
            except_func = "PreStartOneCT";
            bool ret = mc->PreStartOneCT(mp.get_axis());
                
            if (ret == true)
            {
                except_func = "StartOneCT";
                mc->StartOneCT(mp.get_axis());
            }
            else
            {
                TangoSys_OMemStream o;
                o << "Impossible to start counting for device "
                  << implied_cts[loop].ct_pool.name << " ("
                  << implied_cts[loop].ct_pool.get_full_name() << ")"
                  << ". The PreStartOneCT() function returns false" << ends;
    
                Tango::Except::throw_exception("Pool_PrestartOneCT", o.str(),
                                               "Pool::send_to_ctrl");
            }
        }
        
//
// Send the StartAllCT to all implied controller
//
        except_func = "StartAllCT";
        loop = -1;
        for (impl_ctrl_ite = implied_ctrls.begin();
             impl_ctrl_ite != implied_ctrls.end(); ++impl_ctrl_ite)
        {
            ControllerPool &cp = impl_ctrl_ite->ct;
            CoTiController *mc = static_cast<CoTiController *>(cp.get_controller());
            mc->StartAllCT();
        }
        
//
// If this is a group movement repeat the procedure above but just for the 
// master channel
//
        if(th->group_id != -1)
        {
            CTExpChannelPool &mp = implied_cts[aq_info.master_idx_in_cts].ct_pool;
            ControllerPool &cp = implied_cts[aq_info.master_idx_in_cts].cp;
            CoTiController *mc = static_cast<CoTiController *>(cp.get_controller());

//
// Send the PreStartAllCT to the controller which has the master
//
            mc->PreStartAllCT();

//
// Send PreStartOneCT and StartOneCT to the master
//
            except_func = "PreStartOneCT_OnMaster";
            bool ret = mc->PreStartOneCT(mp.get_axis());
                
            if (ret == true)
            {
                except_func = "StartOneCT_OnMaster";
                mc->StartOneCT(mp.get_axis());
            }
            else
            {
                TangoSys_OMemStream o;
                o << "Impossible to start counting for the Master device " 
                  << mp.name << " (" << mp.get_full_name() << ")"
                  << ". The PreStartOneCT() function on returns false" << ends;
    
                Tango::Except::throw_exception("StartOneCT_OnMaster", o.str(),
                                               "Pool::send_to_ctrl");
            }
//
// Send the StartAllCT to the controller which has the master
//
            except_func = "StartAllCT_OnMaster";
            mc->StartAllCT();
        }

//
// Send a User Event and internal event on state attribute for each implied 
// counters. It is not necessary to lock the device between the state setting 
// and the event firing because the user thread is still in the counter 
// start() method and therefore, the counter device is locked.
// Locking the counter device by this thread at that moment will be
// a dead lock
//

        state_changed = true;
        for (loop = 0;loop < ct_nb;loop++)
        {   
            CtInCount &ct_cnt = implied_cts[loop];
            CTExpChannelPool &mp = ct_cnt.ct_pool;
            Tango::DevState old_state = ct_cnt.ct_dev->get_state();
            ct_cnt.ct_dev->set_state(Tango::MOVING);
            
            ct_cnt.state_att.fire_change_event();
            
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
        
        if (th->group_id != -1)
        {
            implied_group->grp->clear_event_fired_array();
            Tango::DevState old_state = implied_group->grp->get_state();
            implied_group->grp->set_state(Tango::MOVING);
            
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
    catch (Tango::DevFailed &e)
    {
        th->manage_thread_exception(e, implied_ctrls, implied_cts, implied_group,
                                    except_func, state_changed, loop);
    }
    catch (...)
    {
        Tango::DevErrorList err_list(1);
        err_list.length(1);

        err_list[0].severity = Tango::ERR;
        err_list[0].origin = CORBA::string_dup("Pool::forward_count");
        err_list[0].reason = CORBA::string_dup("CounterTimer_ControllerFailed");
        err_list[0].desc = CORBA::string_dup("Controller has sent an unknown exception");
    
        Tango::DevFailed e(err_list);
        th->manage_thread_exception(e, implied_ctrls, implied_cts, implied_group,
                                    except_func, state_changed, loop);
    }

//
// Unlock all the controllers implied in this move in reversed order!
//
    for_each(implied_ctrls.rbegin(), implied_ctrls.rend(), mem_fun_ref(&CtrlInCount::Unlock));

//
// Unlock all counters (only for group) in reversed order
//
    if (th->group_id != -1)
        for_each(implied_cts.rbegin(), implied_cts.rend(), mem_fun_ref(&CtInCount::Unlock));
            
//
// Inform counter/group device that all the check are OK
//
    if (th->group_id == -1)
        implied_cts[0].ct_dev->th_failed = false;
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
 *	method:	Pool::counting_loop
 *
 *	description:	Wait for end of counting and send appropriate
 * 					event(s) to the right device at the right moment
 *
 * arg(s) : - implied_ctrls:
 * 			- implied_cts:
 * 			- implied_group:
 * 			- th: The thread object
 * 			- obj_trigg :
 */
//+------------------------------------------------------------------

void Pool::counting_loop(AquisitionInfo &aq_info,
                         vector<CtrlInCount> &implied_ctrls,
                         vector<CtInCount> &implied_cts,
                         auto_ptr<GrpInCount> &implied_group,
                         CTPoolThread *th,
                         vector<bool> &obj_trigg)
{

    size_t ct_nb = implied_cts.size();

//
// Wait for state to be something different than MOVING
// Read controller every 10 mS and fire an event as soon
// as the state is something different than MOVING
// Lock the device between the state reading and the event
// firing
// If we are in a shutdown phase, while a counter is moving, the 
// counter object is made unavailable from Proxy devices.
// In such a case, use direct counter access
//

    Tango::DevState d_state = Tango::UNKNOWN;
    struct timespec wait,rem;
        
    wait.tv_sec = 0;
    wait.tv_nsec = cTThreadLoop_SleepTime * 1000000;

    Tango::DeviceImpl *running_dev;
    Tango::DeviceProxy *proxy_dev;
    
    CTExpChannelPool &mp = implied_cts[0].ct_pool;
    
//
// Init some data according to group or counter
//

    if (th->group_id == -1)
    {
        running_dev = implied_cts[0].ct_dev;
        proxy_dev = get_element_proxy(mp);
    }
    else
    {
        running_dev = implied_group->grp;
        proxy_dev = implied_group->grp_proxy;
    }
    assert(proxy_dev != NULL);
    
    bool by_proxy = true;
    int32_t read_ctr = 0;
    string except_func = "NoFunc";

    // end of count internal events
    vector<DelayedEvt> end_cnt_int_evts;

    while(1)
    {
        vector<DelayedEvt> internal_events;
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
                    d_state = (th->group_id != -1) ? 
                                running_dev->dev_state() : 
                                running_dev->get_state();
                }
                
                // If in group mode, the current state becomes the state of 
                // the master channel
                if (th->group_id != -1)
                    d_state = (static_cast<PoolGroupBaseDev*>(running_dev))->get_state_array()[aq_info.master_idx_in_grp];
                    
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

//
// Force an abort on channels in case the master channel is not able to stop
// Ex.: Unix Timer is not able to stop channels of a VCT6 card directly
//
            if (th->group_id != -1 && implied_group->grp->abort_cmd_executed == false)
            {
                if (d_state != Tango::MOVING)
                {
                    vector<Tango::DevFailed> v_except;
                    implied_group->grp->abort_all_channels(v_except);
                }
            }

//
// Do not send event if the thread exit because the CT
// (or the group) has received a Stop/Abort command
//
            if (d_state != Tango::MOVING)
            {
                if (th->group_id != -1)
                {
                    if (implied_group->grp->abort_cmd_executed == false)
                    {
                        read_val_while_counting(aq_info, implied_cts,
                            implied_group, NULL, th, obj_trigg, false, false);

//
// Force updating the state. This is because last time the state was checked was before the
// abort command on all channels. Therefore if we didn't do this the measurement group would
// still think it is in moving state
//
                        proxy_dev->state();
                    }
                    break;
                }
                else
                {
                    if (implied_cts[0].ct_dev->abort_cmd_executed == false)
                    {
                        read_val_while_counting(aq_info, implied_cts,
                            implied_group, NULL, th, obj_trigg, false, false);
                        break;
                    }
                    else
                    {
                        break;
                    }
                }
            }

//
// Is it time to read the value ?
//
            read_ctr++;
            if (read_ctr == nbStatePerRead)
            {
                read_ctr = 0;
                read_val_while_counting(aq_info, implied_cts, implied_group,
                    &internal_events, th, obj_trigg, false, true);
            }
        }

//
// Send any pending internal events. It is done here (outside the monitor)
// to avoid dead lock.
// 
        vector<DelayedEvt>::iterator evt_ite = internal_events.begin();
        
        for(;evt_ite != internal_events.end(); evt_ite++)
        {
            evt_ite->src->fire_pool_elem_change(&evt_ite->evt,evt_ite->exception);
        }
//
// Sleep a while
//
        nanosleep(&wait,&rem);
    } // end while

//
// Send pending end-of-motion internal events now that the lock on the device
// that originated the motion has been released
//
    vector<DelayedEvt>::iterator dl_evt_ite = end_cnt_int_evts.begin();

    for(;dl_evt_ite != end_cnt_int_evts.end(); dl_evt_ite++)
    {
        dl_evt_ite->src->fire_pool_elem_change(&dl_evt_ite->evt, dl_evt_ite->exception);
    }
    
//
// Remove value from polling buffer
// Do this after the lock on counter/group has been
// removed. Otherwise, it could generates a dead-lock with
// the polling thread
//

    if (by_proxy == true)
        reset_ext_trigg(implied_cts, implied_group, th, obj_trigg);
        
//
// Read the Value a last time and send a forced user event
//
        
    vector<DelayedEvt> internal_events;	
    
    // Forcing...
    for (size_t ctr = 0;ctr < ct_nb;ctr++)
        implied_cts[ctr].val_att.set_change_event(true, false);
            
    if (th->group_id != -1)
    {
        for(size_t l = 0; l < implied_group->ct_value_att.size(); l++)
            implied_group->ct_value_att[l]->set_change_event(true, false);
        for(size_t l = 0; l < implied_group->pc_value_att.size(); l++)
            implied_group->pc_value_att[l]->set_change_event(true, false);
    }
        
    {
        Tango::AutoTangoMonitor atm(running_dev);
        read_val_while_counting(aq_info, implied_cts, implied_group,
            &internal_events, th, obj_trigg, true, true);
    }

//
// Send pending internal events. It is done here (outside the above monitor)
// to avoid dead lock.
//
    vector<DelayedEvt>::iterator int_evt_ite = internal_events.begin();
    
    for(;int_evt_ite != internal_events.end(); int_evt_ite++)
    {
        int_evt_ite->src->fire_pool_elem_change(&int_evt_ite->evt, 
                                                int_evt_ite->exception);
    }

    // Restore non forcing...
    for (size_t ctr = 0;ctr < ct_nb;ctr++)
        implied_cts[ctr].val_att.set_change_event(true,true);
    
    if (th->group_id != -1)
    {
        for(size_t l = 0; l < implied_group->ct_value_att.size(); l++)
            implied_group->ct_value_att[l]->set_change_event(true,true);
        for(size_t l = 0; l < implied_group->pc_value_att.size(); l++)
            implied_group->pc_value_att[l]->set_change_event(true,true);
    }

//
// Finally send the state event
//
    if (th->group_id != -1)
    {
        vector<Tango::DevState> &sta_array = implied_group->grp->get_state_array();
        vector<bool> &event_array = implied_group->grp->get_event_fired_array();
        
        for (size_t loop = 0;loop < ct_nb;loop++)
        {
            if ((sta_array[loop] != Tango::MOVING) && (event_array[loop] != true))
            {
                if (implied_cts[loop].ct_dev->abort_cmd_executed == false)
                {
                    implied_cts[loop].state_att.fire_change_event();
                    
                    if(implied_cts[loop].ct_pool.has_listeners())
                    {
                        PoolElementEvent evt(StateChange,&implied_cts[loop].ct_pool);
                        evt.old.state = MOVING;
                        evt.curr.state = PoolTango::toPool(sta_array[loop]);
                        implied_cts[loop].ct_pool.fire_pool_elem_change(&evt, &implied_group->mgp);
                    }
                    event_array[loop] = true;
                }
            }
        }
    
        if (implied_group->grp->abort_cmd_executed == false)
        {
            implied_group->state_att.fire_change_event();

            if(implied_group->mgp.has_listeners())
            {
                DelayedEvt delayed_evt(StateChange,&implied_group->mgp);
                delayed_evt.evt.old.state = MOVING;
                delayed_evt.evt.curr.state = PoolTango::toPool(d_state);
                delayed_evt.exception = &implied_group->mgp;
                end_cnt_int_evts.push_back(delayed_evt);
            }
        }
    }
    else
    {
        if (implied_cts[0].ct_dev->abort_cmd_executed == false)
        {
            implied_cts[0].state_att.fire_change_event();
    
            if(implied_cts[0].ct_pool.has_listeners())
            {
                DelayedEvt delayed_evt(StateChange,&implied_cts[0].ct_pool);
                delayed_evt.evt.old.state = MOVING;
                delayed_evt.evt.curr.state = PoolTango::toPool(d_state);
                end_cnt_int_evts.push_back(delayed_evt);
            }
        }
    }
    
//
// Update counter and group data that the counting thread has ended
//
    
    for (size_t loop = 0;loop < ct_nb;loop++)
        implied_cts[loop].ct_dev->set_mov_th_id(0);
    
    if (th->group_id != -1)
        implied_group->grp->set_mov_th_id(0);
}

//+------------------------------------------------------------------
/**
 *	method:	Pool::read_val_while_counting()
 *
 *	description:	Read counter(s) value while they are counting
 *
 * arg(s) : - aq_info:
 *			- implied_cts:
 * 			- implied_group:
 * 			- th: The thread object
 * 			- obj_trigg:
 * 
 * \return returns <code>true</code> if the master is a monitor and its 
 * 		   value was reached or <code>false</code> otherwise
 */
//+------------------------------------------------------------------

void Pool::read_val_while_counting(AquisitionInfo &aq_info,
                                 vector<CtInCount> &implied_cts,
                                 auto_ptr<GrpInCount> &implied_group,
                                 vector<DelayedEvt> *internal_events,
                                 CTPoolThread *th,
                                 vector<bool> &obj_trigg,
                                 bool last_call,
                                 bool send_event)
{
    size_t ct_nb = implied_cts.size();
    bool thresold_crossed = false;

//
// If a group is moving, lock channel device(s)
// Not necessary to lock group device because it is already done
//

    if (th->group_id != -1)
        for_each(implied_cts.begin(), implied_cts.end() ,mem_fun_ref(&CtInCount::Lock));

/*
// Do all the following in a try/catch block to be protected
// against major Tango error (should never happen...)
// in order to unlock locked device
*/

    try
    {

//
// Read value and send event
// For group, read value once with group attribute and
// send event using data gathered from this read
//

        Tango::Util *tg = Tango::Util::instance();
        string attr_name = "Value";
        time_t when = time(NULL);
        Tango::DevFailed except;
        bool read_except = false;

        if (th->group_id != -1)
        {
            try
            {
                const double *master_value_ptr = implied_group->grp->get_ct_data_from_index(aq_info.master_idx_in_cts);
                double old_master_value = *master_value_ptr;
                implied_group->grp->read_values(Pool_ns::CT_EXP_CHANNEL);
                implied_group->grp->read_values(Pool_ns::PSEUDO_EXP_CHANNEL);
                double new_master_value = *master_value_ptr;

//
// If we are in monitor mode check if the monitor value was crossed. 
//
                if(!last_call)
                {
                    if(aq_info.mode == aqMonitor)
                    {
                        double master_value = -aq_info.master_value;
                        if(new_master_value >= old_master_value &&
                           new_master_value >= master_value)
                            thresold_crossed = true;
                        if(new_master_value < old_master_value &&
                           new_master_value <= master_value)
                            thresold_crossed = true;
                            
//
// If the thresold was crossed don't waist time: We want
// to be able to stop everything as soon as possible. Ex.: If a unix timer
// is used we have to stop it immediately because the monitor will not stop it
//
                        if(thresold_crossed)
                        {
                            vector<Tango::DevFailed> v_except;
                            implied_group->grp->abort_all_channels(v_except);
                        }
                    }
                }

                if (send_event == true)
                {
                    for_each(implied_group->ct_value_att.begin(),
                             implied_group->ct_value_att.end(),
                             bind2nd(mem_fun(&Tango::Attribute::fire_change_event),
                                     (Tango::DevFailed *)NULL));

                    for_each(implied_group->pc_value_att.begin(),
                             implied_group->pc_value_att.end(),
                             bind2nd(mem_fun(&Tango::Attribute::fire_change_event),
                                     (Tango::DevFailed *)NULL));
                        
                    //TODO: Decide how to notify listeners of value change
                    // So far nobody is a listener of a measurement group so there is no problem
                }
            }
            catch (Tango::DevFailed &e)
            {
                except = e;
                read_except = true;
                if (send_event == true)
                {
                    for_each(implied_group->ct_value_att.begin(),implied_group->ct_value_att.end(),
                             bind2nd(mem_fun(&Tango::Attribute::fire_change_event),&e));
                                        
                    //TODO: Decide how to notify listeners of value change
                    // So far nobody is a listener of a measurement group so there is no problem
                }
            }

//
// Fill polling buffer with the read value
// Do this only if the device was successfully set as externally
// polled.
// If the read sent an exception, send this exception in the
// polling buffer
//
        
//            if ((obj_trigg[ct_nb] == true) && (last_call == false))
//            {
//                for (size_t idx = 0;idx < ct_nb;idx++)
//                {
//                    if (read_except == false)
//                    {
//                        Tango::AttrHistoryStack<Tango::DevDouble> ahs;
//                        ahs.length(1);
//                        double *data = implied_group->grp->get_ct_data_from_index(idx);
//                        Tango::TimedAttrData<Tango::DevDouble> tad(data,1,Tango::ATTR_CHANGING,when);
//                        ahs.push(tad);
//                        string attr_name_idx = implied_cts[idx].ct_pool.name + "_value";
//                        tg->fill_attr_polling_buffer(implied_group->grp,attr_name_idx,ahs);
//                    }
//                }
//            }
            
            for (size_t idx = 0;idx < ct_nb;idx++)
            {
                double *data = NULL;
                if (send_event == true)
                {
                    if (read_except == false)
                    {
                        data = implied_group->grp->get_ct_data_from_index(idx);
                        implied_cts[idx].ct_dev->push_change_event("Value",data);

                        if(implied_cts[idx].ct_pool.has_listeners())
                        {
                            Pool_ns::PoolElementEvent evt(Pool_ns::CTValueChange, &implied_cts[idx].ct_pool);
                            evt.old.value = (double)LONG_MIN;
                            evt.curr.value = *data;
                            evt.priority = last_call;
                            implied_cts[idx].ct_pool.fire_pool_elem_change(&evt, &implied_group->mgp);
                        }
                    }
                    else
                        implied_cts[idx].ct_dev->push_change_event("Value",&except);
                }
                
//                if ((obj_trigg[idx] == true) && (last_call == false))
//                {
    
//                    if (read_except == false)
//                    {
//                        Tango::AttrHistoryStack<Tango::DevDouble> ahs;
//                        ahs.length(1);
//                        data = implied_group->grp->get_ct_data_from_index(idx);
//                        Tango::TimedAttrData<Tango::DevDouble> tad(data, Tango::ATTR_CHANGING, when);
//                        ahs.push(tad);
//                        tg->fill_attr_polling_buffer(implied_cts[idx].ct_dev, attr_name, ahs);
//                    }
//                }
            }
        }
        else
        {
        
//
// The same thing for counter
//

            try
            {
                implied_cts[0].ct_dev->read_Value(implied_cts[0].val_att);
                if (send_event == true)
                {
                    implied_cts[0].val_att.fire_change_event();
                    
                    if(implied_cts[0].ct_pool.has_listeners())
                    {
                        Pool_ns::PoolElementEvent evt(Pool_ns::CTValueChange, &implied_cts[0].ct_pool);
                        evt.old.value = (double)LONG_MIN;
                        evt.curr.value = *implied_cts[0].ct_dev->attr_Value_read;
                        evt.priority = last_call;
                        implied_cts[0].ct_pool.fire_pool_elem_change(&evt);
                    }
                }
            }
            catch (Tango::DevFailed &e)
            {
                except = e;
                read_except = true;
                if (send_event == true)
                {
                    implied_cts[0].val_att.fire_change_event(&e);
                    
                    if(implied_cts[0].ct_pool.has_listeners())
                    {
                        Pool_ns::PoolElementEvent evt(Pool_ns::CTValueChange, &implied_cts[0].ct_pool);
                        evt.old.value = LONG_MIN;
                        evt.curr.value = LONG_MIN;
                        evt.priority = last_call;
                        implied_cts[0].ct_pool.fire_pool_elem_change(&evt);
                    }
                }
            }
                
    
//            if ((obj_trigg[0] == true) && (last_call == false))
//            {
//                if (read_except == false)
//                {
//                    Tango::AttrHistoryStack<Tango::DevDouble> ahs;
//                    ahs.length(1);
//                    Tango::TimedAttrData<Tango::DevDouble> tad(implied_cts[0].ct_dev->attr_Value_read,Tango::ATTR_CHANGING,when);
//                    ahs.push(tad);
//                    tg->fill_attr_polling_buffer(implied_cts[0].ct_dev,attr_name,ahs);
//                }
//            }
        }
    }
    catch (Tango::DevFailed &e)
    {
        if (th->group_id != -1)
            for_each(implied_cts.rbegin(), implied_cts.rend(), mem_fun_ref(&CtInCount::Unlock));
        
        throw;
    }

//
// Unlock devices
//
    if (th->group_id != -1)
        for_each(implied_cts.rbegin(), implied_cts.rend(), mem_fun_ref(&CtInCount::Unlock));
}

//+------------------------------------------------------------------
/**
 *	method:	Pool::set_ext_trigg()
 *
 *	description:	Add all object implied in this movement to the
 * 					list of externally triggered polled objects
 *
 * arg(s) : - implied_cts:
 * 			- implied_group:
 * 			- th: The thread object
 * 			- obj_trigg : A vector of flag to memorize which objects 
 * 						  is externally triggered
 */
//+------------------------------------------------------------------

void Pool::set_ext_trigg(vector<CtInCount> &implied_cts,auto_ptr<GrpInCount> &implied_group,CTPoolThread *th,vector<bool> &obj_trigg)
{
    return;
    size_t ct_nb = implied_cts.size();
    size_t ctr;

//
// Get process admin device
//

    Tango::Util *tg = Tango::Util::instance();
    Tango::DServer *adm_dev = tg->get_dserver_device();
    
//
// For each counter(s)
//

    Tango::DevVarLongStringArray dvlsa;
    dvlsa.lvalue.length(1);
    dvlsa.svalue.length(3);
    
    dvlsa.lvalue[0] = 0;
    dvlsa.svalue[1] = CORBA::string_dup("attribute");
    dvlsa.svalue[2] = CORBA::string_dup("Value");
    
    for (ctr = 0;ctr < ct_nb;ctr++)
    {
        try
        {
            dvlsa.svalue[0] = CORBA::string_dup(implied_cts[ctr].ct_pool.get_full_name().c_str());
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
        dvlsa.svalue[0] = CORBA::string_dup(implied_group->grp->get_name().c_str());
        
        for (size_t idx = 0;idx < ct_nb;idx++)
        {
            string attr_name = implied_cts[idx].ct_pool.name + "_value";
            dvlsa.svalue[2] = CORBA::string_dup(attr_name.c_str());
            try
            {
                Tango::AutoTangoMonitor atm(adm_dev);
                adm_dev->add_obj_polling(&dvlsa,false);
            }
            catch (Tango::DevFailed &e)
            {
                string reas = e.errors[0].reason.in();
                if (reas != "API_AlreadyPolled")
                    obj_trigg[ctr] = false;
            }
        }
    }
}


//+------------------------------------------------------------------
/**
 *	method:	Pool::reset_ext_trigg()
 *
 *	description:	Remove all object implied in this movement from the
 * 					list of externally triggered polled objects
 *
 * arg(s) : - implied_cts:
 * 			- implied_group:
 * 			- th: The thread object
 * 			- obj_trigg : A vector of flag to memorize which objects 
 * 						  is externally triggered
 */
//+------------------------------------------------------------------

void Pool::reset_ext_trigg(vector<CtInCount> &implied_cts,auto_ptr<GrpInCount> &implied_group,CTPoolThread *th,vector<bool> &obj_trigg)
{
    return;
    size_t ct_nb = implied_cts.size();
    size_t ctr;

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
    dvsa[2] = CORBA::string_dup("Value");

    for (ctr = 0;ctr < ct_nb;ctr++)
    {
        try
        {
            if (obj_trigg[ctr] == true)
            {
                dvsa[0] = CORBA::string_dup(implied_cts[ctr].ct_pool.get_full_name().c_str());
                {
                    Tango::AutoTangoMonitor atm(adm_dev);
                    adm_dev->rem_obj_polling(&dvsa,false);
                }
            }
        }
        catch (Tango::DevFailed &e)
        {
            cout << "Gasp, an exception while removing objet from extrenally triggered polling" << endl;
        }
    }
            
//
// Even for group if necessary
//

    if ((th->group_id != -1) && (obj_trigg[ctr] == true))
    {
        dvsa[0] = CORBA::string_dup(implied_group->grp->get_name().c_str());
        
        for (size_t idx = 0;idx < ct_nb;idx++)
        {
            string attr_name = implied_cts[idx].ct_pool.name + "_value";
            dvsa[2] = CORBA::string_dup(attr_name.c_str());
            try
            {
                Tango::AutoTangoMonitor atm(adm_dev);
                adm_dev->rem_obj_polling(&dvsa,false);
            }
            catch (Tango::DevFailed &e)
            {
                cout << "Gasp, an exception while removing objet from extrenally triggered polling on attribute " << attr_name << endl;
            }
        }		
    }
    
}

//+------------------------------------------------------------------
/**
 *	method:	CTPoolThread::manage_thread_exception
 *
 *	description:	Take all the necessary actions if something failed
 *  				during the movement starting phase
 *
 * arg(s) : 
 */
//+------------------------------------------------------------------	
        
void CTPoolThread::manage_thread_exception(Tango::DevFailed &e,vector<CtrlInCount> &implied_ctrls,
                                   vector<CtInCount> &implied_cts,auto_ptr<GrpInCount> &implied_group,
                                   string &except_func,bool state_changed,int32_t loop)
{
        
//
// Unlock all the implied controllers
//

    for_each(implied_ctrls.rbegin(), implied_ctrls.rend(), mem_fun_ref(&CtrlInCount::Unlock));

//
// Reset the counter state to ON if already changed to MOVING
//

    if (state_changed == true)
    {
        for (size_t ll = 0;ll < implied_cts.size();ll++)
        {
            CtInCount &ct_cnt = implied_cts[ll];
            CTExpChannelPool &mp = ct_cnt.ct_pool;		
            Tango::DevState old_state = ct_cnt.ct_dev->get_state();
            ct_cnt.ct_dev->set_state(Tango::ON);
            ct_cnt.state_att.fire_change_event();
            
            if(mp.has_listeners())
            {
                PoolElementEvent evt(StateChange,&mp);
                evt.old.state = PoolTango::toPool(old_state);
                evt.curr.state = ON;
                implied_cts[0].ct_pool.fire_pool_elem_change(&evt);			
            }
        }
        
        if (group_id != -1)
        {
            Tango::DevState old_state = implied_group->grp->get_state();
            implied_group->grp->set_state(Tango::ON);
            implied_group->state_att.fire_change_event();
            
            
            if(implied_group->mgp.has_listeners())
            {
                PoolElementEvent evt(StateChange,&implied_group->mgp);
                evt.old.state = PoolTango::toPool(old_state);
                evt.curr.state = ON;
                implied_group->mgp.fire_pool_elem_change(&evt);
            }
        }
    }
    
//
// Unlock all counters (only for group)
//

    if (group_id != -1)
    {
        for_each(implied_cts.rbegin(), implied_cts.rend(), mem_fun_ref(&CtInCount::Unlock));
    }
            
        
    TangoSys_OMemStream o;
    if (loop != -1)
    {
        o << "Impossible to start counting on device " << implied_cts[loop].ct_pool.name << " (";
        o << implied_cts[loop].ct_pool.get_full_name() << ")";
    }
    if (except_func != "NoFunc")
        o << ". The " << except_func << "() controller method throws an exception" << ends;

    Tango::Except::re_throw_exception(e,(const char *)"CoTi_ControllerFailed",
                                    o.str(),(const char *)"Pool::manage_thread_exception");	
}	
    
}	//	namespace
