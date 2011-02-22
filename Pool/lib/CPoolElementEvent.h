#ifndef _CPOOL_ELEMENTEVENT_H_
#define _CPOOL_ELEMENTEVENT_H_

#include <iostream>
#include <list>

#include <CPoolDefs.h>

namespace Pool_ns 
{

/**
 * @brief Types of internal events
 *
 * StateChange - the state has changed
 * ElementStructureChange - the internal structure of an element changed.
 *                          Ex.: the controller code of a motor was reloaded.
 * ElementsChange - the list of elements changed. Ex.: a new motor was added
 *                  to a motor group
 * PositionChange - the position has changed
 * PositionArrayChange - the positions have changed
 * CTValueChange - the value of a counter timer changed
 * ZeroDValueChange - the value of a 0D channel changed
 * OneDValueChange - the value of a 1D channel changed
 * TwoDValueChange - the value of a 2D channel changed
 * PseudoCoValueChange - the value of a pseudo counter changed
 * MotionEnded - the position has changed for the last time. An event of
 *               this type is sent usually at the end of a motor,
 *                motor group, or pseudo motor motion
 * NameChange - the name of the element has changed
**/
enum PoolEventType
{
    StateChange = 0,
    ElementStructureChange,
    ElementListChange,
    PositionChange,
    PositionArrayChange,
    CTValueChange,
    ZeroDValueChange,
    OneDValueChange,
    TwoDValueChange,
    PseudoCoValueChange,
    MotionEnded,
    NameChange
};

struct PoolElement;

union Value
{
    double    value;
    double    position;
    double*   position_array;
    PoolState state;
    char*     name;
};


/**
 * The data related to an internal event inside the pool
 */
struct PoolElementEvent
{
    /** Type of event */
    PoolEventType           type;

    /** Element which originated the event */
    PoolElement*            src;

    /** number of elements (in case of a PositionArrayChange type of event) */
    int32_t                 dim;

    /** set to <code>true</code> if it is a priority event */
    bool                    priority;

    /** Union for the old value */
    Value                   old;

    /** union for the new value */
    Value                   curr;

    /**
     * Constructor for the PoolElementEvent class
     *
     * @param[in] evt_type type of event
     * @param[in] src_elem element which triggered the event
     */
    PoolElementEvent(PoolEventType evt_type, PoolElement* src_elem);

    /**
     * Copy constructor
     *
     * @param[in] rhs the original object
     */
    PoolElementEvent(const PoolElementEvent &rhs);

    inline PoolEventType get_type() { return type; }
    
    inline PoolElement *get_src() { return src; }
    
    inline int32_t get_dim() { return dim; }
    
    inline bool is_priority() { return priority; }
    
    inline const Value & get_old_value() { return old; }
    
    inline const Value & get_curr_value() { return curr; }

    std::ostream & printToStream(std::ostream &flux, int indent = 0) const;
};
typedef std::list<PoolElementEvent*> PoolElemEventList;

/**
 * The Pool Listener interface. Any object interested in receiving events must
 * implement this interface and register itself in the event supplier object.
 */
struct IPoolElementListener
{
    /**
     * Destructor
     */
    virtual ~IPoolElementListener()
    { }
    
    /**
     * Called when an event occurs.
     *
     * @param[in] evt stack of event data elements.
     */
    virtual void pool_elem_changed(PoolElemEventList &evt) = 0;
};

struct DelayedEvt
{
	PoolElement			*src;
	PoolElementEvent	evt;
	PoolElement			*exception;

	DelayedEvt(PoolEventType evt_type, PoolElement* src_elem):
		src(src_elem), evt(evt_type,src_elem), exception(NULL) 
	{}
	
	DelayedEvt(const DelayedEvt &rhs):
		src(rhs.src),evt(rhs.evt),exception(rhs.exception)
	{}
};

}

#endif // _CPOOL_ELEMENTEVENT_H_
