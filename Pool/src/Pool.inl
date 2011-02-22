#include "CPoolElement.h"
#include "CPoolController.h"
#include "CPoolMotor.h"
#include "CPoolMotorGroup.h"
#include "CPoolPseudoMotor.h"
#include "CPoolCTExpChannel.h"
#include "CPoolZeroDExpChannel.h"
#include "CPoolOneDExpChannel.h"
#include "CPoolTwoDExpChannel.h"
#include "CPoolMeasurementGroup.h"
#include "CPoolPseudoCounter.h"
#include "CPoolCommunicationChannel.h"
#include "CPoolIORegister.h"

#include "PoolBaseDev.h"
#include "PoolIndBaseDev.h"
#include "PoolGroupBaseDev.h"
#include "Motor.h"
#include "MotorGroup.h"
#include "CTExpChannel.h"
#include "ZeroDExpChannel.h"
#include "OneDExpChannel.h"
#include "TwoDExpChannel.h"
#include "PseudoMotor.h"
#include "PseudoCounter.h"
#include "MeasurementGroup.h"
#include "CommunicationChannel.h"
#include "IORegister.h"

namespace Pool_ns
{

inline TangoElement &Pool::get_tango_element(ElementId id)
{
    TangoElementMapIt it = tango_elements.find(id);
    if(it == tango_elements.end())
    {
        TangoSys_OMemStream o;
        o << "No element device with ID " << id << " found" << std::ends;

        Tango::Except::throw_exception((const char *)"Pool_UnknownElement",
                                       o.str(),
                                       (const char *)"Pool::get_tango_element");            
    }
    TangoElement &te_ref = it->second;
    return te_ref;
}

inline TangoElement &Pool::get_tango_element(PoolElement &pe)
{ return get_tango_element(pe.get_id()); }

inline Tango::DeviceProxy *Pool::get_element_proxy(ElementId id)
{ return get_tango_element(id).dev_proxy; }

inline Tango::DeviceProxy *Pool::get_element_proxy(PoolElement &pe)
{ return get_element_proxy(pe.get_id()); }

inline Tango::Device_4Impl *Pool::get_element_device(ElementId id)
{ return get_tango_element(id).dev; }

inline Tango::Device_4Impl *Pool::get_element_device(PoolElement &pe)
{ return get_element_device(pe.get_id()); }

inline Motor_ns::Motor *Pool::get_motor_device(ElementId id)
{ return static_cast<Motor_ns::Motor *>(get_element_device(id)); }

inline Motor_ns::Motor *Pool::get_motor_device(MotorPool &m)
{ return get_motor_device(m.get_id()); }

inline MotorGroup_ns::MotorGroup *Pool::get_motor_group_device(ElementId id)
{ return static_cast<MotorGroup_ns::MotorGroup *>(get_element_device(id)); }

inline MotorGroup_ns::MotorGroup *Pool::get_motor_group_device(MotorGroupPool &mg)
{ return get_motor_group_device(mg.get_id()); }

inline PseudoMotor_ns::PseudoMotor *Pool::get_pseudo_motor_device(ElementId id)
{ return static_cast<PseudoMotor_ns::PseudoMotor *>(get_element_device(id)); }

inline PseudoMotor_ns::PseudoMotor *Pool::get_pseudo_motor_device(PseudoMotorPool &pm)
{ return get_pseudo_motor_device(pm.get_id()); }

inline CTExpChannel_ns::CTExpChannel *Pool::get_countertimer_device(ElementId id)
{ return static_cast<CTExpChannel_ns::CTExpChannel *>(get_element_device(id)); }

inline CTExpChannel_ns::CTExpChannel *Pool::get_countertimer_device(CTExpChannelPool &ct)
{ return get_countertimer_device(ct.get_id()); }

inline ZeroDExpChannel_ns::ZeroDExpChannel *Pool::get_zerod_device(ElementId id)
{ return static_cast<ZeroDExpChannel_ns::ZeroDExpChannel *>(get_element_device(id)); }

inline ZeroDExpChannel_ns::ZeroDExpChannel *Pool::get_zerod_device(ZeroDExpChannelPool &zerod)
{ return get_zerod_device(zerod.get_id()); }

inline OneDExpChannel_ns::OneDExpChannel *Pool::get_oned_device(ElementId id)
{ return static_cast<OneDExpChannel_ns::OneDExpChannel *>(get_element_device(id)); }

inline OneDExpChannel_ns::OneDExpChannel *Pool::get_oned_device(OneDExpChannelPool &oned)
{ return get_oned_device(oned.get_id()); }

inline TwoDExpChannel_ns::TwoDExpChannel *Pool::get_twod_device(ElementId id)
{ return static_cast<TwoDExpChannel_ns::TwoDExpChannel *>(get_element_device(id)); }

inline TwoDExpChannel_ns::TwoDExpChannel *Pool::get_twod_device(TwoDExpChannelPool &twod)
{ return get_twod_device(twod.get_id()); }

inline PseudoCounter_ns::PseudoCounter *Pool::get_pseudo_counter_device(ElementId id)
{ return static_cast<PseudoCounter_ns::PseudoCounter *>(get_element_device(id)); }

inline PseudoCounter_ns::PseudoCounter *Pool::get_pseudo_counter_device(PseudoCounterPool &pc)
{ return get_pseudo_counter_device(pc.get_id()); }

inline MeasurementGroup_ns::MeasurementGroup *Pool::get_measurement_group_device(ElementId id)
{ return static_cast<MeasurementGroup_ns::MeasurementGroup *>(get_element_device(id)); }

inline MeasurementGroup_ns::MeasurementGroup *Pool::get_measurement_group_device(MeasurementGroupPool &mg)
{ return get_measurement_group_device(mg.get_id()); }

inline CommunicationChannel_ns::CommunicationChannel *Pool::get_communication_channel_device(ElementId id)
{ return static_cast<CommunicationChannel_ns::CommunicationChannel *>(get_element_device(id)); }

inline CommunicationChannel_ns::CommunicationChannel *Pool::get_communication_channel_device(CommunicationChannelPool &com)
{ return get_communication_channel_device(com.get_id()); }

inline IORegister_ns::IORegister *Pool::get_ioregister_device(ElementId id)
{ return static_cast<IORegister_ns::IORegister *>(get_element_device(id)); }

inline IORegister_ns::IORegister *Pool::get_ioregister_device(IORegisterPool &ior)
{ return get_ioregister_device(ior.get_id()); }

inline bool Pool::has_element_proxy(ElementId id)
{
    try { return get_element_proxy(id) != NULL; }
    catch(Tango::DevFailed &) {}
    return false;
}

inline bool Pool::has_element_proxy(PoolElement &pe)
{ return has_element_proxy(pe.get_id()); }

inline void Pool::set_element_proxy(ElementId id, Tango::DeviceProxy *proxy)
{
    TangoElementMapIt it = tango_elements.find(id);
    if(it != tango_elements.end())
    {
        SAFE_DELETE(it->second.dev_proxy)
        it->second.dev_proxy = proxy;
    }
    else
    {
        TangoElement te(proxy);
        tango_elements.insert(TangoElementMapVT(id, te));
    }
}

inline void Pool::set_element_proxy(PoolElement &pe, Tango::DeviceProxy *proxy)
{ set_element_proxy(pe.get_id(), proxy); }

inline void Pool::set_tango_element(ElementId id, Tango::DeviceProxy *proxy, Tango::Device_4Impl *dev)
{
    TangoElementMapIt it = tango_elements.find(id);
    if(it != tango_elements.end())
    {
        SAFE_DELETE(it->second.dev_proxy)
    }
    else
    {
        TangoElement te;
        tango_elements.insert(TangoElementMapVT(id, te));
        it = tango_elements.find(id);
    }
    it->second.dev_proxy = proxy;
    it->second.dev = dev;
}
    
inline void Pool::set_tango_element(PoolElement &pe, Tango::DeviceProxy *proxy, Tango::Device_4Impl *dev)
{ set_tango_element(pe.get_id(), proxy, dev); }

}	// namespace_ns
