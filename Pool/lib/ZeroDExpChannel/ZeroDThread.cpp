//+=============================================================================
//
// file :         ZeroDThread.cpp
//
// description :  C++ source for the ZeroDThread class. 
//
// project :      TANGO Device Server
//
// $Author: tiagocoutinho $
//
// $Revision: 295 $
//
// $Log$
// Revision 1.5  2007/06/13 15:17:59  etaurel
// - Fix memory leak
//
// Revision 1.4  2007/05/25 13:28:19  tcoutinho
// - small changes
//
// Revision 1.3  2007/05/11 08:43:56  tcoutinho
// - fixed bugs
//
// Revision 1.2  2007/05/10 09:32:34  etaurel
// - Small changes for better 64 bits portability
//
// Revision 1.1  2007/02/08 07:56:49  etaurel
// - Changes after compilation -Wall. Added the CumulatedValue attribute and
// everything to implement it (thread....)
//
//
// copyleft :   CELLS/ALBA
//		Edifici Ciences Nord
//		Campus Universitari de Bellaterra
//		Universitat Autonoma de Barcelona
//		08193 Bellaterra, Barcelona, SPAIN
//
//=============================================================================

#include "ExternalFiCa.h"
#include "CtrlFiCa.h"
#include "ZeroDThread.h"

#include "PyUtils.h"

#include <pool/ZeroDCtrl.h>

namespace ZeroDExpChannel_ns
{

//-----------------------------------------------------------------------------
//
// method : 		ZeroDThread::run_undetached
// 
// description : 	The thread main code
//
//-----------------------------------------------------------------------------
    
void *ZeroDThread::run_undetached(void *ptr)
{
    AutoCleanPythonGIL auto_clean_gil;
        
    DEBUG_STREAM << "The ZeroD thread starts..." << endl;

//
// Some initialisation
//

    int32_t local_ct_idx = the_dev->get_axis();
    ZeroDController *typed_ctrl = static_cast<ZeroDController *>(the_dev->get_controller());
    
    gettimeofday(&start_th_time,NULL);
    
    Tango::MultiAttribute *dev_attrs = the_dev->get_device_attr();
    Tango::Attribute &state_att = dev_attrs->get_attr_by_name("State");
    Tango::Attribute &c_value_att = dev_attrs->get_attr_by_name("CumulatedValue");
    
//
// Get some static data from the shared data
//

    {
        omni_mutex_lock lo(the_mutex);
        local_cont_error = the_shared_data.cont_error;
        local_stop_time = the_shared_data.stop_if_no_time;
        local_cum_time = the_shared_data.cum_time * 1000;
        local_cum_type = the_shared_data.cum_type;
        local_nb_read_event = the_shared_data.fire_event;
        local_sleep_time = the_shared_data.sleep_time;
    }
    
//
// If in one shot mode, the cumulation time is set to infinite so we
// are sure to have enought time to get the single data sample 
//
    if(local_cum_type == Pool_ns::ONE_SHOT)
        local_cum_time = 0;

    struct timeval start,stop;
    bool got_error = false;
    int32_t read_ctr = 0;
    bool first_event = true;
                    
//
// An endless loop
//

    while(1)
    {
        
//
// Check if we need to exit
//

        {
            omni_mutex_lock lo(the_mutex);
            local_th_exit = the_shared_data.th_exit;
        }

//
// We need to exit
// Do not try to fire event now, because the client thread has the device monitor
// and it will not be possible for this thread to get it to fire the event.
// (DeadLock). The client thread will do it.
//

        if (local_th_exit == true)
        {
            DEBUG_STREAM << "Arrg, I have been killed by my master" << endl;
            th_exit(c_value_att,false);
        }

//
// Read the value from the controller
// and manage 3 kinds of error.
// 1 - A classical DevFailed exception thrown by the controller
// 2 - An unknown exception thrown by the controller
// 3 - A controller which has not redefined the readOne method
//

        double tmp_read_value;
        bool valid_data = true;
        
        {
            gettimeofday(&start,NULL);
            
            try
            {
                Tango::AutoTangoMonitor tg_mon(the_dev);
                Pool_ns::AutoPoolLock lo(the_dev->get_fica_ptr()->get_mon());
                typed_ctrl->PreReadAll();
                typed_ctrl->PreReadOne(local_ct_idx);
                typed_ctrl->ReadAll();
                tmp_read_value = typed_ctrl->ReadOne(local_ct_idx);
            }
            catch (Tango::DevFailed &e)
            {
                {
                    omni_mutex_lock lo(the_mutex);
                    the_shared_data.errors = e.errors;
                    the_shared_data.error_nb++;
                }
                valid_data = false;
            }
            catch (...)
            {
                {
                    omni_mutex_lock lo(the_mutex);
                    the_shared_data.errors.length(1);
                
                    the_shared_data.errors[0].severity = Tango::ERR;
                    the_shared_data.errors[0].origin = CORBA::string_dup("ZeroDThread::run_undetached()");
                    the_shared_data.errors[0].reason = CORBA::string_dup("Pool_UnkExceptFromCtrl");
                    the_shared_data.errors[0].desc = CORBA::string_dup("The controller has sent an unknown exception");
                
                    the_shared_data.error_nb++;
                }
                valid_data = false;
            }
            
            gettimeofday(&stop,NULL);
        }
            
        if (isnan(tmp_read_value) != 0)
        {
            {
                omni_mutex_lock lo(the_mutex);
                the_shared_data.errors.length(1);
                
                the_shared_data.errors[0].severity = Tango::ERR;
                the_shared_data.errors[0].origin = CORBA::string_dup("ZeroDThread::run_undetached()");
                the_shared_data.errors[0].reason = CORBA::string_dup("ZeroDExpChannel_BadController");
                the_shared_data.errors[0].desc = CORBA::string_dup("The Zero D Exp Channel controller class has not re-defined method to read value (readOne(...))");	
            
                the_shared_data.error_nb++;
            }
            valid_data = false;
        }

//
// Update the shared data or exit if the continue on error flag
// is false
//

        if (valid_data == true)
        {
            omni_mutex_lock lo(the_mutex);
            the_shared_data.read_values.push_back(tmp_read_value);
            read_ctr++;
            the_shared_data.acq_dates.push_back(111);
        }
        else
        {
            got_error = true;
            if (local_cont_error == false)
            {
                {
                    Tango::AutoTangoMonitor atm(the_dev);
                    the_dev->set_state(Tango::ALARM);
                    
                    state_att.fire_change_event(); 
                }
                DEBUG_STREAM << "Arrg, I have been killed by an error" << endl;
                th_exit(c_value_att,true);
            }
        }

//
// If needed, check if we have time to get another point
//

        if(local_cum_time != 0)
        {
        
//
// Compute time needed by the last read
//

            long needed_time;
            if (start.tv_sec == stop.tv_sec)
                needed_time = stop.tv_usec - start.tv_usec;
            else
            {
                long nb_sec = stop.tv_sec - start.tv_sec;
                long nb_usec = (1000000 - start.tv_usec) + stop.tv_usec;
            
                needed_time = (1000000 * (nb_sec - 1)) + nb_usec;
            }

//
// Check if we still have time
//

            long remain_time;
            if (((is_enough_time(needed_time,stop,remain_time) == false) && (local_stop_time == true)) ||
               (remain_time <= 0))
            {
                {
                    Tango::AutoTangoMonitor atm(the_dev);
                    if (got_error == true)
                        the_dev->set_state(Tango::ALARM);
                    else
                        the_dev->set_state(Tango::ON);
                    
                    state_att.fire_change_event(); 
                }
                
                DEBUG_STREAM << "Arrg, I have no time to get one more point "
                    "(needed time=" << needed_time << ") "
                    "(remaining time=" << remain_time << ")"<< endl;
                th_exit(c_value_att,true);
            }
                
        }

//
// Fire event if necessary but only if the "Stop" commmand
// has not been already received by the device otherwise,
// a deadlock will happen
//

        if (read_ctr == local_nb_read_event ||
            local_cum_type == Pool_ns::ONE_SHOT)
        {
            {
                omni_mutex_lock lo(the_mutex);
                local_th_exit = the_shared_data.th_exit;
            }
            
            if (local_th_exit == false)
            {
//
// For the first event, we want to send it whatever the value is
//
                if(local_cum_type != Pool_ns::NO_COMPUTATION)
                {
                    if (first_event == true)
                        c_value_att.set_change_event(true,false);
                    
                    {
                        Tango::AutoTangoMonitor atm(the_dev);
                        try
                        {
                            the_dev->read_CumulatedValue(c_value_att);
                            c_value_att.fire_change_event();
                        }
                        catch(Tango::DevFailed &df)
                        {
                            c_value_att.fire_change_event(&df);
                        }
                        catch(...) {}
                    }
                    
                    if (first_event == true)
                    {
                        c_value_att.set_change_event(true,true);
                        first_event = false;
                    }
                    
                    if(local_cum_type == Pool_ns::ONE_SHOT)
                    {
                        {
                            Tango::AutoTangoMonitor atm(the_dev);
                            if (got_error == true)
                                the_dev->set_state(Tango::ALARM);
                            else
                                the_dev->set_state(Tango::ON);
                            
                            state_att.fire_change_event(); 
                        }
                        
                        th_exit(c_value_att,false);
                    }
                }
            }
            read_ctr = 0;
        }

//
// Sleep a while to give other user(s) a chance to do something on the controller
//
        
        nanosleep(&local_sleep_time,NULL);
        DEBUG_STREAM << "This stupid thread has executed a new loop" << endl;
    }
    return NULL;
}

//-----------------------------------------------------------------------------
//
// method : 		ZeroDThread::th_exit
// 
// description : 	Terminate the thread
//
// args: In : - the_att : Reference to the attribute on which event will (or not)
//						  be fired
//			  - fire_last_event : Boolean set to true if a lat change-event
//								  has to be fired
//
//-----------------------------------------------------------------------------

void ZeroDThread::th_exit(Tango::Attribute &the_att,bool fire_last_event)
{
    if (fire_last_event == true)
    {
        the_att.set_change_event(true,false);
        {
            Tango::AutoTangoMonitor atm(the_dev);
            try
            {
                the_dev->read_CumulatedValue(the_att);
                the_att.fire_change_event();
            }
            catch(Tango::DevFailed &df)
            {
                the_att.fire_change_event(&df);
            }
            catch(...) {}
        }
        the_att.set_change_event(true,true);
    }
    
    {
        omni_mutex_lock lo(the_mutex);
        the_shared_data.i_am_dead = true;
    }
    omni_thread::exit();
}

//-----------------------------------------------------------------------------
//
// method : 		ZeroDThread::is_enough_time
// 
// description : 	Compute if there is enogh time to get one more point
//					Return true if yes. Returns false otherwise
//
// args : in : - needed : The time needed (uS) by the last read
//			   - stop : The data of the end of the last read
//
//-----------------------------------------------------------------------------

bool ZeroDThread::is_enough_time(long needed,struct timeval &stop,long &remain_time)
{
    bool ret_value;
    
    long runned_time;
    if (stop.tv_sec == start_th_time.tv_sec)
        runned_time = stop.tv_usec - start_th_time.tv_usec;
    else
    {
        long nb_sec = stop.tv_sec - start_th_time.tv_sec;
        long nb_usec = (1000000 - start_th_time.tv_usec) + stop.tv_usec;
    
        runned_time = (1000000 * (nb_sec - 1)) + nb_usec;
    }
    
    remain_time = local_cum_time - runned_time;
    if ((runned_time + needed + (local_sleep_time.tv_nsec/1000)) >= local_cum_time)
        ret_value = false;
    else
        ret_value = true;
        
    return ret_value;
}

} // namespace
