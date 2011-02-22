#include <CPoolIORegister.h>

namespace Pool_ns
{

//------------------------------------------------------------------------------
// IORegisterPool::pool_elem_changed
//
void IORegisterPool::pool_elem_changed(PoolElemEventList &evt_lst)
{
//
// Call super method to propagate received event to all listeners
//
	PoolElement::pool_elem_changed(evt_lst);
}

}
