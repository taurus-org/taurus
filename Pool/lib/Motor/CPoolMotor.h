#pragma once

#include "CPoolSingleElement.h"
#include "CPoolMoveable.h"

namespace Pool_ns
{ 

/**
 * The motor object
 */
struct MotorPool: public SinglePoolElement, 
                  public PoolMoveable
{
    /**
     * Returns the type of element this object represents.
     * @see ElementType
     *
     * @return This element type
     */
    inline virtual ElementType get_type()
    { return MOTOR_ELEM; }

    /**
     * IPoolElementListener interface implementation. Called when an event
     * occurs.
     *
     * @param[in] evt stack of event data elements.
     */
    virtual void pool_elem_changed(PoolElemEventList &);

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
    inline virtual void calc_move(double *src, CtrlValueMap& dest)
    {
        dest[get_ctrl_id()][get_id()] = src[0];
    }
};

}

