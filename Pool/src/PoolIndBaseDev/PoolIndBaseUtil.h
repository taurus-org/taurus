//=============================================================================
//
// file :        PoolIndBaseUtil.h
//
// description : Include for the PoolIndBaseDev class.
//
// project :	Sardana Device Pool
//
// $Author: tiagocoutinho $
//
// copyleft :   CELLS/ALBA
//		Edifici Ciences Nord
//		Campus Universitari de Bellaterra
//		Universitat Autonoma de Barcelona
//		08193 Bellaterra, Barcelona, SPAIN
//
//=============================================================================

#ifndef _POOLINDBASEUTIL_H
#define _POOLINDBASEUTIL_H

/**
 * @author	$Author: tiagocoutinho $
 * @version	$Revision: 1 $
 */
 
#include <PoolBaseUtil.h>

namespace Pool_ns
{

/**
 * The IndBase utility class
 */
class PoolIndBaseUtil : public PoolBaseUtil
{
public:
    PoolIndBaseUtil(Pool_ns::Pool *p_ptr):Pool_ns::PoolBaseUtil(p_ptr) {}
};

}

#endif // _POOLINDBASEUTIL_H
