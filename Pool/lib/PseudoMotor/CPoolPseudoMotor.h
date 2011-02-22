#pragma once

#include "CPoolSingleElement.h"

namespace Pool_ns
{

struct MotorGroupPool;

/**
 * Pseudo motor element
 */
struct PseudoMotorPool: public SinglePoolElement
{
    /** list of motor elements */
    ElemIdVector                mot_elts;

    /** extra full name data */
    std::string                 user_full_name_extra;

    /** hidden motor group id */
    ElementId                   motor_group_id;

    /**
     * Returns the type of element this object represents.
     * @see ElementType
     *
     * @return This element type
     */
    virtual ElementType get_type()
    { return PSEUDO_MOTOR_ELEM; }

    inline ElementId get_motor_group_id()
    { return motor_group_id; }

    /**
     * IPoolElementListener interface implementation. Called when an event
     * occurs.
     *
     * @param[in] evt stack of event data elements.
     */
    virtual void pool_elem_changed(PoolElemEventList &evt);

    /**
     * Determines if the given motor is a member of this group
     * @param[in] elem_id element id
     * @return <code>true</code> if the element is a member or <code>false</code>
     *         otherwise
     */
    virtual bool is_member(ElementId);

    /**
     * Returns a pointer to the list of elements in this group
     * @return the list of elements pointer
     */
    inline virtual ElemIdVector *get_elems()
    { return &mot_elts; }
    
    /**
     * updates the user full name string
     */
    virtual void update_info();
};

}

