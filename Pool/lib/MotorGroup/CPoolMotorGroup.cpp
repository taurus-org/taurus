#include "CPool.h"
#include "CPoolMotorGroup.h"
#include "CPoolPseudoMotor.h"
#include <algorithm>

namespace Pool_ns
{

//------------------------------------------------------------------------------
// MotorGroupPool::update_info
//
void MotorGroupPool::update_info() 
{
    user_full_name = get_name() + " (" + get_full_name() + ")";
    
    if(!device_pool)
        return;
    
    user_full_name += " Motor list: ";
    
    for(ElemIdVectorIt it = group_elts.begin(); it != group_elts.end(); ++it)
    {
        user_full_name += device_pool->get_element(*it)->get_name();
        if (it != group_elts.end() - 1)
            user_full_name += ", ";
    }
    
    user_full_name += " (";
    
    for(ElemIdVectorIt it = mot_ids.begin(); it != mot_ids.end(); ++it)
    {
        user_full_name += device_pool->get_element(*it)->get_name();
        if (it != mot_ids.end() - 1)
            user_full_name += ", ";
    }
    
    user_full_name += ")";
}

//------------------------------------------------------------------------------
// MotorGroupPool::is_member
//
bool MotorGroupPool::is_member(ElementId elem_id)
{
    if (PoolGroupElement::is_member(elem_id))
        return true;

    ElemIdVectorIt ite;
    for (ite = pm_elts.begin(); ite != pm_elts.end(); ++ite)
        if (device_pool->get_element(*ite)->is_member(elem_id))
            return true;

    for (ite = mg_elts.begin(); ite != mg_elts.end(); ++ite)
        if (device_pool->get_element(*ite)->is_member(elem_id))
            return true;

    return false;
}

//------------------------------------------------------------------------------
// MotorGroupPool::calc_move
//
void MotorGroupPool::calc_move(double *src, CtrlValueMap& dest)
{
    /**
     * Map where: 
     * key = Pseudo motor controller ID
     * value = map where key is pseudo motor ID and value is its assigned position
     */
    CtrlValueMap pm_ctrl_positions;
/*
    double *_pos = src;
    std::vector<ElementId>::iterator elem_it = _moveables.begin(), 
                                    elem_end = _moveables.end();
    for(; elem_it != elem_end; ++elem_it)
    {
        ElementId eid = *elem_it;
        PoolElement &pe = device_pool->get_element(eid);
        PoolMoveable &moveable = *static_cast<PoolMoveable*>(&pe);

        // Handle pseudo motors later
        if(pe.get_type() == PSEUDO_MOTOR_ELEM)
        {
            pm_ctrl_positions[pe.get_ctrl_id()][pe.get_id()] = _pos;
        }
        else
        {
            moveable.calc_move(_pos, dest);
        }
        _pos += moveable.get_size();
    }
    
    // Find out which pseudo motors are missing in each pseudo motor controller.
    // For each missing pseudo motor we have to get its current position value
    
    ValueMapIt pm_ctrl_it = pm_ctrl_positions.begin();
               pm_ctrl_end = pm_ctrl_positions.end();
    for(; pm_ctrl_it != pm_ctrl_end; ++pm_ctrl_it)
    {
        PseudoMotorPool &first_pm = 
            device_pool->get_pseudo_motor(pm_ctrl_it->second.begin()->first);
        MotorGroupPool &first_pm_motgrp =
            device_pool->get_motor_group(first_pm.get_motor_group_id());
        
        //
        
        ControllerPool &pm_ctrl_pool = device_pool->get_controller(pm_ctrl_it->first);
        PseudoMotorController *pm_ctrl = static_cast<PseudoMotorController*>
                (pm_ctrl_pool.ctrl);
                
    }
*/
}

//------------------------------------------------------------------------------
// MotorGroupPool::get_size
//
int32_t MotorGroupPool::get_size()
{
    return 1;
}

}
