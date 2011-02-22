#ifndef _MOTIONTHREAD_H
#define _MOTIONTHREAD_H

#include <tango.h>

#include "CPoolDefs.h"


namespace Pool_ns
{
    
class DevicePool;



struct AbstractPoolElementInMotion
{
    PoolElement     *element;
    
    AbstractPoolElementInMotion(PoolElement *pe): element(pe)
    {}
    
    virtual void lock() = 0;
    virtual void unlock() = 0;
};

struct PoolElementInMotion: public AbstractPoolElementInMotion
{
    AutoPoolMonitor *mon;

    PoolElementInMotion(PoolElement *pe): 
        AbstractPoolElementInMotion(pe)
    {}    
    
    inline virtual void lock()
    { 
        assert(mon == NULL);
        mon = new AutoPoolMonitor(element); 
    }
    
    inline virtual void unlock()
    { SAFE_DELETE(mon); }
};

struct MotorInMotion : public PoolElementInMotion
{
    double destination;
    
    MotorInMotion(PoolElement *pe, double dest): 
        PoolElementInMotion(pe), destination(dest)
    {}
    
    inline MotorPool *get_motor()
    { return static_cast<MotorPool *>(element); }
    
};

struct ControllerPoolInMotion: public AbstractPoolElementInMotion
{
    AutoPoolLock    *lock_ptr;
    
    ControllerPoolInMotion(ControllerPool *pe): 
        AbstractPoolElementInMotion(pe), lock_ptr(NULL)
    {}
    
    inline ControllerPool *get_ctrl()
    { return static_cast<ControllerPool *>(element); }
    
    inline PoolLock &get_monitor()
    { return get_ctrl()->get_ctrl_class_mon(); }
    
    inline virtual void lock()
    { 
        assert(lock_ptr == NULL);
        lock_ptr = new AutoPoolLock(get_monitor()); 
    }
    
    inline virtual void unlock()
    { SAFE_DELETE(lock_ptr);}

};

typedef std::vector<MotorInMotion*> MotorInMotionVector;
typedef MotorInMotionVector::iterator MotorInMotionVectorIt;

/**
 * a map definition intended to contain: 
 * - key is controller ID,
 * - value is a map where:
 *   - key is a pool element ID,
 *   - value is its value
 */	
typedef std::map<ControllerPoolInMotion *, MotorInMotionVector> CtrlInMotionMap;
typedef CtrlInMotionMap::iterator CtrlInMotionMapIt;


class MotionThread: public omni_thread
{
    DevicePool                  *pool;
    PoolElement                 *motion_src;
    CtrlInMotionMap             positions;

    /**
     * Useful precalculated values in order to save some time
     */ 
    int32_t                     elem_nb;
    
    void move(bool wait_flag = true);
    
    void send_to_ctrls(bool wait_flag = true);
    
    void moving_loop(void );
    
    inline bool is_group_motion() 
    { return motion_src->get_type() == MOTOR_GROUP_ELEM; }

    inline PoolElement *get_motion_src_elem()
    { return motion_src; }

    inline PoolMoveable* get_motion_src()
    { return (PoolMoveable*)get_motion_src_elem(); }
    
    inline PoolMonitor* get_notification_monitor()
    { return motion_src->get_notification_monitor(); }

public:
    
    MotionThread(DevicePool &p): 
        pool(&p), motion_src(NULL), elem_nb(0)
    { }

    void setup(ElementId src, CtrlValueMap &pos);
    
    void cleanup();
    
    void run(void *);

};

}   // namespace_ns

#endif  // _MOTIONTHREAD_H
