//=============================================================================
//
// file :        ZeroDExpChannelUtil.cpp
//
// description : Source for the ZeroDExpChannelUtil class.
//
// project :	Sardana Device Pool
//
// $Author$
//
// $Revision$
//
// $Log$
// Revision 1.2  2007/06/27 12:23:02  tcoutinho
// string changes for consistency sake
//
// Revision 1.1  2007/01/26 08:35:02  etaurel
// - We now have a first release of ZeroDController
//
//
// copyleft :   CELLS/ALBA
//		Edifici Ciences Nord
//		Campus Universitari de Bellaterra
//		Universitat Autonoma de Barcelona
//		08193 Bellaterra, Barcelona, SPAIN
//
//=============================================================================

#include <Python.h>
#include "Pool.h"
#include "ZeroDExpChannelUtil.h"
#include "ZeroDExpChannel.h"
#include "ZeroDExpChannelClass.h"

namespace ZeroDExpChannel_ns
{

void ZeroDExpChannelUtil::remove_object(Tango::Device_4Impl *dev)
{
    pool_dev->remove_element((static_cast<ZeroDExpChannel_ns::ZeroDExpChannel *>(dev))->get_id());
}

int32_t ZeroDExpChannelUtil::get_static_attr_nb(Tango::DeviceClass *cl_ptr)
{
    return (static_cast<ZeroDExpChannel_ns::ZeroDExpChannelClass *>(cl_ptr))->nb_static_attr;
}

}	// namespace_ns

