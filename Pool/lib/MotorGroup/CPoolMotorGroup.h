#ifndef _CPOOL_MOTORGROUP_H_
#define _CPOOL_MOTORGROUP_H_

#include "CPoolGroupElement.h"
#include "CPoolMoveable.h"

namespace Pool_ns
{

struct MotorPool;
struct PseudoMotorPool;

/**
 * Motor group element
 */
struct MotorGroupPool: public PoolGroupElement,
                       public PoolMoveable
{
    /** list of motor ids */
    ElemIdVector            mot_ids;

    /** list of USER motors */
    ElemIdVector            mot_elts;

    /** list of USER pseudo motors */
    ElemIdVector            pm_elts;

    /** list of USER motor groups */
    ElemIdVector            mg_elts;

    /**
     * Returns the type of element this object represents.
     * @see ElementType
     *
     * @return This element type
     */
    inline virtual ElementType get_type()
    { return MOTOR_GROUP_ELEM; }

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
    virtual void calc_move(double *src, CtrlValueMap& dest);

    /**
     * Returns the number of values this moveable receives as input to a 
     * calc_move.
     *
     * @return the number of values this moveable receives as input to a 
     *         calc_move
     */
    virtual int32_t get_size();

    /**
     * updates the user full name string
     */
    virtual void update_info();

    /**
     * Determines if the given element id is part of this element. 
     *
     * @param[in] elem_id the element id to be checked.
     *
     * @return <code>true</code> if the given element is part of this element
     *         or <code>false</code> otherwise
     */
    virtual bool is_member(ElementId );
};

} 

#endif // _CPOOL_MOTORGROUP_H_
