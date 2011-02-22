#include "CPool.h"
#include "CPoolObject.h"

namespace Pool_ns
{

//------------------------------------------------------------------------------
// PoolObject::PoolObject
//
PoolObject::PoolObject():
device_pool(DevicePool::get_instance()), id(InvalidId), name("unknown")
{}

//------------------------------------------------------------------------------
// PoolObject::PoolObject
//
PoolObject::PoolObject(DevicePool *dp, ElementId identif, const std::string& n):
device_pool(dp), id(identif), name(n)
{}

//------------------------------------------------------------------------------
// PoolObject::~PoolObject
//
PoolObject::~PoolObject()
{}

}
