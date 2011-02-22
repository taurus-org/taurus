#include "CtrlFiCa.h"
#include <tango.h>
#include "Utils.h"
#include "Pool.h"
#include "PoolUtil.h"
#include "PoolIndBaseDev.h"
#include "Motor.h"

namespace Pool_ns
{

//------------------------------------------------------------------------------
// PoolIndBaseDev::PoolIndBaseDev
//
PoolIndBaseDev::PoolIndBaseDev(Tango::DeviceClass *cl,string &s)
:PoolBaseDev(cl,s.c_str())
{
}

//------------------------------------------------------------------------------
// PoolIndBaseDev::PoolIndBaseDev
//
PoolIndBaseDev::PoolIndBaseDev(Tango::DeviceClass *cl,const char *s)
:PoolBaseDev(cl,s)
{
}

//------------------------------------------------------------------------------
// PoolIndBaseDev::PoolIndBaseDev
//
PoolIndBaseDev::PoolIndBaseDev(Tango::DeviceClass *cl,const char *s,const char *d)
:PoolBaseDev(cl,s,d)
{
}

//------------------------------------------------------------------------------
// PoolIndBaseDev::init_device
//
void PoolIndBaseDev::init_device()
{
    PoolBaseDev::init_device();
    
    ctrl_code_online = true;
    simulation_mode = false;
    sf_index = 0;
    unknown_state = false;

    Tango::Attribute &instrument_att = dev_attr->get_attr_by_name("instrument");
    instrument_att.set_change_event(true,false);
}

//------------------------------------------------------------------------------
// PoolIndBaseDev::delete_device
//
void PoolIndBaseDev::delete_device()
{
    PoolBaseDev::delete_device();
}

//------------------------------------------------------------------------------
// PoolIndBaseDev::get_single_pool_element
//
SinglePoolElement &PoolIndBaseDev::get_single_pool_element()
{
    return static_cast<SinglePoolElement &>(get_pool_element());
}

//------------------------------------------------------------------------------
// PoolIndBaseDev::read_SimulationMode
//
void PoolIndBaseDev::read_SimulationMode(Tango::Attribute &attr)
{
    simulation_mode = get_pool_element().get_simulation_mode();
    attr.set_value(&simulation_mode);
}

//------------------------------------------------------------------------------
// PoolIndBaseDev::write_SimulationMode
//
void PoolIndBaseDev::write_SimulationMode(Tango::WAttribute &attr)
{
    attr.get_write_value(simulation_mode);
    get_pool_element().set_simulation_mode(simulation_mode);
}

//------------------------------------------------------------------------------
// PoolIndBaseDev::is_SimulationMode_allowed
//
bool PoolIndBaseDev::is_SimulationMode_allowed(Tango::AttReqType type)
{
    if (get_state() == Tango::FAULT	||
        get_state() == Tango::UNKNOWN)
    {
        // End of Generated Code
        return false;
    }
    else
    {
        if ((type == Tango::WRITE_REQ) && ((pool_sd == true) || (get_state() == Tango::MOVING)))

        // Re-Start of Generated Code
        return false;
    }
    return true;
}

//------------------------------------------------------------------------------
// PoolIndBaseDev::read_Instrument
//
void PoolIndBaseDev::read_Instrument(Tango::Attribute &attr)
{
    ElementId instrument_id = get_pool_element().get_instrument_id();
    instrument_str = "";
    if (instrument_id != InvalidId)
    {
        InstrumentPool& instrument = get_pool().get_instrument(instrument_id);
        instrument_str = instrument.get_user_full_name();
    }
    char *ret = const_cast<char*>(instrument_str.c_str());
    attr.set_value(&ret);
}

//------------------------------------------------------------------------------
// PoolIndBaseDev::write_Instrument
//
void PoolIndBaseDev::write_Instrument(Tango::WAttribute &attr)
{
    Tango::DevString v = NULL;
    attr.get_write_value(v);
    InstrumentPool &instrument = get_pool().get_instrument(v, true);
    instrument_id = instrument.get_id();
    get_pool_element().set_instrument_id(instrument_id);
    
    Tango::DbDatum i_id("instrument_id");
    Tango::DbData db_data;

    i_id << (Tango::DevLong)instrument_id;
    db_data.push_back(i_id);

    get_db_device()->put_property(db_data);

    std::string attr_name = "instrument";
    
    char *user_full_name = const_cast<char *>(instrument.get_user_full_name().c_str());
    push_change_event(attr_name, &user_full_name);
}

//------------------------------------------------------------------------------
// PoolIndBaseDev::is_Instrument_allowed
//
bool PoolIndBaseDev::is_Instrument_allowed(Tango::AttReqType type)
{
    if (get_state() == Tango::UNKNOWN)
    {
        // End of Generated Code
        return false;
    }
    else
    {
        if ((type == Tango::WRITE_REQ) && ((pool_sd == true) || (get_state() == Tango::MOVING)))
        // Re-Start of Generated Code
        return false;
    }
    return true;
}

//------------------------------------------------------------------------------
// PoolIndBaseDev::should_be_in_fault
//
bool PoolIndBaseDev::should_be_in_fault() 
{
    SinglePoolElement &single_pool_element = get_single_pool_element();
    return is_fica_built() == false || this->ctrl_code_online == false ||
           single_pool_element.is_add_device_done() == false;
}

//------------------------------------------------------------------------------
// PoolIndBaseDev::is_add_device_done
//
bool PoolIndBaseDev::is_add_device_done()
{
    return get_single_pool_element().is_add_device_done();
}

//------------------------------------------------------------------------------
// PoolIndBaseDev::get_ctrl
//
ControllerPool &PoolIndBaseDev::get_ctrl()
{ 
    return pool_dev->get_controller(get_ctrl_id()); 
}

//------------------------------------------------------------------------------
// PoolIndBaseDev::get_ctrl_name
//
std::string PoolIndBaseDev::get_ctrl_name()
{ 
    return get_ctrl().get_name();
}

//------------------------------------------------------------------------------
// PoolIndBaseDev::get_controller
//
Controller *PoolIndBaseDev::get_controller()
{ 
    return get_ctrl().get_controller();
}

//------------------------------------------------------------------------------
// PoolIndBaseDev::init_pool_element
//
void PoolIndBaseDev::init_pool_element(PoolElement *pe)
{
    Pool_ns::ControllerPool &ctrl_pool = pool_dev->get_controller(get_ctrl_id());
    
    this->fica_built = ctrl_pool.ctrl_class_built;
    this->fica_ptr = this->fica_built ? *(ctrl_pool.ite_ctrl_class) : NULL;

    pe->set_axis(get_axis());
    pe->set_ctrl_id(get_ctrl_id());
    pe->set_instrument_id(get_instrument_id());
    PoolBaseDev::init_pool_element(pe);
}

void PoolIndBaseDev::get_device_property()
{
    PoolBaseDev::get_device_property();

    //	Read device properties from database.
    //------------------------------------------------------------------
    Tango::DbData	dev_prop;
    dev_prop.push_back(Tango::DbDatum("ctrl_id"));
    dev_prop.push_back(Tango::DbDatum("axis"));
    dev_prop.push_back(Tango::DbDatum("instrument_id"));
    
    //	Call database and extract values
    //--------------------------------------------
    if (Tango::Util::instance()->_UseDb==true)
        get_db_device()->get_property(dev_prop);
    
    ctrl_id = InvalidId;
    //	try to extract ctrl_id value from database
    if (dev_prop[0].is_empty()==false)
    {
        Tango::DevLong tmp_ctrl_id;
        dev_prop[0]  >>  tmp_ctrl_id;
        ctrl_id = (int32_t)tmp_ctrl_id;
    }

    // In principle there is no invalid axis value.
    // It is up to each controller to decice which axis values to use for their
    // elements. As a general rule axis should start in 1.
    //	try to extract axis value from database
    if (dev_prop[1].is_empty()==false)
    {
        Tango::DevLong tmp_axis;
        dev_prop[1]  >>  tmp_axis;
        axis = (int32_t)tmp_axis;
    }
    
    instrument_id = InvalidId;
    //	try to extract instrument_id value from database
    if (dev_prop[2].is_empty()==false)
    {
        Tango::DevLong tmp_instrument_id;
        dev_prop[2]  >>  tmp_instrument_id;
        instrument_id = (int32_t)tmp_instrument_id;
    }

}

//------------------------------------------------------------------------------
// PoolIndBaseDev::a_new_child
//
void PoolIndBaseDev::a_new_child(ElementId ctrl_id)
{
    if (is_fica_built())
    {
        SinglePoolElement &single_pool_element = get_single_pool_element();
        try
        {
            Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());
            
            Pool_ns::ControllerPool &ctrl = *single_pool_element.get_ctrl();
            Controller *controller = ctrl.get_controller();
            ctrl.nb_dev++;

            controller->AddDevice(get_axis());
            single_pool_element.set_add_device_done();
        }
        catch (Tango::DevFailed &e)
        {
            std::string err = "\nError reported by the controller during its AddDevice method:\n\t";
            err += e.errors[0].desc.in();
            single_pool_element.set_add_device_done(false, err);
            set_state(Tango::FAULT);
        }
    }
    else
        set_state(Tango::FAULT);
}

//------------------------------------------------------------------------------
// PoolIndBaseDev::suicide
//
void PoolIndBaseDev::suicide()
{
    if (is_fica_built())
    {
        Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());
        if (this->ctrl_code_online)
        {
            Pool_ns::ControllerPool &ctrl = get_ctrl();
            Controller *controller = ctrl.get_controller();
            controller->DeleteDevice(get_axis());
            ctrl.nb_dev--;
        }
    }
}

//------------------------------------------------------------------------------
// PoolIndBaseDev::delete_from_pool
//
void PoolIndBaseDev::delete_from_pool()
{
    suicide();
    PoolBaseDev::delete_from_pool();
}

//------------------------------------------------------------------------------
// PoolIndBaseDev::base_always_executed_hook
//
void PoolIndBaseDev::base_always_executed_hook(bool motor,bool propagate)
{
    SinglePoolElement &single_pool_element = get_single_pool_element();
    
    if (!single_pool_element.get_simulation_mode())
    {
        Tango::DevState old_state = get_state();
        
        if (is_fica_built())
        {
            unknown_state = false;
            Pool_ns::PoolLock &pl = fica_ptr->get_mon();
            Pool_ns::AutoPoolLock lo(pl);
            if (!this->ctrl_code_online)
            {
                set_state(Tango::FAULT);
            }
            else
            {
                if (single_pool_element.is_add_device_done())
                {
                    MotorController::MotorState mi;
                    try
                    {
                        
//
// There is a trick here for client getting position using polling mode
// The motion thread stores motor position in the polling buffer and
// the client is getting position from this polling buffer
// When the motion thread detects that the motion is over
// (state != MOVING), it invalidates data from the polling buffer and
// therefore all clients will get data from hardware access.
// What could happens, is that a client thread detects first the
// end of the motion (before the motion thread). If this thread
// immediately reads the position after it detects the motion end, it will
// get the last value written in the polling buffer because the mov thread has not
// yet invalidate it.
// Therefore, if the thread executing this code is not the mov thread and if the state
// changed from MOVING to ON, delay the state changes that it will be detected by the
// motion thread. This motion thread is doing a motor call every 10 mS
//

                        int th_id = omni_thread::self()->id();

                        read_state_from_ctrl(mi, false);
                        
                        set_state((Tango::DevState)mi.state);
                        ctrl_str = mi.status;
                        
                        if (mov_th_id != 0)
                        {
                            if ((old_state == Tango::MOVING) && 
                                ((get_state() == Tango::ON) || (get_state() == Tango::ALARM)) && 
                                (th_id != mov_th_id) &&
                                (abort_cmd_executed == false))
                                    set_state(Tango::MOVING);
                        }

                        if (motor == true)
                        {
                            if ((mi.switches >= 2) && (get_state() != Tango::MOVING))
                                set_state(Tango::ALARM);
                        }
                    }
                    catch(Tango::DevFailed &e)
                    {
                        set_state(Tango::UNKNOWN);
                        ctrl_str = "Error reported from controller when requesting for object state\n\t";
                        ctrl_str += e.errors[0].desc.in();
                    }
                }
                else
                    set_state(Tango::FAULT);
            }
        }
        else
        {
            set_state(Tango::FAULT);
        }
        
//
// If necessary notify the ghost group of changes in this element.
// The ghost group will itself notify any internal listeners. 
//
        if(propagate == true)
        {
            inform_ghost(old_state,get_state());
        }
    }
}

//------------------------------------------------------------------------------
// PoolIndBaseDev::read_state_from_ctrl
//
void PoolIndBaseDev::read_state_from_ctrl(Controller::CtrlState &sta,bool lock)
{
    try
    {
        Controller *ctrl = get_controller();
        
        if (lock == true)
        {
            Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());
            ctrl->PreStateAll();
            ctrl->PreStateOne(get_axis());
            ctrl->StateAll();
            ctrl->StateOne(get_axis(), &sta);
        }
        else
        {
            ctrl->PreStateAll();
            ctrl->PreStateOne(get_axis());
            ctrl->StateAll();
            ctrl->StateOne(get_axis(), &sta);
        }
    }
    SAFE_CATCH(fica_ptr->get_name(), "read_state_from_controller");
}

//------------------------------------------------------------------------------
// PoolIndBaseDev::base_dev_status
//
void PoolIndBaseDev::base_dev_status(Tango::ConstDevString base_status)
{
    SinglePoolElement &single_pool_element = get_single_pool_element();
    
    tmp_status = base_status;
    Tango::DevState sta = get_state();

    if (ctrl_str.size() > 0)
        tmp_status += '\n' + ctrl_str;
//
// If the counter is in FAULT, it could be because the ctrl is not OK.
// Otherwise, checks if the controller send an error string
//

    if (sta == Tango::FAULT)
    {
        if (is_fica_built())
        {
            if (!single_pool_element.is_add_device_done())
            {
                tmp_status += single_pool_element.get_add_device_error_str();
            }
            else
            {
                bool ctrl_ok = true;
                {
                    Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());

                    if (this->ctrl_code_online == false)
                    {
                        tmp_status += "\nMy controller code (" + get_ctrl_name() + ") is not loaded in memory";
                        ctrl_ok = false;
                    }
                }
                    
                if (unknown_state == true)
                {
                    tmp_status += "\nThe controller returns an unforeseen state";
                }
            }
        }
        else
        {
            tmp_status += "\nMy controller object (" + get_ctrl_name() + ") is not initialized";
        }
    }
    
    if (single_pool_element.get_simulation_mode())
        tmp_status += "\nDevice is in simulation mode";
}

//------------------------------------------------------------------------------
// PoolIndBaseDev::get_extra_attributes
//
vector<PoolExtraAttr> &PoolIndBaseDev::get_extra_attributes()
{
    if(!fica_built)
    {
        TangoSys_OMemStream o;
        o << "Can't get extra attribute information from " << alias << ".";
        o << "The FiCa is not build." << ends;
        Tango::Except::throw_exception((const char *)"Pool_CantGetExtraAttributes",o.str(),
                                       (const char *)"MeasurementGroup::get_extra_attributes()");
    }
    
    return fica_ptr->get_extra_attributes();
}

}	//	namespace
