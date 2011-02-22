#include "CPoolMotor.h"

namespace Pool_ns
{

//------------------------------------------------------------------------------
// MotorPool::pool_elem_changed
//
void MotorPool::pool_elem_changed(PoolElemEventList &evt_lst)
{
    // nothing to be done here
    // so far a motor does not listen for events on other PoolElements because
    // it is the lowest level in the hierarchy

//
// Call super method to propagate received event to all listeners
//
    PoolElement::pool_elem_changed(evt_lst);
}

}
