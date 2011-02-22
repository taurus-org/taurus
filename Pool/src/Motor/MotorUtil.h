//=============================================================================
//
// file :        MotorUtil.h
//
// description : Include for the MotorUtil class.
//
// project :	Sardana Device Pool
//
// $Author$
//
// $Revision$
//
// $Log$
// Revision 1.2  2007/08/17 13:07:30  tcoutinho
// - pseudo motor restructure
// - pool base dev class restructure
// - initial commit for pseudo counters
//
// Revision 1.1  2007/01/16 14:26:02  etaurel
// - First release with the PoolBaseDev base class
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

#ifndef _MOTORUTIL_H
#define _MOTORUTIL_H

#include "PoolIndBaseUtil.h"

/**
 * @author	$Author$
 * @version	$Revision$
 */

namespace Motor_ns
{

/**
 * The Motor utility class
 */
class MotorUtil : public Pool_ns::PoolIndBaseUtil
{
public:
    MotorUtil(Pool_ns::Pool *p_ptr):Pool_ns::PoolIndBaseUtil(p_ptr) {}
    virtual ~MotorUtil() {}
    
    virtual void remove_object(Tango::Device_4Impl *dev);
    virtual int32_t get_static_attr_nb(Tango::DeviceClass *);
};

}	// namespace_ns

#endif	// _CTEXPCHANNELUTIL_H
