//=============================================================================
//
// file :        OneDExpChannelUtil.cpp
//
// description : Source for the OneDExpChannelUtil class.
//
// project :	Sardana Device Pool
//
// $Author: tcoutinho $
//
// $Revision: 16 $
//
// $Log$
// Revision 1.2  2007/06/27 12:23:02  tcoutinho
// string changes for consistency sake
//
// Revision 1.1  2007/01/26 08:35:02  etaurel
// - We now have a first release of OneDController
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
#include "OneDExpChannelUtil.h"
#include "OneDExpChannel.h"
#include "OneDExpChannelClass.h"

namespace OneDExpChannel_ns
{

void OneDExpChannelUtil::remove_object(Tango::Device_4Impl *dev)
{
    pool_dev->remove_element((static_cast<OneDExpChannel_ns::OneDExpChannel *>(dev))->get_id());
}

int32_t OneDExpChannelUtil::get_static_attr_nb(Tango::DeviceClass *cl_ptr)
{
    return (static_cast<OneDExpChannel_ns::OneDExpChannelClass *>(cl_ptr))->nb_static_attr;
}

}	// namespace_ns

