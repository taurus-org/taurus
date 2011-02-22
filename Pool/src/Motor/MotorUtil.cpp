//=============================================================================
//
// file :        MotorUtil.cpp
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
// Revision 1.2  2007/08/17 13:07:29  tcoutinho
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

#include <Python.h>
#include <tango.h>
#include "MotorUtil.h"
#include "Motor.h"
#include "MotorClass.h"
#include "Pool.h"

namespace Motor_ns
{

void MotorUtil::remove_object(Tango::Device_4Impl *dev)
{
    pool_dev->remove_element((static_cast<Motor_ns::Motor *>(dev))->get_id());
}

int32_t MotorUtil::get_static_attr_nb(Tango::DeviceClass *cl_ptr)
{
    return (static_cast<Motor_ns::MotorClass *>(cl_ptr))->nb_static_attr;
}

}   // namespace_ns

