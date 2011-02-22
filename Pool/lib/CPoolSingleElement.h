#pragma once

#include "CPoolElement.h"

namespace Pool_ns
{
    
/**
 * A PoolElement directly for a single element (motor, counter, 0D, etc)
 */
struct SinglePoolElement : public PoolElement
{
    /** Wheater or not the Ctrl.AddDevice has been called for this element */
    bool                        add_device_done;

    /** The AddDevice error string in case an error occured during AddDevice */
    std::string                 add_device_error_str;

    /**
     * The default constructor
     */
    SinglePoolElement():
    PoolElement(),
    add_device_done(false), add_device_error_str("")
    {}

    /**
     * Constructor
     *
     * @param dp the pool of devices to which this element will belong
     * @param identif the element ID
     * @param n the element name
     */
    SinglePoolElement(DevicePool *dp, ElementId identif, const std::string &n):
    PoolElement(dp, identif, n),
    add_device_done(false), add_device_error_str("")
    {}

    inline void set_add_device_done(bool done = true, const std::string err = "")
    { 
        this->add_device_done = done; 
        this->add_device_error_str = err;
    }
    
    /**
     * Determines if the AddDevice was successfully done or not
     *
     * @return true if the AddDevice was successfully done or false otherwise
     */
    inline bool is_add_device_done()
    { return this->add_device_done; }
    
    inline const std::string &get_add_device_error_str()
    { return add_device_error_str; }

};

}
