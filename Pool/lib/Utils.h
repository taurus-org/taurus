//=============================================================================
//
// file :        Utils.h
//
// description : Include for some utility classes for the Sardana project
//				 pool device
//
// project :	Sardana pool device
//
// $Author: tiagocoutinho $
//
// copyleft :     CELLS/ALBA
//				  Edifici Ciències Nord. Mòdul C-3 central.
//  			  Campus Universitari de Bellaterra. Universitat Autònoma de Barcelona
//  			  08193 Bellaterra, Barcelona
//  			  Spain
//
//=============================================================================

#pragma once

#include <utility>
#include <functional>
#include <iostream>
#include <string>
#include <omnithread.h>

#include "CPoolDefs.h"
#include "CPoolExcept.h"

#define SAFE_DELETE(x) { if((x)!=NULL) { delete (x); (x)=NULL; } } 
#define SAFE_DELETE_ARRAY(x) { if(x) { delete[] (x); (x)=NULL; } }

#define EPSILON                 1E-9

#define DEFAULT_MON_TIMEOUT     3200

namespace Pool_ns
{

/**
 * @brief The PoolMonitor class
 */
class PoolMonitor: public omni_mutex
{
    int32_t         time_out;
    omni_condition  cond;
    omni_thread     *locking_thread;
    int32_t         locked_ctr;
    std::string     name;

public :
    PoolMonitor(const std::string &n): 
        time_out(DEFAULT_MON_TIMEOUT), cond(this),
        locking_thread(NULL), locked_ctr(0), name(n) 
    {}
    
    PoolMonitor(): 
        time_out(DEFAULT_MON_TIMEOUT), cond(this),
        locking_thread(NULL), locked_ctr(0), name("unknown") 
    {}
    
    ~PoolMonitor() 
    {}

    /**
     * Get a monitor. The thread will wait (with timeout) if the monitor is 
     * already locked. If the thread is already the monitor owner thread, 
     * simply increment the locking counter
     */
    inline void get_monitor();
    
    /** 
     * Release a monitor if the caller thread is the locking thread. Signal 
     * other threads if the locking counter goes down to zero
     */
    inline void rel_monitor();
    
    /**
     * Sets the maximum time the lock should wait
     */
    inline void timeout(int32_t new_to) 
    { time_out = new_to; }
    
    /**
     * Gets the time out value
     */
    inline int32_t timeout() 
    { return time_out; }
    
    /**
     * Waits for the condition
     */
    inline void wait() 
    { cond.wait(); }
    
    /**
     * Waits for the condition with a timeout (in miliseconds)
     */
    inline int wait(int32_t nb_millis);
    
    /**
     * Signals the condition
     */
    inline void signal() 
    { cond.signal(); }
    
    /**
     * Gets the locking thread id or 0 if there is no locking thread
     */
    inline int get_locking_thread_id()
    { return (locking_thread != NULL) ? locking_thread->id() : 0; }
};

class PoolElement;

class AutoPoolMonitor
{
    /** the pool omni monitor to acquire */
    PoolMonitor          *monitor;
    
public:
    AutoPoolMonitor(PoolMonitor *mon);
    
    AutoPoolMonitor(PoolElement *elem);
    
    ~AutoPoolMonitor();
};


class StringEqualsIgnoreCase
{

    static inline bool lessThanIgnoreCase(char c1, char c2)
    {
        return tolower(c1) < tolower(c2);
    }

public:

    inline bool operator() (const std::string &s1, const std::string &s2) const
    {
        return lexicographical_compare(s1.begin(), s1.end(),
                                       s2.begin(), s2.end(),
                                       lessThanIgnoreCase);
    }
};

bool doubleEqual(double, double);

inline std::ostream & indentToStream(std::ostream & flux, int indent)
{
    while (indent-- > 0) flux << '\t';
    return flux;
}

/*-----------------------------------------------------------------------------
Title :	Function adaptors for pair associative containers
Owner :	Adapted from Jay Kint

    Copyright (C) 2003, Jay Kint, All Rights Reserved
-------------------------------------------------------------------------------
Description:
Make using pair associative containers (map and hash_map) a little easier with
the algorithms.
*/

//-----------------------------------------------------------------------------
//							Types and Structures
//-----------------------------------------------------------------------------

/** call_class_with_data_t */
template <typename Functor>
struct call_class_with_data_t {

    Functor f_;
    typedef typename Functor::result_type Result;
    typedef typename Functor::argument_type Arg;

    explicit call_class_with_data_t( Functor f ) : f_(f) {}
    
    template <typename A, typename B>
    Result operator()( const std::pair<A,B>& v ) const {

        Arg value = v.second;     // to enforce the equality of the data with the argument type instantiated

        return f_( value );
    }
};

/** call_func_with_data_t */
template <typename Result, typename Arg>
struct call_func_with_data_t {

    typedef Result (*Func)(Arg);
    Func f_;

    explicit call_func_with_data_t( Func f ) : f_(f) {}
    
    template <typename A, typename B>
    Result operator()( const std::pair<A,B>& v ) const {

        Arg value = v.second;     // to enforce the equality of the data with the argument type instantiated

        return f_( value );
    }
};

/** call_class_with_data_t */
template <typename Functor>
call_class_with_data_t<Functor> with_data( Functor f  )
{
    return call_class_with_data_t<Functor>( f );
}

/** call_func_with_data_t */
template <typename Result, typename Arg>
call_func_with_data_t<Result, Arg> with_data( Result (*f)(Arg) )
{
    return call_func_with_data_t<Result, Arg>( f );
}

/** call_func_with_key_t */
template <typename Result, typename Arg>
struct call_func_with_key_t {

    typedef Result (*Func)(Arg);
    Func f_;

    explicit call_func_with_key_t( Func f ) : f_(f) {}
    
    template <typename A, typename B>
    Result operator()( const std::pair<A,B>& v ) const {

        Arg value = v.first;     // to enforce the equality of the data with the argument type instantiated

        return f_( value );
    }
};

/** call_class_with_key_t */
template <typename Functor>
struct call_class_with_key_t {

    Functor f_;
    typedef typename Functor::result_type Result;
    typedef typename Functor::argument_type Arg;

    explicit call_class_with_key_t( Functor f ) : f_(f) {}
    
    template <typename A, typename B>
    Result operator()( const std::pair<A,B>& v ) const {

        Arg value = v.first;     // to enforce the equality of the data with the argument type instantiated

        return f_( value );
    }
};

/** call_func_with_key_t */
template <typename Result, typename Arg>
call_func_with_key_t<Result, Arg> with_key( Result (*f)(Arg) )
{
    return call_func_with_key_t<Result, Arg>( f );
}

/**
 * call_class_with_key_t
 */
template <typename Functor>
call_class_with_key_t<Functor> with_key( Functor f  )
{
    return call_class_with_key_t<Functor>( f );
}

}

#include "Utils.inl"


