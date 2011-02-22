#ifndef _CPOOL_GROUP_ELEMENT_H_
#define _CPOOL_GROUP_ELEMENT_H_

#include <iostream>
#include <list>

#include "CPoolElement.h"

namespace Pool_ns
{

/**
 * A generic element of the Pool representing a group of elements.
 *
 */
struct PoolGroupElement: public PoolElement
{
    /** list of all USER elements */
    ElemIdVector            group_elts;

    /**
     * The default constructor
     */
    PoolGroupElement();
    
    /**
     * Constructor
     * 
     * @param dp the pool of devices to which this element will belong
     * @param identif the element ID
     * @param n the element name
     */
    PoolGroupElement(DevicePool *dp, ElementId identif, const std::string &n);
    
    /**
     * The destructor
     */
    virtual ~PoolGroupElement();
    
    /**
     * IPoolElementListener interface implementation. Called when an event
     * occurs.
     *
     * @param[in] evt stack of event data elements.
     */
    virtual void pool_elem_changed(PoolElemEventList &);

    /**
     * Determines if the given element id is a member of this group
     * @param[in] elem_id element id
     * @return <code>true</code> if the element is a member or <code>false</code>
     *         otherwise
     */
    virtual bool is_member(ElementId );

    /**
     * Determines if the given element name is a member of this group at the
     * USER level
     * @param[in] name element name
     * @return <code>true</code> if the element is a member or <code>false</code>
     *         otherwise
     */
    bool is_user_member(std::string &);

    /**
     * Determines if the given element name is a member of this group at the
     * USER level
     * @param[in] name element name
     * @param[out] pos index for the element in this motor group. If the element
     *                  is not part of the motor group, this value is undefined
     * @return <code>true</code> if the element is a member or <code>false</code>
     *         otherwise
     */
    bool is_user_member(std::string &, int32_t &);

    /**
     * Determines if the given element id is a member of this group at the
     * USER level
     * @param[in] elem_id element id
     * @return <code>true</code> if the element is a member or <code>false</code>
     *         otherwise
     */
    bool is_user_member(ElementId );

    /**
     * Determines if the given element id is a member of this group at the
     * USER level
     * @param[in] elem_id element id
     * @param[out] pos index for the element in this motor group. If the element
     *                  is not part of the motor group, this value is undefined
     * @return <code>true</code> if the element is a member or <code>false</code>
     *         otherwise
     */
    bool is_user_member(ElementId, int32_t &);

    /**
     * Determines if the given list of names matches the list of USER elements
     * of this motor group. If exact flag is true it means the order matters.
     *
     * @param[in] elems list of element ids
     * @param[in] exact_order wheater or not the order of the elements matters.
     *
     * @return <code>true</code> if the elements are members or <code>false</code>
     *         otherwise
     */
    bool matches_user_members(ElemIdVector &, bool exact_order = false);
    
    /**
     * Determines if the given list of names matches the list of USER elements
     * of this motor group. If exact flag is true it means the order matters.
     *
     * @param[in] elems list of element strings
     * @param[in] exact_order wheater or not the order of the elements matters.
     *
     * @return <code>true</code> if the elements are members or <code>false</code>
     *         otherwise
     */
    bool matches_user_members(std::vector<std::string> &, bool exact_order = false);

    /**
     * Returns a pointer to the list of elements in this group
     * @return the list of elements pointer
     */
    inline virtual ElemIdVector *get_elems()
    { return &group_elts; }
};

}

#endif
