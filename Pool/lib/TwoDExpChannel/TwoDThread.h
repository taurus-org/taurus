//=============================================================================
//
// file :        TwoDthread.h
//
// description : Include for the TwoDThread class.
//
// project :	Sardana's device pool
//
// $Author: tcoutinho $
//
// $Revision: 16 $
//
// $Log$
// Revision 1.2  2007/05/11 08:43:56  tcoutinho
// - fixed bugs
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

#ifndef _TWODTHREADL_H
#define _TWODTHREAD_H

#include <tango.h>
#include <TwoDExpChannel.h>

namespace TwoDExpChannel_ns
{

class TwoDExpChannel;

/**
 * A thread class specific for 1D experiment channel data acquisition
 */
class TwoDThread: public omni_thread, public Tango::LogAdapter
{
public:
	TwoDThread(TwoDExpChannel *dev,omni_mutex &mut,TwoDExpChannel::ShData &dat):
	omni_thread(),Tango::LogAdapter(dev),the_mutex(mut),the_shared_data(dat),the_dev(dev)
	{start_undetached();}

	virtual ~TwoDThread() {}

	void *run_undetached(void *);
	void th_exit(Tango::Attribute &,bool);
	bool is_enough_time(long,struct timeval &,long &);

private:
	omni_mutex 					&the_mutex;
	TwoDExpChannel::ShData		&the_shared_data;
	
	bool						local_th_exit;
	bool						local_cont_error;
	bool						local_stop_time;
	long						local_cum_time;
	long						local_cum_type;
	long						local_nb_read_event;
	struct timespec				local_sleep_time;
	struct timeval				start_th_time;
	TwoDExpChannel				*the_dev;
	
};

}  // namespace

#endif // _TWODTHREAD_H
