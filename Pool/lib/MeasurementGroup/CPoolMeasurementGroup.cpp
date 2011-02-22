#include "CPool.h"
#include "CPoolMeasurementGroup.h"
#include <algorithm>

namespace Pool_ns
{

//------------------------------------------------------------------------------
// MeasurementGroupPool::update_info
//
void MeasurementGroupPool::update_info() 
{
    user_full_name = get_name() + " (" + get_full_name() + ")";
    
    if(!device_pool)
        return;
    
    user_full_name += " ExpChannel list: ";
    
    for(ElemIdVectorIt it = group_elts.begin(); it != group_elts.end(); ++it)
    {
        user_full_name += device_pool->get_element(*it)->get_name();
        if (it != group_elts.end() - 1)
            user_full_name += ", ";
    }
    
    user_full_name += " (";
    
    for(ElemIdVectorIt it = ch_ids.begin(); it != ch_ids.end(); ++it)
    {
        user_full_name += device_pool->get_element(*it)->get_name();
        if (it != ch_ids.end() - 1)
            user_full_name += ", ";
    }
    
    user_full_name += ")";
}

}
