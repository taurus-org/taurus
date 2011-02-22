#include <iostream>
#include <UxTimerCtrl.h>
#include <signal.h>
#include <sys/time.h>

using namespace std;

//-----------------------------------------------------------------------------
//
// method : 		UnixTimer::UnixTimer
// 
// description : 	Ctor of the UnixTimer class
//					It retrieve some properties from Tango DB, build a 
//					connection to the Simulated controller and ping it
//					to check if it is alive
//
//-----------------------------------------------------------------------------

UnixTimer::UnixTimer(const char *inst,vector<Controller::Properties> &prop):CoTiController(inst),
cl_ptr(NULL),dev_ptr(NULL),nb_ms(0),stop_time_ms(0),remain_ms(0),start_th(0)
{

//
// Build a faked Tango device that we can use the
// tango system to install the alarm signal used by the
// timer
//

	string cl_name("UxTiClass");
	cl_ptr = new UxTiClass(cl_name);
	
	string faked_dev_name("a/b/c");
	dev_ptr = new UxTi(cl_ptr,faked_dev_name);
	dev_ptr->set_state(Tango::ON);
	
//
// Some data member init
//

	nb_sec = nb_usec = 0;
}

//-----------------------------------------------------------------------------
//
// method : 		UnixTimer::~UnixTimer
// 
// description : 	Dtor of the UnixTimer class
//
//-----------------------------------------------------------------------------

UnixTimer::~UnixTimer()
{
	//cout << "[UnixTimer] class dtor" << endl;
	if(cl_ptr != NULL)
		delete cl_ptr;
	if (dev_ptr != NULL)
		delete dev_ptr;
}

//-----------------------------------------------------------------------------
//
// method : 		UnixTimer::AddDevice
// 
// description : 	Register a new device for the controller
//					For the simulated controller, this simply means increment
//					motor count
//
//-----------------------------------------------------------------------------

void UnixTimer::AddDevice(int32_t idx)
{
	//cout << "[UnixTimer] Creating a new Counter Timer with index " << idx << " on controller UnixTimer/" << inst_name << endl;
	dev_ptr->register_signal(SIGALRM);
}

//-----------------------------------------------------------------------------
//
// method : 		UnixTimer::DeleteDevice
// 
// description : 	Unregister a new device for the controller
//					For the simulated controller, this simply means decrement
//					motor count
//
//-----------------------------------------------------------------------------

void UnixTimer::DeleteDevice(int32_t idx)
{
	//cout << "[UnixTimer] Deleting Counter Timer with index " << idx << " on controller UnixTimer/" << inst_name  << endl;
	dev_ptr->unregister_signal(SIGALRM);
}

//-----------------------------------------------------------------------------
//
// method : 		UnixTimer::AbortOne
// 
// description : 	Abort a movement.
//
// arg(s) : - idx : The motor number (starting at 1)
//
//-----------------------------------------------------------------------------

void UnixTimer::AbortOne(int32_t idx)
{
	//cout << "[UnixTimer] Aborting one timer with index " << idx << " on controller UnixTimer/" << inst_name << endl;

//
// The Stop command will not be executed by the same thread than the thread which has done
// the start (which is a Pool internal thread). Therefore, the getitimer() call will return 0
// To know at what moment the stop command has been executed, take the time of the last read
// and correct the value with the delta between now and the last read
//
       		
	struct timeval now;
	gettimeofday(&now,NULL);
	
	if (now.tv_sec == last_read.tv_sec)
	{
		stop_time_ms = remain_ms - ((now.tv_usec - last_read.tv_usec) / 1000);
	}
	else
	{
		int32_t delta_usec = ((now.tv_sec - last_read.tv_sec) * 1000000) + last_read.tv_usec - now.tv_usec;
		stop_time_ms = remain_ms - delta_usec / 1000;
	}
	
//
// Stop the timer
//
	
	struct itimerval new_it;
	new_it.it_value.tv_sec = 0;
	new_it.it_value.tv_usec = 0;
	new_it.it_interval.tv_sec = 0;
	new_it.it_interval.tv_usec = 0;
	
	int res = setitimer(ITIMER_REAL,&new_it,NULL);
	if (res != 0)
	{
		TangoSys_OMemStream o;
		o << "Error when trying to stop the OS timer. Error code returned: " << errno << ends;
		
		Tango::Except::throw_exception((const char *)"UnixTimer_BadCtrlPtr",o.str(),
					       			   (const char *)"UnixTimer::StartOneCT()");
	}	
	dev_ptr->set_state(Tango::ON);
}

//-----------------------------------------------------------------------------
//
// method : 		UnixTimer::ReadOne
// 
// description : 	Read a counter timer
//
// arg(s) : - idx : The counter timer number
//
// This method returns the counter timer value
//-----------------------------------------------------------------------------

double UnixTimer::ReadOne(int32_t idx)
{
	//cout << "[UnixTimer] Getting Value for timer with index " << idx << " on controller UnixTimer/" << inst_name << endl;
	double returned_time;

//
// There is a UNIX trap here. The getitimer() call returns something different
// than zero only for the thread which has started the timer.
// Take care of this
//
	
	if (dev_ptr != NULL)
	{
		int th = omni_thread::self()->id();
		if (th == start_th)
		{
			gettimeofday(&last_read,NULL);
			if (dev_ptr->get_state() == Tango::MOVING)
			{
				struct itimerval ti;
				getitimer(ITIMER_REAL,&ti);
		    
		    	remain_ms = ti.it_value.tv_sec * 1000 + (int32_t)(ti.it_value.tv_usec / 1000);
		    	returned_time = double((nb_ms - remain_ms) / 1000.0);
			}
			else
				returned_time = (double)((nb_ms - stop_time_ms) / 1000.0);
		}
		else
		{
			if (dev_ptr->get_state() == Tango::MOVING)	
				returned_time = (double)((nb_ms - remain_ms) / 1000.0);
			else
				returned_time = (double)((nb_ms - stop_time_ms) / 1000.0);
		}
	}
	else
	{
		TangoSys_OMemStream o;
		o << "Unix Timer controller for controller UnixTimer/" << get_name() << " is not correctly constructed" << ends;
		
		Tango::Except::throw_exception((const char *)"UnixTimer_BadCtrlPtr",o.str(),
					       			   (const char *)"UnixTimer::StateOne()");
	}
	return returned_time;
}


//-----------------------------------------------------------------------------
//
// method : 		UnixTimer::StateOne
// 
// description : 	Get one timer status. Timer status means two things :
//					1 - The Timer state (Tango sense)
//					2 - The timer error message if any
//
// arg(s) : - idx : The timer number
//			- ct_info_ptr : Pointer to a struct. which will be filled with
//							timer status
//
//-----------------------------------------------------------------------------

void UnixTimer::StateOne(int32_t idx,Controller::CtrlState *ct_info_ptr)
{
	//cout << "[UnixTimer] Getting state for Timer with index " << idx << " on controller UnixTimer/" << inst_name << ", thread = " << omni_thread::self()->id() << endl;

	if (dev_ptr != NULL)
	{
		ct_info_ptr->state = dev_ptr->get_state();
	}
	else
	{
		TangoSys_OMemStream o;
		o << "Unix Timer controller for controller UnixTimer/" << get_name() << " is not correctly constructed" << ends;
		
		Tango::Except::throw_exception((const char *)"UnixTimer_BadCtrlPtr",o.str(),
					       			   (const char *)"UnixTimer::StateOne()");
	}
}

//-----------------------------------------------------------------------------
//
// method : 		UnixTimer::LoadOne
// 
// description : 	Load a timer counter
//
// arg(s) : - idx : The timer number
//			- val : The timer value
//
//-----------------------------------------------------------------------------

void UnixTimer::LoadOne(int32_t idx, double val)
{
	
//
// Convert the input value (S unit) in second and usec
//

	long tmp_val = (long)(val * 1000);
	if (tmp_val >= 1000)
	{
		nb_sec = (long)(tmp_val / 1000);
		nb_usec = (tmp_val - (nb_sec * 1000)) * 1000;
	}
	else
	{
		nb_sec = 0;
		nb_usec = tmp_val * 1000;
	}
	
	nb_ms = tmp_val;
	stop_time_ms = nb_ms;
}

//-----------------------------------------------------------------------------
//
// method : 		UnixTimer::StartOne
// 
// description : 	Start the timer
//
// arg(s) : - idx : The timer number
//
//-----------------------------------------------------------------------------
void UnixTimer::StartOneCT(int32_t idx)
{
	if ((nb_sec == 0) && (nb_usec == 0))
	{
		Tango::Except::throw_exception((const char *)"UnixTimer_NoTime",
									   (const char *)"No time value loaded in the timer. Can' start",
					       			   (const char *)"UnixTimer::StartOneCT()");
	}
	
	struct itimerval new_it;
	new_it.it_value.tv_sec = nb_sec;
	new_it.it_value.tv_usec = nb_usec;
	new_it.it_interval.tv_sec = 0;
	new_it.it_interval.tv_usec = 0;

	int res = setitimer(ITIMER_REAL,&new_it,NULL);
	if (res != 0)
	{
		TangoSys_OMemStream o;
		o << "Error when trying to set the OS timer. Error code returned: " << errno << ends;
		
		Tango::Except::throw_exception((const char *)"UnixTimer_BadCtrlPtr",o.str(),
					       			   (const char *)"UnixTimer::StartOneCT()");
	}	
	dev_ptr->set_state(Tango::MOVING);
	stop_time_ms = 0;
	start_th = omni_thread::self()->id();
}
	
//
//==============================================================================================
//

void UxTi::signal_handler(long signo)
{
	//cout << "In device signal_handler for signal " << signo << endl;
	set_state(Tango::ON);
}
	
//
//===============================================================================================
//

const char *CounterTimer_Ctrl_class_name[] = {"UnixTimer",NULL};
const char *UnixTimer_doc = "This is the Unix Timer controller class";
const char *UnixTimer_gender = "Timer";
const char *UnixTimer_model = "Linux";
const char *UnixTimer_image = "unix_timer.png";
const char *UnixTimer_icon = "unix_timer_icon.png";
const char *UnixTimer_organization = "CELLS - ALBA";
const char *UnixTimer_logo = "ALBA_logo.png";
							  			 
int32_t UnixTimer_MaxDevice = 1;

extern "C"
{
	
Controller *_create_UnixTimer(const char *inst,vector<Controller::Properties> &prop)
{
	return new UnixTimer(inst,prop);
}


}
