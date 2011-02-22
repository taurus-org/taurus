#include "CPool.h"
#include "CPoolInstrument.h"

namespace Pool_ns
{
    
InstrumentPool::InstrumentPool(DevicePool *dp, const std::string &type,
                               const std::string &full_name,
                               ElementId elem_id /*= InvalidId */):
PoolElement(dp, elem_id == InvalidId ? dp->get_new_id() : elem_id , full_name),
instrument_type(type), parent_instrument(NULL)
{
    size_t sep = full_name.rfind('/');
    std::string parent = sep == 0 ? "" : full_name.substr(0, sep);
    
    set_name(full_name);
    set_full_name(full_name);
    
    if (!parent.empty())
    {
        this->set_parent_instrument(&dp->get_instrument(parent));
    }
    
    set_user_full_name(full_name + "(" + type + ")");
}

void InstrumentPool::add_element(ElementId id)
{ 
    this->add_element(get_device_pool()->get_element(id)); 
}

void InstrumentPool::add_child(ElementId id)
{
    this->add_child(&get_device_pool()->get_instrument(id)); 
}

}
