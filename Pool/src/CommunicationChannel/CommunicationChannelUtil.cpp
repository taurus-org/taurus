//=============================================================================
//
// file :        CommunicationChannelUtil.h
//
// description : Include for the CommunicationChannelUtil class.
//
// project :	Sardana Device Pool

// copyleft :   CELLS/ALBA
//		Edifici Ciences Nord
//		Campus Universitari de Bellaterra
//		Universitat Autonoma de Barcelona
//		08193 Bellaterra, Barcelona, SPAIN
//
//=============================================================================

#include <Python.h>
#include "Pool.h"
#include "CommunicationChannelUtil.h"
#include "CommunicationChannel.h"
#include "CommunicationChannelClass.h"


namespace CommunicationChannel_ns
{

void CommunicationChannelUtil::remove_object(Tango::Device_4Impl *dev)
{
    pool_dev->remove_element((static_cast<CommunicationChannel_ns::CommunicationChannel *>(dev))->get_id());
}

int32_t CommunicationChannelUtil::get_static_attr_nb(Tango::DeviceClass *cl_ptr)
{
    return (static_cast<CommunicationChannel_ns::CommunicationChannelClass *>(cl_ptr))->nb_static_attr;
}

}	// namespace_ns

