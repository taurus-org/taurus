//=============================================================================
//
// file :        OneDExpChannelUtil.h
//
// description : Include for the PoolBaseDev class.
//
// project :	Sardana Device Pool
//
// $Author: tcoutinho $
//
// $Revision: 16 $
//
// $Log$
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

#ifndef _ONEDEXPCHANNELUTIL_H
#define _ONEDEXPCHANNELUTIL_H

#include "PoolIndBaseUtil.h"

/**
 * @author	$Author: tcoutinho $
 * @version	$Revision: 16 $
 */

namespace Pool_ns
{
struct PoolElement;
}

namespace OneDExpChannel_ns
{

/**
 * The 1D Experiment Channel utility class
 */
class OneDExpChannelUtil:public Pool_ns::PoolIndBaseUtil
{
public:
    /// Constructor
    OneDExpChannelUtil(Pool_ns::Pool *p_ptr):Pool_ns::PoolIndBaseUtil(p_ptr) {}
    /// Destructor
    virtual ~OneDExpChannelUtil() {}
    
    virtual void remove_object(Tango::Device_4Impl *dev);
    virtual int32_t get_static_attr_nb(Tango::DeviceClass *);
};

}	// namespace_ns

#endif	// _ONEDEXPCHANNELUTIL_H
