#include "CPool.h"
#include "CPoolDefs.h"
#include "CPoolGroupElement.h"
#include <algorithm>

namespace Pool_ns
{

//------------------------------------------------------------------------------
// PoolGroupElement::PoolGroupElement
//
PoolGroupElement::PoolGroupElement(): PoolElement()
{}

//------------------------------------------------------------------------------
// PoolGroupElement::PoolGroupElement
//
PoolGroupElement::PoolGroupElement(DevicePool *dp, ElementId identif, const std::string &n):
    PoolElement(dp, identif, n)
{}

//------------------------------------------------------------------------------
// PoolGroupElement::~PoolGroupElement
//
PoolGroupElement::~PoolGroupElement()
{}

//------------------------------------------------------------------------------
// PoolGroupElement::pool_elem_changed
//
void PoolGroupElement::pool_elem_changed(PoolElemEventList &evt_lst)
{
    if(pool_elem_listeners.size() == 0)
        return;

    PoolElementEvent *last_evt = evt_lst.back();
    PoolElementEvent new_evt(last_evt->type,this);

//
// Forward the event to the MeasurementGroup tango object. He will know want to
// do with the event
//
    helper->pool_elem_changed(evt_lst,new_evt);

    evt_lst.push_back(&new_evt);

//
// Call super method to propagate received event to all listeners
//
    PoolElement::pool_elem_changed(evt_lst);

//
// Remove the evt object created by this element from the event list
//
    evt_lst.pop_back();
}

//------------------------------------------------------------------------------
// PoolGroupElement::is_user_member
//
bool PoolGroupElement::is_user_member(std::string &name)
{
    int32_t pos;
    return is_user_member(name, pos);
}

//------------------------------------------------------------------------------
// PoolGroupElement::is_user_member
//
bool PoolGroupElement::is_user_member(std::string &name, int32_t &pos)
{
    return is_user_member(device_pool->get_element(name)->get_id(), pos);
}

//------------------------------------------------------------------------------
// PoolGroupElement::is_user_member
//
bool PoolGroupElement::is_user_member(ElementId elem_id)
{
    int32_t pos = -1;
    return is_user_member(elem_id, pos);
}

//------------------------------------------------------------------------------
// PoolGroupElement::is_user_member
//
bool PoolGroupElement::is_user_member(ElementId elem_id, int32_t &pos)
{
    ElemIdVectorIt it = find(group_elts.begin(), group_elts.end(), elem_id);
    if (it == group_elts.end())
        return false;
    
    pos = (int32_t)distance(group_elts.begin(), it);
    return true;
}

//------------------------------------------------------------------------------
// PoolGroupElement::matches_user_members
//
bool PoolGroupElement::matches_user_members(std::vector<std::string> &elems, 
                                            bool exact_order /* = false */)
{
    std::vector<string>::size_type elems_len = elems.size();
    
    if (group_elts.size() != elems_len)
        return false;

    ElemIdVector elem_ids;
    for(std::vector<std::string>::iterator it = elems.begin(); it != elems.end(); ++it)
        elem_ids.push_back(device_pool->get_element_id(*it));
    return matches_user_members(elem_ids, exact_order);
}

//------------------------------------------------------------------------------
// PoolGroupElement::matches_user_members
//
bool PoolGroupElement::matches_user_members(ElemIdVector &elems,
                                            bool exact_order /* = false */)
{
    if (exact_order)
        return elems == group_elts;

    std::vector<string>::size_type elems_len = elems.size();
    
    if (group_elts.size() != elems_len)
        return false;

    for(ElemIdVector::size_type l = 0; l < elems_len; ++l)
    {
        ElementId elem_id = elems[l];
        if (!is_user_member(elem_id))
            return false;
    }
    return true;
}

//------------------------------------------------------------------------------
// PoolGroupElement::is_member
//
bool PoolGroupElement::is_member(ElementId elem_id)
{
    return is_user_member(elem_id);
}

}
