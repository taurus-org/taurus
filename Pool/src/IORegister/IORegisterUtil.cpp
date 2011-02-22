//=============================================================================
//
// file :        IORegisterUtil.h
//
// description : Include for the IORegisterUtil class.
//
// project :	Sardana Device Pool

// copyleft :   CELLS/ALBA
//		Edifici Ciences Nord
//		Campus Universitari de Bellaterra
//		Universitat Autonoma de Barcelona
//		08193 Bellaterra, Barcelona, SPAIN
//
//=============================================================================

#include <Python.h>
#include <Pool.h>
#include <IORegisterUtil.h>
#include <IORegister.h>
#include <IORegisterClass.h>


namespace IORegister_ns
{

    
void IORegisterUtil::remove_object(Tango::Device_4Impl *dev)
{
    pool_dev->remove_element((static_cast<IORegister_ns::IORegister *>(dev))->get_id());
}

int32_t IORegisterUtil::get_static_attr_nb(Tango::DeviceClass *cl_ptr)
{
    return (static_cast<IORegister_ns::IORegisterClass *>(cl_ptr))->nb_static_attr;
}

}	// namespace_ns

