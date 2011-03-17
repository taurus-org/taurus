//=============================================================================
//
// file :        PoolUtil.h
//
// description : Include for some utility classes for the Sardana project
//				 pool device
//
// project :	Sardana pool device
//
// $Author$
//
// $Revision$
//
// $Log$
// Revision 1.4  2007/02/08 16:18:14  tcoutinho
// - controller safety on PoolGroupBaseDev
//
// Revision 1.3  2007/02/06 09:41:03  tcoutinho
// - added MeasurementGroup
//
// Revision 1.2  2006/07/07 12:38:43  etaurel
// - Some changes in file header
// - Commit after implementing the group multi motor read
//
// Revision 1.1  2006/06/19 12:31:50  etaurel
// -Split Pool.cpp file in two
//
// copyleft :     CELLS/ALBA
//				  Edifici Ciències Nord. Mòdul C-3 central.
//  			  Campus Universitari de Bellaterra. Universitat Autònoma de Barcelona
//  			  08193 Bellaterra, Barcelona
//  			  Spain
//
//=============================================================================


#ifndef POOLUTIL_H_
#define POOLUTIL_H_

#include "Pool.h"
#include "Utils.h"

#define SAFE_CATCH(A,B)\
    catch (Pool_ns::PoolFailed &e1) {throw;}\
    catch (Tango::DevFailed &e2) {throw;}\
    catch (...)\
    {\
        TangoSys_OMemStream o,p;\
        o << "Controller " << A << " has thrown an unknown exception" << ends;\
        p << "Pool::" << B << ends;\
        Tango::Except::throw_exception((const char *)"Pool_UnkExceptFromCtrl",\
                                       o.str(), p.str());\
    }

#define DEV_FATAL_STREAM(d) \
  if ((d)->get_logger()->is_fatal_enabled()) \
    (d)->get_logger()->fatal_stream() \
      << log4tango::LogInitiator::_begin_log

#define DEV_ERROR_STREAM(d) \
  if ((d)->get_logger()->is_error_enabled()) \
    (d)->get_logger()->error_stream() \
      << log4tango::LogInitiator::_begin_log

#define DEV_WARN_STREAM(d) \
  if ((d)->get_logger()->is_warn_enabled()) \
    (d)->get_logger()->warn_stream() \
      << log4tango::LogInitiator::_begin_log

#define DEV_INFO_STREAM(d) \
  if ((d)->get_logger()->is_info_enabled()) \
    (d)->get_logger()->info_stream() \
      << log4tango::LogInitiator::_begin_log
 
#define DEV_DEBUG_STREAM(d) \
  if ((d)->get_logger()->is_debug_enabled()) \
    (d)->get_logger()->debug_stream() \
      << log4tango::LogInitiator::_begin_log
      
namespace Pool_ns
{

class TangoThrower: public Pool_ns::PoolThrower
{
public:

    virtual inline void throw_exception(const char *reason,
                                        const char *desc,
                                        const char *origin)
    {
        Tango::Except::throw_exception(reason, desc, origin);
    }
    
    virtual inline void throw_exception(const char *reason,
                                        const std::string &desc,
                                        const char *origin)
    {
        Tango::Except::throw_exception(reason, desc, origin);
    }
};

class PoolTango
{
public:

    static void throw_tango_exception(Pool_ns::PoolFailed &);
    
    static inline Tango::DevState toTango(Pool_ns::PoolState state)
    { return static_cast<Tango::DevState>(state); }

    static inline Pool_ns::PoolState toPool(Tango::DevState state)
    { return static_cast<Pool_ns::PoolState>(state); }

    static void toPool(std::vector<Tango::DevLong> &in, ElemIdVector &out)
    {
        for(std::vector<Tango::DevLong>::iterator it = in.begin(); it != in.end(); ++it)
            out.push_back((ElementId)*it);
    }

    static void toTango(ElemIdVector &in, std::vector<Tango::DevLong> &out)
    {
        for(ElemIdVectorIt it = in.begin(); it != in.end(); ++it)
            out.push_back((Tango::DevLong)*it);
    }
};

/**
 * This class stores the State of a specific Pool device at the creation
 * time of this object.
 * When the destructor is called the new state is compared with the previously
 * stored state. If there is a difference, a state event is sent.
 */
class PoolStateEvent
{
public:
	
	/**
	 * Constructor
	 * @param dev a pointer to the Pool device
	 */
	PoolStateEvent(Pool *dev):the_pool(dev) {d_state = the_pool->get_state();}
	
	/// Destructor
	~PoolStateEvent();
	
protected:
	/** a pointer to the Pool device */
	Pool				*the_pool;
	
	/** the state of the Pool device */
	Tango::DevState		d_state;
};

#define CORBA_String_to_double(s,d) \
    { TangoSys_MemStream str; str << s; str >> d; }

#define double_to_CORBA_String(d,s) \
    { TangoSys_MemStream str; str << d; s = CORBA::string_dup(str.str().c_str()); }

#define String_to_double(s,d) \
    { TangoSys_MemStream str; str << s; str >> d; }

#define double_to_String(d,s) \
    { TangoSys_MemStream str; str << d; s = str.str(); }
}

#endif /*POOLUTIL_H_*/
