#include <CPoolController.h>

namespace Pool_ns
{

ControllerPool::~ControllerPool()
{
    if (ctrl != NULL) 
    {
        AutoPoolLock lo(get_ctrl_class_mon());
        SAFE_DELETE(controller);
    }
    SAFE_DELETE(cpp_ctrl_prop);
}
    
//------------------------------------------------------------------------------
// ControllerPool::pool_elem_changed
//
void ControllerPool::pool_elem_changed(PoolElemEventList &evt_lst)
{
// nothing to be done here
// so far a controller does not listen for events on other PoolElements
// because it is the lowest level in the hierarchy

//
// Call super method to propagate received event to all listeners
//
    PoolElement::pool_elem_changed(evt_lst);
}

}
