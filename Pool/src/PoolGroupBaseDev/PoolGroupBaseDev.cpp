//+=============================================================================
//
// file :         PoolGroupBaseDev.cpp
//
// description :  C++ source for the PoolGroupBaseDev class
//
// project :      Sardana device Pool
//
// $Author$
//
// $Revision$
//
// $Log$
// Revision 1.21  2007/09/07 15:00:07  tcoutinho
// safety commit
//
// Revision 1.20  2007/08/30 12:40:39  tcoutinho
// - changes to support Pseudo counters.
//
// Revision 1.19  2007/08/17 13:07:30  tcoutinho
// - pseudo motor restructure
// - pool base dev class restructure
// - initial commit for pseudo counters
//
// Revision 1.18  2007/07/26 10:25:15  tcoutinho
// - Fix bug 1 :  Automatic temporary MotorGroup/MeasurementGroup deletion
//
// Revision 1.17  2007/07/13 14:11:20  tcoutinho
// fix bug. Comparison on elements will be case insensitive
//
// Revision 1.16  2007/07/12 13:24:24  tcoutinho
// nothing changed... just safety commit
//
// Revision 1.15  2007/05/30 14:48:04  etaurel
// - Add an abort if the two state_array vector sizes are different
//
// Revision 1.14  2007/05/25 09:34:55  tcoutinho
// - fix internal event propagation to ghost motor group when client asks for state and the new calculated state is different from the one previously stored
//
// Revision 1.13  2007/05/22 12:56:42  etaurel
// - Fix some bugs in event propagation
//
// Revision 1.12  2007/05/17 07:00:08  etaurel
// - Some tabs....
//
// Revision 1.11  2007/05/16 07:56:35  tcoutinho
// - added some logging to find bug
//
// Revision 1.10  2007/04/30 14:51:20  tcoutinho
// - make possible to Add/Remove elements on motorgroup that are part of other motor group(s)
//
// Revision 1.9  2007/02/22 12:04:13  tcoutinho
// - support for pool_elem_changed
//
// Revision 1.8  2007/02/16 10:01:40  tcoutinho
// - development checkin
//
// Revision 1.7  2007/02/13 14:39:43  tcoutinho
// - fix bug in motor group when a motor or controller are recreated due to an InitController command
//
// Revision 1.6  2007/02/08 16:18:14  tcoutinho
// - controller safety on PoolGroupBaseDev
//
// Revision 1.5  2007/02/07 16:53:06  tcoutinho
// safe guard commit
//
// Revision 1.4  2007/02/06 19:36:51  tcoutinho
// safe guard commit
//
// Revision 1.3  2007/02/06 19:11:23  tcoutinho
// safe guard commit
//
// Revision 1.2  2007/02/06 09:37:45  tcoutinho
// - Motor Group now uses PoolGroupBaseDev
//
// Revision 1.1  2007/02/03 15:19:41  tcoutinho
// new base tango group device
//
//
// Revision 1.1  2007/01/16 14:22:25  tcoutinho
// - Initial revision
//
//
// copyleft :   CELLS/ALBA
//		Edifici Ciences Nord
//		Campus Universitari de Bellaterra
//		Universitat Autonoma de Barcelona
//		08193 Bellaterra, Barcelona, SPAIN
//
//-=============================================================================

#include "Pool.h"
#include "PoolUtil.h"
#include "PoolBaseUtil.h"
#include "PoolGroupBaseUtil.h"
#include "PoolGroupBaseDev.h"

namespace Pool_ns
{

CtrlGrp::CtrlGrp(ControllerPool &ref, Tango::Device_4Impl *dev /*= NULL*/):
Tango::LogAdapter(dev),	ctrl_id(ref.id),ct(&ref),lock_ptr(NULL)
{}

void CtrlGrp::Lock(vector<Controller *> *failed)
{
    DEBUG_STREAM << "[ START] Locking " << ct->name << "..." << endl;

    if(lock_ptr != NULL)
    {
        WARN_STREAM << ct->name << " was already locked! - Will unlock it first..." << endl;
        Unlock();
    }

    try
    {
        if (ct->ctrl_class_built == true)
        {
            lock_ptr = new AutoPoolLock(ct->get_ctrl_class_mon());
            DEBUG_STREAM << "[   END] Locking " << ct->name << "" << endl;
        }
        else
        {
            lock_ptr = NULL;
            failed->push_back(ct->get_controller());
            WARN_STREAM << "[FAILED] - ctrl_fica not built!" << endl;
        }

    }
    catch (...)
    {
        lock_ptr = NULL;
        failed->push_back(ct->get_controller());
        ERROR_STREAM << "[FAILED] Locking " << ct->name << "..." << endl;
    }

}

void CtrlGrp::Unlock()
{
    DEBUG_STREAM << "[ START] Unlocking " << ct->name << "... " << endl;
    bool needs = lock_ptr != NULL;
    SAFE_DELETE(lock_ptr);
    DEBUG_STREAM << "[   END] Unlocking " << ct->name << "... "
                    << (needs ? "" : " (actually nothing was done!)") << endl;
}

void CtrlGrp::PreStateAll(vector<Controller *> *failed)
{
    Controller *ctrl = ct->get_controller();
    try
    {
        if (ctrl == NULL)
            return;

        if (failed->empty() != true)
            if (find(failed->begin(),failed->end(),ctrl) != failed->end())
                return;

        ctrl->PreStateAll();
    }
    catch (...)
    {
        failed->push_back(ctrl);
    }
}

void CtrlGrp::StateAll(vector<Controller *> *failed)
{
    Controller *ctrl = ct->get_controller();
    try
    {
        if (ctrl != NULL && find(failed->begin(),failed->end(),ctrl) == failed->end())
            ctrl->StateAll();
    }
    catch (...)
    {
        failed->push_back(ctrl);
    }
}

void CtrlGrp::add_channel(IndEltGrp *ch)
{
    channels[ch->id] = ch;
}

void CtrlGrp::remove_channel(IndEltGrp *ch)
{
    channels.erase(ch->id);
}

IndEltGrp::IndEltGrp(Pool_ns::PoolElement &ref,CtrlGrp *ctrl_ptr,
                     Tango::Device_4Impl *device, ElementId grp, 
                     Tango::Device_4Impl *logger /*= NULL*/):
    Tango::LogAdapter(logger),
    pe(&ref),
    ctrl_grp(ctrl_ptr), 
    state_att(device->get_device_attr()->get_attr_by_name("state")),
    atm_ptr(NULL),
    obj_proxy(NULL),
    dev(device),
    name(ref.name),
    id(ref.id), 
    idx_in_ctrl(ref.get_axis()),
    idx_in_ctrlgrp(-1),
    grp_id(grp)
{
    if(ctrl_ptr)
        ctrl_ptr->add_channel(this);
}

IndEltGrp::~IndEltGrp()
{
    if(ctrl_grp)
        ctrl_grp->remove_channel(this);
    SAFE_DELETE(obj_proxy);
    Unlock();
}

string &IndEltGrp::get_alias()
{ return pe->name; }

void IndEltGrp::Lock()
{
    DEBUG_STREAM << "[ START] Locking " << name << "..." << endl;
    try
    {
        if(atm_ptr != NULL)
        {
            WARN_STREAM << name << " was already locked! - Will unlock it first..." << endl;
            Unlock();
        }

        atm_ptr = new Tango::AutoTangoMonitor(get_device());
        DEBUG_STREAM << "[   END] Locking " << name << "" << endl;
    }
    catch (Tango::DevFailed &e)
    {
        ERROR_STREAM << "[FAILED] Locking " << name << "..." << endl;
        //cout << endl << "\tIndEltGrp ("<< name <<"): UNEXPECTED - failed to get AutoTangoMonitor: " << endl;
        //Tango::Except::print_exception(e);
    }
}

void IndEltGrp::Unlock()
{
    DEBUG_STREAM << "[ START] Unlocking " << name << "... " << endl;
    bool needs = atm_ptr != NULL;
    SAFE_DELETE(atm_ptr);
    DEBUG_STREAM << "[   END] Unlocking " << name << "... "
                    << (needs ? "" : " (actually nothing was done!)") << endl;
}

void IndEltGrp::PreStateOne(vector<Controller *> *failed)
{
    try
    {
        Controller *ctrl = ctrl_grp->ct->get_controller();
        if (failed->empty() != true)
            if (find(failed->begin(),failed->end(),ctrl) != failed->end())
                return;

        if ((ctrl != NULL) && (atm_ptr != NULL))
            ctrl->PreStateOne(idx_in_ctrl);
    }
    catch (...) {}
}

void IndEltGrp::abort(bool send_state_evt)
{
    get_base_device()->base_abort(send_state_evt);
}

void IndEltGrp::abort_no_evt(vector<Tango::DevFailed> *v_exp)
{
    try
    {
        abort(false);
    }
    catch(Tango::DevFailed &e)
    {
        v_exp->push_back(e);
    }
}

void IndEltGrp::abort_evt(vector<Tango::DevFailed> *v_exp)
{
    try
    {
        abort(true);
    }
    catch(Tango::DevFailed &e)
    {
        v_exp->push_back(e);
    }
}
//+----------------------------------------------------------------------------
//
// method : 		PoolGroupBaseDev::PoolGroupBaseDev
//
// description : 	Ctor of the PoolGroupBaseDev class
//
//-----------------------------------------------------------------------------
PoolGroupBaseDev::PoolGroupBaseDev(Tango::DeviceClass *cl,string &s)
:PoolBaseDev(cl,s.c_str())
{
    polling_thread_id = 0;
}

PoolGroupBaseDev::PoolGroupBaseDev(Tango::DeviceClass *cl,const char *s)
:PoolBaseDev(cl,s)
{
    polling_thread_id = 0;
}

PoolGroupBaseDev::PoolGroupBaseDev(Tango::DeviceClass *cl,const char *s,const char *d)
:PoolBaseDev(cl,s,d)
{
    polling_thread_id = 0;
}

void PoolGroupBaseDev::init_device()
{
    PoolBaseDev::init_device();
    
    pool_init_cmd = false;
    age = -1;
}

void PoolGroupBaseDev::delete_device()
{
    for(vector<IndEltGrp*>::size_type l = 0; l < ind_elts.size(); l++)
        delete ind_elts[l];
    ind_elts.clear();

    for(vector<CtrlGrp*>::size_type l = 0; l < implied_ctrls.size(); l++)
        delete implied_ctrls[l];
    implied_ctrls.clear();
    
    PoolBaseDev::delete_device();
}

void PoolGroupBaseDev::init_pool_element(PoolElement *pe)
{
    if(!is_ghost())
    {
        PoolBaseDev::init_pool_element(pe);
    }
    else
    {
        // if it is ghost group we still need to initialize some things
        pe->id = get_id();
    }

    
    pe->set_axis(-1);  // groups don't have index in other elements
    pe->set_ctrl_id(InvalidId);  // groups don't have a single ctrl associated
}

//+----------------------------------------------------------------------------
//
// method : 		PoolGroupBaseDev::delete_from_pool
//
// description : 	Delete a device from the pool structure
//
//-----------------------------------------------------------------------------

void PoolGroupBaseDev::delete_from_pool()
{
    init_cmd = true;

    if(!is_ghost())
    {
        Tango::AutoTangoMonitor atm(pool_dev);
        utils->remove_object(this);
    }
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::dev_state
 *
 *	description:	method to execute "State"
 *                  This method is just used to restore the age of a
 * 					temporary group device.
 *					If overwritten, the subclass should still call this
 *                  method.
 *
 * @return	State Code
 */
//+------------------------------------------------------------------
Tango::DevState PoolGroupBaseDev::dev_state()
{
    DEBUG_STREAM << "PoolGroupBaseDev::dev_state(): entering... !" << endl;
    restore_age();

//
// The ghost group will increase the age of all temporary objects
//
    if(is_ghost())
        handle_temporary_siblings();

    return Tango::ON;
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::dev_status
 *
 *	description:	method to execute "Status"
 *                  This method is just used to restore the age of a
 * 					temporary group device.
 *					If overwritten, the subclass should still call this
 *                  method.
 *
 *
 * @return	State Code
 */
//+------------------------------------------------------------------
Tango::ConstDevString PoolGroupBaseDev::dev_status()
{
    Tango::ConstDevString	argout = DeviceImpl::dev_status();
    DEBUG_STREAM << "PoolGroupBaseDev::dev_status(): entering... !" << endl;
    restore_age();
    return argout;
}

//+----------------------------------------------------------------------------
//
// method : 		PoolGroupBaseDev::always_executed_hook()
//
// description : 	method always executed before any command is executed
//
//-----------------------------------------------------------------------------
void PoolGroupBaseDev::always_executed_hook()
{
    reset_age();
}

//+----------------------------------------------------------------------------
//
// method : 		PoolGroupBaseDev::base_dev_status
//
// description :
//
//-----------------------------------------------------------------------------

void PoolGroupBaseDev::base_dev_status(Tango::ConstDevString base_status)
{
    tmp_status = base_status;
}

//+------------------------------------------------------------------
/**
 *	method:	PoolGroupBaseDev::send_state_event()
 *
 *	description:	Send change event on ind element state for
 * 					state change not generated by the motion thread
 *
 *  arg(s) : In : old_state_array : Ind elements state array
 * 				  state_array : New ind elements state array
 */
//+------------------------------------------------------------------

void PoolGroupBaseDev::send_state_event(vector<Tango::DevState> &old_state_array,
                                        vector<Tango::DevState> &state_array)
{

//
// Forget the first poll, where old_state_array size is 0
//

    if (old_state_array.size() == 0)
        return;

    if (old_state_array.size() != state_array.size())
    {
        cout << "The two state arrays size are differents (old,new) = (" <<
                old_state_array.size() << ", " << state_array.size() <<
                ")\nI abort!" << endl;
        abort();
    }

    vector<Tango::DevState>::size_type nb_state = state_array.size();
    vector<Tango::DevState>::size_type loop;

    for (loop = 0;loop < nb_state;loop++)
    {
        Tango::DevState old_state = old_state_array[loop];
        Tango::DevState state = state_array[loop];

//
// Filter state change done by the motion thread
//

        if (old_state != state)
        {
            PoolBaseDev *dev = static_cast<PoolBaseDev *>(ind_elts[loop]->get_device());
            if (dev->get_mov_th_id() != 0)
            {
                continue;
            }
            else
            {

//
// Push event on the element device
//
                Tango::AutoTangoMonitor atm(dev);
                Tango::Attribute &state_att = dev->get_device_attr()->get_attr_by_name("State");
                state_att.fire_change_event();

                PoolElement *pe = ind_elts[loop]->pe;
                if(pe->has_listeners())
                {
                    Pool_ns::PoolElementEvent evt(Pool_ns::StateChange, pe);
                    evt.old.state = Pool_ns::PoolTango::toPool(old_state);
                    evt.curr.state = Pool_ns::PoolTango::toPool(state);
                    pe->fire_pool_elem_change(&evt);
                }
            }
        }
    }
}

//+------------------------------------------------------------------
/**
 *	method:	PoolGroupBaseDev::read_state_from_ctrls
 *
 *	description:	method to read State from controller trying
 * 					to read several state from the same controller in
 * 					only one access to the controller
 *
 *	This method push every ind element state in the device state_array vector
 */
//+------------------------------------------------------------------

void PoolGroupBaseDev::read_state_from_ctrls()
{
    read_state_from_ctrls_lockall();
}

void PoolGroupBaseDev::read_state_from_ctrls_lockall()
{
    INFO_STREAM << get_name() << ".read_state_from_ctrls: START" << endl;
    vector<Controller *> failed;

    vector<IndEltGrp *>::iterator elts_begin = ind_elts.begin();
    vector<IndEltGrp *>::iterator elts_end = ind_elts.end();
    vector<CtrlGrp *>::iterator ctrls_begin = implied_ctrls.begin();
    vector<CtrlGrp *>::iterator ctrls_end = implied_ctrls.end();

    vector<IndEltGrp *>::reverse_iterator elts_rbegin = ind_elts.rbegin();
    vector<IndEltGrp *>::reverse_iterator elts_rend = ind_elts.rend();
    vector<CtrlGrp *>::reverse_iterator ctrls_rbegin = implied_ctrls.rbegin();
    vector<CtrlGrp *>::reverse_iterator ctrls_rend = implied_ctrls.rend();

//
// Lock all elements
//
    DEBUG_STREAM << "read_state_from_ctrls: locking all elements"<<endl;
    for_each(elts_begin, elts_end,mem_fun(&Pool_ns::IndEltGrp::Lock));

//
// Lock all controllers
//
    DEBUG_STREAM << "read_state_from_ctrls: locking all controllers"<<endl;
    for_each(ctrls_begin,ctrls_end,bind2nd(mem_fun(&Pool_ns::CtrlGrp::Lock),&failed));

//
// PreStateAll to all controllers
//
    DEBUG_STREAM << "read_state_from_ctrls: PreStateAll all controllers"<<endl;
    for_each(ctrls_begin,ctrls_end,bind2nd(mem_fun(&Pool_ns::CtrlGrp::PreStateAll),&failed));

//
// PreStateOne to all elements
//
    DEBUG_STREAM << "read_state_from_ctrls: PreStateOne to all elements"<<endl;
    for_each(elts_begin,elts_end,bind2nd(mem_fun(&Pool_ns::IndEltGrp::PreStateOne),&failed));

//
// StateAll to all controllers
//
    DEBUG_STREAM << "read_state_from_ctrls: StateAll to all controllers"<<endl;
    for_each(ctrls_begin,ctrls_end,bind2nd(mem_fun(&Pool_ns::CtrlGrp::StateAll),&failed));

//
// Get the state for all elements
//
    DEBUG_STREAM << "read_state_from_ctrls: state for all elements"<<endl;
    State_all_ind(failed);

//
// Unlock the implied controllers
//
    DEBUG_STREAM << "read_state_from_ctrls: unlocking all controllers"<<endl;
    for_each(ctrls_rbegin,ctrls_rend,mem_fun(&Pool_ns::CtrlGrp::Unlock));

//
// Unlock the implied channels
//
    DEBUG_STREAM << "read_state_from_ctrls: unlocking all elements"<<endl;
    for_each(elts_rbegin,elts_rend,mem_fun(&Pool_ns::IndEltGrp::Unlock));
    
    INFO_STREAM << get_name() << ".read_state_from_ctrls: END" << endl;
}

void PoolGroupBaseDev::read_state_from_ctrls_lockone()
{
    std::vector<Controller *> failed;
    
    std::vector<CtrlGrp *>::iterator ctrl_it = implied_ctrls.begin();
    std::vector<CtrlGrp *>::iterator ctrl_end = implied_ctrls.end();

    for (; ctrl_it != ctrl_end; ++ctrl_it)
    {
        CtrlGrp &ctrl_grp = *(*ctrl_it);
        std::map<ElementId, IndEltGrp*>::iterator elts_it,
            elts_beg = ctrl_grp.channels.begin(),
            elts_end = ctrl_grp.channels.end();

        std::map<ElementId, IndEltGrp*>::reverse_iterator elts_rit,
            elts_rbeg = ctrl_grp.channels.rbegin(),
            elts_rend = ctrl_grp.channels.rend();
        
        // Lock elements
        for(elts_it = elts_beg; elts_it != elts_end; ++elts_it)
            elts_it->second->Lock();
        
        // Lock controller
        ctrl_grp.Lock(&failed);
        
        // PreStateAll 
        ctrl_grp.PreStateAll(&failed);
        
        // PreStateOne
        for(elts_it = elts_beg; elts_it != elts_end; ++elts_it)
            elts_it->second->PreStateOne(&failed);
        
        // StateAll
        State_ctrl_ind(&ctrl_grp, failed);
        
        // Unlock Controller
        ctrl_grp.Unlock();

        // Unlock elements
        for(elts_rit = elts_rbeg; elts_rit != elts_rend; ++elts_rit)
            elts_rit->second->Unlock();
        
    }
}

//+------------------------------------------------------------------
/**
 *	method:	PoolGroupBaseDev::get_ind_elt_from_name
 *
 *	description: Obtains the IndEltGrp structure for
 *               the given ind element name
 *
 * @return A reference to an IndEltGrp data structure
 *         for the given ind element name
 */
//+------------------------------------------------------------------

IndEltGrp &PoolGroupBaseDev::get_ind_elt_from_name(const std::string &name)
{
    string name_lower(name);
    transform(name_lower.begin(),name_lower.end(),name_lower.begin(),::tolower);

    vector<IndEltGrp*>::iterator ind_ite = ind_elts.begin();
    for(; ind_ite != ind_elts.end(); ind_ite++)
    {
        IndEltGrp *ind = (*ind_ite);

        string ind_name_lower(ind->name);
        transform(ind_name_lower.begin(),ind_name_lower.end(),ind_name_lower.begin(),::tolower);
        if(ind_name_lower == name_lower)
            break;
    }

    if (ind_ite == ind_elts.end())
    {
        TangoSys_OMemStream o;
        o << "No IndEltGrp with name " << name << " found in ind element list" << ends;

        Tango::Except::throw_exception((const char *)"Pool_BadArgument",o.str(),
                                       (const char *)"PoolGroupBaseDev::get_ind_elt_from_name");
    }
    return *(*ind_ite);
}

//+------------------------------------------------------------------
/**
 *	method:	PoolGroupBaseDev::get_ind_elt_idx_from_id
 *
 *	description: Obtains the index in the group for the given
 *               ind element id
 *
 * @return The index in the group for the given ind element id
 */
//+------------------------------------------------------------------
int32_t PoolGroupBaseDev::get_ind_elt_idx_from_id(ElementId id)
{
    int32_t idx = 0;
    vector<IndEltGrp*>::iterator ind_ite = ind_elts.begin();
    for(; ind_ite != ind_elts.end(); ind_ite++)
    {
        IndEltGrp *ind = (*ind_ite);
        if(ind->id == id)
            return idx;
        idx++;
    }

    if (ind_ite == ind_elts.end())
    {
        TangoSys_OMemStream o;
        o << "No IndEltGrp with id " << id << " found in ind element list" << ends;

        Tango::Except::throw_exception((const char *)"Pool_BadArgument",o.str(),
                                       (const char *)"PoolGroupBaseDev::get_ind_elt_idx_from_id");
    }
    return idx;
}

//+------------------------------------------------------------------
/**
 *	method:	PoolGroupBaseDev::get_ind_elt_from_id
 *
 *	description: Obtains the IndEltGrp structure for
 *               the given ind element id
 *
 * @return A reference to an IndEltGrp data structure
 *         for the given ind element id
 */
//+------------------------------------------------------------------

IndEltGrp &PoolGroupBaseDev::get_ind_elt_from_id(ElementId id)
{
    vector<IndEltGrp*>::iterator ind_ite = ind_elts.begin();
    for(; ind_ite != ind_elts.end(); ind_ite++)
    {
        IndEltGrp *ind = (*ind_ite);
        if(ind->id == id)
            break;
    }

    if (ind_ite == ind_elts.end())
    {
        TangoSys_OMemStream o;
        o << "No IndEltGrp with id " << id << " found in ind element list" << ends;

        Tango::Except::throw_exception((const char *)"Pool_BadArgument",o.str(),
                                       (const char *)"PoolGroupBaseDev::get_ind_elt_from_id");
    }
    return *(*ind_ite);
}

//+------------------------------------------------------------------
/**
 *	method:	PoolGroupBaseDev::get_ind_elt_from_id
 *
 *	description: Obtains the IndEltGrp structure for
 *               the given ind element id
 *
 * @return A reference to an IndEltGrp data structure
 *         for the given ind element id
 */
//+------------------------------------------------------------------

IndEltGrp &PoolGroupBaseDev::get_ind_elt_from_id(ElementId id, ElementType type)
{
    vector<IndEltGrp*>::iterator ind_ite = ind_elts.begin();
    for(; ind_ite != ind_elts.end(); ind_ite++)
    {
        IndEltGrp *ind = (*ind_ite);
        if(ind->id == id && ind->pe->get_type() == type)
            break;
    }

    if (ind_ite == ind_elts.end())
    {
        TangoSys_OMemStream o;
        o << "No IndEltGrp with id " << id << " found in ind element list" << ends;

        Tango::Except::throw_exception((const char *)"Pool_BadArgument",o.str(),
                                       (const char *)"PoolGroupBaseDev::get_ind_elt_from_id");
    }
    return *(*ind_ite);
}

//+------------------------------------------------------------------
/**
 *	method:	PoolGroupBaseDev::get_ctrl_grp_from_id
 *
 *	description: Obtains the CtrlGrp structure for
 *               the given ind element name
 *
 * @return A reference to an CtrlGrp data structure
 *         for the given ind element id
 */
//+------------------------------------------------------------------

CtrlGrp	&PoolGroupBaseDev::get_ctrl_grp_from_id(ElementId ctrl_id, int32_t &pos)
{
    vector<CtrlGrp*>::iterator ctrl_ite = implied_ctrls.begin();
    int32_t p = 0;
    for(; ctrl_ite != implied_ctrls.end(); ++ctrl_ite, ++p)
    {
        CtrlGrp *ctrl = (*ctrl_ite);
        if(ctrl->ctrl_id == ctrl_id)
            break;
    }

    if (ctrl_ite == implied_ctrls.end())
    {
        TangoSys_OMemStream o;
        o << "No CtrlGrp with id " << ctrl_id << " found in controller element list" << ends;

        Tango::Except::throw_exception((const char *)"Pool_BadArgument",o.str(),
                                       (const char *)"PoolGroupBaseDev::get_ctrl_grp_from_id");
    }
    pos = p;
    return *(*ctrl_ite);
}

//+------------------------------------------------------------------
/**
 *	method:	PoolGroupBaseDev::is_ctrl_member
 *
 *	description: Determines if the given controller is used by
 *               this motor group
 *
 * @return <code>true</code> if the controller is used by the motor
 *         group or <code>false</code> otherwise.
 */
//+------------------------------------------------------------------

bool PoolGroupBaseDev::is_ctrl_member(ElementId ctrl_id)
{
    vector<CtrlGrp*>::iterator ite = implied_ctrls.begin();
    for(; ite != implied_ctrls.end(); ite++)
    {
        CtrlGrp *ctrl = (*ite);
        if(ctrl->ctrl_id == ctrl_id)
            return true;
    }
    return false;
}

int PoolGroupBaseDev::get_polling_thread_id()
{
    if(polling_thread_id == 0)
    {
        Tango::Util *tg = Tango::Util::instance();
        polling_thread_id = tg->get_polling_thread_id_by_name(get_name().c_str());
    }
    return polling_thread_id;
}

}	//	namespace
