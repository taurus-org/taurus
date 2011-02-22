#ifndef _CPOOL_MEASUREMENTGROUP_H_
#define _CPOOL_MEASUREMENTGROUP_H_

#include "CPoolGroupElement.h"

namespace Pool_ns
{

/** 
 * Measurement group element
 */
struct MeasurementGroupPool : public PoolGroupElement
{
    /** list of physical channels */
    ElemIdVector               ch_ids;

    /**
     * Returns the type of element this object represents.
     * @see ElementType
     *
     * @return This element type
     */
    virtual ElementType get_type()
    { return MEASUREMENT_GROUP_ELEM; }

    /**
     * updates the user full name string
     */
    virtual void update_info();
};


}

#endif // _CPOOL_MOTORGROUP_H_
