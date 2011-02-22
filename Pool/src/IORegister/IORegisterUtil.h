//=============================================================================
//
// file :        IORegisterUtil.h
//
// description : Include for the IORegisterUtil class.
//
// project :	Sardana Device Pool
//
// copyleft :   CELLS/ALBA
//		Edifici Ciences Nord
//		Campus Universitari de Bellaterra
//		Universitat Autonoma de Barcelona
//		08193 Bellaterra, Barcelona, SPAIN
//
//=============================================================================

#ifndef _IOREGISTERUTIL_H
#define _IOREGISTERUTIL_H

#include <PoolIndBaseUtil.h>

/**
 * @author	$Author: tcoutinho $
 * @version	$Revision: 16 $
 */

/**
 * The namespace for the pool tango class
 */
namespace Pool_ns
{
	struct PoolElement;
}

namespace IORegister_ns
{

/**
 * The IORegister utility class
 */
class IORegisterUtil:public Pool_ns::PoolIndBaseUtil
{
public:
	IORegisterUtil(Pool_ns::Pool *p_ptr):Pool_ns::PoolIndBaseUtil(p_ptr) {}
	virtual ~IORegisterUtil() {}
	
	virtual void remove_object(Tango::Device_4Impl *dev);
	virtual int32_t get_static_attr_nb(Tango::DeviceClass *);
};

}	// namespace_ns

#endif	// _IOREGISTERUTIL_H
