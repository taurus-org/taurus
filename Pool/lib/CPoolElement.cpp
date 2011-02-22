#include "CPool.h"
#include "CPoolController.h"
#include "CPoolElement.h"
#include <algorithm>

namespace Pool_ns
{
//------------------------------------------------------------------------------
// PoolElement::PoolElement
//
PoolElement::PoolElement():
    PoolObject(), axis(InvalidAxis), ctrl_id(InvalidId), instrument_id(InvalidId),
    ctrl(NULL), simulation_mode(false), helper(NULL), notif_mon(NULL), 
    ser_mon(NULL)
{
    init();
}

//------------------------------------------------------------------------------
// PoolElement::PoolElement
//
PoolElement::PoolElement(DevicePool *dp, ElementId identif, const std::string &n):
    PoolObject(dp, identif, n), axis(InvalidAxis),
    ctrl_id(InvalidId), instrument_id(InvalidId), ctrl(NULL),
    simulation_mode(false), helper(NULL), notif_mon(NULL), ser_mon(NULL)
{
    init();
}

//------------------------------------------------------------------------------
// PoolElement::~PoolElement
//
PoolElement::~PoolElement()
{
    SAFE_DELETE(ser_mon);
    SAFE_DELETE(notif_mon);
}

//------------------------------------------------------------------------------
// PoolElement::init
//
void PoolElement::init()
{
    std::string mon_name = FullElementTypeStr[get_type()];
    name += " Thread";
    notif_mon = new PoolMonitor(mon_name);
    ser_mon = new PoolMonitor(get_name());
}

//------------------------------------------------------------------------------
// PoolElement::set_ctrl_id
//
void PoolElement::set_ctrl_id(ElementId id)
{
    this->ctrl_id = id;
    this->ctrl = id != InvalidId ? &get_device_pool()->get_controller(id) : NULL;
}

//------------------------------------------------------------------------------
// PoolElement::get_controller
//
Controller *PoolElement::get_controller()
{
    ControllerPool *ctrl = get_ctrl();
    return ctrl ? ctrl->get_controller() : NULL;
}

//------------------------------------------------------------------------------
// PoolElement::update_info
//
void PoolElement::update_info()
{
    user_full_name = get_name() + " (" + get_full_name() + ")";

    ControllerPool *ctrl_ptr = get_ctrl();

    if (ctrl_ptr)
    {
        user_full_name += " (" + ctrl_ptr->get_name() + "/";
    }
    else
    {
        user_full_name += " (unknown/";
    }
    std::stringstream str;
    str << get_axis() << ") ";
    user_full_name += str.str();
    user_full_name += get_type_str();
}

//------------------------------------------------------------------------------
// PoolElement::add_pool_elem_listener
//
void PoolElement::add_pool_elem_listener(IPoolElementListener *listener)
{
    if(listener != NULL)
    {
        if(std::find(pool_elem_listeners.begin(),pool_elem_listeners.end(),listener)
                == pool_elem_listeners.end())
        {
            pool_elem_listeners.push_back(listener);
        }
    }
}

//------------------------------------------------------------------------------
// PoolElement::remove_pool_elem_listener
//
void PoolElement::remove_pool_elem_listener(IPoolElementListener *listener)
{
    if(listener != NULL)
    {
        std::list<IPoolElementListener*>::iterator it =
            std::find(pool_elem_listeners.begin(),pool_elem_listeners.end(),listener);
        if(it != pool_elem_listeners.end())
            pool_elem_listeners.erase(it);
    }
}

//------------------------------------------------------------------------------
// PoolElement::fire_pool_elem_change
//
void PoolElement::fire_pool_elem_change(PoolElementEvent *evt,
                                        IPoolElementListener *exclude /* = NULL*/, 
                                        bool handle_exceptions /* = true */)
{
    std::list<IPoolElementListener*>::iterator it = pool_elem_listeners.begin();

    PoolElemEventList evt_lst;
    evt_lst.push_back(evt);

    for(; it != pool_elem_listeners.end(); it++)
    {
        IPoolElementListener *listener = *it;

        if(listener != exclude)
        {
            try
            {
                listener->pool_elem_changed(evt_lst);
            }
            catch(...)
            {
                if (!handle_exceptions) throw;
            }
        }
    }
}

//------------------------------------------------------------------------------
// PoolElement::propagate_event
//
void PoolElement::propagate_event(PoolElemEventList &evt_lst)
{
    std::list<IPoolElementListener*>::iterator it = pool_elem_listeners.begin();

    for(; it != pool_elem_listeners.end(); it++)
    {
        // Avoid generating an event on the element that originated the events
        if(evt_lst.front()->src != (*it))
            (*it)->pool_elem_changed(evt_lst);
    }
}

//------------------------------------------------------------------------------
// PoolElement::pool_elem_changed
//
void PoolElement::pool_elem_changed(PoolElemEventList &evt_lst)
{
    propagate_event(evt_lst);
}

//------------------------------------------------------------------------------
// PoolElement::is_member
//
bool PoolElement::is_member(std::string &elt)
{
    if (!device_pool)
        return false;

    return is_member(device_pool->get_element_id(elt));
}

}
