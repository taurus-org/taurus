#include "Pool.h"
#include "MotorGroupUtil.h"
#include "MotorGroup.h"
#include "MotorGroupClass.h"

namespace MotorGroup_ns
{
    
void MotorGroupUtil::remove_object(Tango::Device_4Impl *dev)
{
    pool_dev->remove_element((static_cast<MotorGroup_ns::MotorGroup *>(dev))->get_id());
}

int32_t MotorGroupUtil::get_static_attr_nb(Tango::DeviceClass *cl_ptr)
{
    // So far there are no dynamic attributes for the motor group
    // So the three static attributes are: State, Status, Position
    return 3;
}

}	// namespace_ns
