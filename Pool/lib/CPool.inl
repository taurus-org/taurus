#include <CPoolController.h>
#include <CPoolMoveable.h>
#include <CPoolMotor.h>
#include <CPool.h>
#include <CPoolPseudoMotor.h>
#include <CPoolMotorGroup.h>
#include <CPoolCTExpChannel.h>
#include <CPoolZeroDExpChannel.h>
#include <CPoolOneDExpChannel.h>
#include <CPoolTwoDExpChannel.h>
#include <CPoolPseudoCounter.h>
#include <CPoolMeasurementGroup.h>
#include <CPoolIORegister.h>
#include <CPoolCommunicationChannel.h>
//#include <CPoolConstraint.h>
#include <CPoolInstrument.h>

namespace Pool_ns
{

//------------------------------------------------------------------------------
// DevicePool::get_new_id
//
inline ElementId DevicePool::get_new_id() 
{ 
    return ++last_id; 
}

//------------------------------------------------------------------------------
// DevicePool::get_last_assigned_id
//
inline ElementId DevicePool::get_last_assigned_id() 
{ 
    return last_id; 
}

//------------------------------------------------------------------------------
// DevicePool::reserve_id
//
inline void DevicePool::reserve_id(ElementId id)
{ 
    if (id > last_id) last_id = id; 
}

//------------------------------------------------------------------------------
// DevicePool::get_new_internal_id
//
inline ElementId DevicePool::get_new_internal_id() 
{ 
    return ++last_internal_id; 
}

//------------------------------------------------------------------------------
// DevicePool::get_last_assigned_internal_id
//
inline ElementId DevicePool::get_last_assigned_internal_id() 
{ 
    return last_internal_id; 
}

//------------------------------------------------------------------------------
// DevicePool::reserve_internal_id
//
inline void DevicePool::reserve_internal_id(ElementId id)
{ 
    if (id > last_internal_id) last_internal_id = id; 
}

//------------------------------------------------------------------------------
// DevicePool::get_new_ghost_id
//
inline ElementId DevicePool::get_new_ghost_id() 
{ 
    return --last_ghost_id; 
}

//------------------------------------------------------------------------------
// DevicePool::get_last_assigned_ghost_id
//
inline ElementId DevicePool::get_last_assigned_ghost_id() 
{ 
    return last_ghost_id; 
}

//------------------------------------------------------------------------------
// DevicePool::reserve_ghost_id
//
inline void DevicePool::reserve_ghost_id(ElementId id)
{ 
    if (id < last_ghost_id) last_ghost_id = id; 
}

//------------------------------------------------------------------------------
// DevicePool::get_version_str
//
inline const std::string &DevicePool::get_version_str()
{
    return pool_version_str;
}

//------------------------------------------------------------------------------
// DevicePool::get_version_nb
//
inline int32_t DevicePool::get_version_nb()
{
    return pool_version_nb;
}

//------------------------------------------------------------------------------
// DevicePool::get_controller
//
inline ControllerPool &DevicePool::get_controller(ElementId id)
{
    return *static_cast<ControllerPool *>(get_element(id, CTRL_ELEM));
}

//------------------------------------------------------------------------------
// DevicePool::get_controller
//
inline ControllerPool &DevicePool::get_controller(PoolElement &element)
{
    return get_controller(element.get_ctrl_id());
}

//------------------------------------------------------------------------------
// DevicePool::get_controller_from_element
//
inline ControllerPool &DevicePool::get_controller_from_element(ElementId id)
{
    return get_controller(*get_element(id));
}

//------------------------------------------------------------------------------
// DevicePool::get_physical_motor
//
inline MotorPool &DevicePool::get_physical_motor(ElementId id)
{
    return *static_cast<MotorPool *>(get_element(id, MOTOR_ELEM));
}

//------------------------------------------------------------------------------
// DevicePool::get_pseudo_motor
//
inline PseudoMotorPool &DevicePool::get_pseudo_motor(ElementId id)
{
    return *static_cast<PseudoMotorPool *>(get_element(id, PSEUDO_MOTOR_ELEM));
}

//------------------------------------------------------------------------------
// DevicePool::get_motor
//
inline PoolElement &DevicePool::get_motor(ElementId id)
{
    PoolElement *ret = get_element(id);
    ElementType type = ret->get_type();
    if(!IS_MOTOR(type))
    {
        std::ostringstream o;
        o << "No motor with ID '" << id << "' found."
          << " A " << ElementTypeStr[type] << " named '" << ret->name
          << "' was found instead" << std::ends;
        thrower->throw_exception("DevicePool_WrongElementType", o.str(),
                                 "DevicePool::get_motor");
    }
    return *ret;
}

//------------------------------------------------------------------------------
// DevicePool::get_motor_group
//
inline MotorGroupPool &DevicePool::get_motor_group(ElementId id)
{
    return *static_cast<MotorGroupPool *>(get_element(id, MOTOR_GROUP_ELEM));
}

//------------------------------------------------------------------------------
// DevicePool::get_countertimer
//
inline CTExpChannelPool &DevicePool::get_countertimer(ElementId id)
{
    return *static_cast<CTExpChannelPool *>(get_element(id, COTI_ELEM));
}

//------------------------------------------------------------------------------
// DevicePool::get_zerod
//
inline ZeroDExpChannelPool &DevicePool::get_zerod(ElementId id)
{
    return *static_cast<ZeroDExpChannelPool *>(get_element(id, ZEROD_ELEM));
}

//------------------------------------------------------------------------------
// DevicePool::get_oned
//
inline OneDExpChannelPool &DevicePool::get_oned(ElementId id)
{
    return *static_cast<OneDExpChannelPool *>(get_element(id, ONED_ELEM));
}

//------------------------------------------------------------------------------
// DevicePool::get_twod
//
inline TwoDExpChannelPool &DevicePool::get_twod(ElementId id)
{
    return *static_cast<TwoDExpChannelPool *>(get_element(id, TWOD_ELEM));
}

//------------------------------------------------------------------------------
// DevicePool::get_pseudo_counter
//
inline PseudoCounterPool &DevicePool::get_pseudo_counter(ElementId id)
{
    return *static_cast<PseudoCounterPool *>(get_element(id, PSEUDO_COUNTER_ELEM));
}

//------------------------------------------------------------------------------
// DevicePool::get_experiment_channel
//
inline PoolElement &DevicePool::get_experiment_channel(ElementId id)
{
    PoolElement *ret = get_element(id);
    ElementType type = ret->get_type();
    if(!IS_EXPERIMENT_CHANNEL(type))
    {
        std::ostringstream o;
        o << "No experiment channel with ID '" << id << "' found."
          << " A " << ElementTypeStr[type] << " named '" << ret->name
          << "' was found instead" << std::ends;
        thrower->throw_exception("DevicePool_WrongElementType", o.str(),
                                 "DevicePool::get_experiment_channel");
    }
    return *ret;
}

//------------------------------------------------------------------------------
// DevicePool::get_measurement_group
//
inline MeasurementGroupPool &DevicePool::get_measurement_group(ElementId id)
{
    return *static_cast<MeasurementGroupPool *>(get_element(id, MEASUREMENT_GROUP_ELEM));
}

//------------------------------------------------------------------------------
// DevicePool::get_communication_channel
//
inline CommunicationChannelPool &DevicePool::get_communication_channel(ElementId id)
{
    return *static_cast<CommunicationChannelPool *>(get_element(id, COM_ELEM));
}

//------------------------------------------------------------------------------
// DevicePool::get_ioregister
//
inline IORegisterPool &DevicePool::get_ioregister(ElementId id)
{
    return *static_cast<IORegisterPool *>(get_element(id, IOREGISTER_ELEM));
}

//------------------------------------------------------------------------------
// DevicePool::get_instrument
//
inline InstrumentPool &DevicePool::get_instrument(ElementId id)
{
    return *static_cast<InstrumentPool *>(get_element(id, INSTRUMENT_ELEM));
}

/*
//------------------------------------------------------------------------------
// DevicePool::get_constraint
//
inline ConstraintPool &DevicePool::get_constraint(ElementId id)
{
    return *static_cast<ConstraintPool *>(get(id, CONSTRAINT_ELEM));
}
*/

//------------------------------------------------------------------------------
// DevicePool::get_physical_element
//
inline PoolElement &DevicePool::get_physical_element(ElementId id)
{
    PoolElement *ret = get_element(id);
    ElementType type = ret->get_type();
    if(!IS_PHYSICAL(type))
    {
        std::ostringstream o;
        o << "No physical element with ID '" << id << "' found."
          << " A " << ElementTypeStr[type] << " named '" << ret->name
          << "' was found instead" << std::ends;
        thrower->throw_exception("DevicePool_WrongElementType", o.str(),
                                 "DevicePool::get_physical_element");
    }
    return *ret;
}

//------------------------------------------------------------------------------
// DevicePool::get_pseudo_element
//
inline PoolElement &DevicePool::get_pseudo_element(ElementId id)
{
    PoolElement *ret = get_element(id);
    ElementType type = ret->get_type();
    if(!IS_PSEUDO(type))
    {
        std::ostringstream o;
        o << "No pseudo element with ID '" << id << "' found."
          << " A " << ElementTypeStr[type] << " named '" << ret->name
          << "' was found instead" << std::ends;
        thrower->throw_exception("DevicePool_WrongElementType", o.str(),
                                 "DevicePool::get_pseudo_element");
    }
    return *ret;
}

//------------------------------------------------------------------------------
// DevicePool::get_group_element
//
inline PoolElement &DevicePool::get_group_element(ElementId id)
{
    PoolElement *ret = get_element(id);
    ElementType type = ret->get_type();
    if(!IS_GROUP(type))
    {
        std::ostringstream o;
        o << "No group with ID '" << id << "' found."
          << " A " << ElementTypeStr[type] << " named '" << ret->name
          << "' was found instead" << std::ends;
        thrower->throw_exception("DevicePool_WrongElementType", o.str(),
                                 "DevicePool::get_group_element");
    }
    return *ret;
}

//------------------------------------------------------------------------------
// DevicePool::get_moveable
//
inline PoolMoveable &DevicePool::get_moveable(ElementId id)
{
    PoolElement *ret = get_element(id);
    ElementType type = ret->get_type();
    if(!IS_MOVEABLE(type))
    {
        std::ostringstream o;
        o << "No moveable element with ID '" << id << "' found."
          << " A " << ElementTypeStr[type] << " named '" << ret->name
          << "' was found instead" << std::ends;
        thrower->throw_exception("DevicePool_WrongElementType", o.str(),
                                 "DevicePool::get_moveable");
    }
    return *((PoolMoveable*)ret);
}

//------------------------------------------------------------------------------
// DevicePool::get_controller
//
inline ControllerPool &DevicePool::get_controller(const std::string &name,
                                                  bool any_name /* = false */)
{
    PoolElement *pe = NULL;
    try
    {
        pe = get_element(name, CTRL_ELEM, any_name);
    }
    catch(...)
    {
        if(!any_name) throw;
        pe = &_get_controller_from_inst_name(name);
    }
    return *static_cast<ControllerPool *>(pe);
}

//------------------------------------------------------------------------------
// DevicePool::get_physical_motor
//
inline MotorPool &DevicePool::get_physical_motor(const std::string &name,
                                                 bool any_name /* = false */)
{
    return *static_cast<MotorPool *>(get_element(name, MOTOR_ELEM, any_name));
}

//------------------------------------------------------------------------------
// DevicePool::get_pseudo_motor
//
inline PseudoMotorPool &DevicePool::get_pseudo_motor(const std::string &name,
                                                 bool any_name /* = false */)
{
    return *static_cast<PseudoMotorPool *>(get_element(name, PSEUDO_MOTOR_ELEM, any_name));
}

//------------------------------------------------------------------------------
// DevicePool::get_motor
//
inline PoolElement &DevicePool::get_motor(const std::string &name,
                                          bool any_name /* = false */)
{
    PoolElement *ret = get_element(name, any_name);
    ElementType type = ret->get_type();
    if(!IS_MOTOR(type))
    {
        std::ostringstream o;
        o << "No motor with name '" << name << "' found."
          << " A " << ElementTypeStr[type] << " with the same name" 
          << " was found instead" << std::ends;
        thrower->throw_exception("DevicePool_WrongElementType", o.str(),
                                 "DevicePool::get_experiment_channel");
    }
    return *ret;
}

//------------------------------------------------------------------------------
// DevicePool::get_motor_group
//
inline MotorGroupPool &DevicePool::get_motor_group(const std::string &name,
                                                   bool any_name /* = false */)
{
    return *static_cast<MotorGroupPool *>(get_element(name, MOTOR_GROUP_ELEM, any_name));
}

//------------------------------------------------------------------------------
// DevicePool::get_countertimer
//
inline CTExpChannelPool &DevicePool::get_countertimer(const std::string &name,
                                                      bool any_name /* = false */)
{
    return *static_cast<CTExpChannelPool *>(get_element(name, COTI_ELEM, any_name));
}

//------------------------------------------------------------------------------
// DevicePool::get_zerod
//
inline ZeroDExpChannelPool &DevicePool::get_zerod(const std::string &name,
                                                  bool any_name /* = false */)
{
    return *static_cast<ZeroDExpChannelPool *>(get_element(name, ZEROD_ELEM, any_name));
}

//------------------------------------------------------------------------------
// DevicePool::get_oned
//
inline OneDExpChannelPool &DevicePool::get_oned(const std::string &name,
                                                bool any_name /* = false */)
{
    return *static_cast<OneDExpChannelPool *>(get_element(name, ONED_ELEM, any_name));
}

//------------------------------------------------------------------------------
// DevicePool::get_twod
//
inline TwoDExpChannelPool &DevicePool::get_twod(const std::string &name,
                                                bool any_name /* = false */)
{
    return *static_cast<TwoDExpChannelPool *>(get_element(name, TWOD_ELEM, any_name));
}

//------------------------------------------------------------------------------
// DevicePool::get_pseudo_counter
//
inline PseudoCounterPool &DevicePool::get_pseudo_counter(const std::string &name,
                                                         bool any_name /* = false */)
{
    return *static_cast<PseudoCounterPool *>(get_element(name, PSEUDO_COUNTER_ELEM, any_name));
}

//------------------------------------------------------------------------------
// DevicePool::get_experiment_channel
//
inline PoolElement &
DevicePool::get_experiment_channel(const std::string &name, 
                                   bool any_name /* = false */)
{
    PoolElement *ret = get_element(name, any_name);
    ElementType type = ret->get_type();
    if(!IS_EXPERIMENT_CHANNEL(type))
    {
        std::ostringstream o;
        o << "No experiment channel with name '" << name << "' found."
          << " A " << ElementTypeStr[type] << " with the same name" 
          << " was found instead" << std::ends;
        thrower->throw_exception("DevicePool_WrongElementType", o.str(),
                                 "DevicePool::get_experiment_channel");
    }
    return *ret;
}

//------------------------------------------------------------------------------
// DevicePool::get_group_element
//
inline PoolElement &
DevicePool::get_group_element(const std::string &name, bool any_name /* = false */)
{
    PoolElement *ret = get_element(name, any_name);
    ElementType type = ret->get_type();
    if(!IS_GROUP(type))
    {
        std::ostringstream o;
        o << "No group with name '" << name << "' found."
          << " A " << ElementTypeStr[type] << " with the same name" 
          << " was found instead" << std::ends;
        thrower->throw_exception("DevicePool_WrongElementType", o.str(),
                                 "DevicePool::get_group_element");
    }
    return *ret;
}

//------------------------------------------------------------------------------
// DevicePool::get_measurement_group
//
inline MeasurementGroupPool &
DevicePool::get_measurement_group(const std::string &name, bool any_name /* = false */)
{
    return *static_cast<MeasurementGroupPool *>(get_element(name, MEASUREMENT_GROUP_ELEM, any_name));
}

//------------------------------------------------------------------------------
// DevicePool::get_communication_channel
//
inline CommunicationChannelPool &
DevicePool::get_communication_channel(const std::string &name, bool any_name /* = false */)
{
    return *static_cast<CommunicationChannelPool *>(get_element(name, COM_ELEM, any_name));
}

//------------------------------------------------------------------------------
// DevicePool::get_ioregister
//
inline IORegisterPool &DevicePool::get_ioregister(const std::string &name,
                                                  bool any_name /* = false */)
{
    return *static_cast<IORegisterPool *>(get_element(name, IOREGISTER_ELEM, any_name));
}

//------------------------------------------------------------------------------
// DevicePool::get_instrument
//
inline InstrumentPool &DevicePool::get_instrument(const std::string &name,
                                                  bool any_name /* = false */)
{
    return *static_cast<InstrumentPool *>(get_element(name, INSTRUMENT_ELEM, any_name));
}

/*
//------------------------------------------------------------------------------
// DevicePool::get_constraint
//
inline ConstraintPool &DevicePool::get_constraint(const std::string &name,
                                                  bool any_name)
{
    return *static_cast<Pool *>(get(name, CONSTRAINT_ELEM, any_name));
}
*/

//------------------------------------------------------------------------------
// DevicePool::get_physical_element
//
inline PoolElement &DevicePool::get_physical_element(const std::string &name, bool any_name /* = false */)
{
    PoolElement *ret = get_element(name, any_name);
    ElementType type = ret->get_type();
    if(!IS_PHYSICAL(type))
    {
        std::ostringstream o;
        o << "No physical element with name '" << name << "' found."
          << " A " << ElementTypeStr[type] << " with the same name" 
          << " was found instead" << std::ends;
        thrower->throw_exception("DevicePool_WrongElementType", o.str(),
                                 "DevicePool::get_physical_element");
    }
    return *ret;
}

//------------------------------------------------------------------------------
// DevicePool::get_pseudo_element
//
inline PoolElement &
DevicePool::get_pseudo_element(const std::string &name, bool any_name /* = false */)
{
    PoolElement *ret = get_element(name, any_name);
    ElementType type = ret->get_type();
    if(!IS_PSEUDO(type))
    {
        std::ostringstream o;
        o << "No pseudo element with name '" << name << "' found."
          << " A " << ElementTypeStr[type] << " with the same name" 
          << " was found instead" << std::ends;
        thrower->throw_exception("DevicePool_WrongElementType", o.str(),
                                 "DevicePool::get_pseudo_element");
    }
    return *ret;
}

//------------------------------------------------------------------------------
// DevicePool::get_moveable
//
inline PoolMoveable &
DevicePool::get_moveable(const std::string &name, bool any_name /* = false */)
{
    PoolElement *ret = get_element(name, any_name);
    ElementType type = ret->get_type();
    if(!IS_MOVEABLE(type))
    {
        std::ostringstream o;
        o << "No moveable with name '" << name << "' found."
          << " A " << ElementTypeStr[type] << " with the same name" 
          << " was found instead" << std::ends;
        thrower->throw_exception("DevicePool_WrongElementType", o.str(),
                                 "DevicePool::get_moveable");
    }
    return *((PoolMoveable*)ret);
}

//------------------------------------------------------------------------------
// DevicePool::get_controllers
//
inline void DevicePool::get_controllers(std::vector<ElementId> &res)
{
    PoolElementTypeIt beg, end, it;
    get_all_controller(beg, end);
    for(it = beg; it != end; ++it) 
        res.push_back(it->second);
}

//------------------------------------------------------------------------------
// DevicePool::get_controllers
//
inline void DevicePool::get_controllers(std::vector<ControllerPool *> &res)
{
    PoolElementTypeIt beg, end, it;
    get_all_controller(beg, end);
    for(it = beg; it != end; ++it) 
        res.push_back(&get_controller(it->second));
}

//------------------------------------------------------------------------------
// DevicePool::get_controllers
//
inline void DevicePool::get_controllers(std::vector<std::string> &res)
{
    PoolElementTypeIt beg, end, it;
    get_all_controller(beg, end);
    for(it = beg; it != end; ++it) 
        res.push_back(get_physical_motor(it->second).name);
}

//------------------------------------------------------------------------------
// DevicePool::get_physical_motors
//
inline void DevicePool::get_physical_motors(std::vector<ElementId> &res)
{
    PoolElementTypeIt beg, end, it;
    get_all_physical_motor(beg, end);
    for(it = beg; it != end; ++it) 
        res.push_back(it->second);
}

//------------------------------------------------------------------------------
// DevicePool::get_physical_motors
//
inline void DevicePool::get_physical_motors(std::vector<MotorPool *> &res)
{
    PoolElementTypeIt beg, end, it;
    get_all_physical_motor(beg, end);
    for(it = beg; it != end; ++it) 
        res.push_back(&get_physical_motor(it->second));
}

//------------------------------------------------------------------------------
// DevicePool::get_physical_motors
//
inline void DevicePool::get_physical_motors(std::vector<std::string> &res)
{
    PoolElementTypeIt beg, end, it;
    get_all_physical_motor(beg, end);
    for(it = beg; it != end; ++it) 
        res.push_back(get_physical_motor(it->second).name);
}

//------------------------------------------------------------------------------
// DevicePool::get_all_controller
//
inline void DevicePool::get_all_controller(PoolElementTypeIt &beg, PoolElementTypeIt &end)
{
    get_all_elements(CTRL_ELEM, beg, end);
}

//------------------------------------------------------------------------------
// DevicePool::get_all_physical_motor
//
inline void DevicePool::get_all_physical_motor(PoolElementTypeIt &beg, PoolElementTypeIt &end)
{
    get_all_elements(MOTOR_ELEM, beg, end);
} 

//------------------------------------------------------------------------------
// DevicePool::get_all_pseudo_motor
//
inline void DevicePool::get_all_pseudo_motor(PoolElementTypeIt &beg, PoolElementTypeIt &end)
{
    get_all_elements(PSEUDO_MOTOR_ELEM, beg, end);
}

//------------------------------------------------------------------------------
// DevicePool::get_all_motor_group
//
inline void DevicePool::get_all_motor_group(PoolElementTypeIt &beg, PoolElementTypeIt &end)
{
    get_all_elements(MOTOR_GROUP_ELEM, beg, end);
}

//------------------------------------------------------------------------------
// DevicePool::get_all_countertimer
//
inline void DevicePool::get_all_countertimer(PoolElementTypeIt &beg, PoolElementTypeIt &end)
{
    get_all_elements(COTI_ELEM, beg, end);
}

//------------------------------------------------------------------------------
// DevicePool::get_all_zerod
//
inline void DevicePool::get_all_zerod(PoolElementTypeIt &beg, PoolElementTypeIt &end)
{
    get_all_elements(ZEROD_ELEM, beg, end);
}

//------------------------------------------------------------------------------
// DevicePool::get_all_oned
//
inline void DevicePool::get_all_oned(PoolElementTypeIt &beg, PoolElementTypeIt &end)
{
    get_all_elements(ONED_ELEM, beg, end);
}

//------------------------------------------------------------------------------
// DevicePool::get_all_twod
//
inline void DevicePool::get_all_twod(PoolElementTypeIt &beg, PoolElementTypeIt &end)
{
    get_all_elements(TWOD_ELEM, beg, end);
}

//------------------------------------------------------------------------------
// DevicePool::get_all_pseudo_counter
//
inline void DevicePool::get_all_pseudo_counter(PoolElementTypeIt &beg, PoolElementTypeIt &end)
{
    get_all_elements(PSEUDO_COUNTER_ELEM, beg, end);
}

//------------------------------------------------------------------------------
// DevicePool::get_all_measurement_group
//
inline void DevicePool::get_all_measurement_group(PoolElementTypeIt &beg, PoolElementTypeIt &end)
{
    get_all_elements(MEASUREMENT_GROUP_ELEM, beg, end);
}

//------------------------------------------------------------------------------
// DevicePool::get_all_communication_channel
//
inline void DevicePool::get_all_communication_channel(PoolElementTypeIt &beg, PoolElementTypeIt &end)
{
    get_all_elements(COM_ELEM, beg, end);
}

//------------------------------------------------------------------------------
// DevicePool::get_all_ioregister
//
inline void DevicePool::get_all_ioregister(PoolElementTypeIt &beg, PoolElementTypeIt &end)
{
    get_all_elements(IOREGISTER_ELEM, beg, end);
}

//------------------------------------------------------------------------------
// DevicePool::get_all_instrument
//
inline void DevicePool::get_all_instrument(PoolElementTypeIt &beg, PoolElementTypeIt &end)
{
    get_all_elements(INSTRUMENT_ELEM, beg, end);
}

/*
//------------------------------------------------------------------------------
// DevicePool::get_all_constraint
//
inline void DevicePool::get_all_constraint(PoolElementTypeIt &beg, PoolElementTypeIt &)
{
    return get_all(CONSTRAINT_ELEM, beg, end);
}
*/

//------------------------------------------------------------------------------
// DevicePool::get_controller_nb
//
inline int32_t DevicePool::get_controller_nb()
{
    return get_element_nb(CTRL_ELEM);
}

//------------------------------------------------------------------------------
// DevicePool::get_motor_nb
//
inline int32_t DevicePool::get_motor_nb()
{
    return get_physical_motor_nb() + get_pseudo_motor_nb();
}

//------------------------------------------------------------------------------
// DevicePool::get_physical_motor_nb
//
inline int32_t DevicePool::get_physical_motor_nb()
{
    return get_element_nb(MOTOR_ELEM);
}

//------------------------------------------------------------------------------
// DevicePool::get_pseudo_motor_nb
//
inline int32_t DevicePool::get_pseudo_motor_nb()
{
    return get_element_nb(PSEUDO_MOTOR_ELEM);
}

//------------------------------------------------------------------------------
// DevicePool::get_motor_group_nb
//
inline int32_t DevicePool::get_motor_group_nb()
{
    return get_element_nb(MOTOR_GROUP_ELEM);
}

//------------------------------------------------------------------------------
// DevicePool::get_countertimer_nb
//
inline int32_t DevicePool::get_countertimer_nb()
{
    return get_element_nb(COTI_ELEM);
}

//------------------------------------------------------------------------------
// DevicePool::get_zerod_nb
//
inline int32_t DevicePool::get_zerod_nb()
{
    return get_element_nb(ZEROD_ELEM);
}

//------------------------------------------------------------------------------
// DevicePool::get_oned_nb
//
inline int32_t DevicePool::get_oned_nb()
{
    return get_element_nb(ONED_ELEM);
}

//------------------------------------------------------------------------------
// DevicePool::get_twod_nb
//
inline int32_t DevicePool::get_twod_nb()
{
    return get_element_nb(TWOD_ELEM);
}

//------------------------------------------------------------------------------
// DevicePool::get_pseudo_counter_nb
//
inline int32_t DevicePool::get_pseudo_counter_nb()
{
    return get_element_nb(PSEUDO_COUNTER_ELEM);
}

//------------------------------------------------------------------------------
// DevicePool::get_measurement_group_nb
//
inline int32_t DevicePool::get_measurement_group_nb()
{
    return get_element_nb(MEASUREMENT_GROUP_ELEM);
}

//------------------------------------------------------------------------------
// DevicePool::get_communication_channel_nb
//
inline int32_t DevicePool::get_communication_channel_nb()
{
    return get_element_nb(COM_ELEM);
}

//------------------------------------------------------------------------------
// DevicePool::get_ioregister_nb
//
inline int32_t DevicePool::get_ioregister_nb()
{
    return get_element_nb(IOREGISTER_ELEM);
}

//------------------------------------------------------------------------------
// DevicePool::get_instrument_nb
//
inline int32_t DevicePool::get_instrument_nb()
{
    return get_element_nb(INSTRUMENT_ELEM);
}

/*
//------------------------------------------------------------------------------
// DevicePool::get_constraint_nb
//
inline int32_t DevicePool::get_constraint_nb()
{
    return get_element_nb(CONSTRAINT_ELEM);
}
*/

//------------------------------------------------------------------------------
// DevicePool::controller_exists
//
inline bool DevicePool::controller_exists(const std::string &name, 
                                          bool any_name /*= false */)
{
    try 
    { 
        get_controller(name, any_name); 
        return true; 
    }
    catch(...) 
    { 
        return false; 
    }
}

//------------------------------------------------------------------------------
// DevicePool::physical_motor_exists
//
inline bool DevicePool::physical_motor_exists(const std::string &name,
                                              bool any_name /*= false */)
{
    return element_exists(name, MOTOR_ELEM, any_name);
}

//------------------------------------------------------------------------------
// DevicePool::motor_group_exists
//
inline bool DevicePool::motor_group_exists(const std::string &name,
                                           bool any_name /*= false */)
{
    return element_exists(name, MOTOR_GROUP_ELEM, any_name);    
}

//------------------------------------------------------------------------------
// DevicePool::pseudo_motor_exists
//
inline bool DevicePool::pseudo_motor_exists(const std::string &name,
                                            bool any_name /*= false */)
{
    return element_exists(name, PSEUDO_MOTOR_ELEM, any_name);
}

//------------------------------------------------------------------------------
// DevicePool::motor_exists
//
inline bool DevicePool::motor_exists(const std::string &name,
                                     bool any_name /*= false */)
{
    return physical_motor_exists(name, any_name) || 
           pseudo_motor_exists(name, any_name);
}

//------------------------------------------------------------------------------
// DevicePool::countertimer_exists
//
inline bool DevicePool::countertimer_exists(const std::string &name, 
                                            bool any_name /*= false*/)
{
    return element_exists(name, COTI_ELEM, any_name);
}

//------------------------------------------------------------------------------
// DevicePool::zerod_exists
//
inline bool DevicePool::zerod_exists(const std::string &name, 
                                     bool any_name /*= false*/)
{
    return element_exists(name, ZEROD_ELEM, any_name);
}

//------------------------------------------------------------------------------
// DevicePool::oned_exists
//
inline bool DevicePool::oned_exists(const std::string &name, 
                                    bool any_name /*= false*/)
{
    return element_exists(name, ONED_ELEM, any_name);
}

//------------------------------------------------------------------------------
// DevicePool::twod_exists
//
inline bool DevicePool::twod_exists(const std::string &name, 
                                    bool any_name /*= false*/)
{
    return element_exists(name, TWOD_ELEM, any_name);
}

//------------------------------------------------------------------------------
// DevicePool::pseudo_counter_exists
//
inline bool DevicePool::pseudo_counter_exists(const std::string &name, 
                                              bool any_name /*= false*/)
{
    return element_exists(name, PSEUDO_COUNTER_ELEM, any_name);
}

//------------------------------------------------------------------------------
// DevicePool::communication_channel_exists
//
inline bool DevicePool::communication_channel_exists(const std::string &name, 
                                                     bool any_name /*= false*/)
{
    return element_exists(name, COM_ELEM, any_name);
}

//------------------------------------------------------------------------------
// DevicePool::ioregister_exists
//
inline bool DevicePool::ioregister_exists(const std::string &name,
                                          bool any_name /*= false*/)
{
    return element_exists(name, IOREGISTER_ELEM, any_name);
}

//------------------------------------------------------------------------------
// DevicePool::ioregister_exists
//
inline bool DevicePool::instrument_exists(const std::string &name,
                                          bool any_name /*= false*/)
{
    return element_exists(name, INSTRUMENT_ELEM, any_name);
}

//------------------------------------------------------------------------------
// DevicePool::remove_controller
//
inline void DevicePool::remove_controller(ElementId id)
{
    assert(get_element(id)->get_type() == CTRL_ELEM);
    remove_element(id);
}

//------------------------------------------------------------------------------
// DevicePool::remove_physical_motor
//
inline void DevicePool::remove_physical_motor(ElementId id)
{
    assert(get_element(id)->get_type() == MOTOR_ELEM);
    remove_element(id);
}

//------------------------------------------------------------------------------
// DevicePool::remove_pseudo_motor
//
inline void DevicePool::remove_pseudo_motor(ElementId id)
{
    assert(get_element(id)->get_type() == PSEUDO_MOTOR_ELEM);
    remove_element(id);
}

//------------------------------------------------------------------------------
// DevicePool::remove_motor_group
//
inline void DevicePool::remove_motor_group(ElementId id)
{
    assert(get_element(id)->get_type() == MOTOR_GROUP_ELEM);
    remove_element(id);
}

//------------------------------------------------------------------------------
// DevicePool::remove_countertimer
//
inline void DevicePool::remove_countertimer(ElementId id)
{
    assert(get_element(id)->get_type() == COTI_ELEM);
    remove_element(id);
}

//------------------------------------------------------------------------------
// DevicePool::remove_zerod
//
inline void DevicePool::remove_zerod(ElementId id)
{
    assert(get_element(id)->get_type() == ZEROD_ELEM);
    remove_element(id);
}

//------------------------------------------------------------------------------
// DevicePool::remove_oned
//
inline void DevicePool::remove_oned(ElementId id)
{
    assert(get_element(id)->get_type() == ONED_ELEM);
    remove_element(id);
}

//------------------------------------------------------------------------------
// DevicePool::remove_twod
//
inline void DevicePool::remove_twod(ElementId id)
{
    assert(get_element(id)->get_type() == TWOD_ELEM);
    remove_element(id);
}

//------------------------------------------------------------------------------
// DevicePool::remove_pseudo_counter
//
inline void DevicePool::remove_pseudo_counter(ElementId id)
{
    assert(get_element(id)->get_type() == PSEUDO_COUNTER_ELEM);
    remove_element(id);
}

//------------------------------------------------------------------------------
// DevicePool::remove_measurement_group
//
inline void DevicePool::remove_measurement_group(ElementId id)
{
    assert(get_element(id)->get_type() == MEASUREMENT_GROUP_ELEM);
    remove_element(id);
}

//------------------------------------------------------------------------------
// DevicePool::remove_communication_channel
//
inline void DevicePool::remove_communication_channel(ElementId id)
{
    assert(get_element(id)->get_type() == COM_ELEM);
    remove_element(id);
}

//------------------------------------------------------------------------------
// DevicePool::remove_ioregister
//
inline void DevicePool::remove_ioregister(ElementId id)
{
    assert(get_element(id)->get_type() == IOREGISTER_ELEM);
    remove_element(id);
}

//------------------------------------------------------------------------------
// DevicePool::remove_controllers
//
inline void DevicePool::remove_controllers()
{
    remove_all_elements(CTRL_ELEM);
}

//------------------------------------------------------------------------------
// DevicePool::remove_physical_motors
//
inline void DevicePool::remove_physical_motors()
{
    remove_all_elements(MOTOR_ELEM);
}

//------------------------------------------------------------------------------
// DevicePool::remove_pseudo_motors
//
inline void DevicePool::remove_pseudo_motors()
{
    remove_all_elements(PSEUDO_MOTOR_ELEM);
}

//------------------------------------------------------------------------------
// DevicePool::remove_motor_groups
//
inline void DevicePool::remove_motor_groups()
{
    remove_all_elements(MOTOR_GROUP_ELEM);
}

//------------------------------------------------------------------------------
// DevicePool::remove_countertimers
//
inline void DevicePool::remove_countertimers()
{
    remove_all_elements(COTI_ELEM);
}

//------------------------------------------------------------------------------
// DevicePool::remove_zerods
//
inline void DevicePool::remove_zerods()
{
    remove_all_elements(ZEROD_ELEM);
}

//------------------------------------------------------------------------------
// DevicePool::remove_oneds
//
inline void DevicePool::remove_oneds()
{
    remove_all_elements(ONED_ELEM);
}

//------------------------------------------------------------------------------
// DevicePool::remove_twods
//
inline void DevicePool::remove_twods()
{
    remove_all_elements(TWOD_ELEM);
}

//------------------------------------------------------------------------------
// DevicePool::remove_pseudo_counters
//
inline void DevicePool::remove_pseudo_counters()
{
    remove_all_elements(PSEUDO_COUNTER_ELEM);
}

//------------------------------------------------------------------------------
// DevicePool::remove_measurement_groups
//
inline void DevicePool::remove_measurement_groups()
{
    remove_all_elements(MEASUREMENT_GROUP_ELEM);
}

//------------------------------------------------------------------------------
// DevicePool::remove_communication_channels
//
inline void DevicePool::remove_communication_channels()
{
    remove_all_elements(COM_ELEM);
}

//------------------------------------------------------------------------------
// DevicePool::remove_ioregisters
//
inline void DevicePool::remove_ioregisters()
{
    remove_all_elements(IOREGISTER_ELEM);
}

//------------------------------------------------------------------------------
// DevicePool::is_physical_element
//
inline bool DevicePool::is_physical_element(ElementId elem_id)
{
    return IS_PHYSICAL(get_element(elem_id)->get_type());
}

}
