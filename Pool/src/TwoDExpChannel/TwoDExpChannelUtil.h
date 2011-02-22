//=============================================================================
//
// file :        TwoDExpChannelUtil.h
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
// - We now have a first release of TwoDController
//
//
// copyleft :   CELLS/ALBA
//		Edifici Ciences Nord
//		Campus Universitari de Bellaterra
//		Universitat Autonoma de Barcelona
//		08193 Bellaterra, Barcelona, SPAIN
//
//=============================================================================

#ifndef _TWODEXPCHANNELUTIL_H
#define _TWODEXPCHANNELUTIL_H

#include "PoolIndBaseUtil.h"

/**
 * @author	$Author: tcoutinho $
 * @version	$Revision: 16 $
 */

namespace Pool_ns
{
struct PoolElement;
}

namespace TwoDExpChannel_ns
{

/**
 * The 2D Experiment Channel utility class
 */
class TwoDExpChannelUtil:public Pool_ns::PoolIndBaseUtil
{
public:
    /// Constructor
    TwoDExpChannelUtil(Pool_ns::Pool *p_ptr):Pool_ns::PoolIndBaseUtil(p_ptr) {}
    /// Destructor
    virtual ~TwoDExpChannelUtil() {}
    
    virtual void remove_object(Tango::Device_4Impl *dev);
    virtual int32_t get_static_attr_nb(Tango::DeviceClass *);
};

}	// namespace_ns

#endif	// _TWODEXPCHANNELUTIL_H
