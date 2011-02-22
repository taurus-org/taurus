//=============================================================================
//
// file :        MotorUtil.cpp
//
// description : Include for the PoolBaseDev class.
//
// project :	Sardana Device Pool
//
// $Author$
//
// $Revision$
//
// $Log$
// Revision 1.2  2007/08/23 10:33:42  tcoutinho
// - basic pseudo counter check
// - some fixes regarding pseudo motors
//
// Revision 1.1  2007/08/17 13:11:25  tcoutinho
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
#include "PseudoMotorUtil.h"
#include "PseudoMotor.h"
#include "PseudoMotorClass.h"
#include "Pool.h"


namespace PseudoMotor_ns
{

    
void PseudoMotorUtil::remove_object(Tango::Device_4Impl *dev)
{
    pool_dev->remove_element((static_cast<PseudoMotor_ns::PseudoMotor *>(dev))->get_id());
}

int32_t PseudoMotorUtil::get_static_attr_nb(Tango::DeviceClass *cl_ptr)
{
    return (static_cast<PseudoMotor_ns::PseudoMotorClass *>(cl_ptr))->nb_static_attr;
}

}	// namespace_ns

