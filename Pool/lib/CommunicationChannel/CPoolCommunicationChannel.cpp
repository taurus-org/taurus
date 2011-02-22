#include "CPoolCommunicationChannel.h"

namespace Pool_ns
{

//------------------------------------------------------------------------------
// CommunicationChannelPool::pool_elem_changed
//
void CommunicationChannelPool::pool_elem_changed(PoolElemEventList &evt_lst)
{
//
// Call super method to propagate received event to all listeners
//
	PoolElement::pool_elem_changed(evt_lst);
}

}
