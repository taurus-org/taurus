//=============================================================================
//
// file :        CTExpChannelUtil.h
//
// description : Include for the PoolBaseUtil class.
//
// project :	Sardana Device Pool
//
// $Author$
//
// $Revision$
//
// $Log$
// Revision 1.3  2007/08/17 13:07:29  tcoutinho
// - pseudo motor restructure
// - pool base dev class restructure
// - initial commit for pseudo counters
//
// Revision 1.2  2007/06/27 12:23:02  tcoutinho
// string changes for consistency sake
//
// Revision 1.1  2007/01/16 14:23:19  etaurel
// - First release with Counter Timer
//
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
#include "CTExpChannelUtil.h"
#include "CTExpChannel.h"
#include "CTExpChannelClass.h"

namespace CTExpChannel_ns
{

void CTExpChannelUtil::remove_object(Tango::Device_4Impl *dev)
{
    pool_dev->remove_element((static_cast<CTExpChannel_ns::CTExpChannel *>(dev))->get_id());
}

int32_t CTExpChannelUtil::get_static_attr_nb(Tango::DeviceClass *cl_ptr)
{
    return (static_cast<CTExpChannel_ns::CTExpChannelClass *>(cl_ptr))->nb_static_attr;
}

}	// namespace_ns

