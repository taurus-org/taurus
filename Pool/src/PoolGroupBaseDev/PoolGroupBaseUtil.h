//=============================================================================
//
// file :        PoolGroupBaseUtil.h
//
// description : Include for the PoolGroupBaseDev class.
//
// project :	Sardana Device Pool
//
// $Author$
//
// $Revision$
//
// $Log$
// Revision 1.1  2007/02/03 15:19:41  tcoutinho
// new base tango group device
//
// Revision 1.1  2007/01/16 14:22:25  tcoutinho
// - Initial revision
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

#ifndef _POOLGROUPBASEUTIL_H
#define _POOLGROUPBASEUTIL_H


/**
 * @author	$Author$
 * @version	$Revision$
 */

#include "Pool.h"

namespace Pool_ns
{

class Pool;
struct PoolElement;

/**
 * The PoolGroupBase utility class
 */
class PoolGroupBaseUtil
{
public:
    PoolGroupBaseUtil(Pool *p_ptr):pool_dev(p_ptr) {}
    virtual ~PoolGroupBaseUtil() {}
    
    virtual void remove_object(Tango::Device_4Impl *) = 0;
    virtual long get_static_attr_nb(Tango::DeviceClass *) = 0;

protected:
    Pool        *pool_dev;
};

}	// namespace_ns

#endif	// _POOLGROUPBASEUTIL_H
