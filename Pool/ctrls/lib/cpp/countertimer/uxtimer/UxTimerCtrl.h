#ifndef _DUMMYCOTI_H
#define _DUMMYCOTI_H

#include <pool/CoTiCtrl.h>
#include <tango.h>

extern "C"
{
	/**
	 * The create controller method for the UnixTimer controller.
	 */
	Controller *_create_UnixTimer(const char *,vector<Controller::Properties> &);
}

/**
 * This class has the purpose of providing a ghost device that could handle
 * signals for the UnixTimer controller inside a tango device server
 */
class UxTiClass: public Tango::DeviceClass
{
public:
	/// Constructor
	UxTiClass(string &na):Tango::DeviceClass(na) {}
	/// Destructor
	virtual ~UxTiClass() {}

	/// device factory
	virtual void device_factory(const Tango::DevVarStringArray *devlist_ptr) {}
	
	/// command factory
	virtual void command_factory() {}	
};


/**
 * This class has the purpose of providing a ghost device that could handle
 * signals for the UnixTimer controller inside a tango device server
 */
class UxTi: public Tango::Device_3Impl
{
public:
	/// Constructor
	UxTi(Tango::DeviceClass *cl,string &s):Tango::Device_3Impl(cl,s.c_str()) {}
	/// Destructor
	virtual ~UxTi() {}
	
	/// init device
	virtual void init_device() {}
	/// signal handler
	virtual void signal_handler(long);
};

/**
 * A Counter/Timer controller that can handle a single timer. The timing is 
 * handled by unix signals.
 */
class UnixTimer:public CoTiController
{
public:
	/// Constructor
	UnixTimer(const char *,vector<Controller::Properties> &);
	/// Destructor
	virtual ~UnixTimer();

	/// AddDevice
	virtual void AddDevice(int32_t );
	/// DeleteDevice
	virtual void DeleteDevice(int32_t );

	/// ReadOne
	virtual double ReadOne(int32_t);
	/// AbortOne
	virtual void AbortOne(int32_t );
	
	/// LoadOne
	virtual void LoadOne(int32_t, double);
	/// StartOneCT
	virtual void StartOneCT(int32_t);
	
	/// StateOne
	virtual void StateOne(int32_t, Controller::CtrlState *);
					
protected:
	
	UxTiClass		*cl_ptr;		///< pointer to the Helper DeviceClass
	UxTi			*dev_ptr;		///< pointer to the Helper DeviceImpl
	
	int32_t			nb_sec;			///< number of seconds
	int32_t			nb_usec;		///< number of micro seconds
	
	int32_t			nb_ms;			///< number of mili seconds
	int32_t			stop_time_ms;	///< instance to stop (ms)
	int32_t 			remain_ms;		///< remaining time (ms)
	struct timeval	last_read;		///< last read time
	
	int 			start_th;		///< start thread
};

#endif /* _DUMMYCOTI_H */
