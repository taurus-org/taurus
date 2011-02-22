#ifndef _CPOOL_MOVEABLE_H_
#define _CPOOL_MOVEABLE_H_

#include <CPoolData.h>

namespace Pool_ns 
{

/**
 * A motion element. By definition, a motion element is an element which is
 * moveable.
 */
struct PoolMoveable
{
    /** array of moveable elements */
    std::vector<ElementId>  _moveables;
    
    /** The thread id which is responsible for the current motion of this object */
    int                     motion_thread;
    
    /**
     * the destructor
     */
    virtual ~PoolMoveable()
    {}
    
    /**
     * Calculates the positions that the moveables in this Moveable should move
     * to according to the given position array.
     *
     * @param[in] src the array of positions that this moveable should move to.
     * @param[out] dest a map where: 
     *                  key is physical motor controller ID,
     *                  value is a map where:
     *                          key is motor ID,
     *                          value is its calculated position
     */    
    virtual void calc_move(double *src, CtrlValueMap& dest) = 0;
    
    /**
     * Returns the number of values this moveable receives as input to a 
     * calc_move.
     *
     * @return the number of values this moveable receives as input to a 
     *         calc_move
     */
    inline virtual int32_t get_size() 
    { return 1; }
    
    /**
     * sets the motion thread for the current motion
     */
    inline void set_motion_thread(int id, bool propagate = true)
    { motion_thread = id; }
    
    /**
     * clears the motion thread
     */
    inline void clear_motion_thread(bool propagate = true)
    { set_motion_thread(0, propagate); }

    /**
     * gets the motion thread for the current motion
     */
    inline int get_motion_thread()
    { return motion_thread; }
    
    
};

}

#endif // _CPOOL_MOVEABLE_H_

