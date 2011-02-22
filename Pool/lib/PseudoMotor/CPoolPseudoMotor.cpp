#include "CPool.h"
#include "CPoolPseudoMotor.h"
#include <algorithm>

namespace Pool_ns
{

//------------------------------------------------------------------------------
// PseudoMotorPool::update_info
//
void PseudoMotorPool::update_info() 
{
    PoolElement::update_info();
    user_full_name_extra = user_full_name + " Motor list: ";
    
    ElemIdVectorIt mot_elts_end = mot_elts.end();
    for(ElemIdVectorIt it = mot_elts.begin(); it != mot_elts_end; ++it)
    {
        ElementId id = *it;
        if (id == InvalidId)
        {
            user_full_name_extra += "<pending>";
        }
        else
        {
            user_full_name_extra += device_pool->get_element(id)->get_name();
        }
        if (it != mot_elts_end - 1)
        {
            user_full_name_extra += ", ";
        }
    }
}

//------------------------------------------------------------------------------
// PseudoMotorPool::pool_elem_changed
//
void PseudoMotorPool::pool_elem_changed(PoolElemEventList &evt_lst)
{
	PoolElementEvent *last_evt = evt_lst.back();
	PoolElementEvent new_evt(last_evt->type,this);

//
// Forward the event to the PseudoMotor tango object. He will know want to do
// with the event
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
// PseudoMotorPool::is_member
//
bool PseudoMotorPool::is_member(ElementId elem_id)
{
    return find(mot_elts.begin(), mot_elts.end(), elem_id) != mot_elts.end();
}

}
