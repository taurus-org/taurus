#include <algorithm>
#include <CPoolPseudoCounter.h>

namespace Pool_ns
{

//------------------------------------------------------------------------------
// PseudoCounterPool::update_info
//
void PseudoCounterPool::update_info() 
{
    PoolElement::update_info();
    user_full_name_extra = user_full_name + " Counter list: ";
}

//------------------------------------------------------------------------------
// PseudoCounterPool::is_member
//
bool PseudoCounterPool::is_member(ElementId elem_id)
{
    return find(ch_elts.begin(), ch_elts.end(), elem_id) != ch_elts.end();
}

//------------------------------------------------------------------------------
// PseudoCounterPool::pool_elem_changed
//
void PseudoCounterPool::pool_elem_changed(PoolElemEventList &evt_lst)
{

	PoolElementEvent *last_evt = evt_lst.back();
	PoolElementEvent new_evt(last_evt->type,this);

//
// Forward the event to the PseudoCounter tango object. He will know wat to do
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

//
// Call super method to propagate received event to all listeners
//
	PoolElement::pool_elem_changed(evt_lst);
}

}
