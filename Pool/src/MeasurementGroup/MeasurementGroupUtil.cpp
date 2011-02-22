#include "Pool.h"
#include "MeasurementGroupUtil.h"
#include "MeasurementGroup.h"
#include "MeasurementGroupClass.h"

namespace MeasurementGroup_ns
{

void MeasurementGroupUtil::remove_object(Tango::Device_4Impl *dev)
{
    pool_dev->remove_element((static_cast<MeasurementGroup_ns::MeasurementGroup *>(dev))->get_id());
}

int32_t MeasurementGroupUtil::get_static_attr_nb(Tango::DeviceClass *cl_ptr)
{
    return (static_cast<MeasurementGroup_ns::MeasurementGroupClass *>(cl_ptr))->nb_static_attr;
}

}	// namespace_ns

