#ifndef _CPOOL_ELEMENT_H_
#define _CPOOL_ELEMENT_H_

#include <iostream>
#include <list>

#include "CPoolElementEvent.h"
#include "CPoolData.h"
#include "CPoolObject.h"

class Controller;

namespace Pool_ns
{

class DevicePool;
class ControllerPool;

struct PoolElementProxy
{
    /**
     * The destructor
     */
    virtual ~PoolElementProxy()
    { }

    virtual void pool_elem_changed(PoolElemEventList &, PoolElementEvent &) = 0;
};

typedef std::list<IPoolElementListener*> IPoolElemListenerList;

/**
 * A generic element of the Pool. It implements a IPoolElementListener.
 *
 */
struct PoolElement: public PoolObject, public IPoolElementListener
{
protected:

    /** the index in the controller */
    int32_t                     axis;

    /** the controller identifier for which this element belongs to */
    ElementId                   ctrl_id;

    /** the instrument identifier for which this element belongs to */
    ElementId                   instrument_id;

    /* the controller pointer */
    ControllerPool*             ctrl;

    /** simulation mode */
    bool                        simulation_mode;

    /** list of listeners for this element */
    IPoolElemListenerList       pool_elem_listeners;

    /** a pointer to the external helper object */
    PoolElementProxy*           helper;

    /** The motion/acquisition monitor */
    PoolMonitor*                notif_mon;

    /** the serialization monitor */
    PoolMonitor*                ser_mon;

    /**
     * The following members are cache values for parameters whoose value
     * is obtained from the HW (controller)
     */
    PoolState                   state;

public:
     
    /**
     * The default constructor
     */
    PoolElement();

    /**
     * Constructor
     *
     * @param dp the pool of devices to which this element will belong
     * @param identif the element ID
     * @param n the element name
     */
    PoolElement(DevicePool *dp, ElementId identif, const std::string &n);

    /**
     * The destructor
     */
    virtual ~PoolElement();

    /**
     * Sets this element axis
     *
     * @param[in] axis the axis
     */
    inline void set_axis(int32_t axis)
    { this->axis = axis; }
    
    /**
     * Gets the element axis in the controller
     *
     * @return the element axis in the controller
     */
    inline int32_t get_axis() const
    { return axis; }

    /**
     * Sets the controller for this element
     *
     * @param[in] id id of the new controller
     */
    void set_ctrl_id(ElementId id);
    
    /**
     * Gets the controller ID
     *
     * @return the controller ID
     */
    inline ElementId get_ctrl_id() const
    { return ctrl_id; }

    /**
     * Sets the instrument for this element
     *
     * @param[in] id id of the new instrument
     */
    inline void set_instrument_id(ElementId id)
    { this->instrument_id = id; }
    
    /**
     * Gets the instrument ID
     *
     * @return the instrument ID
     */
    inline ElementId get_instrument_id() const
    { return instrument_id; }

    /**
     * Gets a reference to the controller object
     *
     * @return a reference to the controller object
     */
    inline ControllerPool *get_ctrl() const
    { return ctrl; }

    /**
     * Gets a reference to the controller object
     *
     * @return a reference to the controller object
     */
    virtual Controller *get_controller();
    
    /**
     * Gets the pointer to the notification monitor
     *
     * @return the pointer to the notification monitor
     */
    inline PoolMonitor* get_notification_monitor() const
    { return notif_mon; }

    /**
     * Gets the pointer to the serialization monitor
     *
     * @return the pointer to the serialization monitor
     */
    inline PoolMonitor* get_serialization_monitor() const
    { return ser_mon; }

    /**
     * Sets the element proxy for this element
     *
     * @param[in] proxy pointer to the element proxy
     */
    inline void set_proxy(PoolElementProxy *proxy)
    { helper = proxy; }

    /**
     * Gets the element proxy for this element
     *
     * @return the element proxy for this element
     */
    inline PoolElementProxy* get_proxy() const
    { return helper; }

    /**
     * Determines if in simulation mode
     * @return <code>true</code> if in simulation mode or
     *         <code>false</code> otherwise
     */
    inline bool get_simulation_mode() const
    { return simulation_mode; }
    
    /** 
     * Sets/Unsets simulation mode
     * @param[in] sim <code>true</code> to set simulation or <code>false</code>
     *            to switch it off
     */ 
    inline void set_simulation_mode(bool sim)
    { simulation_mode = sim; }

    /**
     * Appends the given listener to the list of listeners
     *
     * @param[in] listener the listener to be added.
     */
    void add_pool_elem_listener(IPoolElementListener *);

    /**
     * Removes the given listener from the list of listeners
     *
     * @param[in] listener the listener to be removed.
     */
    void remove_pool_elem_listener(IPoolElementListener *);

    /**
     * Determines if this element has any listeners.
     *
     * @return <code>true</code> if there are listeners or <code>false</code>
     *         otherwise
     */
    inline bool has_listeners() const
    { return !pool_elem_listeners.empty(); }

    /**
     * Returns a reference to the list of listeners.
     *
     * @return a reference to the list of listeners.
     */
    inline const IPoolElemListenerList& get_pool_elem_listeners() const
    { return pool_elem_listeners; }
    
    /**
     * Sets the list of listeners of this element
     *
     * @param[in] listeners the new list of listeners
     */
    inline void set_pool_elem_listeners(const IPoolElemListenerList& listeners)
    { this->pool_elem_listeners = listeners; }
    
    /**
     * Propagates the given event to all listeners of this element.
     *
     * @param[in] evt_data the event to be forwarded to the listeners.
     */
    void propagate_event(PoolElemEventList &);

    /**
     * Returns the type of element this object represents.
     * @see ElementType
     *
     * @return This element type
     */
    inline virtual ElementType get_type()
    { return UNDEF_ELEM; }

    /**
     * Returns a string representing the type of element.
     * @see ElementType
     *
     * @return This element type string
     */
    inline const char * get_type_str()
    { return ElementTypeStr[get_type()]; }

    /**
     * Determines if the given element id is part of this element. Default
     * implementation always returns false.
     *
     * @param[in] elem_id the element id to be checked.
     *
     * @return <code>true</code> if the given element is part of this element
     *         or <code>false</code> otherwise
     */
    inline virtual bool is_member(ElementId elem_id)
    { return false; }

    /**
     * Determines if the given element name is part of this element.
     *
     * @param[in] elt the element name to be checked.
     *
     * @return <code>true</code> if the given element is part of this element
     *         or <code>false</code> otherwise
     */
    bool is_member(std::string &elt);

    /**
     * Returns the list of elements that are part of this element or NULL if
     * this element does not have any elements.
     *
     * @return list of elements that are part of this element or NULL.
     */
    inline virtual ElemIdVector *get_elems()
    { return NULL; }

    /**
     * IPoolElementListener interface implementation. Called when an event
     * occurs.
     *
     * @param[in] evt stack of event data elements.
     */
    virtual void pool_elem_changed(PoolElemEventList &evt);

    /**
     * Fires an event to all listeners.
     *
     * @param[in] evt     the event data
     * @param[in] exclude optional element to be exclude from the event.
     *                     (default is NULL - meaning no listener is excluded)
     * @param[in] handle_exceptions handles all exceptions internally.
     *                     (default is true - meaning no exception is thrown)
     */
    void fire_pool_elem_change(PoolElementEvent *evt,
                               IPoolElementListener *exclude = NULL,
                               bool handle_exceptions = true);

    /**
     * updates the user full name string
     */
    virtual void update_info();

    /**
     * Get the state as it is stored in cache
     *
     * @return the state of this element
     */
    inline PoolState get_state() const
    { return this->state; }
    
    
protected:

    virtual void init();

};

inline bool PoolElemNameSort(const PoolElement *p1, const PoolElement *p2)
{
    return p1->get_name() < p2->get_name();
}

struct PoolElemIdSorter
{
    inline bool operator()(const PoolElement *p1, const PoolElement *p2) const
    {
        return p1->get_id() < p2->get_id();
    }
};

typedef std::vector<PoolElement*>                ElemVector;
typedef ElemVector::iterator                     ElemVectorIt;
typedef ElemVector::const_iterator               ElemVectorCIt;

typedef std::set<PoolElement*, PoolElemIdSorter> ElemSet;
typedef ElemSet::iterator                        ElemSetIt;
typedef ElemSet::const_iterator                  ElemSetCIt;

typedef std::map<ElementId, PoolElement*>        ElemIdMap;
typedef ElemIdMap::iterator                      ElemIdMapIt;
typedef ElemIdMap::const_iterator                ElemIdMapCIt;

typedef std::map<ElementType, ElementId>         ElemTypeMap;
typedef ElemTypeMap::iterator                    ElemTypeMapIt;
typedef ElemTypeMap::const_iterator              ElemTypeMapCIt;

typedef std::multimap<ElementType, ElementId>    ElemTypeMultiMap;
typedef ElemTypeMultiMap::iterator               ElemTypeMultiMapIt;
typedef ElemTypeMultiMap::const_iterator         ElemTypeMultiMapCIt;

typedef std::map<std::string, ElementId, StringEqualsIgnoreCase> ElemNameMap;
typedef ElemNameMap::iterator                                    ElemNameMapIt;
typedef ElemNameMap::const_iterator                              ElemNameMapCIt;



}

#endif // _CPOOL_ELEMENT_H_

