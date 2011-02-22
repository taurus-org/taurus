#include <CPoolTwoDExpChannel.h>

namespace Pool_ns
{

//------------------------------------------------------------------------------
// OneDExpChannelPool::pool_elem_changed
//
void TwoDExpChannelPool::pool_elem_changed(PoolElemEventList &evt_lst)
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
