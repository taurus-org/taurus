#include <CPool.h>
#include <MotionThread.h>

namespace Pool_ns
{

void MotionThread::setup(ElementId src, CtrlValueMap &pos)
{
    cleanup();
    for (CtrlValueMapIt cit = pos.begin(); cit != pos.end(); ++cit)
    {
        ControllerPool &ctrl = pool->get_controller(cit->first);
        ControllerPoolInMotion *ctrl_motion = new ControllerPoolInMotion(&ctrl);
        
        MotorInMotionVector &motors = positions[ctrl_motion];
        
        for (ValueMapIt vit = cit->second.begin(); vit != cit->second.end(); ++vit)
        {
            PoolElement *elem = pool->get_element(vit->first);
            MotorInMotion *motor_motion = new MotorInMotion(elem, vit->second);
            motors.push_back(motor_motion);
        }
        elem_nb += (int32_t)motors.size();
    }
}

void MotionThread::cleanup()
{
    for (CtrlInMotionMapIt cit = positions.begin(); cit != positions.end(); ++cit)
    {
        ControllerPoolInMotion *ctrl_motion = cit->first;
        SAFE_DELETE(ctrl_motion);
        for (MotorInMotionVectorIt mit = cit->second.begin(); mit != cit->second.begin(); ++mit)
        {
            MotorInMotion *motor_motion = *mit;
            SAFE_DELETE(motor_motion);
        }
    }
    positions.clear();
    elem_nb = 0;
}

void MotionThread::run(void *)
{
    try
    {
        move();
    }
    catch(PoolFailed &e)
    {
        PoolMonitor *monitor = get_notification_monitor();
        omni_mutex_lock lo(*monitor);
        monitor->signal();
    }
}

void MotionThread::move(bool wait_flag /*= true*/)
{
    send_to_ctrls(wait_flag);
    
//
// By now everything was sent to the controllers so the motors should have start
// moving already. 
// Leave method if we don't want to wait for the end of moving
//
    if (wait_flag == false)
        return;
    
    moving_loop();
    
    
}
    
void MotionThread::send_to_ctrls(bool wait_flag /*= true*/)
{
    int thread_id = omni_thread::self()->id();
    
    try
    {
        std::string except_func = "LockAllControllers";
        
        // register the motion thread id in all elements
        get_motion_src()->set_motion_thread(thread_id);
        
        // lock the controllers
        for(CtrlInMotionMapIt it = positions.begin(); it != positions.end(); ++it)
        {
            it->first->lock();
        }
        
        
        
    }
    catch(...)
    {}
}

void MotionThread::moving_loop()
{
    
}

}	// namespace_ns
